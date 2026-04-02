import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    songs: List[Dict] = []
    with open(csv_path, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            songs.append(
                {
                    "id": int(row["id"]),
                    "title": row["title"],
                    "artist": row["artist"],
                    "genre": row["genre"],
                    "mood": row["mood"],
                    "energy": float(row["energy"]),
                    "tempo_bpm": int(row["tempo_bpm"]),
                    "valence": float(row["valence"]),
                    "danceability": float(row["danceability"]),
                    "acousticness": float(row["acousticness"]),
                }
            )
    return songs

def score_song(user_prefs: Dict, song: Dict) -> float:
    """
    Scores a song against user preferences.

    Scoring rule:
    - +2 if genre matches
    - +1 if mood matches
    - Add numeric similarities using 1 - abs(x_song - x_target)
    - For tempo, scale difference by 100 before similarity
    """
    def _first_value(source: Dict, keys: List[str]) -> Optional[float]:
        for key in keys:
            if key in source and source[key] is not None:
                return source[key]
        return None

    score = 0.0

    user_genre = _first_value(user_prefs, ["genre", "favorite_genre"])
    user_mood = _first_value(user_prefs, ["mood", "favorite_mood"])

    if user_genre is not None and song.get("genre") == user_genre:
        score += 2.0
    if user_mood is not None and song.get("mood") == user_mood:
        score += 1.0

    numeric_features = [
        ("energy", ["energy", "target_energy"], 1.0),
        ("valence", ["valence", "target_valence"], 1.0),
        ("danceability", ["danceability", "target_danceability"], 1.0),
        ("acousticness", ["acousticness", "target_acousticness"], 1.0),
        ("tempo_bpm", ["tempo_bpm", "tempo", "target_tempo_bpm", "target_tempo"], 100.0),
    ]

    for song_key, user_keys, scale in numeric_features:
        song_value = song.get(song_key)
        target_value = _first_value(user_prefs, user_keys)

        if song_value is None or target_value is None:
            continue

        difference = abs(float(song_value) - float(target_value)) / scale
        score += 1.0 - difference

    return score

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    scored_songs: List[Tuple[Dict, float, str]] = []

    for song in songs:
        score = score_song(user_prefs, song)

        reasons: List[str] = []
        if song.get("genre") == user_prefs.get("genre"):
            reasons.append("genre match")
        if song.get("mood") == user_prefs.get("mood"):
            reasons.append("mood match")

        if not reasons:
            reasons.append("similar numeric profile")

        explanation = ", ".join(reasons)
        scored_songs.append((song, score, explanation))

    scored_songs.sort(key=lambda item: item[1], reverse=True)
    return scored_songs[:k]
