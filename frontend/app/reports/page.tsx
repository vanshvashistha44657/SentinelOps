"use client";
import DashboardLayout from '@/components/DashboardLayout';
import { useReports } from '@/hooks/useData';
import { Card } from '@/components/ui/components';

export default function ReportsPage() {
  const { data: reports, isLoading } = useReports();
  return (
    <DashboardLayout>
      <h1 className="text-3xl font-bold mb-6">Reports</h1>
      {isLoading ? <div>Loading...</div> : (
        <div className="space-y-4">
          {reports?.map((r: any) => (
            <Card key={r.id}>{r.title} ({r.type})</Card>
          ))}
        </div>
      )}
    </DashboardLayout>
  );
}
