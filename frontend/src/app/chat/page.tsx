'use client';
import { useState } from 'react';
import Link from 'next/link';

export default function ChatPage() {
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState('');
  const [incidentId, setIncidentId] = useState('');

  async function send() {
    if (!input.trim()) return;
    const userMsg = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');

    try {
      const res = await fetch('/api/v1/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input, incident_id: incidentId || null }),
      });
      const data = await res.json();
      if (data.messages) {
        setMessages(prev => [...prev, ...data.messages.filter((m: any) => m.role === 'assistant')]);
      }
    } catch { setMessages(prev => [...prev, { role: 'assistant', content: 'Error: khong ket noi duoc server' }]); }
  }

  return (
    <div className="min-h-screen flex flex-col p-6 max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-xl font-bold">💬 Chat with AI Agent</h1>
        <Link href="/dashboard" className="text-blue-400 text-sm">← Dashboard</Link>
      </div>
      <div className="mb-3">
        <input className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm w-96"
          placeholder="Incident ID (optional)" value={incidentId} onChange={e => setIncidentId(e.target.value)} />
      </div>
      <div className="flex-1 bg-gray-900 rounded-lg p-4 overflow-y-auto mb-4 min-h-[400px]">
        {messages.map((m, i) => (
          <div key={i} className={`mb-3 ${m.role === 'user' ? 'text-right' : ''}`}>
            <span className={`inline-block px-4 py-2 rounded-lg text-sm max-w-[80%] ${
              m.role === 'user' ? 'bg-blue-600' : 'bg-gray-800'}`}>
              {m.step && <span className="text-xs text-blue-300 block mb-1">[{m.step.toUpperCase()}]</span>}
              {m.content}
            </span>
          </div>
        ))}
      </div>
      <div className="flex gap-2">
        <input className="flex-1 bg-gray-800 border border-gray-700 rounded px-4 py-3 outline-none focus:border-blue-500"
          placeholder="Hoi AI ve su co..." value={input} onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && send()} />
        <button onClick={send} className="bg-blue-600 hover:bg-blue-700 px-6 rounded font-semibold">Gui</button>
      </div>
    </div>
  );
}