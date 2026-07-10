"use client";
import { useAuthStore } from '@/store/useAuthStore';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import { useAlerts, useIncidents, useCases } from '@/hooks/useData';
import { KPICard, AlertTrendChart, RecentActivityFeed } from '@/components/dashboard/DashboardWidgets';
import { AlertTriangle, ShieldAlert, Briefcase, ShieldCheck } from 'lucide-react';

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

  const stats = [
    { title: "Critical Alerts", value: alerts?.filter((a: any) => a.severity === 'CRITICAL').length || 0, trend: 12, icon: AlertTriangle, variant: "critical" },
    { title: "Open Incidents", value: incidents?.filter((i: any) => i.status !== 'CLOSED').length || 0, trend: -5, icon: ShieldAlert, variant: "warning" },
    { title: "Active Cases", value: cases?.filter((c: any) => c.status !== 'CLOSED').length || 0, trend: 8, icon: Briefcase, variant: "info" },
    { title: "Intel Matches", value: 12, trend: 2, icon: ShieldCheck, variant: "success" },
  ];

  const trendData = [
    { name: '00:00', alerts: 12 },
    { name: '04:00', alerts: 18 },
    { name: '08:00', alerts: 45 },
    { name: '12:00', alerts: 32 },
    { name: '16:00', alerts: 67 },
    { name: '20:00', alerts: 21 },
  ];

  const activityFeed = alerts?.slice(0, 8).map((a: any) => ({
    title: a.title,
    description: `Source: ${a.source_ip} -> Dest: ${a.destination_ip}`,
    severity: a.severity,
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
  })) || [];

  return (
    <DashboardLayout>
      <div className="flex flex-col gap-8">
        <header className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-text-primary tracking-tight">Executive Overview</h1>
            <p className="text-text-secondary text-sm">Security posture and real-time threat landscape</p>
          </div>
          <div className="flex gap-3">
            <button className="soc-btn-secondary text-xs">Export Report</button>
            <button className="soc-btn-primary text-xs">System Refresh</button>
          </div>
        </header>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {stats.map((stat) => (
            <KPICard 
              key={stat.title} 
              title={stat.title} 
              value={stat.value} 
              trend={stat.trend} 
              icon={stat.icon} 
              variant={stat.variant as any} 
            />
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <AlertTrendChart data={trendData} />
          </div>
          <div className="lg:col-span-1">
            <RecentActivityFeed activities={activityFeed} />
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
