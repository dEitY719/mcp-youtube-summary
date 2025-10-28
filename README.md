# YouTube Summary MCP Server

A powerful MCP (Model Context Protocol) server for summarizing YouTube videos with transcript fetching, intelligent summarization, key point extraction, and metadata retrieval. Built with **FastMCP** for simple, decorator-based tool registration and automatic MCP protocol handling.

**[한국어 문서](README_ko.md) | English Documentation**

---

## 📋 프로젝트 개요

이 프로젝트는 MCP(Model Context Protocol)를 통해 YouTube 비디오의 트랜스크립트를 가져오고, 자동으로 요약하며, 핵심 포인트를 추출하는 서버입니다. Claude Desktop, Cursor 등 MCP를 지원하는 AI 클라이언트에서 YouTube 비디오를 직접 분석할 수 있습니다.

---

## 🎯 주요 기능

- **📝 트랜스크립트 추출**: YouTube 비디오에서 자막 텍스트 추출 (4가지 URL 형식 지원)
- **📊 지능형 요약**: 다양한 길이의 요약 생성 (짧음, 중간, 긴 버전)
- **✨ 핵심 포인트 추출**: TF-IDF 기반 자동 핵심 문장 추출
- **🎬 메타데이터 조회**: 비디오 제목, 채널, 조회수 등 정보 제공
- **🌍 다국어 지원**: 7개 언어 지원 (영어, 한국어, 스페인어, 프랑스어, 독일어, 일본어, 중국어)
- **⚡ FastMCP 프레임워크**: 데코레이터 기반의 간단한 구현
- **🔒 오류 처리**: 포괄적인 에러 처리 및 로깅
- **🏗️ SOLID 원칙**: 확장 가능한 아키텍처

---

## 🏗️ 아키텍처

### 시스템 구성도

```
┌─────────────────────────┐      ┌──────────────────────┐      ┌─────────────┐
│   AI Client             │◄────►│   MCP Server         │◄────►│  YouTube    │
│   (Claude, Cursor, etc) │      │   (FastMCP Python)   │      │  API        │
└─────────────────────────┘      └──────────────────────┘      └─────────────┘
                                           │
                                           ▼
                                  ┌──────────────────┐
                                  │ Core Components  │
                                  │ - Transcript API │
                                  │ - Summarizer     │
                                  │ - Metadata       │
                                  └──────────────────┘
```

### 핵심 컴포넌트

1. **MCP Server Core** (`server.py`)
   - MCP 프로토콜 구현 (FastMCP 사용)
   - 클라이언트와의 통신 관리
   - 요청/응답 처리

2. **Transcript Retriever** (`transcript_retriever.py`)
   - YouTube 트랜스크립트 추출
   - 다양한 URL 형식 지원
   - 언어 자동 감지 및 폴백

3. **Summary Generator** (`summary_generator.py`)
   - TF-IDF 기반 텍스트 요약
   - 핵심 포인트 자동 추출
   - 다국어 스톱워드 지원

4. **Metadata Extractor** (`metadata_extractor.py`)
   - 비디오 메타데이터 추출
   - 썸네일 URL 생성

5. **Config Manager** (`config_manager.py`)
   - Pydantic 기반 설정 관리
   - 환경 변수 지원

---

## 🛠️ 기술 스택

| 카테고리 | 기술 |
|---------|------|
| **언어** | Python 3.10+ |
| **MCP 프레임워크** | FastMCP (Model Context Protocol) |
| **YouTube 처리** | youtube-transcript-api |
| **자연언어처리** | NLTK (TF-IDF, stopwords) |
| **설정 관리** | Pydantic, Pydantic Settings |
| **패키지 관리** | uv |
| **테스트** | pytest |
| **타입 체킹** | mypy |
| **코드 포매팅** | black, ruff |

---

## 📁 프로젝트 구조

