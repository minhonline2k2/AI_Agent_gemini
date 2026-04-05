'use client';
import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';

export default function IncidentDetailPage() {
  const { id } = useParams();
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    if (id) fetch(`/api/v1/incidents/${id}`).then(r => r.json()).then(setData).catch(console.error);
  }, [id]);

  if (!data) return <div className="p-6">Loading...</div>;
  const inc = data.incident;
  const rcas = data.rca_results || [];

  return (
    <div className="min-h-screen p-6 max-w-5xl mx-auto">
      <Link href="/incidents" className="text-blue-400 hover:underline text-sm">← Back to Incidents</Link>
      <div className="bg-gray-900 rounded-lg p-6 mt-4">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-xl font-bold">{inc.title}</h1>
            <p className="text-gray-400 mt-1">Host: {inc.impacted_host} | Service: {inc.impacted_service}</p>
          </div>
          <span className="px-3 py-1 rounded bg-red-600 text-sm font-bold">{inc.severity}</span>
        </div>
        <p className="mt-2 text-sm">Status: <span className="text-blue-400 font-medium">{inc.status}</span></p>
      </div>

      <h2 className="text-lg font-bold mt-8 mb-4">RCA Analysis (P→R→A→O Rounds)</h2>
      {rcas.length === 0 ? <p className="text-gray-500">No analysis yet</p> : rcas.map((rca: any) => (
        <div key={rca.id} className="bg-gray-900 rounded-lg p-5 mb-4 border-l-4 border-blue-500">
          <div className="flex items-center gap-3 mb-3">
            <span className="bg-blue-600 text-xs px-2 py-1 rounded">Round {rca.round_number}</span>
            <span className="text-sm">Confidence: <strong className={rca.confidence > 0.6 ? 'text-green-400' : 'text-yellow-400'}>
              {(rca.confidence * 100).toFixed(0)}%</strong></span>
            {rca.override_applied && <span className="bg-orange-600 text-xs px-2 py-1 rounded">OVERRIDE</span>}
          </div>
          <div className="space-y-2 text-sm">
            <p><strong className="text-gray-300">Summary:</strong> {rca.executive_summary}</p>
            <p><strong className="text-gray-300">Probable Cause:</strong> {rca.probable_cause}</p>
            {rca.missing_context?.length > 0 && (
              <div><strong className="text-gray-300">Missing Context:</strong>
                <ul className="list-disc list-inside text-yellow-400 mt-1">
                  {rca.missing_context.map((m: string, i: number) => <li key={i}>{m}</li>)}
                </ul>
              </div>
            )}
            {rca.next_checks?.length > 0 && (
              <div><strong className="text-gray-300">Next Checks:</strong>
                <ul className="list-disc list-inside text-blue-400 mt-1">
                  {rca.next_checks.map((c: string, i: number) => <li key={i}>{c}</li>)}
                </ul>
              </div>
            )}
            {rca.override_reason && <p className="text-orange-400"><strong>Override:</strong> {rca.override_reason}</p>}
          </div>
        </div>
      ))}
    </div>
  );
}