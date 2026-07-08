"use client";
import DashboardLayout from '@/components/DashboardLayout';
import { useThreatIntel } from '@/hooks/useData';
import { Card } from '@/components/ui/components';

export default function ThreatIntelPage() {
  const { data: intel, isLoading } = useThreatIntel();
  return (
    <DashboardLayout>
      <h1 className="text-3xl font-bold mb-6">Threat Intelligence</h1>
      {isLoading ? <div>Loading...</div> : (
        <div className="space-y-4">
          {intel?.map((i: any) => (
            <Card key={i.id}>{i.value} - {i.source}</Card>
          ))}
        </div>
      )}
    </DashboardLayout>
  );
}
