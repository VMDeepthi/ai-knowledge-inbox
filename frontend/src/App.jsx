import { useEffect, useState } from 'react'
import { askQuestion, getItems, ingest } from './api'

export default function App() {
  const [type, setType] = useState('text')
  const [content, setContent] = useState('')
  const [items, setItems] = useState([])
  const [question, setQuestion] = useState('')
  const [result, setResult] = useState(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')

  async function refreshItems() {
    try { setItems(await getItems()) } catch (err) { setError(err.message) }
  }
  useEffect(() => { refreshItems() }, [])

  async function handleIngest(event) {
    event.preventDefault()
    setBusy(true); setError(''); setNotice('')
    try {
      const saved = await ingest({ type, content })
      setNotice(`${saved.message} ${saved.chunk_count} chunk(s) indexed.`)
      setContent('')
      await refreshItems()
    } catch (err) { setError(err.message) }
    finally { setBusy(false) }
  }

  async function handleAsk(event) {
    event.preventDefault()
    setBusy(true); setError(''); setResult(null)
    try { setResult(await askQuestion({ question, top_k: 4 })) }
    catch (err) { setError(err.message) }
    finally { setBusy(false) }
  }

  return <main className="shell">
    <header className="hero">
      <div className="eyebrow">YOUR PERSONAL RESEARCH SPACE</div>
      <h1>AI Knowledge Inbox</h1>
      <p>Save useful ideas. Ask better questions. Find answers in what you know.</p>
    </header>

    <div className="layout">
      <section className="panel">
        <div className="section-heading"><div><span className="step">01</span><h2>Add to your inbox</h2></div></div>
        <form onSubmit={handleIngest}>
          <div className="tabs">
            <button type="button" className={type === 'text' ? 'tab active' : 'tab'} onClick={() => setType('text')}>Text note</button>
            <button type="button" className={type === 'url' ? 'tab active' : 'tab'} onClick={() => setType('url')}>Web URL</button>
          </div>
          {type === 'text'
            ? <textarea value={content} onChange={e => setContent(e.target.value)} placeholder="Paste an idea, meeting note, documentation, or anything you want to remember..." rows="7" required />
            : <input value={content} onChange={e => setContent(e.target.value)} placeholder="https://example.com/article" type="url" required />}
          <button className="primary" disabled={busy || content.trim().length < 5}>{busy ? 'Working...' : 'Save to inbox'} <span>↗</span></button>
        </form>
        {notice && <p className="success">{notice}</p>}
      </section>

      <section className="panel ask-panel">
        <div className="section-heading"><div><span className="step">02</span><h2>Ask your knowledge</h2></div></div>
        <form onSubmit={handleAsk}>
          <textarea value={question} onChange={e => setQuestion(e.target.value)} placeholder="What would you like to know from your saved content?" rows="4" required />
          <button className="primary" disabled={busy || question.trim().length < 3}>{busy ? 'Searching...' : 'Ask AI'} <span>✳</span></button>
        </form>
        {result && <div className="answer">
          <h3>Answer</h3><p className="answer-text">{result.answer}</p>
          <h3>Sources ({result.sources.length})</h3>
          {result.sources.map(source => <article className="source" key={source.chunk_id}>
            <div className="source-title">{source.title} <span>#{source.item_id}</span></div>
            <p>{source.snippet}</p>
            {source.source_url && <a href={source.source_url} target="_blank" rel="noreferrer">Open original ↗</a>}
            <small>Relevance score: {source.score}</small>
          </article>)}
        </div>}
      </section>

      <section className="panel inbox-panel">
        <div className="section-heading"><div><span className="step">03</span><h2>Saved items</h2></div><span className="count">{items.length} ITEMS</span></div>
        {items.length === 0 ? <div className="empty"><div className="empty-icon">▤</div><p>Your inbox is empty.</p><small>Add a note or URL to get started.</small></div> :
          <div className="items">{items.map(item => <article className="item" key={item.id}>
            <div className="item-icon">{item.source_type === 'url' ? '↗' : '▤'}</div>
            <div className="item-body"><strong>{item.title}</strong><p>{item.preview}{item.preview.length >= 180 ? '…' : ''}</p><small>{item.source_type.toUpperCase()} · {new Date(item.created_at).toLocaleString()}</small></div>
          </article>)}</div>}
      </section>
    </div>
    {error && <div className="error" role="alert">{error}<button onClick={() => setError('')}>×</button></div>}
    <footer>Built with React · FastAPI · SQLite · Retrieval-Augmented Generation</footer>
  </main>
}