```
youtube-summary-mcp/
├── youtube_summary_mcp/           # 메인 패키지
│   ├── __init__.py                # 패키지 초기화
│   ├── server.py                  # FastMCP 서버 구현
│   ├── main.py                    # 진입점
│   ├── config_manager.py          # 설정 관리 (Pydantic)
│   ├── transcript_retriever.py    # 트랜스크립트 추출
│   ├── summary_generator.py       # 텍스트 요약 엔진
│   └── metadata_extractor.py      # 메타데이터 추출
│
├── tests/                         # 테스트 스위트
│   ├── test_config_manager.py     # 설정 테스트
│   ├── test_transcript_retriever.py
│   ├── test_summary_generator.py
│   └── test_metadata_extractor.py
│
├── pyproject.toml                 # 프로젝트 설정
├── .env.example                   # 환경 변수 템플릿
├── .gitignore                     # Git 무시 파일
└── README.md                      # 이 파일
```

---

## 🚀 설치 및 설정

### 1️⃣ 사전 요구사항

```bash
# 필수
- Python 3.10 이상
- uv 패키지 관리자

# 선택사항 (향상된 메타데이터를 위해)
- YouTube Data API Key
```

### 2️⃣ 의존성 설치

```bash
# 프로젝트 디렉토리로 이동
cd youtube-summary-mcp

# 의존성 설치 및 환경 구성
uv sync
```

**설치되는 주요 패키지:**
- `mcp>=0.1.0` - Model Context Protocol
- `youtube-transcript-api>=0.6.1` - YouTube 트랜스크립트
- `pydantic>=2.0.0` - 데이터 검증
- `nltk>=3.9.2` - 자연언어처리

### 3️⃣ 환경 변수 설정 (선택사항)

`.env.example`을 복사하여 `.env` 파일을 생성합니다:

```bash
cp .env.example .env
```

**`.env` 파일 내용:**

```bash
# 로깅 설정
LOG_LEVEL=INFO                    # DEBUG, INFO, WARNING, ERROR, CRITICAL

# 요약 설정
SUMMARY_RATIO=0.35               # 원본의 35% 길이로 요약

# 서버 설정
SERVER_NAME=YouTube Summary MCP
SERVER_VERSION=0.1.0
```

---

## ⚡ 빠른 설정 (Quick Setup)

설정 파일만 수정하면 바로 사용 가능합니다!

### Claude Desktop 설정 (claude_desktop_config.json)

**Windows:**
```json
{
  "mcpServers": {
    "youtube-summary": {
      "command": "python",
      "args": ["-m", "youtube_summary_mcp.main"],
      "env": {
        "PYTHONPATH": "C:\\path\\to\\youtube-summary-mcp"
      }
    }
  }
}
```

**macOS/Linux:**
```json
{
  "mcpServers": {
    "youtube-summary": {
      "command": "python3",
      "args": ["-m", "youtube_summary_mcp.main"],
      "env": {
        "PYTHONPATH": "/path/to/youtube-summary-mcp"
      }
    }
  }
}
```

### Cursor 설정 (cursor_mcp_config.json 또는 settings.json)

```json
{
  "mcp": {
    "servers": [
      {
        "id": "youtube-summary",
        "name": "YouTube Summary",
        "type": "command",
        "command": "python",
        "args": ["-m", "youtube_summary_mcp.main"],
        "env": {
          "PYTHONPATH": "/path/to/youtube-summary-mcp"
        }
      }
    ]
  }
}
```

**설정 파일 위치:**
- **Claude Desktop (Windows)**: `C:\Users\[사용자명]\AppData\Roaming\Claude\claude_desktop_config.json`
- **Claude Desktop (macOS)**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Claude Desktop (Linux)**: `~/.config/Claude/claude_desktop_config.json`
- **Cursor (모든 OS)**: 설정 → MCP 섹션 또는 `~/.config/Cursor/User/settings.json`

> 💡 **팁**: `/path/to/youtube-summary-mcp` 부분을 실제 프로젝트 경로로 바꾸세요!

