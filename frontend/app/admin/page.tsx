"use client";
import DashboardLayout from '@/components/DashboardLayout';
import { useAdminUsers } from '@/hooks/useData';
import { Card } from '@/components/ui/components';

export default function AdminPage() {
  const { data: users, isLoading } = useAdminUsers();
  return (
    <DashboardLayout>
      <h1 className="text-3xl font-bold mb-6">Admin Panel</h1>
      {isLoading ? <div>Loading...</div> : (
        <div className="space-y-4">
          {users?.map((u: any) => (
            <Card key={u.id}>{u.full_name} ({u.email})</Card>
          ))}
        </div>
      )}
    </DashboardLayout>
  );
}
