"use client";
import { useAuthStore } from '@/store/useAuthStore';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import { useAlerts, useIncidents, useCases } from '@/hooks/useData';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
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
    { title: "Critical Alerts", value: alerts?.filter((a: any) => a.severity === 'CRITICAL').length || 0, icon: AlertTriangle, color: "text-critical" },
    { title: "Open Incidents", value: incidents?.filter((i: any) => i.status !== 'CLOSED').length || 0, icon: ShieldAlert, color: "text-warning" },
    { title: "Active Cases", value: cases?.filter((c: any) => c.status !== 'CLOSED').length || 0, icon: Briefcase, color: "text-primary" },
    { title: "Threat Intel Matches", value: 12, icon: ShieldCheck, color: "text-success" },
  ];

  return (
    <DashboardLayout>
      <h1 className="text-2xl font-bold mb-8">Executive Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat) => (
          <Card key={stat.title} className="bg-card border-border">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-text-secondary">{stat.title}</CardTitle>
              <stat.icon className={`h-4 w-4 ${stat.color}`} />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{stat.value}</div>
            </CardContent>
          </Card>
        ))}
      </div>
    </DashboardLayout>
  );
}
