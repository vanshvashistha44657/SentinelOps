"use client";
import { useState } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import { useAlerts } from '@/hooks/useData';
import { SOCTable, SOCBadge, SOCButton, SOCCard, SOCCardHeader, SOCCardContent } from '@/components/soc-ui';
import { SOCDrawer } from '@/components/soc-drawer';
import { Filter, Download, MoreVertical, Search, ShieldAlert } from 'lucide-react';

export default function AlertsPage() {
  const { data: alerts, isLoading } = useAlerts();
  const [selectedAlert, setSelectedAlert] = useState<any>(null);
  const [searchTerm, setSearchTerm] = useState('');

  const filteredAlerts = alerts?.filter((a: any) => 
    a.title.toLowerCase().includes(searchTerm.toLowerCase()) || 
    a.source_ip?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    a.destination_ip?.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  const columns = [
    { label: 'Severity', accessor: 'severity' },
    { label: 'Alert Title', accessor: 'title' },
    { label: 'Source IP', accessor: 'source_ip' },
    { label: 'Destination IP', accessor: 'destination_ip' },
    { label: 'Status', accessor: 'status' },
    { label: 'Hostname', accessor: 'hostname' },
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
            <button className="soc-btn-secondary text-xs flex items-center gap-2">
              <Download size={14} /> Export CSV
            </button>
            <button className="soc-btn-primary text-xs">Assign Analyst</button>
          </div>
        </header>

        <div className="flex gap-4 items-center mb-4">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" size={16} />
            <input 
              type="text" 
              placeholder="Search alerts, IPs, hostnames..." 
              className="soc-input pl-10 w-full"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <button className="soc-btn-secondary text-xs flex items-center gap-2">
            <Filter size={14} /> Filters
          </button>
        </div>

        <SOCCard>
          <SOCCardHeader title="Detection Events" />
          <SOCCardContent className="p-0">
            <SOCTable 
              headers={columns} 
              data={filteredAlerts}
              renderCell={(item: any, col: string) => {
                if (col === 'severity') {
                  const variant = item.severity === 'CRITICAL' ? 'critical' : 
                                  item.severity === 'HIGH' ? 'warning' : 'info';
                  return <SOCBadge variant={variant}>{item.severity}</SOCBadge>;
                }
                if (col === 'status') {
                  return <SOCBadge variant="info">{item.status}</SOCBadge>;
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
        title={`Alert Analysis: ${selectedAlert?.id}`}
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

            <div>
              <h4 className="text-sm font-semibold mb-3 flex items-center gap-2">
                <ShieldAlert size={16} className="text-primary" /> Event Details
              </h4>
              <div className="p-4 bg-surface-3 rounded-lg border border-border space-y-3 text-sm">
                <div className="flex justify-between py-1 border-b border-border/50">
                  <span className="text-text-muted">Source IP</span>
                  <span className="text-text-primary font-mono">{selectedAlert.source_ip}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-border/50">
                  <span className="text-text-muted">Destination IP</span>
                  <span className="text-text-primary font-mono">{selectedAlert.destination_ip}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-border/50">
                  <span className="text-text-muted">Hostname</span>
                  <span className="text-text-primary font-mono">{selectedAlert.hostname}</span>
                </div>
              </div>
            </div>

            <div>
              <h4 className="text-sm font-semibold mb-3">Timeline</h4>
              <div className="space-y-4 relative before:absolute before:left-2 before:top-2 before:bottom-2 before:w-px before:bg-border">
                {[1, 2, 3].map(i => (
                  <div key={i} className="pl-6 relative">
                    <div className="absolute left-0 top-1 w-4 h-4 rounded-full bg-surface-1 border-2 border-primary z-10" />
                    <div className="p-3 bg-surface-2 rounded border border-border text-xs">
                      <p className="text-text-primary font-medium mb-1">Event detected by Detection Engine v1.2</p>
                      <p className="text-text-muted">Timestamp: {new Date().toISOString()}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex gap-3 mt-auto pt-6">
              <SOCButton variant="primary" className="flex-1">Promote to Incident</SOCButton>
              <SOCButton variant="secondary">Dismiss Alert</SOCButton>
            </div>
          </div>
        )}
      </SOCDrawer>
    </DashboardLayout>
  );
}
