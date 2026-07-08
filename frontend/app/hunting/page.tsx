"use client";
import DashboardLayout from '@/components/DashboardLayout';
import { useThreatHunting } from '@/hooks/useData';
import { Card } from '@/components/ui/components';

export default function HuntingPage() {
  const { data: queries, isLoading } = useThreatHunting();
  return (
    <DashboardLayout>
      <h1 className="text-3xl font-bold mb-6">Threat Hunting</h1>
      {isLoading ? <div>Loading...</div> : (
        <div className="space-y-4">
          {queries?.map((q: any) => (
            <Card key={q.id}>{q.query_string}</Card>
          ))}
        </div>
      )}
    </DashboardLayout>
  );
}