---

## 🔧 MCP 클라이언트 설정 (매우 중요!)

### 📌 MCP란?

**Model Context Protocol (MCP)**는 AI 모델이 외부 도구와 리소스에 접근하는 표준 방식입니다. 클라이언트 설정을 통해 Claude, Cursor 등이 YouTube Summary MCP 서버에 접근할 수 있습니다.

### ⚙️ Claude Desktop 설정

#### Windows

1. **Claude Desktop 설정 파일 열기:**
   ```
   C:\Users\[사용자명]\AppData\Roaming\Claude\claude_desktop_config.json
   ```

2. **다음 내용 추가 또는 수정:**
   ```json
   {
     "mcpServers": {
       "youtube-summary": {
         "command": "python",
         "args": ["-m", "youtube_summary_mcp.main"],
         "env": {
           "PYTHONPATH": "C:\\path\\to\\youtube-summary-mcp"
         }
       }
     }
   }
   ```

   **또는 절대 경로 사용:**
   ```json
   {
     "mcpServers": {
       "youtube-summary": {
         "command": "C:\\Python310\\python.exe",
         "args": [
           "C:\\path\\to\\youtube-summary-mcp\\youtube_summary_mcp\\main.py"
         ]
       }
     }
   }
   ```

#### macOS

1. **Claude Desktop 설정 파일 열기:**
   ```bash
   ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

2. **다음 내용 추가 또는 수정:**
   ```json
   {
     "mcpServers": {
       "youtube-summary": {
         "command": "python3",
         "args": ["-m", "youtube_summary_mcp.main"],
         "env": {
           "PYTHONPATH": "/path/to/youtube-summary-mcp"
         }
       }
     }
   }
   ```

#### Linux

1. **Claude Desktop 설정 파일 열기:**
   ```bash
   ~/.config/Claude/claude_desktop_config.json
   ```

2. **다음 내용 추가 또는 수정:**
   ```json
   {
     "mcpServers": {
       "youtube-summary": {
         "command": "python3",
         "args": ["-m", "youtube_summary_mcp.main"],
         "env": {
           "PYTHONPATH": "/home/username/path/to/youtube-summary-mcp"
         }
       }
     }
   }
   ```

3. **Claude Desktop 재시작**

---

### 🎨 Cursor IDE 설정

#### Windows/macOS/Linux 통일

1. **Cursor 설정 파일 열기:**
   - **Windows**: `C:\Users\[사용자명]\AppData\Roaming\Cursor\User\settings.json`
   - **macOS**: `~/Library/Application Support/Cursor/User/settings.json`
   - **Linux**: `~/.config/Cursor/User/settings.json`

2. **다음 설정 추가:**
   ```json
   {
     "mcp": {
       "servers": [
         {
           "id": "youtube-summary",
           "name": "YouTube Summary",
           "type": "command",
           "command": "python",
           "args": ["-m", "youtube_summary_mcp.main"],
           "env": {
             "PYTHONPATH": "/path/to/youtube-summary-mcp"
           }
         }
       ]
     }
   }
   ```

---

### 📌 VS Code (with MCP Extension)

1. **VS Code MCP 확장 설치:**
   - "Model Context Protocol" 검색하여 설치

2. **VS Code 설정 열기** (`Ctrl+,` 또는 `Cmd+,`)

3. **settings.json 수정:**
   ```json
   {
     "mcp.servers": {
       "youtube-summary": {
         "command": "python",
         "args": ["-m", "youtube_summary_mcp.main"],
         "env": {
           "PYTHONPATH": "/path/to/youtube-summary-mcp"
         }
       }
     }
   }
   ```

---

### 🔍 설정 확인 및 문제 해결

#### 1. 서버가 정상적으로 시작하는지 확인

```bash
# 터미널에서 직접 실행하여 로그 확인
uv run youtube-summary-mcp
```

정상이면 다음과 같은 로그가 나타납니다:
```
2025-10-28 14:59:48,114 - youtube_summary_mcp.server - INFO - Initialized YouTube Summary MCP v0.1.0
```

#### 2. 설정 파일 경로 확인

```bash
# Windows (PowerShell)
$env:APPDATA\Claude\claude_desktop_config.json

