"use client";
import { useState } from 'react';
import { useAuthStore } from '@/store/useAuthStore';
import api from '@/lib/api';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const setAuth = useAuthStore((state) => state.setAuth);
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      // Backend auth.py takes email and password
      const formData = new FormData();
      formData.append('username', email); // FastAPI OAuth2 expects 'username'
      formData.append('password', password);
      
      const res = await api.post('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });
      setAuth(res.data.access_token, res.data.user);
      router.push('/');
    } catch (error) {
      console.error('Login failed', error);
    }
  };

  return (
    <div className="flex h-screen items-center justify-center bg-background">
      <form onSubmit={handleLogin} className="p-8 border border-slate-700 rounded-lg">
        <h1 className="text-2xl mb-4">SentinelOps Login</h1>
        <input type="text" value={email} onChange={(e) => setEmail(e.target.value)} className="block w-full p-2 mb-2 bg-slate-900" placeholder="Email" />
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} className="block w-full p-2 mb-4 bg-slate-900" placeholder="Password" />
        <button type="submit" className="w-full bg-blue-600 p-2 rounded">Login</button>
      </form>
    </div>
  );
}
