"""Send a prompt to a free-tier Gemini model and return the text response.

Requires GEMINI_API_KEY in your environment or .env file.
Get a free key at https://aistudio.google.com/apikey

The bot's personality is read from PERSONALITY_FILE (default: personality.txt
next to this script) and sent as Gemini's system instruction.

Usage:
    python prompt_gemini.py "Tell me a joke"
    python prompt_gemini.py            # prompts interactively
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# Flash models are available on the Gemini API free tier.
# Override with GEMINI_MODEL in .env if you want a different one.
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

# Text file describing the bot's personality, sent to Gemini as the system
# instruction. Override with PERSONALITY_FILE in .env. Relative paths are
# resolved against this script's folder. If the file is missing or empty,
# Gemini runs with no personality.
PERSONALITY_FILE = os.getenv("PERSONALITY_FILE", "personality.txt")

_client = None


def load_personality(path: str | os.PathLike | None = PERSONALITY_FILE) -> str | None:
    """Return the personality text from `path`, or None if missing/empty.

    Read on every call, so edits to the file take effect without a restart.
    """
    if not path:
        return None
    file = Path(path)
    if not file.is_absolute():
        file = Path(__file__).parent / file
    try:
        text = file.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return None
    return text or None


def _build_config(personality_file: str | os.PathLike | None) -> types.GenerateContentConfig | None:
    personality = load_personality(personality_file)
    if personality is None:
        return None
    return types.GenerateContentConfig(system_instruction=personality)


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Add it to your .env file "
                "(get one free at https://aistudio.google.com/apikey)."
            )
        _client = genai.Client(api_key=api_key)
    return _client


def prompt_gemini(
    prompt: str,
    model: str = DEFAULT_MODEL,
    personality_file: str | os.PathLike | None = PERSONALITY_FILE,
) -> str:
    """Send `prompt` to Gemini and return the response text (blocking)."""
    response = _get_client().models.generate_content(
        model=model, contents=prompt, config=_build_config(personality_file)
    )
    return response.text or ""


async def prompt_gemini_async(
    prompt: str,
    model: str = DEFAULT_MODEL,
    personality_file: str | os.PathLike | None = PERSONALITY_FILE,
) -> str:
    """Async version, safe to await inside discord.py event handlers."""
    response = await _get_client().aio.models.generate_content(
        model=model, contents=prompt, config=_build_config(personality_file)
    )
    return response.text or ""


if __name__ == "__main__":
    user_prompt = " ".join(sys.argv[1:]) or input("Prompt: ")
    print(prompt_gemini(user_prompt))
