# ClipForge

ClipForge generates ready-to-post TikTok/Reels videos from a Spocket CSV export + product images (no scraping).

## Stack
- Backend: FastAPI + SQLModel (SQLite)
- Video: FFmpeg via safe subprocess invocation
- Frontend: Next.js + TypeScript + Tailwind
- Assets: Local filesystem under `backend/data`

## Folder Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/routes.py
│   │   ├── core/db.py
│   │   ├── services/{copygen.py,quality.py,queue.py,templates.py,video.py}
│   │   ├── main.py
│   │   └── models.py
│   ├── data/{audio,exports,uploads}
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/app/{globals.css,layout.tsx,page.tsx}
│   ├── src/lib/api.ts
│   ├── package.json
│   └── Dockerfile
├── sample_data/
│   ├── spocket_sample.csv
│   └── images/{1001,1002,1003}
├── docker-compose.yml
└── README.md
```

## Run (Docker)

```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs

## Run (Local)

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Quick Start Data Seed
1. Open ClipForge UI.
2. Go to **Library** -> **Import CSV** and upload `sample_data/spocket_sample.csv`.
3. Upload image sets to each product using `POST /api/products/{id}/images` (or add upload button in UI).
4. Select products, choose template, and generate queue jobs.

## Features Implemented
- Product library grid with CSV import
- 3 reusable templates (8-12s)
- Rule-based hooks/benefits/CTA generation (no external LLM)
- Brand Voice settings: tone, banned phrases, preferred CTAs
- Batch queue + status polling + retry endpoint
- Variant generator (up to 3 variants/product)
- Quality controls: safe-area warning, repeated-word detection, low-res warnings, auto-trimming
- FFmpeg vertical video render (1080x1920), Ken Burns zoom, burned captions + SRT
- Posting pack storage: caption/hashtags/hooks/cta + file location
- Music placeholder: accepts user-uploaded audio files only

## Compliance
- No Spocket scraping logic included.
- No copyrighted music or platform logos bundled.
