'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';

export default function GovernancePage() {
  const [data, setData] = useState<any>(null);
  useEffect(() => { fetch('/api/v1/governance').then(r => r.json()).then(setData); }, []);

  return (
    <div className="min-h-screen p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">🛡️ Governance Panel</h1>
        <Link href="/dashboard" className="text-blue-400 text-sm">← Dashboard</Link>
      </div>
      {data && <>
        <div className="grid grid-cols-3 gap-4 mb-8">
          <div className="bg-gray-900 p-4 rounded-lg"><p className="text-gray-400 text-xs">AI Auto Actions</p><p className="text-2xl font-bold mt-1">{data.total_ai_actions}</p></div>
          <div className="bg-gray-900 p-4 rounded-lg"><p className="text-gray-400 text-xs">Overrides</p><p className="text-2xl font-bold mt-1 text-orange-400">{data.total_overrides}</p></div>
          <div className="bg-gray-900 p-4 rounded-lg"><p className="text-gray-400 text-xs">Pending Approvals</p><p className="text-2xl font-bold mt-1">{data.pending_approvals?.length || 0}</p></div>
        </div>
        <h2 className="text-lg font-bold mb-3">Recent AI Actions</h2>
        <div className="space-y-2">{data.auto_actions?.slice(0, 20).map((a: any) => (
          <div key={a.id} className="bg-gray-900 p-3 rounded text-sm flex items-center gap-3">
            <span className="text-gray-500 text-xs w-40">{a.created_at?.slice(0,19)}</span>
            <span className="bg-gray-700 px-2 py-0.5 rounded text-xs">{a.event_type}</span>
            <span>{a.action}</span>
            <span className="text-gray-500">{a.actor}</span>
          </div>
        ))}</div>
        {data.overrides?.length > 0 && <>
          <h2 className="text-lg font-bold mb-3 mt-8">Override History</h2>
          <div className="space-y-2">{data.overrides.map((o: any) => (
            <div key={o.id} className="bg-gray-900 p-3 rounded text-sm border-l-4 border-orange-500">
              <span className="text-gray-500 text-xs">{o.created_at?.slice(0,19)}</span>
              <pre className="text-xs text-orange-300 mt-1">{JSON.stringify(o.details, null, 2)}</pre>
            </div>
          ))}</div>
        </>}
      </>}
    </div>
  );
}