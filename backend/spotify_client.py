"""
Spotify Web API client using Client Credentials flow.
Used for: search, track metadata, audio features.
Credentials from .env (SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET).
"""
import os
import random
import time
import base64
import requests
from typing import Any, Optional

TOKEN_URL = "https://accounts.spotify.com/api/token"
API_BASE = "https://api.spotify.com/v1"

_token: Optional[str] = None
_token_expires: float = 0


def _env(key: str) -> str:
    v = os.getenv(key)
    if not v:
        raise ValueError(
            f"Missing {key}. Add it to .env in the project root (cs125/.env). "
            "Run 'python main.py' from the backend/ folder."
        )
    return v.strip().strip('"').strip("'")


def _get_token() -> str:
    """Get access token (cached until expiry)."""
    global _token, _token_expires
    if _token and time.time() < _token_expires:
        return _token
    client_id = _env("SPOTIFY_CLIENT_ID")
    client_secret = _env("SPOTIFY_CLIENT_SECRET")
    auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    r = requests.post(
        TOKEN_URL,
        headers={"Authorization": f"Basic {auth}", "Content-Type": "application/x-www-form-urlencoded"},
        data={"grant_type": "client_credentials"},
        timeout=10,
    )
    if r.status_code == 401:
        raise ValueError(
            "Spotify rejected credentials (401). Check SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in .env. "
            "Get them from https://developer.spotify.com/dashboard"
        )
    r.raise_for_status()
    data = r.json()
    _token = data["access_token"]
    _token_expires = time.time() + data.get("expires_in", 3600) - 60
    return _token


def _get(path: str, params: Optional[dict] = None) -> dict:
    """GET Spotify API with auth."""
    url = f"{API_BASE}{path}" if path.startswith("/") else f"{API_BASE}/{path}"
    r = requests.get(url, params=params, headers={"Authorization": f"Bearer {_get_token()}"}, timeout=10)
    if not r.ok:
        try:
            err = r.json()
            msg = err.get("error", {}).get("message", r.text) or r.reason
        except Exception:
            msg = r.text or r.reason
        raise requests.HTTPError(f"Spotify API: {msg}", response=r)
    return r.json()


def search_tracks(q: str, limit: int = 10) -> list[dict]:
    """Search tracks by query. Returns list of track objects (simplified).
    Spotify search requires limit in 0-10 and a market when using client credentials.
    """
    limit = max(1, min(10, limit))  # Spotify search limit range is 0-10
    data = _get("/search", params={"q": q, "type": "track", "limit": limit, "market": "US"})
    items = data.get("tracks", {}).get("items", [])
    return [_track_summary(t) for t in items]


def get_track(track_id: str) -> Optional[dict]:
    """Fetch track metadata by Spotify ID."""
    try:
        data = _get(f"/tracks/{track_id}")
        return _track_summary(data)
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            return None
        raise


# Base fallback when Spotify returns 403, 502, 404, or other failure.
DEFAULT_AUDIO_FEATURES: dict[str, Any] = {
    "danceability": 0.5,
    "energy": 0.5,
    "key": 0,
    "loudness": -10.0,
    "mode": 1,
    "speechiness": 0.1,
    "acousticness": 0.5,
    "instrumentalness": 0.0,
    "liveness": 0.2,
    "valence": 0.5,
    "tempo": 120.0,
    "note": "fallback_due_to_api_restriction_or_unavailable",
}


def get_fallback_audio_features() -> dict[str, Any]:
    """Return fallback features with slight random jitter so tracks aren't all identical (avoids 100% similarity)."""
    jitter = lambda base, lo, hi: base + random.uniform(lo, hi)
    return {
        "danceability": max(0, min(1, jitter(0.5, -0.15, 0.15))),
        "energy": max(0, min(1, jitter(0.5, -0.15, 0.15))),
        "key": int(max(0, min(11, jitter(0, -2, 2)))),
        "loudness": jitter(-10.0, -8, 8),
        "mode": 1 if random.random() > 0.5 else 0,
        "speechiness": max(0, min(1, jitter(0.1, -0.05, 0.15))),
        "acousticness": max(0, min(1, jitter(0.5, -0.2, 0.2))),
        "instrumentalness": max(0, min(1, jitter(0.0, 0, 0.2))),
        "liveness": max(0, min(1, jitter(0.2, -0.1, 0.15))),
        "valence": max(0, min(1, jitter(0.5, -0.15, 0.15))),
        "tempo": max(50, min(200, jitter(120.0, -25, 25))),
        "note": "fallback_due_to_api_restriction_or_unavailable",
    }


def get_audio_features(track_id: str) -> dict:
    """Fetch audio features by Spotify track ID. On 403/502/404 or any error, returns jittered fallback so similarity isn't identical."""
    try:
        return _get(f"/audio-features/{track_id}")
    except Exception:
        return get_fallback_audio_features()


def _track_summary(t: dict) -> dict:
    """Normalize track object to our shape: id, name, artist, artist_id, popularity, etc."""
    artists = t.get("artists", [])
    artist_name = artists[0]["name"] if artists else ""
    artist_id = artists[0]["id"] if artists else ""
    return {
        "id": t["id"],
        "name": t.get("name", ""),
        "artist": artist_name,
        "artist_id": artist_id,
        "popularity": t.get("popularity"),
        "duration_ms": t.get("duration_ms"),
    }


def get_artist_genres(artist_id: str) -> list[str]:
    """Fetch artist's genres from Spotify. Returns empty list on error (e.g. 403)."""
    if not artist_id:
        return []
    try:
        data = _get(f"/artists/{artist_id}")
        return data.get("genres", [])[:3]  # top 3 genres
    except Exception:
        return []
