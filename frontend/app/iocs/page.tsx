"use client";
import DashboardLayout from '@/components/DashboardLayout';
import { useIOCs } from '@/hooks/useData';
import { Card } from '@/components/ui/components';

export default function IOCsPage() {
  const { data: iocs, isLoading } = useIOCs();
  return (
    <DashboardLayout>
      <h1 className="text-3xl font-bold mb-6">IOC Management</h1>
      {isLoading ? <div>Loading...</div> : (
        <div className="space-y-4">
          {iocs?.map((ioc: any) => (
            <Card key={ioc.id}>{ioc.value} - {ioc.type}</Card>
          ))}
        </div>
      )}
    </DashboardLayout>
  );
}
