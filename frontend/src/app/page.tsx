'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const router = useRouter();

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    try {
      const res = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });
      if (!res.ok) { setError('Sai ten dang nhap hoac mat khau'); return; }
      const data = await res.json();
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('role', data.role);
      router.push('/dashboard');
    } catch { setError('Khong ket noi duoc server'); }
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="bg-gray-900 p-8 rounded-xl shadow-lg w-96">
        <h1 className="text-2xl font-bold text-blue-400 mb-6 text-center">AI Incident Platform</h1>
        <form onSubmit={handleLogin} className="space-y-4">
          <input className="w-full p-3 bg-gray-800 rounded border border-gray-700 focus:border-blue-500 outline-none"
            placeholder="Username" value={username} onChange={e => setUsername(e.target.value)} />
          <input className="w-full p-3 bg-gray-800 rounded border border-gray-700 focus:border-blue-500 outline-none"
            type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} />
          {error && <p className="text-red-400 text-sm">{error}</p>}
          <button className="w-full p-3 bg-blue-600 hover:bg-blue-700 rounded font-semibold" type="submit">Dang Nhap</button>
        </form>
        <p className="text-gray-500 text-xs mt-4 text-center">Demo: admin / admin123</p>
      </div>
    </div>
  );
}