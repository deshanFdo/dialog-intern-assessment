import React, { useMemo, useState } from 'react'
import './styles.css'

type AskResponse = {
  answer: string
  sources: Array<{ id: number; score: number; text: string; source: string }>
}

const apiBaseDefault = 'https://dialog-intern-assessment.onrender.com'

export default function App() {
  const apiBase = useMemo(() => import.meta.env.VITE_API_BASE_URL || apiBaseDefault, [])

  const [ingestText, setIngestText] = useState('')
  const [ingestFile, setIngestFile] = useState<File | null>(null)
  const [ingestStatus, setIngestStatus] = useState<{msg: string, type: 'success'|'error'|'info'} | null>(null)
  const [question, setQuestion] = useState('')
  const [conversationId, setConversationId] = useState('demo')
  const [askStatus, setAskStatus] = useState<{msg: string, type: 'success'|'error'|'info'} | null>(null)
  const [result, setResult] = useState<AskResponse | null>(null)
  const [busy, setBusy] = useState(false)

  async function ingest() {
    setBusy(true)
    setIngestStatus(null)
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
      setIngestStatus({msg: `Ingested successfully. Added ${data.chunks_added} chunks. (Total: ${data.total_chunks})`, type: 'success'})
    } catch (e: any) {
      setIngestStatus({msg: `Ingest failed: ${String(e?.message || e)}`, type: 'error'})
    } finally {
      setBusy(false)
    }
  }

  async function ask() {
    setBusy(true)
    setAskStatus(null)
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
      setAskStatus({msg: `Ask failed: ${String(e?.message || e)}`, type: 'error'})
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="app-container">
      <header>
        <h1>Document Q&A</h1>
        <p>Your AI Assistant for Context-Grounded Answers</p>
        <p style={{marginTop: '0.5rem'}}><span className="mono">API: {apiBase}</span></p>
      </header>

      <main className="main-grid">
        {/* INGEST SECTION */}
        <section className="glass-panel">
          <h2>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
            1. Ingest Knowledge
          </h2>
          
          <div className="file-upload-zone">
            <div className="file-upload-icon">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path><polyline points="13 2 13 9 20 9"></polyline></svg>
            </div>
            <p style={{fontWeight: 500, marginBottom: '0.5rem'}}>
              {ingestFile ? ingestFile.name : 'Drag & drop or click to upload PDF/TXT'}
            </p>
            {!ingestFile && <p style={{fontSize: '0.85rem', color: 'var(--text-muted)'}}>Max size: 10MB</p>}
            <input
              type="file"
              accept=".txt,.pdf"
              onChange={(e) => setIngestFile(e.target.files?.[0] ?? null)}
            />
          </div>

          <div style={{textAlign: 'center', color: 'var(--text-muted)'}}>— OR —</div>

          <div className="form-group">
            <label>Paste Raw Text</label>
            <textarea
              value={ingestText}
              onChange={(e) => {
                setIngestText(e.target.value)
                if (e.target.value) setIngestFile(null)
              }}
              placeholder="Paste any text context here..."
            />
          </div>

          <button disabled={busy || (!ingestFile && ingestText.trim().length === 0)} onClick={ingest}>
            {busy && !result && !askStatus ? <span className="spinner"></span> : 'Process Document'}
          </button>

          {ingestStatus && (
            <div className={`status-msg ${ingestStatus.type}`}>
              {ingestStatus.msg}
            </div>
          )}
        </section>

        {/* ASK SECTION */}
        <section className="glass-panel">
          <h2>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            2. Ask Questions
          </h2>
          
          <div className="form-group">
            <label>Your Question</label>
            <input 
              type="text" 
              value={question} 
              onChange={(e) => setQuestion(e.target.value)} 
              onKeyDown={(e) => e.key === 'Enter' && !busy && question.trim().length > 0 && ask()}
              placeholder="What would you like to know from the document?" 
            />
          </div>

          <div className="form-group">
            <label>Session ID (Optional - for memory)</label>
            <input 
              type="text" 
              value={conversationId} 
              onChange={(e) => setConversationId(e.target.value)} 
              placeholder="e.g. session-123"
            />
          </div>

          <button disabled={busy || question.trim().length === 0} onClick={ask}>
            {busy && !result && !ingestStatus ? <span className="spinner"></span> : 'Ask Assistant'}
          </button>

          {askStatus && (
            <div className={`status-msg ${askStatus.type}`}>
              {askStatus.msg}
            </div>
          )}

          {result && (
            <div className="result-container">
              <div className="answer-box">
                <h3 style={{marginBottom: '0.5rem', color: '#fff'}}>Answer</h3>
                <p style={{fontSize: '1.1rem'}}>{result.answer}</p>
              </div>

              <div>
                <h3 style={{marginBottom: '1rem', color: '#fff', fontSize: '1.1rem'}}>Retrieved Sources</h3>
                {result.sources.length === 0 ? (
                  <p className="mono" style={{color: 'var(--text-muted)'}}>(No context retrieved)</p>
                ) : (
                  <div className="sources-list">
                    {result.sources.map((s) => (
                      <div key={s.id} className="source-card">
                        <div className="source-header">
                          <span>Source: {s.source}</span>
                          <span>Relevance: {s.score.toFixed(2)}</span>
                        </div>
                        <div className="source-text">
                          {s.text}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </section>
      </main>
    </div>
  )
}
