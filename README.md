# Mine Tuning Title Server

A Django REST Framework API that uses `Qwen3.5-4B` to generate a concise
English title from a chat question and answer.

## API

### `GET /api/health/`

```json
{
  "status": "ok",
  "model": "Qwen/Qwen3.5-4B",
  "loaded": true
}
```

### `POST /api/titles/`

Request:

```json
{
  "question": "How do I mine diamonds?",
  "answer": "Search around Y level -59."
}
```

Response:

```json
{
  "title": "Mining Diamonds",
  "source": "model",
  "model": "Qwen/Qwen3.5-4B"
}
```

If model loading or generation fails, `source` is set to `fallback`.

## Run

```powershell
cd C:\Users\SSAFY\Desktop\rladbcks\title-api-server-
.\venv\Scripts\Activate.ps1
python manage.py runserver 127.0.0.1:8100 --noreload
```

Set `TITLE_MODEL_EAGER_LOAD=true` in `.env` to load the model when the server
starts.

## Test

```powershell
python manage.py test
python manage.py check
```
