'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';

export default function DashboardPage() {
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    fetch('/api/v1/dashboard/stats').then(r => r.json()).then(setStats).catch(console.error);
  }, []);

  const nav = [
    { href: '/dashboard', label: 'Dashboard', icon: '📊' },
    { href: '/incidents', label: 'Incidents', icon: '🔔' },
    { href: '/chat', label: 'Chat AI', icon: '💬' },
    { href: '/system-info', label: 'System Info', icon: '🖥️' },
    { href: '/knowledge', label: 'Knowledge', icon: '📚' },
    { href: '/governance', label: 'Governance', icon: '🛡️' },
  ];

  return (
    <div className="min-h-screen flex">
      <aside className="w-56 bg-gray-900 p-4 space-y-2">
        <h2 className="text-blue-400 font-bold text-lg mb-4">AI Incident</h2>
        {nav.map(n => (
          <Link key={n.href} href={n.href}
            className="flex items-center gap-2 p-2 rounded hover:bg-gray-800 text-sm">
            <span>{n.icon}</span>{n.label}
          </Link>
        ))}
      </aside>
      <main className="flex-1 p-6">
        <h1 className="text-2xl font-bold mb-6">Operations Dashboard</h1>
        {!stats ? <p>Loading...</p> : (
          <div className="grid grid-cols-4 gap-4 mb-8">
            <Card title="Total Incidents" value={stats.total_incidents} color="blue" />
            <Card title="Open" value={stats.open_incidents} color="yellow" />
            <Card title="Critical" value={stats.critical_incidents} color="red" />
            <Card title="Agents Online" value={`${stats.agents_online}/${stats.agents_total}`} color="green" />
            <Card title="Avg Confidence" value={`${(stats.avg_confidence * 100).toFixed(0)}%`} color="purple" />
            <Card title="Overrides Today" value={stats.overrides_today} color="orange" />
          </div>
        )}
      </main>
    </div>
  );
}

function Card({ title, value, color }: { title: string; value: any; color: string }) {
  const colors: Record<string, string> = {
    blue: 'border-blue-500', red: 'border-red-500', yellow: 'border-yellow-500',
    green: 'border-green-500', purple: 'border-purple-500', orange: 'border-orange-500',
  };
  return (
    <div className={`bg-gray-900 rounded-lg p-4 border-l-4 ${colors[color] || 'border-gray-500'}`}>
      <p className="text-gray-400 text-xs uppercase">{title}</p>
      <p className="text-2xl font-bold mt-1">{value}</p>
    </div>
  );
}