import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

_API_KEY = os.getenv(
    "NVIDIA_API_KEY",
    "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"
)
_MODEL = "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning"
_BASE_URL = "https://integrate.api.nvidia.com/v1"


def _build_client():
    return OpenAI(base_url=_BASE_URL, api_key=_API_KEY)


def generate_scenarios_batch(user_profile: dict, count: int = 5) -> list:
    """
    Call NVIDIA API to generate `count` phishing scenarios in one request.
    Returns a list of dicts, or empty list on failure.
    """
    role = user_profile.get("role", "professional")
    platform = user_profile.get("platform", "Email")
    tech = user_profile.get("tech_level", "Intermediate")

    prompt = f"""You are a cybersecurity training expert. Generate exactly {count} diverse phishing scenarios for a {role} (tech level: {tech}) who primarily uses {platform}.

Return ONLY a valid JSON array with exactly {count} objects. No markdown fences, no explanation — just the raw JSON array starting with [ and ending with ].

Each object must have these exact keys:
- "platform": one of "email", "tiktok", "instagram", "whatsapp", "sms", "phone"
- "message_content": full realistic phishing message text (for email, include From: and Subject: headers on separate lines)
- "sender_name": display name of the fake sender
- "sender_address": fake email address, phone number, or @username
- "red_flags": JSON array of exactly 3 specific red flags present in the message
- "correct_action": one of "report", "ignore", "verify_elsewhere"
- "explanation": 1-2 sentence explanation of why this is phishing and what to do instead

Rules:
- Use at least 3 different platforms across the {count} scenarios
- Make them realistic and specific to the {role}'s context
- Vary difficulty: some obvious, some subtle
- Include at least one email, one mobile (sms/whatsapp), one social media scenario
- Keep message_content concise but realistic"""

    client = _build_client()
    full_content = ""

    try:
        completion = client.chat.completions.create(
            model=_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            top_p=0.95,
            max_tokens=8192,
            extra_body={
                "chat_template_kwargs": {"enable_thinking": True},
                "reasoning_budget": 2048,
            },
            stream=True,
        )

        for chunk in completion:
            if not chunk.choices:
                continue
            content = chunk.choices[0].delta.content
            if content:
                full_content += content

        scenarios = _extract_json_array(full_content)
        if scenarios:
            for i, s in enumerate(scenarios):
                s["id"] = i + 1
            return scenarios

    except Exception as exc:
        print(f"[NVIDIA API] Error: {exc}")

    return []


def _extract_json_array(text: str) -> list:
    """
    Robustly extract the first complete JSON array from a model response.
    Uses bracket counting so trailing explanation text or extra whitespace
    after the closing ] never causes a parse error.
    """
    # Strip markdown code fences the model sometimes wraps output in
    text = text.strip()
    if "```" in text:
        import re
        text = re.sub(r"```(?:json)?\s*", "", text).strip()

    # Try a direct parse first (handles clean responses)
    try:
        result = json.loads(text)
        if isinstance(result, list):
            return result
    except json.JSONDecodeError:
        pass

    # Find the first '[' and walk forward counting bracket depth
    start = text.find("[")
    if start == -1:
        return []

    depth = 0
    in_string = False
    escape_next = False

    for i, ch in enumerate(text[start:], start):
        if escape_next:
            escape_next = False
            continue
        if ch == "\\" and in_string:
            escape_next = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                # Found the matching close bracket — parse only this slice
                try:
                    result = json.loads(text[start : i + 1])
                    if isinstance(result, list):
                        return result
                except json.JSONDecodeError:
                    pass
                break  # Malformed even after isolation — give up

    return []
