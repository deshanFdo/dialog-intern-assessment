import React, { useMemo, useState } from 'react'

type AskResponse = {
  answer: string
  sources: Array<{ id: number; score: number; text: string; source: string }>
}

const apiBaseDefault = 'http://localhost:8000'

export default function App() {
  const apiBase = useMemo(() => import.meta.env.VITE_API_BASE_URL || apiBaseDefault, [])

  const [ingestText, setIngestText] = useState('')
  const [ingestFile, setIngestFile] = useState<File | null>(null)
  const [ingestStatus, setIngestStatus] = useState<string>('')
  const [question, setQuestion] = useState('')
  const [conversationId, setConversationId] = useState('demo')
  const [askStatus, setAskStatus] = useState<string>('')
  const [result, setResult] = useState<AskResponse | null>(null)
  const [busy, setBusy] = useState(false)

  async function ingest() {
    setBusy(true)
    setIngestStatus('')
    setResult(null)
    try {
      let resp: Response
      if (ingestFile) {
        const form = new FormData()
        form.append('file', ingestFile)
        resp = await fetch(`${apiBase}/ingest`, { method: 'POST', body: form })
      } else {
        resp = await fetch(`${apiBase}/ingest`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: ingestText }),
        })
      }
      if (!resp.ok) {
        throw new Error(await resp.text())
      }
      const data = await resp.json()
      setIngestStatus(`Ingested. chunks_added=${data.chunks_added} total_chunks=${data.total_chunks}`)
    } catch (e: any) {
      setIngestStatus(`Ingest failed: ${String(e?.message || e)}`)
    } finally {
      setBusy(false)
    }
  }

  async function ask() {
    setBusy(true)
    setAskStatus('')
    setResult(null)
    try {
      const resp = await fetch(`${apiBase}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, conversation_id: conversationId || null }),
      })
      if (!resp.ok) {
        throw new Error(await resp.text())
      }
      const data = (await resp.json()) as AskResponse
      setResult(data)
    } catch (e: any) {
      setAskStatus(`Ask failed: ${String(e?.message || e)}`)
    } finally {
      setBusy(false)
    }
  }

  return (
    <main>
      <h1>Document Q&amp;A</h1>
      <p>
        API base: <span className="mono">{apiBase}</span>
      </p>

      <section>
        <h2>1) Ingest</h2>
        <div className="row">
          <div>
            <label>Text</label>
            <textarea
              rows={8}
              value={ingestText}
              onChange={(e) => setIngestText(e.target.value)}
              placeholder="Paste text to ingest"
            />
          </div>
          <div>
            <label>File (.txt or .pdf)</label>
            <input
              type="file"
              accept=".txt,.pdf"
              onChange={(e) => setIngestFile(e.target.files?.[0] ?? null)}
            />
            <p className="mono">{ingestFile ? ingestFile.name : 'No file selected'}</p>
            <p style={{ marginTop: 12 }}>
              Tip: If you select a file, it will be used instead of the text box.
            </p>
          </div>
        </div>
        <button disabled={busy || (!ingestFile && ingestText.trim().length === 0)} onClick={ingest}>
          Ingest
        </button>
        {ingestStatus && <p className="mono">{ingestStatus}</p>}
      </section>

      <section>
        <h2>2) Ask</h2>
        <label>Question</label>
        <input type="text" value={question} onChange={(e) => setQuestion(e.target.value)} />

        <label>Conversation ID (optional)</label>
        <input type="text" value={conversationId} onChange={(e) => setConversationId(e.target.value)} />

        <button disabled={busy || question.trim().length === 0} onClick={ask}>
          Ask
        </button>
        {askStatus && <p className="mono">{askStatus}</p>}

        {result && (
          <div style={{ marginTop: 12 }}>
            <h3>Answer</h3>
            <p className="mono">{result.answer}</p>
            <h3>Sources</h3>
            {result.sources.length === 0 ? (
              <p className="mono">(none)</p>
            ) : (
              <ul>
                {result.sources.map((s) => (
                  <li key={s.id} className="mono">
                    id={s.id} score={s.score.toFixed(2)} source={s.source}\n{s.text.slice(0, 220)}
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </section>
    </main>
  )
}
