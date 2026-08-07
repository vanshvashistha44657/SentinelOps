"use client";
import DashboardLayout from '@/components/DashboardLayout';
import { SOCCard, SOCCardHeader, SOCCardContent } from '@/components/soc-ui';
import { useAdminStats } from '@/hooks/useData';

export default function AdminDashboardPage() {
  const { data: stats } = useAdminStats();

  return (
    <DashboardLayout>
      <div className="flex flex-col gap-6">
        <h1 className="text-2xl font-bold">Administration Dashboard</h1>
        <div className="grid grid-cols-3 gap-6">
          <SOCCard><SOCCardHeader title="Total Users" /><SOCCardContent>{stats?.total_users}</SOCCardContent></SOCCard>
          <SOCCard><SOCCardHeader title="Active Users" /><SOCCardContent>{stats?.active_users}</SOCCardContent></SOCCard>
          <SOCCard><SOCCardHeader title="Audit Events Today" /><SOCCardContent>{stats?.audit_events_today}</SOCCardContent></SOCCard>
        </div>
      </div>
    </DashboardLayout>
  );
}
