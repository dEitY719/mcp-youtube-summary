"""SSE MCP 클라이언트 연결 테스트."""

import logging
import sys
from client_sse_gemini import SSEMCPClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_sse_connection() -> bool:
    """Test SSE MCP server connection."""
    print("\n" + "=" * 60)
    print("SSE MCP 클라이언트 연결 테스트")
    print("=" * 60)

    mcp_client = SSEMCPClient(sse_url="http://localhost:10719/sse")

    try:
        print("\n1. SSE MCP 서버 연결 시도...")
        mcp_client.connect()
        print("   ✓ 연결 성공!")

        # 도구 목록 확인
        if mcp_client.tools:
            print(f"\n2. 사용 가능한 도구: {list(mcp_client.tools.keys())}")
            print(f"   ✓ {len(mcp_client.tools)}개 도구 로드됨")
        else:
            print("   ✗ 도구를 로드하지 못했습니다")
            return False

        # 간단한 도구 호출 테스트
        print("\n3. get_video_metadata 도구 테스트...")
        try:
            result = mcp_client.call_tool(
                "get_video_metadata",
                video_url="https://www.youtube.com/watch?v=HQU2vbsbXkU",
            )
            print(f"   ✓ 도구 호출 성공!")
            print(f"   결과: {result[:100]}..." if len(result) > 100 else f"   결과: {result}")
        except Exception as e:
            print(f"   ✗ 도구 호출 실패: {str(e)}")
            return False

        print("\n" + "=" * 60)
        print("✓ 모든 테스트 통과!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n✗ 연결 오류: {str(e)}")
        print("\n💡 팁: SSE MCP 서버가 실행 중인지 확인하세요")
        print("  터미널에서 다음 명령어를 실행하세요:")
        print("  uv run youtube-summary-mcp-sse")
        return False

    finally:
        try:
            mcp_client.disconnect()
        except Exception as e:
            logger.error(f"연결 해제 오류: {str(e)}")


if __name__ == "__main__":
    success = test_sse_connection()
    sys.exit(0 if success else 1)
