# MCP 클라이언트 사용 가이드

## 🚀 빠른 시작

### 1. 기본 모드 (자동 서버 시작)

```bash
# 4개의 예제가 자동으로 실행됨
uv run simple_client.py
```

### 2. 인터랙티브 모드 (권장)

```bash
# 대화형 모드에서 도구를 직접 호출
uv run simple_client.py --interactive
```

---

## 📋 클라이언트 출력 분석

### 정상 작동 확인

```
============================================================
  🎬 YouTube Summary MCP - Simple Client
============================================================
🚀 Starting server...
✅ Server started
🔧 Initializing MCP connection...
✅ MCP connection initialized

📋 Available Tools
============================================================

🔧 get_transcript
🔧 summarize_video
🔧 extract_key_points
🔧 get_video_metadata
```

**상태**: ✅ **정상** - 모든 도구가 등록됨

---

## 🎯 인터랙티브 모드 사용법

### 명령어 목록

```
> help                                    # 도움말 표시
> list                                    # 도구 목록 보기
> get_transcript <url> [lang]            # 트랜스크립트 가져오기
> summarize <url> [short|medium|long]    # 비디오 요약
> key_points <url> [num]                 # 핵심 포인트 추출
> metadata <url>                         # 메타데이터 조회
> quit                                   # 종료
```

### 실제 사용 예제

#### 예제 1: 트랜스크립트 가져오기

```bash
> get_transcript https://www.youtube.com/watch?v=HQU2vbsbXkU en

📤 Request: {"jsonrpc": "2.0", "id": ..., "method": "tools/call", ...}

📄 Result:
Never gonna give you up, never gonna let you down...
```

#### 예제 2: 비디오 요약

```bash
> summarize https://www.youtube.com/watch?v=HQU2vbsbXkU short

📤 Request: {"jsonrpc": "2.0", "id": ..., "method": "tools/call", ...}

📊 Result:
The video is about a person promising...
```

#### 예제 3: 핵심 포인트 추출

```bash
> key_points https://www.youtube.com/watch?v=HQU2vbsbXkU 3

📤 Request: {"jsonrpc": "2.0", "id": ..., "method": "tools/call", ...}

🎯 Result:
1. Never gonna give you up
2. Never gonna let you down
3. Never gonna desert you
```

#### 예제 4: 메타데이터 조회

```bash
> metadata https://www.youtube.com/watch?v=HQU2vbsbXkU

📤 Request: {"jsonrpc": "2.0", "id": ..., "method": "tools/call", ...}

📹 Result:
Video ID: HQU2vbsbXkU
Title: Rick Astley - Never Gonna Give You Up (Official Video)
Channel: Rick Astley
Views: 1000000000+
Description: Official music video for "Never Gonna Give You Up" by Rick Astley
```

---

## 🔍 실행 결과 분석

### 성공한 요청

```
📤 Request: {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}

🔧 get_transcript
   Description: Fetch the transcript of a YouTube video
   Parameters:
     - video_url: (required)
     - language: (optional)
```

**상태**: ✅ **성공** - 도구 정보 반환됨

### 실패한 요청 (트랜스크립트 없음)

```
📤 Request: {"jsonrpc": "2.0", "id": 3, "method": "tools/call", ...}

📄 Transcript (first 200 chars):
Error: Failed to fetch transcript: ...
```

**상태**: ⚠️ **예상된 오류** - 일부 비디오에는 자막이 없을 수 있음

**해결책**: 다른 비디오 URL 시도

### 성공한 메타데이터 조회

```
📹 Result:
Video ID: HQU2vbsbXkU
Title: Rick Astley - Never Gonna Give You Up (Official Video) (4K Remaster)
Channel: Unknown
Views: None
Upload Date: None
```

**상태**: ✅ **성공** - 비디오 ID와 제목 반환됨

---

## 📊 URL 형식

모든 명령은 다양한 YouTube URL 형식을 지원합니다:

