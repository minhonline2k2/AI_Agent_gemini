'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';

export default function SystemInfoPage() {
  const [data, setData] = useState<any>(null);
  const [adrs, setAdrs] = useState<any>(null);
  const [tab, setTab] = useState('systems');

  useEffect(() => {
    fetch('/api/v1/system-info').then(r => r.json()).then(setData);
    fetch('/api/v1/system-info/adr').then(r => r.json()).then(setAdrs);
  }, []);

  return (
    <div className="min-h-screen p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">System Information</h1>
        <Link href="/dashboard" className="text-blue-400 text-sm">← Dashboard</Link>
      </div>
      <div className="flex gap-2 mb-6">
        <button onClick={() => setTab('systems')} className={`px-4 py-2 rounded ${tab === 'systems' ? 'bg-blue-600' : 'bg-gray-800'}`}>Operational Info</button>
        <button onClick={() => setTab('adr')} className={`px-4 py-2 rounded ${tab === 'adr' ? 'bg-blue-600' : 'bg-gray-800'}`}>Architecture Decisions</button>
      </div>
      {tab === 'systems' && data && (
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
            <p className="text-sm text-gray-400"><strong>Rationale:</strong> {a.rationale}</p>
          </div>
        ))}</div>
      )}
    </div>
  );
}