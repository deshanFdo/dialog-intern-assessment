from __future__ import annotations

import json
from dataclasses import dataclass

import httpx


class LLMError(RuntimeError):
    pass


@dataclass(frozen=True)
class ChatMessage:
    role: str
    content: str


class GroqClient:
    def __init__(self, *, api_key: str, model: str) -> None:
        self._api_key = api_key
        self._model = model
        self._url = "https://api.groq.com/openai/v1/chat/completions"

    async def chat(self, *, messages: list[ChatMessage]) -> str:
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self._model,
            "temperature": 0,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
        }
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(self._url, headers=headers, json=payload)
        if resp.status_code >= 400:
            raise LLMError(f"Groq error {resp.status_code}: {resp.text}")
        data = resp.json()
        try:
            return data["choices"][0]["message"]["content"].strip()
        except Exception as exc:  # noqa: BLE001
            raise LLMError(f"Unexpected Groq response: {json.dumps(data)[:500]}") from exc


class GeminiClient:
    def __init__(self, *, api_key: str, model: str) -> None:
        self._api_key = api_key
        self._model = model

    async def chat(self, *, messages: list[ChatMessage]) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self._model}:generateContent"

        contents = []
        for m in messages:
            if m.role == "system":
                contents.append({"role": "user", "parts": [{"text": m.content}]})
                continue
            role = "user" if m.role == "user" else "model"
            contents.append({"role": role, "parts": [{"text": m.content}]})

        payload = {
            "contents": contents,
            "generationConfig": {"temperature": 0},
        }

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, params={"key": self._api_key}, json=payload)
        if resp.status_code >= 400:
            raise LLMError(f"Gemini error {resp.status_code}: {resp.text}")

        data = resp.json()
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception as exc:  # noqa: BLE001
            raise LLMError(f"Unexpected Gemini response: {json.dumps(data)[:500]}") from exc
