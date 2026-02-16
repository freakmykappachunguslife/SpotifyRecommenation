# Gago Glazers – Minimal Data Model (ER)

In-memory storage is keyed by **track id**. Conceptually we only need **tracks** (and optionally **artists** for display). No separate embeddings table.

```
┌──────────────────────────────────────────────────────────────────┐
│  track (logical entity – stored as one object per track_id)        │
├──────────────────────────────────────────────────────────────────┤
│  id (Spotify ID)     VARCHAR  PK                                  │
│  name                TEXT                                         │
│  artist              TEXT     (or artist_id → artist)             │
│  popularity          INT                                          │
│  duration_ms         INT                                          │
│  audio_features      JSON     (danceability, energy, tempo, …)    │
└──────────────────────────────────────────────────────────────────┘
```

**Optional – if we split artist:**

```
┌─────────────────────────┐       ┌─────────────────────────────────┐
│  artist                  │       │  track                           │
├─────────────────────────┤       ├─────────────────────────────────┤
│  id (Spotify ID)   PK    │◀──┐   │  id (Spotify ID)           PK    │
│  name             TEXT   │   └───│  artist_id        FK             │
│  (genres)         TEXT  │       │  name             TEXT           │
└─────────────────────────┘       │  popularity       INT            │
                                  │  duration_ms      INT            │
                                  │  audio_features   JSON           │
                                  └─────────────────────────────────┘
```

**Current implementation:** One in-memory dict: `track_id → { id, name, artist, popularity, duration_ms, audio_features? }`. No separate artist table. This matches “tracks only, maybe artists” with minimal scope.
