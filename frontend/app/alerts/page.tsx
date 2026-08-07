"use client";
import { useState } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import { useAlerts, useUpdateAlert, useDeleteAlert } from '@/hooks/useData';
import { SOCTable, SOCBadge, SOCButton, SOCCard, SOCCardHeader, SOCCardContent } from '@/components/soc-ui';
import { SOCDrawer } from '@/components/soc-drawer';
import { Filter, Download, Search, ShieldAlert, Trash2 } from 'lucide-react';

export default function AlertsPage() {
  const [params, setParams] = useState({ page: 1, size: 20 });
  const { data: alertResponse, isLoading } = useAlerts(params);
  const updateAlert = useUpdateAlert();
  const deleteAlert = useDeleteAlert();
  
  const [selectedAlert, setSelectedAlert] = useState<any>(null);
  const [searchTerm, setSearchTerm] = useState('');

  const alerts = alertResponse?.items || [];

  const columns = [
    { label: 'Severity', accessor: 'severity' },
    { label: 'Alert Title', accessor: 'title' },
    { label: 'Source IP', accessor: 'source_ip' },
    { label: 'Destination IP', accessor: 'destination_ip' },
    { label: 'Status', accessor: 'status' },
    { label: 'Actions', accessor: 'actions' },
  ];

  if (isLoading) return <DashboardLayout>Loading...</DashboardLayout>;

  return (
    <DashboardLayout>
      <div className="flex flex-col gap-6">
        <header className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-text-primary tracking-tight">Security Alerts</h1>
            <p className="text-text-secondary text-sm">Real-time detection event monitoring</p>
          </div>
          <div className="flex gap-3">
            <SOCButton variant="secondary" size="sm">Export CSV</SOCButton>
          </div>
        </header>

        <div className="flex gap-4 items-center mb-4">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" size={16} />
            <input 
              type="text" 
              placeholder="Search..." 
              className="soc-input pl-10 w-full"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <SOCButton variant="secondary" size="sm" className="flex items-center gap-2">
            <Filter size={14} /> Filters
          </SOCButton>
        </div>

        <SOCCard>
          <SOCCardHeader title="Detection Events" />
          <SOCCardContent className="p-0">
            <SOCTable 
              headers={columns} 
              data={alerts}
              onRowClick={setSelectedAlert}
              renderCell={(item: any, col: string) => {
                if (col === 'severity') {
                  const variant = item.severity === 'CRITICAL' ? 'critical' : 
                                  item.severity === 'HIGH' ? 'warning' : 'info';
                  return <SOCBadge variant={variant}>{item.severity}</SOCBadge>;
                }
                if (col === 'status') {
                  return <SOCBadge variant="info">{item.status}</SOCBadge>;
                }
                if (col === 'actions') {
                  return (
                    <button 
                      onClick={(e) => { e.stopPropagation(); deleteAlert.mutate(item.id); }}
                      className="text-text-muted hover:text-critical"
                    >
                      <Trash2 size={16} />
                    </button>
                  );
                }
                return item[col] as React.ReactNode;
              }}
            />
          </SOCCardContent>
        </SOCCard>
      </div>

      <SOCDrawer 
        isOpen={!!selectedAlert} 
        onClose={() => setSelectedAlert(null)} 
        title={`Alert Analysis`}
      >
        {selectedAlert && (
          <div className="flex flex-col gap-6">
            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 bg-surface-3 rounded-lg border border-border">
                <p className="text-xs text-text-secondary uppercase mb-1">Severity</p>
                <p className="text-lg font-bold text-critical">{selectedAlert.severity}</p>
              </div>
              <div className="p-4 bg-surface-3 rounded-lg border border-border">
                <p className="text-xs text-text-secondary uppercase mb-1">Confidence</p>
                <p className="text-lg font-bold text-text-primary">{selectedAlert.confidence_score}%</p>
              </div>
            </div>

            <div className="flex gap-3 mt-auto pt-6">
              <SOCButton 
                variant="primary" 
                className="flex-1"
                onClick={() => updateAlert.mutate({ id: selectedAlert.id, update: { status: 'INVESTIGATING' } })}
              >
                Start Investigation
              </SOCButton>
              <SOCButton 
                variant="secondary"
                onClick={() => updateAlert.mutate({ id: selectedAlert.id, update: { status: 'CLOSED' } })}
              >
                Dismiss Alert
              </SOCButton>
            </div>
          </div>
        )}
      </SOCDrawer>
    </DashboardLayout>
  );
}