# macOS/Linux
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
# 또는
cat ~/.config/Claude/claude_desktop_config.json
```

#### 3. Python 경로 확인

```bash
# Python이 올바른 버전인지 확인
python --version          # Python 3.10 이상 필요

# uv를 통한 실행
which uv                  # uv 설치 위치 확인
uv python list           # 설치된 Python 버전 확인
```

#### 4. Claude Desktop에서 도구 표시 확인

- Claude Desktop을 시작한 후 채팅창에서 "🔧 도구" 버튼 클릭
- "YouTube Summary" 서버가 표시되는지 확인
- 각 도구 (get_transcript, summarize_video 등)가 나열되는지 확인

---

## 📊 사용 가능한 도구 (Tools)

### 1. **get_transcript** 📝

YouTube 비디오의 트랜스크립트를 추출합니다.

**매개변수:**
- `video_url` (필수): YouTube URL 또는 비디오 ID
- `language` (선택): 언어 코드 (기본값: "en")

**지원 URL 형식:**
```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://youtu.be/dQw4w9WgXcQ
https://www.youtube.com/embed/dQw4w9WgXcQ
dQw4w9WgXcQ  (ID만)
```

**지원 언어:**
- `en` - 영어
- `ko` - 한국어
- `es` - 스페인어
- `fr` - 프랑스어
- `de` - 독일어
- `ja` - 일본어
- `zh` - 중국어

**응답 예시:**
```json
{
  "success": true,
  "transcript": "Never gonna give you up, never gonna let you down..."
}
```

---

### 2. **summarize_video** 📊

YouTube 비디오의 자동 요약을 생성합니다.

**매개변수:**
- `video_url` (필수): YouTube URL 또는 비디오 ID
- `summary_length` (선택): 요약 길이 (기본값: "medium")
  - `short` - 원본의 약 20%
  - `medium` - 원본의 약 35%
  - `long` - 원본의 약 50%
- `language` (선택): 언어 코드 (기본값: "en")

**응답 예시:**
```json
{
  "success": true,
  "summary": "이 영상은 유명한 팝 뮤직 비디오입니다...",
  "length": "medium"
}
```

---

### 3. **extract_key_points** ✨

비디오 트랜스크립트에서 핵심 포인트를 자동 추출합니다.

**매개변수:**
- `video_url` (필수): YouTube URL 또는 비디오 ID
- `num_points` (선택): 추출할 핵심 포인트 개수 (기본값: 5)
- `language` (선택): 언어 코드 (기본값: "en")

**응답 예시:**
```json
{
  "success": true,
  "key_points": [
    "Never gonna give you up",
    "Never gonna let you down",
    "Never gonna desert you"
  ],
  "count": 3
}
```

---

### 4. **get_video_metadata** 🎬

YouTube 비디오의 메타데이터를 조회합니다.

**매개변수:**
- `video_url` (필수): YouTube URL 또는 비디오 ID

**응답 예시:**
```json
{
  "success": true,
  "metadata": "Video ID: dQw4w9WgXcQ\nTitle: Rick Astley - Never Gonna Give You Up (Official Video)\nChannel: Unknown\nViews: None"
}
```

---

## 💻 사용 예제

### Claude Desktop에서 사용

1. **Claude Desktop 열기**
2. **새로운 채팅 시작**
3. **대화창에 요청:**

```
"이 비디오의 요약을 만들어줄 수 있을까?
https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

Claude가 자동으로 YouTube Summary MCP 도구를 사용하여 비디오를 분석합니다.

### Cursor에서 사용

1. **Cursor 편집기 열기**
2. **chat.md 또는 새로운 파일 생성**
3. **MCP 채팅 시작**
4. **다음과 같이 요청:**