```bash
# 표준 URL
> get_transcript https://www.youtube.com/watch?v=HQU2vbsbXkU

# 단축 URL
> get_transcript https://youtu.be/HQU2vbsbXkU

# 임베드 URL
> get_transcript https://www.youtube.com/embed/HQU2vbsbXkU

# 비디오 ID만
> get_transcript HQU2vbsbXkU
```

---

## 🌍 언어 코드

```bash
# 지원되는 언어:
en  - 영어 (기본값)
ko  - 한국어
es  - 스페인어
fr  - 프랑스어
de  - 독일어
ja  - 일본어
zh  - 중국어

# 예:
> get_transcript <url> ko    # 한국어
> get_transcript <url> es    # 스페인어
```

---

## 📊 요약 길이 옵션

```bash
# short: 원본의 약 20%
> summarize <url> short

# medium: 원본의 약 35% (기본값)
> summarize <url> medium

# long: 원본의 약 50%
> summarize <url> long
```

---

## ⚙️ 클라이언트 구조

### SimpleMCPClient 클래스

```python
class SimpleMCPClient:
    def __init__(self, command)      # 클라이언트 초기화
    def start()                      # 서버 시작 및 초기화
    def send_request(method, params) # JSON-RPC 요청 전송
    def list_tools()                 # 도구 목록 조회
    def call_tool(name, arguments)   # 도구 호출
    def close()                      # 연결 종료
```

### 통신 프로토콜

```
클라이언트                 서버
    │
    ├─→ initialize request
    ←─┤ initialize response
    │
    ├─→ tools/list request
    ←─┤ tools/list response (도구 목록)
    │
    ├─→ tools/call request (도구명 + 인자)
    ←─┤ tools/call response (결과)
    │
    └─→ (repeat for each tool call)
```

---

## 🐛 문제 해결

### 문제 1: "연결 거부"

```
❌ Error: Connection refused
```

**해결책:**
```bash
# 포트가 이미 사용 중일 수 있음
# 기존 서버 종료 후 재시도
uv run simple_client.py
```

### 문제 2: "Invalid request parameters"

```
❌ Error: Invalid request parameters
```

**원인**: 초기화 전에 도구 호출
**해결책**: 자동으로 초기화되므로 재시도

### 문제 3: "No transcript available"

```
⚠️ Skipped: No transcript available for this video
```

**원인**: 비디오에 자막이 없음
**해결책**: 다른 비디오 시도 (가장 인기있는 비디오들은 자막이 있음)

### 문제 4: "Type mismatch"

```
❌ Error: type object 'YouTubeTranscriptApi' has no attribute 'get_transcript'
```

**원인**: youtube-transcript-api 버전 호환성
**해결책:**
```bash
uv pip install --upgrade youtube-transcript-api
```

---

## 💡 팁 & 트릭

### 팁 1: 브라우저에서 URL 복사

YouTube 비디오 브라우저에서:
1. 주소창의 URL 복사
2. 클라이언트에 붙여넣기

### 팁 2: 배치 처리

```bash
# 파일에서 URL 읽기
for url in $(cat urls.txt); do
  echo "URL: $url"
  # 스크립트로 처리
done
```

### 팁 3: 재시작 없이 다시 실행

```bash
> quit              # 인터랙티브 모드 종료
> uv run simple_client.py --interactive  # 다시 시작
```

---

## 📈 성능 정보

| 작업 | 소요 시간 |
|------|---------|
| 서버 시작 | ~2초 |
| MCP 초기화 | ~0.1초 |
| 도구 목록 조회 | ~0.1초 |
| 트랜스크립트 가져오기 | 수초 (비디오 길이에 따라) |
| 요약 생성 | ~1초 |
| 메타데이터 조회 | ~2초 |

---

## 🎓 다음 단계

1. **다양한 비디오 시도**: 인기 있는 비디오들은 자막이 있음
2. **다양한 언어 시도**: 한국어 등 다른 언어 자막 시도
3. **스크립트 개발**: Python에서 클라이언트 임포트 및 활용
4. **Claude 통합**: Claude와 함께 MCP 사용

---

**Happy Exploring! 🎬**
