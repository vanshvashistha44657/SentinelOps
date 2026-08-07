"use client";
import DashboardLayout from '@/components/DashboardLayout';
import { useAuditLogs } from '@/hooks/useData';
import { SOCTable, SOCCard, SOCCardHeader, SOCCardContent } from '@/components/soc-ui';

export default function AuditLogsPage() {
  const { data: logs } = useAuditLogs();

  return (
    <DashboardLayout>
      <div className="flex flex-col gap-6">
        <h1 className="text-2xl font-bold">Audit Logs</h1>
        <SOCCard>
          <SOCCardHeader title="System Audit Trail" />
          <SOCCardContent className="p-0">
            <SOCTable 
              headers={[{label: 'Timestamp', accessor: 'timestamp'}, {label: 'User', accessor: 'user_id'}, {label: 'Resource', accessor: 'resource'}, {label: 'Action', accessor: 'action'}]}
              data={logs || []}
            />
          </SOCCardContent>
        </SOCCard>
      </div>
    </DashboardLayout>
  );
}
