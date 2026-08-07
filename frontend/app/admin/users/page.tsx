"use client";
import DashboardLayout from '@/components/DashboardLayout';
import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api';
import { SOCTable, SOCCard, SOCCardHeader, SOCCardContent } from '@/components/soc-ui';

export default function UsersPage() {
  const { data: users } = useQuery({ queryKey: ['admin-users'], queryFn: () => api.get('/admin/users').then(res => res.data) });

  return (
    <DashboardLayout>
      <div className="flex flex-col gap-6">
        <h1 className="text-2xl font-bold">User Management</h1>
        <SOCCard>
          <SOCCardHeader title="System Users" />
          <SOCCardContent className="p-0">
            <SOCTable 
              headers={[{label: 'Name', accessor: 'full_name'}, {label: 'Email', accessor: 'email'}, {label: 'Role', accessor: 'role_id'}]}
              data={users || []}
            />
          </SOCCardContent>
        </SOCCard>
      </div>
    </DashboardLayout>
  );
}
