from __future__ import annotations

import os


def _split_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in value.split(",") if part.strip()]


class Settings:
    def __init__(self) -> None:
        self.cors_allow_origins = _split_csv(os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:5173"))

        self.llm_provider = os.getenv("LLM_PROVIDER", "groq").lower()
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.groq_model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

        self.max_history_turns = int(os.getenv("MAX_HISTORY_TURNS", "6"))


settings = Settings()
