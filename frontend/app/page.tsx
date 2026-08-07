"use client";
import { useAuthStore } from '@/store/useAuthStore';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import { useDashboardOverview, useDashboardMetrics, useDashboardCharts, useDashboardTop, useAlerts } from '@/hooks/useData';
import { KPICard, AlertTrendChart, RecentActivityFeed } from '@/components/dashboard/DashboardWidgets';
import { AlertTriangle, ShieldAlert, Briefcase, ShieldCheck } from 'lucide-react';

export default function Dashboard() {
  const token = useAuthStore((state) => state.token);
  const router = useRouter();
  const { data: overview, isLoading: loadingOverview } = useDashboardOverview();
  const { data: metrics, isLoading: loadingMetrics } = useDashboardMetrics();
  const { data: charts, isLoading: loadingCharts } = useDashboardCharts();
  const { data: top, isLoading: loadingTop } = useDashboardTop();
  const { data: alertsResponse } = useAlerts({ page: 1, size: 8 });

  useEffect(() => {
    if (!token) router.push('/login');
  }, [token, router]);

  if (!token) return null;
  if (loadingOverview || loadingMetrics || loadingCharts || loadingTop) return <DashboardLayout>Loading...</DashboardLayout>;

  const stats = [
    { title: "Critical Alerts", value: overview?.critical_alerts || 0, trend: 12, icon: AlertTriangle, variant: "critical" },
    { title: "Open Incidents", value: overview?.open_incidents || 0, trend: -5, icon: ShieldAlert, variant: "warning" },
    { title: "Active Cases", value: overview?.active_cases || 0, trend: 8, icon: Briefcase, variant: "info" },
    { title: "Cases Closed Today", value: metrics?.cases_closed_today || 0, trend: 2, icon: ShieldCheck, variant: "success" },
  ];

  const activityFeed = alertsResponse?.items.map((a: any) => ({
    title: a.title,
    description: `Source: ${a.source_ip} -> Dest: ${a.destination_ip}`,
    severity: a.severity,
    timestamp: new Date(a.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
  })) || [];

  return (
    <DashboardLayout>
      <div className="flex flex-col gap-8">
        <header className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-text-primary tracking-tight">Executive Overview</h1>
            <p className="text-text-secondary text-sm">Security posture and real-time threat landscape</p>
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
            <AlertTrendChart data={charts?.alerts_over_time || []} />
          </div>
          <div className="lg:col-span-1">
            <RecentActivityFeed activities={activityFeed} />
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
