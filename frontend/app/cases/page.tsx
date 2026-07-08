"use client";
import DashboardLayout from '@/components/DashboardLayout';
import { useCases } from '@/hooks/useData';
import { Card } from '@/components/ui/components';

export default function CasesPage() {
  const { data: cases, isLoading } = useCases();
  return (
    <DashboardLayout>
      <h1 className="text-3xl font-bold mb-6">Cases</h1>
      {isLoading ? <div>Loading...</div> : (
        <div className="space-y-4">
          {cases?.map((c: any) => (
            <Card key={c.id}>{c.title} - {c.status}</Card>
          ))}
        </div>
      )}
    </DashboardLayout>
  );
}
