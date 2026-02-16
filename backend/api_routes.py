"""
Gago Glazers API: 3 endpoints — search, track by id, similar tracks.
Spotify API + in-memory cosine similarity on audio features.
"""
import logging
from fastapi import APIRouter, HTTPException

from spotify_client import (
    search_tracks as spotify_search,
    get_track as spotify_get_track,
    get_audio_features,
    get_fallback_audio_features,
)
from storage import get as storage_get, set_track, set_audio_features, get_all_with_features, get_all_track_ids, clear_storage
from similarity import similar_track_ids

logger = logging.getLogger(__name__)
router = APIRouter()


@router.delete("/cache")
def delete_cache():
    """Clear the in-memory track cache so new searches don't mix with previous results."""
    clear_storage()
    return {"status": "ok", "message": "Cache cleared"}


@router.get("/search")
def search(q: str, limit: int = 10):
    """
    Search tracks by name via Spotify API.
    Clears the cache first so results don't mix with previous searches (e.g. Bad Bunny vs Lady Gaga).
    """
    if not q or not q.strip():
        raise HTTPException(400, "Query 'q' is required")
    clear_storage()
    try:
        items = spotify_search(q.strip(), limit=limit)
    except Exception as e:
        logger.exception("Spotify search failed")
        raise HTTPException(502, f"Spotify search failed: {e}") from e
    for t in items:
        set_track(t["id"], t)
    return {"query": q, "tracks": items}


@router.get("/tracks/{track_id}")
def get_track(track_id: str):
    """
    Get track metadata and audio features.
    Fetches from Spotify if not cached; caches for similarity.
    """
    cached = storage_get(track_id)
    if cached and cached.get("audio_features"):
        return cached
    try:
        meta = spotify_get_track(track_id) if not cached else cached
        if not meta:
            raise HTTPException(404, "Track not found")
        features = get_audio_features(track_id)  # always a dict (real or default fallback)
        set_track(track_id, meta)
        set_audio_features(track_id, features)
        meta["audio_features"] = features
        return meta
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(502, f"Spotify request failed: {e}") from e


@router.get("/tracks/{track_id}/similar")
def get_similar(track_id: str, limit: int = 10):
    """
    Top similar tracks by cosine similarity on Spotify audio features.
    Uses only the tracks already in the cache (from the user's last search). No extra API searches.
    """
    # Ensure this track is in cache with audio features
    cached = storage_get(track_id)
    if not cached or not cached.get("audio_features"):
        meta = spotify_get_track(track_id)
        if not meta:
            raise HTTPException(404, "Track not found")
        set_track(track_id, meta)
        features = get_audio_features(track_id)
        set_audio_features(track_id, features)
    # Backfill audio features for every other cached track (from search), then run cosine similarity
    for tid in get_all_track_ids():
        if tid == track_id:
            continue
        t = storage_get(tid)
        if t and not t.get("audio_features"):
            feats = get_audio_features(tid)
            set_audio_features(tid, feats)
    similar = similar_track_ids(track_id, limit, storage_get, get_all_with_features)
    # Enrich with track metadata; ensure every track has audio_features (dict) so frontend never sees "none"
    results = []
    for tid, score in similar:
        t = storage_get(tid)
        if t:
            if not t.get("audio_features"):
                t = {**t, "audio_features": get_fallback_audio_features()}
            results.append({"track": t, "similarity": round(score, 4)})
        else:
            results.append({
                "track": {"id": tid, "name": None, "artist": None, "audio_features": get_fallback_audio_features()},
                "similarity": round(score, 4),
            })
    return {"track_id": track_id, "similar": results}
