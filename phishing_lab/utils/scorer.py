import os
import pandas as pd
from datetime import datetime

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
_CSV_PATH = os.path.join(_DATA_DIR, "user_progress.csv")

_COLUMNS = [
    "timestamp", "user_id", "user_name", "role", "platform",
    "tech_level", "lab_score", "passed", "date_completed", "certificate_downloaded",
]


def _ensure_csv():
    os.makedirs(_DATA_DIR, exist_ok=True)
    if not os.path.exists(_CSV_PATH):
        pd.DataFrame(columns=_COLUMNS).to_csv(_CSV_PATH, index=False)


def save_survey_to_csv(profile: dict):
    """Write a new row after survey completion (score fields empty)."""
    _ensure_csv()
    row = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_id": profile.get("user_id", ""),
        "user_name": profile.get("name", ""),
        "role": profile.get("role", ""),
        "platform": profile.get("platform", ""),
        "tech_level": profile.get("tech_level", ""),
        "lab_score": "",
        "passed": "",
        "date_completed": "",
        "certificate_downloaded": False,
    }
    df = pd.read_csv(_CSV_PATH) if os.path.exists(_CSV_PATH) else pd.DataFrame(columns=_COLUMNS)
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(_CSV_PATH, index=False)


def update_score_in_csv(user_id: str, score: int, passed: bool):
    """Update the existing row for this user with lab results."""
    _ensure_csv()
    if not os.path.exists(_CSV_PATH):
        return
    df = pd.read_csv(_CSV_PATH)
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mask = df["user_id"].astype(str) == str(user_id)
    if mask.any():
        df.loc[mask, "lab_score"] = score
        df.loc[mask, "passed"] = passed
        df.loc[mask, "date_completed"] = date_str
    else:
        # Fallback: append new row if user not found
        row = {c: "" for c in _COLUMNS}
        row["user_id"] = user_id
        row["lab_score"] = score
        row["passed"] = passed
        row["date_completed"] = date_str
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(_CSV_PATH, index=False)


def mark_certificate_downloaded(user_id: str):
    """Flag that this user downloaded their certificate."""
    if not os.path.exists(_CSV_PATH):
        return
    df = pd.read_csv(_CSV_PATH)
    mask = df["user_id"].astype(str) == str(user_id)
    if mask.any():
        df.loc[mask, "certificate_downloaded"] = True
        df.to_csv(_CSV_PATH, index=False)


def load_all_progress() -> pd.DataFrame:
    """Return the full progress CSV as a DataFrame."""
    _ensure_csv()
    return pd.read_csv(_CSV_PATH)


def calculate_score(answers: list) -> int:
    """Sum points from a list of answer dicts {correct: bool}."""
    return sum(20 for a in answers if a.get("correct"))
