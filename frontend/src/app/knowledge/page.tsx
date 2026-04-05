'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';

export default function KnowledgePage() {
  const [data, setData] = useState<any>(null);
  useEffect(() => { fetch('/api/v1/knowledge').then(r => r.json()).then(setData); }, []);

  return (
    <div className="min-h-screen p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Knowledge Base</h1>
        <Link href="/dashboard" className="text-blue-400 text-sm">← Dashboard</Link>
      </div>
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
  );
}