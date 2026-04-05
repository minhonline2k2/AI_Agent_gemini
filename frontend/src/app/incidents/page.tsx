'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';

export default function IncidentsPage() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    fetch('/api/v1/incidents').then(r => r.json()).then(setData).catch(console.error);
  }, []);

  const sevColor: Record<string, string> = {
    critical: 'bg-red-600', high: 'bg-orange-500', medium: 'bg-yellow-500',
    low: 'bg-blue-500', info: 'bg-gray-500',
  };
  const statusColor: Record<string, string> = {
    open: 'text-red-400', acknowledged: 'text-yellow-400',
    investigating: 'text-blue-400', resolved: 'text-green-400', closed: 'text-gray-400',
  };

  return (
    <div className="min-h-screen p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Incident Console</h1>
        <Link href="/dashboard" className="text-blue-400 hover:underline text-sm">← Dashboard</Link>
      </div>
      {!data ? <p>Loading...</p> : (
        <div className="bg-gray-900 rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-800"><tr>
              <th className="p-3 text-left">Severity</th>
              <th className="p-3 text-left">Title</th>
              <th className="p-3 text-left">Host</th>
              <th className="p-3 text-left">Status</th>
              <th className="p-3 text-left">Created</th>
            </tr></thead>
            <tbody>
              {data.incidents?.map((inc: any) => (
                <tr key={inc.id} className="border-t border-gray-800 hover:bg-gray-800/50 cursor-pointer"
                    onClick={() => window.location.href = `/incidents/${inc.id}`}>
                  <td className="p-3"><span className={`px-2 py-1 rounded text-xs font-bold text-white ${sevColor[inc.severity] || 'bg-gray-500'}`}>{inc.severity}</span></td>
                  <td className="p-3">{inc.title}</td>
                  <td className="p-3 text-gray-400">{inc.impacted_host || '-'}</td>
                  <td className={`p-3 font-medium ${statusColor[inc.status] || ''}`}>{inc.status}</td>
                  <td className="p-3 text-gray-500 text-xs">{inc.created_at?.slice(0,19)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}