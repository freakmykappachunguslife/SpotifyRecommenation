"""
Cosine similarity on audio features only. In-memory; no FAISS.
"""
import math
from typing import Any

# Spotify audio-features keys we use for the vector (numeric only)
FEATURE_KEYS = [
    "danceability",
    "energy",
    "key",
    "loudness",
    "mode",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "valence",
    "tempo",
]


def feature_vector(features: dict[str, Any]) -> list[float]:
    """Build normalized vector from Spotify audio features. Missing keys → 0."""
    # Normalize tempo to ~0-1 (e.g. 50–200 BPM) and loudness (e.g. -60 to 0)
    raw = []
    for k in FEATURE_KEYS:
        v = features.get(k)
        if v is None:
            raw.append(0.0)
        elif k == "tempo":
            raw.append(max(0, min(1, (v - 50) / 150)))
        elif k == "loudness":
            raw.append(max(0, min(1, (v + 60) / 60)))
        else:
            raw.append(float(v))
    return raw


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Cosine similarity between two vectors. Returns value in [0, 1] if vectors non-negative."""
    if len(a) != len(b):
        raise ValueError("Vector length mismatch")
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a)) or 1e-10
    norm_b = math.sqrt(sum(y * y for y in b)) or 1e-10
    return dot / (norm_a * norm_b)


# Diversity: same-artist results are penalized so other artists surface (avoids echo chamber).
SAME_ARTIST_PENALTY = 0.7


def similar_track_ids(track_id: str, limit: int, get_track_fn, get_all_with_features_fn) -> list[tuple[str, float]]:
    """
    Return top `limit` (other_track_id, similarity_score) for tracks that have audio features.
    Applies a diversity penalty (lower score) when the candidate is by the same artist.
    get_track_fn(track_id) -> cached track dict with "audio_features", "artist".
    get_all_with_features_fn() -> list of (tid, data).
    """
    track = get_track_fn(track_id)
    if not track or not track.get("audio_features"):
        return []
    vec = feature_vector(track["audio_features"])
    target_artist = (track.get("artist") or "").strip().lower()
    candidates = get_all_with_features_fn()
    scores: list[tuple[str, float]] = []
    for tid, data in candidates:
        if tid == track_id:
            continue
        other_vec = feature_vector(data["audio_features"])
        sim = cosine_similarity(vec, other_vec)
        # Penalize same artist so diverse results rank higher
        if target_artist and (data.get("artist") or "").strip().lower() == target_artist:
            sim *= SAME_ARTIST_PENALTY
        scores.append((tid, sim))
    scores.sort(key=lambda x: -x[1])
    return scores[:limit]
