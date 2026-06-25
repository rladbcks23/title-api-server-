# Mine Tuning Title Server

A Django REST Framework API that can use `Qwen3.5-0.8B` to generate a concise
English title from a chat question and answer.

## API

### `GET /api/health/`

```json
{
  "status": "ok",
  "model_enabled": false,
  "model": "Qwen/Qwen3.5-0.8B",
  "loaded": false
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
  "model": "Qwen/Qwen3.5-0.8B"
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

Install the optional local model dependencies with:

```powershell
pip install -r requirements-model.txt
```

## Deploy to Render

This repository includes `render.yaml` for a free Render Web Service. The
Render deployment disables the local Qwen model because the free instance does
not have enough memory. The API remains available and returns deterministic
fallback titles.

1. Push these files to GitHub.
2. In Render, select **New > Blueprint**.
3. Connect this repository and apply the detected `render.yaml`.
4. Wait for the health check at `/api/health/` to pass.

The deployed endpoints are:

```text
GET  https://<service-name>.onrender.com/api/health/
POST https://<service-name>.onrender.com/api/titles/
```

To run the same lightweight mode locally:

```powershell
$env:TITLE_MODEL_ENABLED="false"
python manage.py runserver
```

## Test

```powershell
python manage.py test
python manage.py check
```
