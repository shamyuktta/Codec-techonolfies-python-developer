# Automated Resume Parser - Starter Project

Minimal starter for a resume parsing microservice.

## Features
- Flask API with `/upload` endpoint
- Basic text extraction for PDF / DOCX
- Simple contact + skills matching (uses `skills.csv`)
- PostgreSQL (SQLAlchemy) model
- Docker + docker-compose example

## Quick start (Docker)
```bash
git clone <this-repo>
cd resume_parser_starter
docker-compose up --build
```
The API will be at http://localhost:5000. Upload a file with `curl`:
```bash
curl -F "file=@/path/to/resume.pdf" http://localhost:5000/upload
```

## Virtualenv quick-start (no Docker)
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# ensure a Postgres DB is available and DATABASE_URL env var set, or run with sqlite by modifying config.py
python app.py
```

## Notes
- This is a starter scaffold. You should harden file handling, add background workers for heavy parsing, add tests, and improve NER/skill matching.
