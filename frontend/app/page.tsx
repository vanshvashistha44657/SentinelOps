"use client";
import { useAuthStore } from '@/store/useAuthStore';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import DashboardLayout from '@/components/DashboardLayout';

export default function Dashboard() {
  const token = useAuthStore((state) => state.token);
  const router = useRouter();

  useEffect(() => {
    if (!token) router.push('/login');
  }, [token, router]);

  if (!token) return null;

  return (
    <DashboardLayout>
      <h1 className="text-3xl font-bold mb-6">Dashboard</h1>
      <div className="grid grid-cols-3 gap-4">
        <div className="p-4 bg-slate-800 rounded">Security Score: 85</div>
        <div className="p-4 bg-slate-800 rounded">Active Alerts: 12</div>
        <div className="p-4 bg-slate-800 rounded">Open Incidents: 3</div>
      </div>
    </DashboardLayout>
  );
}
