# SSE MCP 클라이언트 가이드

## 현재 상황

### ✅ 작동하는 방식 (Stdio)
```bash
uv run python client_gemini_working.py
```

**장점:**
- 즉시 작동
- LangChain + Gemini 완벽 통합
- 실제 YouTube 영상 분석 가능

---

## ❌ SSE 방식의 문제점

### 로그 분석
```
POST /messages HTTP/1.1" 307 Temporary Redirect
POST /messages/ HTTP/1.1" 400 Bad Request
Received request without session_id
```

### 근본 원인
1. **단순 HTTP POST vs MCP 프로토콜**: 완전히 다른 통신 방식
2. **session_id 부재**: MCP는 양방향 세션이 필수
3. **클라이언트 SDK 부정확**: `requests`로는 불가능, MCP SDK 필요

---

## SSE 방식 개선 방법

### 올바른 MCP SSE 클라이언트 구현

```python
import asyncio
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession

async def test_sse():
    # FastMCP SSE 서버에 연결 (비동기)
    async with sse_client("http://localhost:10719/sse") as session:
        # 도구 목록 조회
        tools = await session.list_tools()
        print(f"도구: {[t.name for t in tools.tools]}")

        # 도구 호출
        result = await session.call_tool(
            "get_video_metadata",
            {"video_url": "https://www.youtube.com/watch?v=..."}
        )
        print(result)

# 실행
asyncio.run(test_sse())
```

### LangChain 통합 (비동기 wrapper 필요)

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
from langchain_core.tools import tool

class AsyncMCPWrapper:
    def __init__(self):
        self.loop = None
        self.executor = ThreadPoolExecutor(max_workers=1)

    async def _async_call(self, method, **kwargs):
        # MCP SSE 호출 로직
        pass

    def call(self, method, **kwargs):
        # asyncio를 별도 스레드에서 실행
        future = asyncio.run_coroutine_threadsafe(
            self._async_call(method, **kwargs),
            self.loop
        )
        return future.result()

@tool()
def get_metadata(video_url: str) -> str:
    """Get video metadata"""
    wrapper = AsyncMCPWrapper()
    return wrapper.call("get_video_metadata", video_url=video_url)
```

---

## 권장 방안

### 지금 (즉시)
```bash
# stdio 방식 사용 - 완벽 작동
uv run python client_gemini_working.py
```

### 향후 (선택사항)
1. **MCP 공식 클라이언트 SDK** 사용 확인
   ```bash
   python -c "from mcp.client.sse import sse_client; help(sse_client)"
   ```

2. **FastMCP 문서** 확인
   - SSE의 정확한 엔드포인트
   - session_id 관리 방법
   - JSON-RPC vs MCP 프로토콜

3. **비동기 wrapper** 구현
   - asyncio를 별도 스레드에서 실행
   - LangChain과의 호환성 확보

---

## 파일 구조

| 파일 | 상태 | 설명 |
|------|------|------|
| `client_gemini_working.py` | ✅ 작동 | stdio 방식 (권장) |
| `client_sse_gemini.py` | ⚠️ 미작동 | SSE 방식 (개선 필요) |
| `youtube_summary_mcp/server.py` | ✅ 작동 | stdio MCP 서버 |
| `youtube_summary_mcp/server_sse.py` | ✅ 작동 | SSE MCP 서버 |

---

## 결론

**현재**: stdio 방식의 클라이언트(`client_gemini_working.py`)를 사용하세요.
- LLM과 MCP 통합이 완벽하게 작동합니다.
- YouTube 영상 분석 기능을 모두 사용할 수 있습니다.

**향후**: MCP 프로토콜을 더 깊이 이해한 후 SSE 방식을 개선할 수 있습니다.
- 이는 선택사항이며 긴급하지 않습니다.
