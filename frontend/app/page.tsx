"use client";
import { useAuthStore } from '@/store/useAuthStore';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import { useAlerts, useIncidents, useCases } from '@/hooks/useData';

export default function Dashboard() {
  const token = useAuthStore((state) => state.token);
  const router = useRouter();
  const { data: alerts } = useAlerts();
  const { data: incidents } = useIncidents();
  const { data: cases } = useCases();

  useEffect(() => {
    if (!token) router.push('/login');
  }, [token, router]);

  if (!token) return null;

  return (
    <DashboardLayout>
      <h1 className="text-3xl font-bold mb-6">Dashboard</h1>
      <div className="grid grid-cols-3 gap-4">
        <div className="p-4 bg-slate-800 rounded">Security Score: 85</div>
        <div className="p-4 bg-slate-800 rounded">Active Alerts: {alerts?.length || 0}</div>
        <div className="p-4 bg-slate-800 rounded">Open Incidents: {incidents?.filter((i:any) => i.status !== 'CLOSED').length || 0}</div>
        <div className="p-4 bg-slate-800 rounded">Open Cases: {cases?.filter((c:any) => c.status !== 'CLOSED').length || 0}</div>
      </div>
    </DashboardLayout>
  );
}
