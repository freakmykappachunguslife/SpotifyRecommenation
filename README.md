# Gago Glazers – CS125 Search & Similarity API

Minimal music search and similarity: **Spotify Web API** (search + track + audio features) + **FastAPI** with 3 endpoints + **cosine similarity** on audio features (in-memory, no database).

---

## ⚠️ Security

**Do not commit Spotify credentials.**

1. Copy env example and add your secrets locally:
   ```bash
   copy .env.example .env
   ```
2. Set in `.env`:
   - `SPOTIFY_CLIENT_ID` – from [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - `SPOTIFY_CLIENT_SECRET`
3. Never commit `.env` (it’s in `.gitignore`). No redirect URI needed for this app (Client Credentials only).

---

## Quick start

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
python main.py
```

- API base: `http://127.0.0.1:8888`
- Health: `GET http://127.0.0.1:8888/health`
- Simple UI: open `http://127.0.0.1:8888/` in a browser (search → Get track / Similar). Or use **Postman**.

---

## Project structure (trimmed)

```
cs125/
├── backend/
│   ├── main.py           # FastAPI app
│   ├── api_routes.py     # /search, /tracks/{id}, /tracks/{id}/similar
│   ├── spotify_client.py # Spotify API (token, search, track, audio features)
│   ├── storage.py        # In-memory track cache
│   ├── similarity.py     # Cosine similarity on audio features
│   └── requirements.txt
├── data/
│   └── raw/              # Optional: CSV dataset
├── docs/
│   ├── ARCHITECTURE.md   # Simple architecture diagram
│   ├── ER_DIAGRAM.md     # Minimal data model (tracks)
│   └── DEMO_OUTLINE.md   # 5-minute presentation outline
├── notebooks/            # Optional EDA
├── .env.example
├── .gitignore
└── README.md
```

---

## API (3 endpoints)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/search?q=...` | Search tracks by name (Spotify). Results cached. |
| GET | `/api/tracks/{id}` | Track metadata + audio features (from cache or Spotify). |
| GET | `/api/tracks/{id}/similar?limit=10` | Top similar tracks by cosine similarity on audio features. |

Similarity is computed in-memory over all cached tracks that have audio features; no FAISS, no DB.

---

## Docs

- **Architecture:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Data model (ER):** [docs/ER_DIAGRAM.md](docs/ER_DIAGRAM.md)
- **5-min demo:** [docs/DEMO_OUTLINE.md](docs/DEMO_OUTLINE.md)

---

CS125 project. Spotify API use subject to [Spotify Developer Terms](https://developer.spotify.com/terms).
