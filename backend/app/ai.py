"""Stretch goal: AI scene brainstorming.

Calls the OpenAI Chat Completions API directly over HTTP (no extra SDK
dependency — one less thing to install/pin). Entirely optional — if
OPENAI_API_KEY isn't set, the feature cleanly reports itself as
unavailable instead of crashing the app.
"""
import re
import httpx
from fastapi import HTTPException

from app.config import OPENAI_API_KEY, OPENAI_MODEL, ai_is_configured

_OPENAI_ENDPOINT = "https://api.openai.com/v1/chat/completions"
_TAG_RE = re.compile(r"<[^>]+>")


def _plain_text(html_or_text: str) -> str:
    """The script is stored as Tiptap HTML; strip tags for a cleaner prompt."""
    return _TAG_RE.sub(" ", html_or_text).strip()


async def suggest_next_scene(script_content: str, direction: str | None = None) -> str:
    if not ai_is_configured():
        raise HTTPException(
            status_code=501,
            detail=(
                "AI scene suggestions aren't configured on this server. "
                "Set OPENAI_API_KEY in the backend .env to enable this "
                "optional feature."
            ),
        )

    script_text = _plain_text(script_content)
    if not script_text:
        raise HTTPException(
            status_code=400,
            detail="Write at least a little bit of script first — there's nothing to build on yet.",
        )

    system_prompt = (
        "You are a writing partner helping brainstorm the next scene for a "
        "video script. Given the script so far, suggest ONE concrete next "
        "scene: a short heading plus 2-4 sentences of what happens, in a "
        "tone that matches the script. Be specific and actionable, not vague."
    )
    user_prompt = f"--- SCRIPT SO FAR ---\n{script_text[:6000]}\n--- END SCRIPT ---\n"
    if direction:
        user_prompt += f"\nExtra direction from the writer: {direction.strip()}\n"

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": OPENAI_MODEL,
        "max_tokens": 400,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(_OPENAI_ENDPOINT, headers=headers, json=body)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"AI suggestion request failed: {exc}")

    if response.status_code >= 400:
        raise HTTPException(
            status_code=502,
            detail=f"AI suggestion request failed: {response.text}",
        )

    payload = response.json()
    choices = payload.get("choices", [])
    text = choices[0]["message"]["content"].strip() if choices else ""
    if not text:
        raise HTTPException(status_code=502, detail="AI returned an empty suggestion.")
    return text
