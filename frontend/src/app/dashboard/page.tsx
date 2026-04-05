'use client'
import { useState, useEffect } from 'react'

// === DASHBOARD CONTENT ===
function DashboardContent() {
  const [s, setS] = useState<any>(null)
  useEffect(() => {
    const load = () => fetch('/api/v1/dashboard/stats').then(r => r.json()).then(setS)
    load(); const t = setInterval(load, 10000); return () => clearInterval(t)
  }, [])
  if (!s) return <p>Loading...</p>
  const cards = [
    ['TOTAL INCIDENTS', s.total_incidents, 'border-blue-500'],
    ['OPEN', s.open_incidents, 'border-yellow-500'],
    ['CRITICAL', s.critical_incidents, 'border-red-500'],
    ['AGENTS ONLINE', `${s.agents_online}/${s.agents_total}`, 'border-green-500'],
    ['AVG CONFIDENCE', `${(s.avg_confidence * 100).toFixed(0)}%`, 'border-purple-500'],
    ['OVERRIDES TODAY', s.overrides_today, 'border-orange-500'],
  ]
  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Operations Dashboard</h1>
      <div className="grid grid-cols-3 gap-4 mb-8">
        {cards.map(([t, v, c]: any, i: number) => (
          <div key={i} className={`bg-gray-900 rounded-lg p-4 border-l-4 ${c}`}>
            <p className="text-gray-400 text-xs uppercase">{t}</p>
            <p className="text-2xl font-bold mt-1">{v}</p>
          </div>
        ))}
      </div>
      {s.noisy_alerts?.length > 0 && (
        <div className="bg-gray-900 rounded-lg p-4 mb-4">
          <h3 className="font-bold mb-3">Noisy Alerts</h3>
          {s.noisy_alerts.map((a: any, i: number) => (
            <div key={i} className="flex justify-between text-sm py-1 border-b border-gray-800">
              <span className="text-gray-300">{a.title?.slice(0, 60)}</span>
              <span className="text-yellow-400 font-bold">{a.count}x</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// === INCIDENTS LIST + DETAIL ===
function IncidentsContent() {
  const [data, setData] = useState<any>(null)
  const [selected, setSelected] = useState<any>(null)
  const [detail, setDetail] = useState<any>(null)

  useEffect(() => {
    const load = () => fetch('/api/v1/incidents').then(r => r.json()).then(setData)
    load(); const t = setInterval(load, 10000); return () => clearInterval(t)
  }, [])

  const openDetail = async (id: string) => {
    setSelected(id)
    const r = await fetch(`/api/v1/incidents/${id}`)
    setDetail(await r.json())
  }

  const sc: any = { critical: 'bg-red-600', high: 'bg-orange-500', medium: 'bg-yellow-500', low: 'bg-blue-500', info: 'bg-gray-500' }

  if (selected && detail) {
    const inc = detail.incident
    const rcas = detail.rca_results || []
    return (
      <div>
        <button onClick={() => { setSelected(null); setDetail(null) }} className="text-blue-400 text-sm mb-4 hover:underline">← Back to list</button>
        <div className="bg-gray-900 rounded-lg p-5 mb-6">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-xl font-bold">{inc.title}</h2>
              <p className="text-gray-400 mt-1 text-sm">Host: {inc.impacted_host} | Service: {inc.impacted_service}</p>
            </div>
            <span className={`px-3 py-1 rounded text-sm font-bold text-white ${sc[inc.severity] || 'bg-gray-500'}`}>{inc.severity}</span>
          </div>
          <p className="mt-2 text-sm">Status: <span className="text-blue-400 font-medium">{inc.status}</span></p>
          <p className="text-gray-500 text-xs mt-1">Created: {inc.created_at?.slice(0, 19)}</p>
        </div>

        <h3 className="text-lg font-bold mb-4">RCA Analysis (P→R→A→O Rounds)</h3>
        {rcas.length === 0 ? <p className="text-gray-500">No analysis yet</p> : rcas.map((r: any) => (
          <div key={r.id} className="bg-gray-900 rounded-lg p-5 mb-4 border-l-4 border-blue-500">
            <div className="flex items-center gap-3 mb-3">
              <span className="bg-blue-600 text-xs px-2 py-1 rounded font-bold">Round {r.round_number}</span>
              <span className="text-sm">Confidence: <strong className={r.confidence > 0.6 ? 'text-green-400' : r.confidence > 0.3 ? 'text-yellow-400' : 'text-red-400'}>
                {(r.confidence * 100).toFixed(0)}%</strong></span>
              {r.override_applied && <span className="bg-orange-600 text-xs px-2 py-1 rounded">OVERRIDE</span>}
            </div>
            <div className="space-y-2 text-sm">
              <p><strong className="text-gray-300">Summary:</strong> {r.executive_summary}</p>
              <p><strong className="text-gray-300">Probable Cause:</strong> {r.probable_cause}</p>
              {r.missing_context?.length > 0 && (
                <div><strong className="text-gray-300">Missing Context:</strong>
                  <ul className="list-disc list-inside text-yellow-400 mt-1">{r.missing_context.map((m: string, i: number) => <li key={i}>{m}</li>)}</ul>
                </div>
              )}
              {r.next_checks?.length > 0 && (
                <div><strong className="text-gray-300">Next Checks:</strong>
                  <ul className="list-disc list-inside text-blue-400 mt-1">{r.next_checks.map((c: string, i: number) => <li key={i}>{c}</li>)}</ul>
                </div>
              )}
              {r.override_reason && <p className="text-orange-400"><strong>Override:</strong> {r.override_reason}</p>}
            </div>
          </div>
        ))}
      </div>
    )
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Incident Console</h1>
      {!data ? <p>Loading...</p> : (
        <div className="bg-gray-900 rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-800">
              <tr>
                <th className="p-3 text-left">Severity</th>
                <th className="p-3 text-left">Title</th>
                <th className="p-3 text-left">Host</th>
                <th className="p-3 text-left">Status</th>
                <th className="p-3 text-left">Created</th>
              </tr>
            </thead>
            <tbody>
              {data.incidents?.map((inc: any) => (
                <tr key={inc.id} className="border-t border-gray-800 hover:bg-gray-800/50 cursor-pointer" onClick={() => openDetail(inc.id)}>
                  <td className="p-3"><span className={`px-2 py-1 rounded text-xs font-bold text-white ${sc[inc.severity] || 'bg-gray-500'}`}>{inc.severity}</span></td>
                  <td className="p-3">{inc.title}</td>
                  <td className="p-3 text-gray-400">{inc.impacted_host || '-'}</td>
                  <td className="p-3 font-medium">{inc.status}</td>
                  <td className="p-3 text-gray-500 text-xs">{inc.created_at?.slice(0, 19)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

// === CHAT ===
function ChatContent() {
  const [msgs, setMsgs] = useState<any[]>([])
  const [inp, setInp] = useState('')
  const [iid, setIid] = useState('')
  const [loading, setLoading] = useState(false)

  const send = async () => {
    if (!inp.trim() || loading) return
    setMsgs(p => [...p, { role: 'user', content: inp }])
    setInp('')
    setLoading(true)
    try {
      const r = await fetch('/api/v1/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: inp, incident_id: iid || null }) })
      const d = await r.json()
      setMsgs(p => [...p, ...(d.messages || []).filter((m: any) => m.role === 'assistant')])
    } catch { setMsgs(p => [...p, { role: 'assistant', content: 'Error connecting' }]) }
    setLoading(false)
  }

  return (
    <div className="flex flex-col h-full">
      <h1 className="text-2xl font-bold mb-4">💬 Chat with AI Agent</h1>
      <input className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm w-80 mb-3" placeholder="Incident ID (optional)" value={iid} onChange={e => setIid(e.target.value)} />
      <div className="flex-1 bg-gray-900 rounded-lg p-4 overflow-y-auto mb-4 min-h-[400px] max-h-[500px]">
        {msgs.length === 0 && <p className="text-gray-500 text-sm">Send a message to start chatting with the AI agent...</p>}
        {msgs.map((m, i) => (
          <div key={i} className={`mb-3 ${m.role === 'user' ? 'text-right' : ''}`}>
            <span className={`inline-block px-4 py-2 rounded-lg text-sm max-w-[80%] ${m.role === 'user' ? 'bg-blue-600' : 'bg-gray-800'}`}>
              {m.step && <span className="text-xs text-blue-300 block mb-1">[{m.step.toUpperCase()}]</span>}
              {m.content}
            </span>
          </div>
        ))}
        {loading && <div className="text-gray-500 text-sm">AI is thinking...</div>}
      </div>
      <div className="flex gap-2">
        <input className="flex-1 bg-gray-800 border border-gray-700 rounded px-4 py-3 outline-none focus:border-blue-500" placeholder="Ask AI about incidents..." value={inp} onChange={e => setInp(e.target.value)} onKeyDown={e => e.key === 'Enter' && send()} />
        <button onClick={send} disabled={loading} className="bg-blue-600 hover:bg-blue-700 px-6 rounded font-semibold disabled:opacity-50">Send</button>
      </div>
    </div>
  )
}

// === SYSTEM INFO ===
function SystemInfoContent() {
  const [data, setData] = useState<any>(null)
  const [adrs, setAdrs] = useState<any>(null)
  const [tab, setTab] = useState('sys')
  useEffect(() => {
    fetch('/api/v1/system-info').then(r => r.json()).then(setData)
    fetch('/api/v1/system-info/adr').then(r => r.json()).then(setAdrs)
  }, [])
  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">System Information</h1>
      <div className="flex gap-2 mb-6">
        <button onClick={() => setTab('sys')} className={`px-4 py-2 rounded text-sm ${tab === 'sys' ? 'bg-blue-600' : 'bg-gray-800 hover:bg-gray-700'}`}>Operational Info</button>
        <button onClick={() => setTab('adr')} className={`px-4 py-2 rounded text-sm ${tab === 'adr' ? 'bg-blue-600' : 'bg-gray-800 hover:bg-gray-700'}`}>Architecture Decisions</button>
      </div>
      {tab === 'sys' && data && (
        <div className="grid gap-3">{data.items?.map((s: any) => (
          <div key={s.id} className="bg-gray-900 p-4 rounded-lg">
            <div className="flex items-center gap-3">
              <span className="font-bold text-blue-400">{s.hostname}</span>
              <span className="text-xs bg-gray-700 px-2 py-0.5 rounded">{s.criticality}</span>
              {s.synced_from_agent && <span className="text-xs text-green-400">Agent Synced</span>}
            </div>
            <p className="text-sm text-gray-400 mt-1">{s.role} | IP: {s.ip_addresses?.join(', ')}</p>
          </div>
        ))}</div>
      )}
      {tab === 'adr' && adrs && (
        <div className="grid gap-3">{adrs.items?.map((a: any) => (
          <div key={a.id} className="bg-gray-900 p-4 rounded-lg border-l-4 border-purple-500">
            <h3 className="font-bold">{a.title}</h3>
            <p className="text-sm text-gray-400 mt-1"><strong>Decision:</strong> {a.decision}</p>
            <p className="text-sm text-gray-500"><strong>Rationale:</strong> {a.rationale}</p>
          </div>
        ))}</div>
      )}
    </div>
  )
}

// === KNOWLEDGE ===
function KnowledgeContent() {
  const [data, setData] = useState<any>(null)
  useEffect(() => { fetch('/api/v1/knowledge').then(r => r.json()).then(setData) }, [])
  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Knowledge Base</h1>
      <div className="grid gap-3">{data?.items?.map((k: any) => (
        <div key={k.id} className="bg-gray-900 p-4 rounded-lg">
          <div className="flex items-center gap-2">
            <span className={`text-xs px-2 py-0.5 rounded ${k.type === 'known_issue' ? 'bg-red-800' : 'bg-green-800'}`}>{k.type}</span>
            <h3 className="font-bold">{k.title}</h3>
          </div>
          <p className="text-sm text-gray-400 mt-2 whitespace-pre-wrap">{k.content}</p>
        </div>
      ))}</div>
    </div>
  )
}

// === GOVERNANCE ===
function GovernanceContent() {
  const [data, setData] = useState<any>(null)
  useEffect(() => { fetch('/api/v1/governance').then(r => r.json()).then(setData) }, [])
  if (!data) return <p>Loading...</p>
  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">🛡️ Governance Panel</h1>
      <div className="grid grid-cols-3 gap-4 mb-8">
        <div className="bg-gray-900 p-4 rounded-lg"><p className="text-gray-400 text-xs">AI Auto Actions</p><p className="text-2xl font-bold mt-1">{data.total_ai_actions}</p></div>
        <div className="bg-gray-900 p-4 rounded-lg"><p className="text-gray-400 text-xs">Overrides</p><p className="text-2xl font-bold mt-1 text-orange-400">{data.total_overrides}</p></div>
        <div className="bg-gray-900 p-4 rounded-lg"><p className="text-gray-400 text-xs">Pending Approvals</p><p className="text-2xl font-bold mt-1">{data.pending_approvals?.length || 0}</p></div>
      </div>
      <h2 className="font-bold mb-3">Recent AI Actions</h2>
      <div className="space-y-2">{data.auto_actions?.slice(0, 20).map((a: any) => (
        <div key={a.id} className="bg-gray-900 p-3 rounded text-sm flex items-center gap-3">
          <span className="text-gray-500 text-xs w-40">{a.created_at?.slice(0, 19)}</span>
          <span className="bg-gray-700 px-2 py-0.5 rounded text-xs">{a.event_type}</span>
          <span>{a.action} — {a.actor}</span>
        </div>
      ))}</div>
      {data.overrides?.length > 0 && (
        <div className="mt-6">
          <h2 className="font-bold mb-3">Override History</h2>
          <div className="space-y-2">{data.overrides.map((o: any) => (
            <div key={o.id} className="bg-gray-900 p-3 rounded text-sm border-l-4 border-orange-500">
              <span className="text-gray-500 text-xs">{o.created_at?.slice(0, 19)}</span>
              <pre className="text-xs text-orange-300 mt-1 whitespace-pre-wrap">{JSON.stringify(o.details, null, 2)}</pre>
            </div>
          ))}</div>
        </div>
      )}
    </div>
  )
}

// === MAIN LAYOUT ===
const NAV = [
  { key: 'dashboard', label: 'Dashboard', icon: '📊' },
  { key: 'incidents', label: 'Incidents', icon: '🔔' },
  { key: 'chat', label: 'Chat AI', icon: '💬' },
  { key: 'sysinfo', label: 'System Info', icon: '🖥️' },
  { key: 'knowledge', label: 'Knowledge', icon: '📚' },
  { key: 'governance', label: 'Governance', icon: '🛡️' },
]

export default function MainApp() {
  const [page, setPage] = useState('dashboard')

  return (
    <div className="min-h-screen flex">
      <aside className="w-56 bg-gray-900 p-4 space-y-1 fixed h-full">
        <h2 className="text-blue-400 font-bold text-lg mb-6">AI Incident</h2>
        {NAV.map(n => (
          <button key={n.key} onClick={() => setPage(n.key)}
            className={`w-full flex items-center gap-3 p-3 rounded text-sm text-left transition-colors ${page === n.key ? 'bg-blue-600 text-white font-semibold' : 'text-gray-300 hover:bg-gray-800'}`}>
            <span>{n.icon}</span>{n.label}
          </button>
        ))}
        <div className="absolute bottom-4 left-4 right-4 text-xs text-gray-600">
          v1.0 • AI Incident Platform
        </div>
      </aside>

      <main className="flex-1 ml-56 p-6 overflow-y-auto">
        {page === 'dashboard' && <DashboardContent />}
        {page === 'incidents' && <IncidentsContent />}
        {page === 'chat' && <ChatContent />}
        {page === 'sysinfo' && <SystemInfoContent />}
        {page === 'knowledge' && <KnowledgeContent />}
        {page === 'governance' && <GovernanceContent />}
      </main>
    </div>
  )
}