# Mine Tuning Title Server

`Qwen3.5-0.8B`로 첫 질문과 첫 답변을 요약해 채팅방 제목을 반환하는 Django REST Framework API 서버입니다.

## API

### `GET /api/health/`

```json
{
  "status": "ok",
  "model": "Qwen/Qwen3.5-0.8B",
  "loaded": false
}
```

### `POST /api/titles/`

요청:

```json
{
  "question": "다이아는 어떻게 캐?",
  "answer": "다이아몬드는 Y -59 부근에서 찾기 좋습니다."
}
```

응답:

```json
{
  "title": "다이아몬드 채굴법",
  "source": "model",
  "model": "Qwen/Qwen3.5-0.8B"
}
```

모델 로드 또는 추론에 실패하면 `source`는 `fallback`이 됩니다.

## 실행

```powershell
cd C:\Users\SSAFY\Desktop\rladbcks\title_server
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py runserver 127.0.0.1:8100
```

첫 제목 요청 시 모델이 다운로드되고 메모리에 로드됩니다. 서버 시작 시 미리 로드하려면 `.env`에 다음 값을 사용합니다.

```env
TITLE_MODEL_EAGER_LOAD=true
```

실제 모델 저장소 ID가 다르면 `TITLE_MODEL_ID`만 변경하면 됩니다.

## 테스트

```powershell
python manage.py test
python manage.py check
```

