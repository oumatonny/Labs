"""
JSON-backed user account store.
Each account is keyed by lowercase email address.

Schema per account:
{
  "user_id":    str,       # 8-char UUID fragment
  "name":       str,
  "email":      str,       # lowercase, canonical key
  "role":       str,
  "platform":   str,
  "tech_level": str,
  "created_at": str,       # "YYYY-MM-DD HH:MM:SS"
  "last_login": str,
  "attempts": [
    {
      "attempt_id": int,
      "date":       str,
      "score":      int,
      "passed":     bool,
      "answers":    list,
      "certificate_downloaded": bool
    }
  ],
  "best_score": int | null
}
"""
import json
import os
import uuid
from datetime import datetime

_DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"
)
_PATH = os.path.join(_DATA_DIR, "accounts.json")


# ── Internal helpers ──────────────────────────────────────────────────────────

def _load() -> dict:
    if not os.path.exists(_PATH):
        return {}
    with open(_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(data: dict):
    os.makedirs(_DATA_DIR, exist_ok=True)
    with open(_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _key(email: str) -> str:
    return email.strip().lower()


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ── Public API ────────────────────────────────────────────────────────────────

def account_exists(email: str) -> bool:
    """True if an account with this email already exists."""
    return _key(email) in _load()


def get_account(email: str) -> dict | None:
    """Return the account dict or None."""
    return _load().get(_key(email))


def login_or_register(name: str, email: str) -> tuple:
    """
    Return (account_dict, is_new_user).
    - New email  → create account, is_new=True
    - Known email → update last_login (and name if provided), is_new=False
    """
    data = _load()
    k = _key(email)
    now = _now()
    is_new = k not in data

    if is_new:
        data[k] = {
            "user_id":    str(uuid.uuid4())[:8],
            "name":       name.strip() or "Participant",
            "email":      k,
            "role":       "",
            "platform":   "",
            "tech_level": "",
            "created_at": now,
            "last_login": now,
            "attempts":   [],
            "best_score": None,
        }
    else:
        data[k]["last_login"] = now
        if name.strip():                         # allow display-name update
            data[k]["name"] = name.strip()

    _save(data)
    return data[k], is_new


def update_profile(email: str, role: str, platform: str, tech_level: str):
    """Persist survey answers to the account."""
    data = _load()
    k = _key(email)
    if k in data:
        data[k].update({"role": role, "platform": platform, "tech_level": tech_level})
        _save(data)


def save_attempt(email: str, score: int, passed: bool, answers: list) -> int:
    """
    Append a completed lab attempt.  Returns the new attempt_id (1-based).
    """
    data = _load()
    k = _key(email)
    if k not in data:
        return 0

    acc = data[k]
    attempt_id = len(acc.get("attempts", [])) + 1
    acc.setdefault("attempts", []).append({
        "attempt_id":             attempt_id,
        "date":                   _now(),
        "score":                  score,
        "passed":                 passed,
        "answers":                answers,
        "certificate_downloaded": False,
    })
    acc["best_score"] = max(a["score"] for a in acc["attempts"])
    _save(data)
    return attempt_id


def mark_cert_downloaded(email: str, attempt_id: int):
    """Flag a specific attempt's certificate as downloaded."""
    data = _load()
    k = _key(email)
    if k in data:
        for a in data[k].get("attempts", []):
            if a["attempt_id"] == attempt_id:
                a["certificate_downloaded"] = True
        _save(data)


def all_accounts() -> list:
    """Return a flat list of all account dicts (for admin view)."""
    return list(_load().values())
