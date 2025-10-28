# MCP Client Guide

간단한 MCP 클라이언트를 사용하여 YouTube Summary MCP Server와 상호작용하는 방법을 설명합니다.

## 🚀 Quick Start

### 1. 기본 실행 (자동으로 서버 시작)

```bash
# 클라이언트만 실행하면 서버가 자동으로 시작됨
uv run client.py
```

**출력:**
```
============================================================
  🎬 YouTube Summary MCP Client
============================================================

📋 Available Tools:
============================================================

🔧 get_transcript
   Description: Fetch the transcript of a YouTube video
   Input Schema:
     - video_url: (required)
     - language: (optional)

🔧 summarize_video
   Description: Generate a summary of a YouTube video
   Input Schema:
     - video_url: (required)
     - summary_length: (optional)
     - language: (optional)
...
```

### 2. 인터랙티브 모드 (권장)

```bash
uv run client.py --interactive
```

**사용 방법:**
```
> list                          # 사용 가능한 도구 목록
> get_transcript <url>          # 트랜스크립트 가져오기
> summarize_video <url> medium  # 요약 생성
> extract_key_points <url> 5    # 핵심 포인트 추출
> get_video_metadata <url>      # 메타데이터 조회
> quit                          # 종료
```

## 📝 사용 예제

### 예제 1: 트랜스크립트 가져오기

**수동으로 서버 실행하는 경우:**
```bash
# 터미널 1: 서버 시작
uv run youtube-summary-mcp

# 터미널 2: 클라이언트 실행
uv run client.py
```

**인터랙티브 모드에서:**
```
> get_transcript https://www.youtube.com/watch?v=HQU2vbsbXkU en
```

**출력:**
```
🚀 Calling: get_transcript
   Arguments: {
     "video_url": "https://www.youtube.com/watch?v=HQU2vbsbXkU",
     "language": "en"
   }
============================================================

📄 Transcript (first 200 chars):
Never gonna give you up, never gonna let you down...
```

### 예제 2: 비디오 요약

```bash
> summarize_video https://www.youtube.com/watch?v=HQU2vbsbXkU short
```

**출력:**
```
🚀 Calling: summarize_video
   Arguments: {
     "video_url": "https://www.youtube.com/watch?v=HQU2vbsbXkU",
     "summary_length": "short"
   }
============================================================

📊 Summary (short):
The song is about never giving up and staying loyal...
```

### 예제 3: 핵심 포인트 추출

```bash
> extract_key_points https://www.youtube.com/watch?v=HQU2vbsbXkU 3
```

**출력:**
```
🚀 Calling: extract_key_points
   Arguments: {
     "video_url": "https://www.youtube.com/watch?v=HQU2vbsbXkU",
     "num_points": 3
   }
============================================================

🎯 Key Points:
1. Never gonna give you up
2. Never gonna let you down
3. Never gonna run around and desert you
```

### 예제 4: 메타데이터 조회

```bash
> get_video_metadata https://www.youtube.com/watch?v=HQU2vbsbXkU
```

**출력:**
```
🚀 Calling: get_video_metadata
   Arguments: {
     "video_url": "https://www.youtube.com/watch?v=HQU2vbsbXkU"
   }
============================================================

📹 Result:
Video ID: HQU2vbsbXkU
Title: Rick Astley - Never Gonna Give You Up
Channel: Rick Astley
Views: 1000000000+
```

## 🎯 지원하는 URL 형식

모든 도구는 다양한 YouTube URL 형식을 지원합니다:

```bash
# 긴 URL
> get_transcript https://www.youtube.com/watch?v=HQU2vbsbXkU

# 짧은 URL
> get_transcript https://youtu.be/HQU2vbsbXkU

# 임베드 URL
> get_transcript https://www.youtube.com/embed/HQU2vbsbXkU

# 비디오 ID만
> get_transcript HQU2vbsbXkU
```

## 🌍 지원하는 언어

