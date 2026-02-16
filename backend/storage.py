"""
In-memory storage for tracks and their audio features.
Used for cosine similarity over cached tracks. Optional: load from CSV later.
"""
from typing import Any, Optional

# track_id -> { track metadata + "audio_features" if fetched }
_cache: dict[str, dict[str, Any]] = {}


def get(track_id: str) -> Optional[dict]:
    return _cache.get(track_id)


def set_track(track_id: str, data: dict) -> None:
    _cache[track_id] = data


def set_audio_features(track_id: str, features: dict) -> None:
    if track_id in _cache:
        _cache[track_id]["audio_features"] = features
    else:
        _cache[track_id] = {"audio_features": features}


def get_all_with_features() -> list[tuple[str, dict]]:
    """Return list of (track_id, data) for tracks that have audio_features."""
    return [(tid, data) for tid, data in _cache.items() if data.get("audio_features")]


def get_all_track_ids() -> list[str]:
    """Return all cached track IDs (for backfilling features when computing similar)."""
    return list(_cache.keys())


def clear_storage() -> None:
    """Empty the in-memory cache so new searches don't mix with stale data."""
    _cache.clear()
