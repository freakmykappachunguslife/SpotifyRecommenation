# Gago Glazers – Simple Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Client (Postman / browser / simple HTML)                        │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  FastAPI Backend (port 8888)                                     │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────────┐ │
│  │ /search     │  │ /tracks/{id} │  │ /tracks/{id}/similar     │ │
│  └──────┬──────┘  └──────┬───────┘  └────────────┬────────────┘ │
│         │                 │                       │              │
│         ▼                 ▼                       ▼              │
│  ┌─────────────┐   ┌─────────────┐        ┌─────────────┐       │
│  │ Spotify     │   │ In-memory   │        │ Cosine      │       │
│  │ Client      │   │ Storage     │        │ Similarity  │       │
│  └──────┬──────┘   └──────▲──────┘        └──────▲──────┘       │
│         │                 │                      │              │
└─────────┼─────────────────┼──────────────────────┼──────────────┘
          │                 │                      │
          ▼                 │                      │
┌─────────────────────────┐ │                      │
│  Spotify Web API         │ │  (cache: track +     │
│  • /v1/search            │ │   audio_features)    │
│  • /v1/tracks/{id}       │◀┘                      │
│  • /v1/audio-features/{id}                        │
└─────────────────────────┘ ◀───────────────────────┘
```

**Flow:**

1. **Search** – Client calls `GET /api/search?q=...` → backend uses Spotify Client Credentials token → calls Spotify `/v1/search` → caches results → returns track list.
2. **Track** – Client calls `GET /api/tracks/{id}` → return from cache or fetch from Spotify (track + audio features) → cache → return.
3. **Similar** – Client calls `GET /api/tracks/{id}/similar` → ensure track (and audio features) in cache → compute cosine similarity on audio-feature vectors over all cached tracks → return top N.

No database; no FAISS. Optional later: load CSV into cache at startup.
