"""SSE 방식의 MCP 서버를 사용하는 LangChain 에이전트 예제.

이 클라이언트는 SSE로 실행 중인 YouTube Summary MCP 서버에 연결하여
LangChain 에이전트가 MCP 도구를 사용하도록 합니다.

사전 요구사항:
1. SSE 서버 실행: `uv run youtube-summary-mcp-sse`
2. 환경 변수 설정: `export GOOGLE_API_KEY=your_key`
"""

import json
import logging
import requests
from typing import Any, Optional

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from youtube_summary_mcp.llm.gemini_llm_factory import GeminiLLMFactory


load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SSEMCPClient:
    """SSE 방식의 MCP 서버와 통신하는 HTTP 기반 클라이언트."""

    def __init__(self, sse_url: str = "http://localhost:10719/sse"):
        """
        Initialize SSE MCP client.

        Args:
            sse_url: SSE MCP server URL (default: http://localhost:10719/sse)
        """
        self.sse_url = sse_url
        self.base_url = sse_url.rstrip("/sse")  # http://localhost:10719
        self.tools: dict[str, Any] = {}
        self._connected = False
        self._request_id = 1

    def connect(self) -> None:
        """Connect to SSE MCP server and load tools."""
        try:
            logger.info(f"SSE MCP 서버에 연결 중: {self.sse_url}")

            # 헬스체크
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code not in [200, 404]:  # 404는 엔드포인트가 없을 수 있음
                logger.warning(f"SSE 서버 헬스체크 상태: {response.status_code}")

            # 도구 목록 가져오기 (JSON-RPC 호출 - HTTP POST)
            # FastMCP는 /sse 엔드포인트에서 JSON-RPC를 처리합니다
            tools_list = self._call_mcp_method("tools/list", {})

            if tools_list and "tools" in tools_list:
                tool_names = [t.get("name") for t in tools_list["tools"]]
                logger.info(f"사용 가능한 도구: {tool_names}")
                self._connected = True
            else:
                logger.warning("도구 목록을 가져올 수 없습니다")
                self._connected = True  # 여전히 연결된 것으로 간주

        except Exception as e:
            logger.error(f"SSE 연결 오류: {str(e)}", exc_info=True)
            raise

    def disconnect(self) -> None:
        """Disconnect from SSE MCP server."""
        self._connected = False
        logger.info("SSE 연결 해제됨")

    def _call_mcp_method(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        """Call MCP method via HTTP POST to SSE server."""
        try:
            # JSON-RPC 요청 구성
            request_payload = {
                "jsonrpc": "2.0",
                "id": self._request_id,
                "method": method,
                "params": params,
            }
            self._request_id += 1

            logger.debug(f"MCP 요청: {method} {params}")

            # HTTP POST 요청 (SSE 서버의 JSON-RPC 엔드포인트)
            # FastMCP는 /message 엔드포인트를 제공할 수 있습니다
            headers = {"Content-Type": "application/json"}

            # 먼저 /messages 엔드포인트 시도
            try:
                response = requests.post(
                    f"{self.base_url}/messages",
                    json=request_payload,
                    headers=headers,
                    timeout=10,
                )
                if response.status_code == 200:
                    result = response.json()
                    if "result" in result:
                        return result["result"]
                    return result
            except Exception as e:
                logger.debug(f"/messages 엔드포인트 실패: {str(e)}")

            # 다른 엔드포인트 시도
            raise RuntimeError(
                "SSE 서버의 JSON-RPC 엔드포인트를 찾을 수 없습니다"
            )

        except Exception as e:
            logger.error(f"MCP 메서드 호출 오류: {str(e)}", exc_info=True)
            raise

    def call_tool(self, tool_name: str, **kwargs: Any) -> str:
        """Call a tool on the MCP server."""
        if not self._connected:
            raise RuntimeError("Not connected. Call connect() first")

        try:
            logger.info(f"도구 호출: {tool_name} with args {kwargs}")

            # JSON-RPC를 통해 도구 호출
            result = self._call_mcp_method(
                "tools/call",
                {
                    "name": tool_name,
                    "arguments": kwargs,
                },
            )

            return json.dumps(
                {"success": True, "result": result},
                ensure_ascii=False,
            )

        except Exception as e:
            logger.error(f"도구 호출 오류 ({tool_name}): {str(e)}", exc_info=True)
            return json.dumps(
                {"success": False, "error": str(e)},
                ensure_ascii=False,
            )


def main() -> None:
    """SSE MCP 서버를 사용하는 LangChain 에이전트 실행."""

    # SSE MCP 클라이언트 초기화
    mcp_client = SSEMCPClient(sse_url="http://localhost:10719/sse")

    try:
        # SSE 서버에 연결 (블로킹)
        logger.info("SSE MCP 서버 연결 시도...")
        mcp_client.connect()
        logger.info("SSE MCP 서버 연결 성공")

        # Gemini LLM 초기화
        llm_factory = GeminiLLMFactory()
        llm = llm_factory.get_llm(temperature=0.3)

        # LangChain 도구 정의 - SSE 서버의 도구를 래핑
        @tool("get_transcript")
        def get_transcript_tool(video_url: str, language: str = "en") -> str:
            """Extract transcript from YouTube video."""
            try:
                logger.info(f"자막 추출 중 (SSE): {video_url}")
                result = mcp_client.call_tool(
                    "get_transcript", video_url=video_url, language=language
                )
                return result
            except Exception as e:
                logger.error(f"자막 추출 오류: {str(e)}")
                return json.dumps(
                    {"success": False, "error": f"오류: {str(e)}"},
                    ensure_ascii=False,
                )

        @tool("summarize_video")
        def summarize_video_tool(
            video_url: str, summary_length: str = "medium", language: str = "en"
        ) -> str:
            """Summarize a YouTube video."""
            try:
                logger.info(f"영상 요약 중 (SSE): {video_url}")
                result = mcp_client.call_tool(
                    "summarize_video",
                    video_url=video_url,
                    summary_length=summary_length,
                    language=language,
                )
                return result
            except Exception as e:
                logger.error(f"요약 오류: {str(e)}")
                return json.dumps(
                    {"success": False, "error": f"오류: {str(e)}"},
                    ensure_ascii=False,
                )

        @tool("extract_key_points")
        def extract_key_points_tool(
            video_url: str, num_points: int = 5, language: str = "en"
        ) -> str:
            """Extract key points from a YouTube video."""
            try:
                logger.info(f"핵심 포인트 추출 중 (SSE): {video_url}")
                result = mcp_client.call_tool(
                    "extract_key_points",
                    video_url=video_url,
                    num_points=num_points,
                    language=language,
                )
                return result
            except Exception as e:
                logger.error(f"핵심 포인트 추출 오류: {str(e)}")
                return json.dumps(
                    {"success": False, "error": f"오류: {str(e)}"},
                    ensure_ascii=False,
                )

        @tool("get_video_metadata")
        def get_video_metadata_tool(video_url: str) -> str:
            """Get metadata of a YouTube video."""
            try:
                logger.info(f"메타데이터 조회 중 (SSE): {video_url}")
                result = mcp_client.call_tool("get_video_metadata", video_url=video_url)
                return result
            except Exception as e:
                logger.error(f"메타데이터 조회 오류: {str(e)}")
                return json.dumps(
                    {"success": False, "error": f"오류: {str(e)}"},
                    ensure_ascii=False,
                )

        # LangChain 도구 목록
        langchain_tools = [
            get_transcript_tool,
            summarize_video_tool,
            extract_key_points_tool,
            get_video_metadata_tool,
        ]

        logger.info(f"SSE MCP 도구 로드됨: {[t.name for t in langchain_tools]}")

        # 시스템 프롬프트
        system_prompt = """당신은 YouTube 영상 분석 전문가입니다.

사용자가 제공한 YouTube URL의 영상을 분석하기 위해 다음 도구들을 활용합니다:
- summarize_video: 영상을 요약합니다
- extract_key_points: 영상의 핵심 포인트를 추출합니다
- get_video_metadata: 영상의 제목, 채널, 길이 등 메타데이터를 조회합니다
- get_transcript: 영상의 자막을 추출합니다

사용자의 요청에 가장 적절한 도구를 선택하여 호출하세요.
모든 응답은 한국어로 제공하세요."""

        # LangChain 에이전트 생성
        agent_graph = create_agent(
            model=llm,
            tools=langchain_tools,
            system_prompt=system_prompt,
            debug=False,
        )

        # YouTube URL
        youtube_url = "https://www.youtube.com/watch?v=HQU2vbsbXkU"

        # 에이전트 실행
        logger.info(f"YouTube 영상 분석 시작 (SSE MCP): {youtube_url}")

        # 메시지 형식
        messages = [
            HumanMessage(
                content=f"""다음 YouTube 영상을 분석해주세요:
URL: {youtube_url}

요청사항:
1. 영상의 요약
2. 핵심 포인트 5개
3. 영상의 메타데이터 (제목, 채널, 길이 등)"""
            )
        ]

        logger.info("SSE MCP를 통한 분석 중...")
        print("\n" + "=" * 60)
        print("YouTube 영상 분석 결과 (SSE MCP)")
        print("=" * 60)

        try:
            # 에이전트 실행 (동기)
            result = agent_graph.invoke({"messages": messages})

            # 최종 메시지 추출
            if "messages" in result:
                final_messages = result["messages"]
                # 역순으로 탐색하여 마지막 AI 메시지 찾기
                for msg in reversed(final_messages):
                    if hasattr(msg, "type") and msg.type == "ai":
                        content = msg.content
                        # content가 list인 경우 처리
                        if isinstance(content, list):
                            for item in content:
                                if isinstance(item, dict) and "text" in item:
                                    print(f"\n{item['text']}")
                                else:
                                    print(f"\n{item}")
                        else:
                            print(f"\n{content}")
                        break

            logger.info("SSE MCP 분석 완료")

        except Exception as e:
            logger.error(f"에이전트 실행 오류: {str(e)}", exc_info=True)
            print(f"오류 발생: {str(e)}")

    except Exception as e:
        logger.error(f"SSE 클라이언트 오류: {str(e)}", exc_info=True)
        print(f"연결 오류: {str(e)}")
        print("\n💡 팁: SSE MCP 서버가 실행 중인지 확인하세요")
        print("  터미널 1에서 다음 명령어를 실행하세요:")
        print("  uv run youtube-summary-mcp-sse")
        print("\n  그 후 다시 이 스크립트를 실행하세요.")

    finally:
        # 연결 해제
        try:
            mcp_client.disconnect()
        except Exception as e:
            logger.error(f"연결 해제 오류: {str(e)}")


if __name__ == "__main__":
    main()
