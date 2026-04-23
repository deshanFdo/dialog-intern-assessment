from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv

    _settings_file = Path(__file__).resolve()
    _backend_dir = _settings_file.parents[1]
    _repo_root = _settings_file.parents[2]

    load_dotenv(_backend_dir / ".env", override=False)
    load_dotenv(_repo_root / ".env", override=False)
    load_dotenv(override=False)
except Exception:
    # dotenv is optional in containerized deployments where env vars are injected.
    pass


def _split_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in value.split(",") if part.strip()]


class Settings:
    def __init__(self) -> None:
        self.cors_allow_origins = _split_csv(os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:5173"))

        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.groq_model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

        provider = os.getenv("LLM_PROVIDER")
        if provider:
            self.llm_provider = provider.lower()
        else:
            if self.gemini_api_key:
                self.llm_provider = "gemini"
            elif self.groq_api_key:
                self.llm_provider = "groq"
            else:
                self.llm_provider = "gemini"

        self.max_history_turns = int(os.getenv("MAX_HISTORY_TURNS", "6"))


settings = Settings()
