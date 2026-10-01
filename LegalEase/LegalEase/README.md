# LegalEase — AI-Powered Legal Document Generator

LegalEase is a complete FastAPI + Streamlit application for generating,
editing, previewing, and exporting AI-assisted legal document drafts.

## Features

- FastAPI backend with `/generate`, `/health`, and export endpoints
- Streamlit frontend
- Google Gemini integration using the current `google-genai` SDK
- Configurable Gemini model
- Demo mode when no Gemini API key is configured
- Editable generated document
- TXT, DOCX, and PDF export
- DOCX branding with logo and footer
- PDF branding with logo and footer
- Input validation
- CORS configuration
- Automated API/export tests
- Docker support

## Architecture

```text
LegalEase/
├── app/
│   ├── ai_core/
│   │   └── gemini_generator.py
│   ├── services/
│   │   └── document_service.py
│   ├── config.py
│   ├── routes.py
│   ├── schemas.py
│   └── main.py
├── frontend/
│   └── app.py
├── assets/
│   └── legalease_logo.png
├── tests/
├── .env.example
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── Procfile
```

## Requirements

- Python 3.11 or 3.12 recommended
- VS Code
- Internet connection for Gemini generation
- Gemini API key for AI mode

## Local setup

### Windows PowerShell

```powershell
cd LegalEase

py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt

Copy-Item .env.example .env
```

Open `.env` and set:

```env
GEMINI_API_KEY=your_real_key
GEMINI_MODEL=gemini-2.5-flash
```

### Windows CMD

```bat
cd LegalEase
py -3.12 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
```

## Run the backend

Open VS Code Terminal 1:

```powershell
.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Test:

- API root: http://127.0.0.1:8000/
- Health: http://127.0.0.1:8000/health
- Swagger UI: http://127.0.0.1:8000/docs

## Run the frontend

Open VS Code Terminal 2:

```powershell
.venv\Scripts\Activate.ps1
streamlit run frontend/app.py
```

Open the URL Streamlit prints, normally:

```text
http://localhost:8501
```

## Demo mode

The application intentionally works without an API key so you can test the
frontend, FastAPI routes, editing, and file exports first.

If `GEMINI_API_KEY` is empty, `/generate` returns a clearly marked local demo
document instead of pretending an AI model was called.

## Test the project

```powershell
pytest -q
```

Expected result: all tests pass.

## API example

```http
POST /generate
Content-Type: application/json
```

```json
{
  "document_type": "Freelance Work Contract",
  "parties": "Jane Doe (Service Provider), TechNova Inc. (Client)",
  "terms": "Payment within 30 days; confidentiality; 15 day termination notice",
  "dates": "April 15, 2026",
  "language": "English"
}
```

## Important AI/legal safety behavior

The generator is instructed not to invent material facts and to use
`[TO BE COMPLETED]` placeholders when required information is missing.
Generated content is AI-assisted drafting, not legal advice. Users should
have the final document reviewed by a qualified legal professional.

## Docker

Create `.env` first, then:

```powershell
docker compose up --build
```

Frontend:
http://localhost:8501

Backend:
http://localhost:8000/docs

## Deployment

The project includes a `Procfile` and Dockerfile. In production, deploy the
FastAPI backend and Streamlit frontend as separate services when your hosting
provider expects separate processes. Store `GEMINI_API_KEY` as a secret rather
than committing `.env`.

## Troubleshooting

### `uvicorn is not recognized`

Activate the virtual environment and run:

```powershell
python -m uvicorn app.main:app --reload
```

### `streamlit is not recognized`

Run:

```powershell
python -m streamlit run frontend/app.py
```

### Gemini error

Check:

1. `.env` exists in the project root.
2. `GEMINI_API_KEY` is valid.
3. `GEMINI_MODEL` is a model available to your API account.
4. Restart the backend after changing `.env`.

### Port already in use

Backend:

```powershell
python -m uvicorn app.main:app --reload --port 8001
```

Then set:

```env
BACKEND_URL=http://127.0.0.1:8001
```

for the frontend process.

## Source specification mapping

This implementation follows the supplied LegalEase specification:
FastAPI backend, Streamlit frontend, Gemini generation, editable preview,
and TXT/DOCX/PDF output, with logo/footer branding.