기본값은 영어('en')입니다. 다른 언어 코드를 사용할 수 있습니다:

```bash
# 영어 (기본값)
> get_transcript <url> en

# 한국어
> get_transcript <url> ko

# 스페인어
> get_transcript <url> es

# 프랑스어
> get_transcript <url> fr

# 독일어
> get_transcript <url> de

# 일본어
> get_transcript <url> ja

# 중국어
> get_transcript <url> zh
```

## 📊 요약 길이 옵션

```bash
# 짧음 (20% of original)
> summarize_video <url> short

# 중간 (35% of original, 기본값)
> summarize_video <url> medium

# 김 (50% of original)
> summarize_video <url> long
```

## ⚙️ 클라이언트 아키텍처

### 모드 1: 자동 서버 시작

```
클라이언트 실행
    ↓
stdio를 통해 서버 프로세스 시작
    ↓
MCP 세션 생성
    ↓
도구 목록 조회 및 예제 실행
    ↓
종료
```

### 모드 2: 인터랙티브

```
클라이언트 실행 (--interactive)
    ↓
서버 자동 시작
    ↓
사용자 입력 대기
    ↓
명령 해석 및 도구 호출
    ↓
결과 출력
    ↓
반복 (quit 입력 시 종료)
```

## 🔧 클라이언트 코드 구조

```python
# 주요 함수:

list_tools(session)
  └─ 사용 가능한 모든 도구 목록 표시

call_tool(session, tool_name, arguments)
  └─ 도구 호출 및 결과 반환

get_transcript_example(session)
  └─ 트랜스크립트 예제

summarize_video_example(session)
  └─ 요약 예제

extract_key_points_example(session)
  └─ 핵심 포인트 예제

get_metadata_example(session)
  └─ 메타데이터 예제

interactive_mode(session)
  └─ 인터랙티브 사용자 입력 처리
```

## 🐛 문제 해결

### 에러: "연결할 수 없음"

```bash
# 해결책 1: 서버를 수동으로 시작
uv run youtube-summary-mcp

# 해결책 2: 클라이언트 다시 실행
uv run client.py
```

### 에러: "Invalid JSON-RPC message"

이는 정상입니다. 서버가 stdin을 모니터링하고 있다는 의미입니다.

```bash
# 클라이언트를 사용하여 제대로 통신
uv run client.py --interactive
```

### 에러: "No module named 'mcp'"

```bash
# 의존성 재설치
uv sync
```

### YouTube API 오류 (No transcript)

- 비디오에 자막이 없을 수 있음
- 비공개 비디오일 수 있음
- 라이브 스트림일 수 있음

다른 비디오를 시도해보세요.

## 📚 추가 예제

### Python으로 직접 호출

```python
import asyncio
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.client.session import ClientSession

async def main():
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "youtube-summary-mcp"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 도구 호출
            result = await session.call_tool(
                "summarize_video",
                {
                    "video_url": "https://www.youtube.com/watch?v=HQU2vbsbXkU",
                    "summary_length": "short",
                }
            )
            print(result.content[0].text)

asyncio.run(main())
```

### 배치 처리

```python
# 여러 비디오 한 번에 처리
videos = [
    "https://www.youtube.com/watch?v=...",
    "https://www.youtube.com/watch?v=...",
    "https://www.youtube.com/watch?v=...",
]

for video_url in videos:
    print(f"Processing: {video_url}")
    # 위의 예제처럼 call_tool 사용
```

## 🎓 학습 리소스

- **README.md** - 전체 API 문서
- **QUICKSTART.md** - 빠른 시작 가이드
- **DEVELOPMENT.md** - 아키텍처 및 확장 방법
- **server.py** - MCP 서버 구현 보기

## 📞 지원

- 문제 발생 시 `.venv` 가상 환경 확인
- 의존성 문제는 `uv sync` 실행
- 포트 충돌 확인 (기본값 사용)

---

**Happy Testing! 🚀**
