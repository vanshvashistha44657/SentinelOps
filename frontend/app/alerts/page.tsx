"use client";
import DashboardLayout from '@/components/DashboardLayout';
import { useAlerts } from '@/hooks/useData';
import { Card, Badge } from '@/components/ui/components';

export default function AlertsPage() {
  const { data: alerts, isLoading } = useAlerts();
  if (isLoading) return <DashboardLayout>Loading...</DashboardLayout>;

  return (
    <DashboardLayout>
      <h1 className="text-3xl font-bold mb-6">Alerts</h1>
      <div className="space-y-4">
        {alerts?.map((alert: any) => (
          <Card key={alert.id} className="flex justify-between">
            <div>
              <h3 className="font-semibold">{alert.title}</h3>
              <p className="text-sm text-slate-400">{alert.description}</p>
            </div>
            <Badge className={alert.severity === 'CRITICAL' ? 'bg-red-500' : 'bg-yellow-500'}>{alert.severity}</Badge>
          </Card>
        ))}
      </div>
    </DashboardLayout>
  );
}
