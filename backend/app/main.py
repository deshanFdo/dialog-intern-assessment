from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from app.llm import ChatMessage, GeminiClient, GroqClient, LLMError
from app.models import AskRequest, AskResponse, IngestResponse, SourceChunk
from app.pdf_utils import extract_text_from_pdf_bytes
from app.rag_store import RAGStore
from app.settings import settings


SYSTEM_PROMPT = (
    "You are a context-grounded question answering assistant. "
    "Answer ONLY using the provided CONTEXT. "
    "If the answer is not explicitly contained in the CONTEXT, reply exactly with: I don't know"
)


app = FastAPI(title="Document Q&A API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

store = RAGStore()
conversation_memory: dict[str, list[ChatMessage]] = {}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


def _get_llm():
    provider = settings.llm_provider
    if provider == "groq":
        if not settings.groq_api_key:
            raise HTTPException(status_code=503, detail="GROQ_API_KEY is not set")
        return GroqClient(api_key=settings.groq_api_key, model=settings.groq_model)
    if provider == "gemini":
        if not settings.gemini_api_key:
            raise HTTPException(status_code=503, detail="GEMINI_API_KEY is not set")
        return GeminiClient(api_key=settings.gemini_api_key, model=settings.gemini_model)
    raise HTTPException(status_code=400, detail=f"Unknown LLM_PROVIDER: {provider}")


@app.post("/ingest", response_model=IngestResponse)
async def ingest(request: Request) -> IngestResponse:
    content_type = request.headers.get("content-type", "")

    text: str | None = None
    source = "text"

    if content_type.startswith("application/json"):
        data = await request.json()
        if not isinstance(data, dict):
            raise HTTPException(status_code=400, detail="JSON body must be an object")
        text = str(data.get("text") or "").strip()
        source = "json"

    elif content_type.startswith("multipart/form-data"):
        form = await request.form()
        if "text" in form and form.get("text"):
            text = str(form.get("text") or "").strip()
            source = "form"
        elif "file" in form and form.get("file"):
            upload = form.get("file")
            filename = getattr(upload, "filename", "") or "uploaded"
            data = await upload.read()  # type: ignore[attr-defined]
            lower = filename.lower()
            if lower.endswith(".pdf"):
                text = extract_text_from_pdf_bytes(data)
                source = filename
            else:
                try:
                    text = data.decode("utf-8")
                except UnicodeDecodeError:
                    text = data.decode("latin-1")
                text = text.strip()
                source = filename
        else:
            raise HTTPException(status_code=400, detail="Provide either 'text' or 'file' in multipart form")

    else:
        raise HTTPException(status_code=415, detail="Use application/json or multipart/form-data")

    if not text:
        raise HTTPException(status_code=400, detail="No text found to ingest")

    added, total = await store.ingest_text(text, source=source)
    return IngestResponse(chunks_added=added, total_chunks=total, source=source)


@app.post("/ask", response_model=AskResponse)
async def ask(payload: AskRequest) -> AskResponse:
    results = await store.search(payload.question, top_k=payload.top_k)
    if not results:
        return AskResponse(answer="I don't know", sources=[])

    llm = _get_llm()

    context_blocks: list[str] = []
    sources: list[SourceChunk] = []
    for chunk, score in results:
        context_blocks.append(f"[source={chunk.source} id={chunk.id}] {chunk.text}")
        sources.append(SourceChunk(id=chunk.id, score=score, text=chunk.text, source=chunk.source))

    context = "\n\n".join(context_blocks)
    user_prompt = (
        f"CONTEXT:\n{context}\n\n"
        f"QUESTION: {payload.question}\n\n"
        "Answer using only the CONTEXT."
    )

    messages: list[ChatMessage] = [ChatMessage(role="system", content=SYSTEM_PROMPT)]

    if payload.conversation_id:
        history = conversation_memory.get(payload.conversation_id, [])
        messages.extend(history[-(settings.max_history_turns * 2) :])

    messages.append(ChatMessage(role="user", content=user_prompt))

    try:
        answer = await llm.chat(messages=messages)
    except LLMError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    if not answer:
        answer = "I don't know"

    if payload.conversation_id:
        mem = conversation_memory.setdefault(payload.conversation_id, [])
        mem.append(ChatMessage(role="user", content=payload.question))
        mem.append(ChatMessage(role="assistant", content=answer))

    return AskResponse(answer=answer, sources=sources)