```
"YouTube 비디오를 요약해줄 수 있을까?
https://youtu.be/dQw4w9WgXcQ

핵심 포인트 5개도 함께 추출해줘."
```

---

## 🔒 보안 및 개인정보

- **로컬 처리**: 모든 데이터는 로컬에서만 처리됩니다
- **no API Key 필요**: YouTube 트랜스크립트 API는 무료로 사용 가능합니다
- **데이터 캐싱 안 함**: 기본적으로 트랜스크립트 캐싱을 하지 않습니다
- **로깅**: 민감한 정보는 로그에 기록되지 않습니다

---

## 🧪 테스트

```bash
# 모든 테스트 실행
uv run pytest tests/

# 특정 테스트 파일 실행
uv run pytest tests/test_summary_generator.py -v

# 커버리지와 함께 실행
uv run pytest tests/ --cov=youtube_summary_mcp
```

---

## 🔧 개발

### 코드 스타일

```bash
# 코드 포매팅
uv run black youtube_summary_mcp/ tests/

# Linting
uv run ruff check youtube_summary_mcp/ tests/

# 타입 체킹
uv run mypy youtube_summary_mcp/
```

---

## 📈 성능 정보

| 작업 | 소요 시간 |
|------|---------|
| 서버 시작 | ~1.8초 |
| 트랜스크립트 추출 | 5-10초 (비디오 길이에 따라) |
| 요약 생성 | ~1초 |
| 핵심 포인트 추출 | ~0.5초 |
| 메타데이터 조회 | ~2초 |

---

## 🐛 문제 해결

### 서버가 시작되지 않는 경우

```bash
# 1. 직접 실행하여 에러 메시지 확인
uv run youtube-summary-mcp

# 2. Python 버전 확인 (3.10 이상 필요)
python --version

# 3. 의존성 재설치
uv sync --refresh
```

### "Tool not found" 오류

- Claude Desktop/Cursor를 완전히 종료 후 재시작
- 설정 파일의 JSON 형식 확인 (쉼표, 따옴표 등)

### 트랜스크립트를 가져올 수 없음

- 비디오에 자막이 있는지 확인
- 인기 있는 비디오는 대부분 자막이 있습니다
- 정확한 URL 형식 사용

---

## 📚 문서

더 자세한 정보는 다음 파일을 참고하세요:

- [FASTMCP_REFACTORING.md](FASTMCP_REFACTORING.md) - FastMCP로의 마이그레이션 상세 보고서
- [QUICKSTART.md](QUICKSTART.md) - 5분 빠른 시작 가이드
- [USE_CLIENT.md](USE_CLIENT.md) - 클라이언트 사용법
- [DEVELOPMENT.md](DEVELOPMENT.md) - 개발자 가이드

---

## 📋 지원 언어 및 형식

### 언어
- 영어, 한국어, 스페인어, 프랑스어, 독일어, 일본어, 중국어

### YouTube URL 형식
- 표준: `https://www.youtube.com/watch?v=VIDEO_ID`
- 단축: `https://youtu.be/VIDEO_ID`
- 임베드: `https://www.youtube.com/embed/VIDEO_ID`
- ID만: `VIDEO_ID`

### 요약 길이
- 짧음 (20%), 중간 (35%), 긴 버전 (50%)

---

## 🎓 버전 정보

- **현재 버전**: 0.2.0 (FastMCP)
- **이전 버전**: 0.1.0 (Low-level MCP)
- **상태**: 🟢 Production Ready

---

## 📝 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능합니다.

---

## 🤝 기여

버그 리포트, 기능 요청, 풀 리퀘스트를 환영합니다!

---

## 📞 지원

문제가 발생하면:

1. 문서를 다시 확인하세요
2. 에러 로그를 확인하세요
3. 설정 파일 형식을 검증하세요

---

**Happy Summarizing! 🚀**
