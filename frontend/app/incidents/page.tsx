"use client";
import DashboardLayout from '@/components/DashboardLayout';
import { useIncidents } from '@/hooks/useData';
import { Card } from '@/components/ui/components';

export default function IncidentsPage() {
  const { data: incidents, isLoading } = useIncidents();
  return (
    <DashboardLayout>
      <h1 className="text-3xl font-bold mb-6">Incidents</h1>
      {isLoading ? <div>Loading...</div> : (
        <div className="space-y-4">
          {incidents?.map((inc: any) => (
            <Card key={inc.id}>{inc.title} - {inc.status}</Card>
          ))}
        </div>
      )}
    </DashboardLayout>
  );
}
