"use client";
import { useState } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import { SOCButton, SOCCard, SOCCardHeader, SOCCardContent, SOCTable, SOCBadge } from '@/components/soc-ui';
import { Upload, Trash2, RefreshCw } from 'lucide-react';
import api from '@/lib/api';
import { useIngestionStatus, useIngestionStatistics, useFailedLogs, useDeleteFailedLog } from '@/hooks/useData';

export default function IngestionPage() {
  const [jsonContent, setJsonContent] = useState('');
  const { data: status } = useIngestionStatus();
  const { data: stats } = useIngestionStatistics();
  const { data: failedLogs } = useFailedLogs();
  const deleteFailed = useDeleteFailedLog();

  const handleUpload = async () => {
    try {
      const event = JSON.parse(jsonContent);
      await api.post('/ingestion/events', event);
      setJsonContent('');
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <DashboardLayout>
      <div className="flex flex-col gap-6">
        <header>
          <h1 className="text-2xl font-bold text-text-primary tracking-tight">Log Ingestion</h1>
        </header>

        <div className="grid grid-cols-3 gap-6">
          <SOCCard className="col-span-1">
            <SOCCardHeader title="Pipeline Status" />
            <SOCCardContent className="space-y-2 text-sm">
                <div>Status: {status?.status}</div>
                <div>Events Processed: {status?.events_processed}</div>
                <div>Failed Events: {status?.failed_events}</div>
            </SOCCardContent>
          </SOCCard>
          <SOCCard className="col-span-2">
            <SOCCardHeader title="Upload JSON Event" />
            <SOCCardContent className="flex flex-col gap-4">
              <textarea 
                value={jsonContent} 
                onChange={(e) => setJsonContent(e.target.value)} 
                className="w-full h-24 p-2 bg-surface-2 border border-border rounded text-xs"
                placeholder='{"event_type": "login", "severity": "CRITICAL", "username": "admin"}'
              />
              <SOCButton onClick={handleUpload} size="sm" className="flex items-center gap-2"><Upload size={14}/> Upload</SOCButton>
            </SOCCardContent>
          </SOCCard>
        </div>

        <SOCCard>
          <SOCCardHeader title="Failed Events" />
          <SOCCardContent className="p-0">
            <SOCTable 
                headers={[{label: 'Connector', accessor: 'source_connector'}, {label: 'Reason', accessor: 'error_reason'}, {label: 'Actions', accessor: 'actions'}]}
                data={failedLogs || []}
                renderCell={(item: any, col: string) => {
                    if (col === 'actions') return <SOCButton variant="secondary" size="xs" onClick={() => deleteFailed.mutate(item.id)}><Trash2 size={12}/></SOCButton>;
                    return item[col];
                }}
            />
          </SOCCardContent>
        </SOCCard>
      </div>
    </DashboardLayout>
  );
}
