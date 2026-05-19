import json
import os
import random

_FALLBACK_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "scenarios_fallback.json",
)


def _load_fallback() -> list:
    try:
        with open(_FALLBACK_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        print(f"[Fallback] Could not load scenarios: {exc}")
        return []


def get_scenarios_for_session(user_profile: dict, use_api: bool = True) -> list:
    """
    Return 5 phishing scenarios for a training session.
    Tries NVIDIA API first; falls back to bundled JSON on any failure.
    """
    if use_api:
        try:
            from utils.nvidia_client import generate_scenarios_batch
            scenarios = generate_scenarios_batch(user_profile, count=5)
            if len(scenarios) >= 3:
                return scenarios[:5]
        except Exception as exc:
            print(f"[ScenarioGenerator] API unavailable, using fallback: {exc}")

    fallback = _load_fallback()
    if len(fallback) >= 5:
        selected = random.sample(fallback, 5)
    else:
        selected = fallback
    return selected
