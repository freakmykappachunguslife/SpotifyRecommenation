# Gago Glazers – 5-Minute Demo Outline

## 1. Intro (30 sec)

- **What:** Gago Glazers is a small search + similarity API for music.
- **Stack:** Spotify Web API + FastAPI + cosine similarity on audio features only.
- **Scope:** CS125 – focus on search, data retrieval, and a simple similarity algorithm.

---

## 2. Live API Demo (2–2.5 min)

Use **Postman** (or browser) and the running backend.

1. **Health check**  
   `GET http://127.0.0.1:8888/health`  
   → `{"status":"ok"}`

2. **Search**  
   `GET http://127.0.0.1:8888/api/search?q=blinding lights`  
   → Show response: list of tracks (id, name, artist).  
   → “Backend calls Spotify search and caches results.”

3. **Get one track (with audio features)**  
   Pick a `id` from search:  
   `GET http://127.0.0.1:8888/api/tracks/{id}`  
   → Show track metadata + `audio_features` (tempo, energy, danceability, etc.).  
   → “We use these numbers as the feature vector for similarity.”

4. **Similar tracks**  
   `GET http://127.0.0.1:8888/api/tracks/{id}/similar?limit=5`  
   → Show top 5 similar tracks and similarity scores.  
   → “Similarity is cosine similarity on these audio-feature vectors over all tracks we’ve cached.”

---

## 3. Algorithm in One Sentence (30 sec)

- We turn each track’s Spotify audio features into a vector, then compute **cosine similarity** between the chosen track and every other cached track; we return the top‑k. No ML training, no FAISS—just in-memory vectors and one clear algorithm.

---

## 4. Wrap (30 sec)

- **What we built:** 3 endpoints (search, track, similar), Spotify integration, in-memory cache, one similarity metric.
- **Possible extensions:** Load CSV at startup, add a simple HTML search page, or compare with Spotify’s own recommendations.

---

**Tips**

- Run backend before the demo: `cd backend && pip install -r requirements.txt && python main.py`.
- Have `.env` set with `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET`.
- Keep one Postman collection with the 4 requests so you can click through quickly.
