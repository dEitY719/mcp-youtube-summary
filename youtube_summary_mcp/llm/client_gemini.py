"""LangChain 에이전트가 MCP tool을 사용하는 예제."""

import asyncio
import json
import logging

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from youtube_summary_mcp.llm.gemini_llm_factory import GeminiLLMFactory


load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    """LangChain 에이전트가 MCP tool을 사용하여 YouTube 영상을 분석합니다."""

    # Gemini LLM 초기화
    llm_factory = GeminiLLMFactory()
    llm = llm_factory.get_llm(temperature=0.3)

    # 개별 MCP tool 함수들을 import
    from youtube_summary_mcp.transcript_retriever import TranscriptRetriever
    from youtube_summary_mcp.summary_generator import SummaryGenerator
    from youtube_summary_mcp.metadata_extractor import MetadataExtractor

    # 컴포넌트 초기화
    transcript_retriever = TranscriptRetriever()
    summary_generator = SummaryGenerator()
    metadata_extractor = MetadataExtractor()

    # LangChain tool로 변환할 도구들을 정의 (sync 버전)
    @tool("get_transcript")
    def get_transcript_tool(
        video_url: str, language: str = "en"
    ) -> str:
        """Extract transcript from YouTube video."""
        try:
            logger.info(f"자막 추출 중: {video_url}")
            transcript = transcript_retriever.get_transcript(video_url, language)
            if not transcript:
                return json.dumps(
                    {
                        "success": False,
                        "error": "이 영상의 자막을 찾을 수 없습니다",
                    },
                    ensure_ascii=False,
                )
            return json.dumps(
                {"success": True, "transcript": transcript},
                ensure_ascii=False,
            )
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
            logger.info(f"영상 요약 중: {video_url}")
            transcript = transcript_retriever.get_transcript(video_url, language)
            if not transcript:
                return json.dumps(
                    {
                        "success": False,
                        "error": "이 영상의 자막을 찾을 수 없습니다",
                    },
                    ensure_ascii=False,
                )
            summary = summary_generator.generate_summary_with_length(
                transcript, summary_length
            )
            if not summary:
                return json.dumps(
                    {
                        "success": False,
                        "error": "요약을 생성할 수 없습니다",
                    },
                    ensure_ascii=False,
                )
            return json.dumps(
                {"success": True, "summary": summary, "length": summary_length},
                ensure_ascii=False,
            )
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
            logger.info(f"핵심 포인트 추출 중: {video_url}")
            transcript = transcript_retriever.get_transcript(video_url, language)
            if not transcript:
                return json.dumps(
                    {
                        "success": False,
                        "error": "이 영상의 자막을 찾을 수 없습니다",
                    },
                    ensure_ascii=False,
                )
            key_points = summary_generator.extract_key_points(
                transcript, num_points
            )
            if not key_points:
                return json.dumps(
                    {
                        "success": False,
                        "error": "핵심 포인트를 추출할 수 없습니다",
                    },
                    ensure_ascii=False,
                )
            return json.dumps(
                {"success": True, "key_points": key_points, "count": len(key_points)},
                ensure_ascii=False,
            )
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
            logger.info(f"메타데이터 조회 중: {video_url}")
            video_id = metadata_extractor.extract_video_id(video_url)
            metadata = metadata_extractor.get_basic_metadata(video_id)
            formatted = metadata_extractor.format_metadata(metadata)
            return json.dumps(
                {"success": True, "metadata": formatted},
                ensure_ascii=False,
            )
        except Exception as e:
            logger.error(f"메타데이터 조회 오류: {str(e)}")
            return json.dumps(
                {"success": False, "error": f"오류: {str(e)}"},
                ensure_ascii=False,
            )

    # LangChain tool 목록
    langchain_tools = [
        get_transcript_tool,
        summarize_video_tool,
        extract_key_points_tool,
        get_video_metadata_tool,
    ]

    logger.info(f"사용 가능한 MCP tool: {[t.name for t in langchain_tools]}")

    # 시스템 프롬프트
    system_prompt = """당신은 YouTube 영상 분석 전문가입니다.

사용자가 제공한 YouTube URL의 영상을 분석하기 위해 다음 도구들을 활용합니다:
- summarize_video: 영상을 요약합니다
- extract_key_points: 영상의 핵심 포인트를 추출합니다
- get_video_metadata: 영상의 제목, 채널, 길이 등 메타데이터를 조회합니다
- get_transcript: 영상의 자막을 추출합니다

사용자의 요청에 가장 적절한 도구를 선택하여 호출하세요.
모든 응답은 한국어로 제공하세요."""

    # LangChain 1.0.1의 create_agent 사용
    agent_graph = create_agent(
        model=llm,
        tools=langchain_tools,
        system_prompt=system_prompt,
        debug=False,
    )

    # YouTube URL
    youtube_url = "https://www.youtube.com/watch?v=HQU2vbsbXkU"

    # Agent 실행
    logger.info(f"YouTube 영상 분석 시작: {youtube_url}")

    # 메시지 형식 (LangChain 1.0.1)
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

    logger.info("분석 중...")
    print("\n" + "=" * 60)
    print("YouTube 영상 분석 결과")
    print("=" * 60)

    try:
        # 에이전트 실행
        result = await asyncio.get_event_loop().run_in_executor(
            None, agent_graph.invoke, {"messages": messages}
        )

        # 최종 메시지 추출 (여러 메시지 중 마지막 AI 응답)
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

        logger.info("분석 완료")

    except Exception as e:
        logger.error(f"에이전트 실행 오류: {str(e)}", exc_info=True)
        print(f"오류 발생: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())