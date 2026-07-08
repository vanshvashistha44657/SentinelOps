"use client";
import DashboardLayout from '@/components/DashboardLayout';
import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api';
import { Card } from '@/components/ui/components';

export default function AssetsPage() {
  const { data: assets, isLoading } = useQuery({ queryKey: ['assets'], queryFn: () => api.get('/assets/').then(res => res.data) });
  
  return (
    <DashboardLayout>
      <h1 className="text-3xl font-bold mb-6">Asset Management</h1>
      {isLoading ? <div>Loading...</div> : (
        <div className="space-y-4">
          {assets?.map((a: any) => (
            <Card key={a.id}>{a.name} - {a.ip_address || 'No IP'}</Card>
          ))}
        </div>
      )}
    </DashboardLayout>
  );
}
