"use client";
import { useState } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import { cn } from '@/lib/utils';
import { useIncidents } from '@/hooks/useData';
import { SOCTable, SOCBadge, SOCButton, SOCCard, SOCCardHeader, SOCCardContent } from '@/components/soc-ui';
import { IncidentKanban } from '@/components/dashboard/IncidentKanban';
import { SOCDrawer } from '@/components/soc-drawer';
import { Search, Download, Filter, ShieldAlert, Clock, User, MessageSquare, Paperclip, Link as LinkIcon } from 'lucide-react';

export default function IncidentsPage() {
  const { data: incidents, isLoading } = useIncidents();
  const [view, setView] = useState<'table' | 'kanban'>('table');
  const [selectedIncident, setSelectedIncident] = useState<any>(null);
  const [searchTerm, setSearchTerm] = useState('');

  const filteredIncidents = incidents?.filter((inc: any) => 
    inc.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (inc.id && inc.id.toLowerCase().includes(searchTerm.toLowerCase()))
  ) || [];

  const columns = [
    { label: 'ID', accessor: 'id' },
    { label: 'Title', accessor: 'title' },
    { label: 'Status', accessor: 'status' },
    { label: 'Severity', accessor: 'severity' },
    { label: 'Owner', accessor: 'owner' },
  ];

  if (isLoading) return <DashboardLayout>Loading...</DashboardLayout>;

  return (
    <DashboardLayout>
      <div className="flex flex-col gap-6">
        <header className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-text-primary tracking-tight">Incident Response</h1>
            <p className="text-text-secondary text-sm">Investigate and manage security incidents</p>
          </div>
          <div className="flex gap-3">
            <button className="soc-btn-secondary text-xs flex items-center gap-2">
              <Download size={14} /> Export CSV
            </button>
            <button className="soc-btn-primary text-xs">New Incident</button>
          </div>
        </header>

        <div className="flex gap-4 items-center">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" size={16} />
            <input 
              type="text" 
              placeholder="Search incidents..." 
              className="soc-input pl-10 w-full"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <div className="flex bg-surface-1 rounded-md p-1 border border-border">
            <button 
              onClick={() => setView('table')}
              className={cn("px-3 py-1 text-xs rounded-md transition-all", view === 'table' ? "bg-surface-2 text-text-primary shadow-sm" : "text-text-muted hover:text-text-primary")}
            >
              Table
            </button>
            <button 
              onClick={() => setView('kanban')}
              className={cn("px-3 py-1 text-xs rounded-md transition-all", view === 'kanban' ? "bg-surface-2 text-text-primary shadow-sm" : "text-text-muted hover:text-text-primary")}
            >
              Kanban
            </button>
          </div>
          <button className="soc-btn-secondary text-xs flex items-center gap-2">
            <Filter size={14} /> Filters
          </button>
        </div>

        {view === 'table' ? (
          <SOCCard>
            <SOCCardHeader title="Incidents List" />
            <SOCCardContent className="p-0">
              <SOCTable 
                headers={columns} 
                data={filteredIncidents}
                renderCell={(item: any, col: string) => {
                  if (col === 'severity') {
                    const variant = item.severity === 'CRITICAL' ? 'critical' : 
                                    item.severity === 'HIGH' ? 'warning' : 'info';
                    return <SOCBadge variant={variant}>{item.severity}</SOCBadge>;
                  }
                  if (col === 'status') {
                    return <SOCBadge variant="info">{item.status}</SOCBadge>;
                  }
                  return item[col];
                }}
              />
            </SOCCardContent>
          </SOCCard>
        ) : (
          <IncidentKanban 
            incidents={filteredIncidents} 
            onIncidentClick={(inc) => setSelectedIncident(inc)} 
          />
        )}
      </div>

      <SOCDrawer 
        isOpen={!!selectedIncident} 
        onClose={() => setSelectedIncident(null)} 
        title={`Incident: ${selectedIncident?.id || ''}`}
      >
        {selectedIncident && (
          <div className="flex flex-col gap-6">
            <div className="flex justify-between items-start">
              <div className="space-y-1">
                <h2 className="text-xl font-bold text-text-primary">{selectedIncident.title}</h2>
                <div className="flex items-center gap-2 text-xs text-text-muted">
                  <span className="bg-surface-3 px-2 py-0.5 rounded">ID: {selectedIncident.id}</span>
                  <span>•</span>
                  <span className="flex items-center gap-1"><Clock size={12} /> Created {new Date(selectedIncident.created_at || Date.now()).toLocaleString()}</span>
                </div>
              </div>
              <SOCBadge variant={selectedIncident.severity === 'CRITICAL' ? 'critical' : 'warning'}>{selectedIncident.severity}</SOCBadge>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 bg-surface-3 rounded-lg border border-border">
                <p className="text-xs text-text-secondary uppercase mb-1">Current Status</p>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-primary" />
                  <span className="text-sm font-medium text-text-primary">{selectedIncident.status}</span>
                </div>
              </div>
              <div className="p-4 bg-surface-3 rounded-lg border border-border">
                <p className="text-xs text-text-secondary uppercase mb-1">Assigned To</p>
                <div className="flex items-center gap-2">
                  <User size={14} className="text-text-muted" />
                  <span className="text-sm font-medium text-text-primary">{selectedIncident.owner || 'Unassigned'}</span>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <h3 className="text-sm font-semibold border-b border-border pb-2">Investigation Workspace</h3>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-4">
                  <div className="p-4 bg-surface-2 rounded-lg border border-border space-y-3">
                    <h4 className="text-xs font-bold text-text-secondary uppercase flex items-center gap-2">
                      <ShieldAlert size={14} /> Evidence Panel
                    </h4>
                    <div className="space-y-2">
                      <div className="p-2 bg-surface-3 rounded text-[11px] font-mono text-text-secondary border border-border/50">
                        IP: 192.168.1.105
                      </div>
                      <div className="p-2 bg-surface-3 rounded text-[11px] font-mono text-text-secondary border border-border/50">
                        User: admin_service
                      </div>
                    </div>
                  </div>

                  <div className="p-4 bg-surface-2 rounded-lg border border-border space-y-3">
                    <h4 className="text-xs font-bold text-text-secondary uppercase flex items-center gap-2">
                      <LinkIcon size={14} /> Related Entities
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      <SOCBadge variant="info">Case #402</SOCBadge>
                      <SOCBadge variant="info">Alert #1290</SOCBadge>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="p-4 bg-surface-2 rounded-lg border border-border space-y-3">
                    <h4 className="text-xs font-bold text-text-secondary uppercase flex items-center gap-2">
                      <MessageSquare size={14} /> Comments
                    </h4>
                    <div className="text-xs text-text-muted italic">No comments yet.</div>
                  </div>
                  <div className="p-4 bg-surface-2 rounded-lg border border-border space-y-3">
                    <h4 className="text-xs font-bold text-text-secondary uppercase flex items-center gap-2">
                      <Paperclip size={14} /> Attachments
                    </h4>
                    <div className="text-xs text-text-muted">0 files</div>
                  </div>
                </div>
              </div>
            </div>

            <div className="space-y-4 pt-4">
              <h3 className="text-sm font-semibold border-b border-border pb-2">Timeline</h3>
              <div className="space-y-4 relative before:absolute before:left-2 before:top-2 before:bottom-2 before:w-px before:bg-border">
                {[1, 2, 3].map(i => (
                  <div key={i} className="pl-6 relative">
                    <div className="absolute left-0 top-1 w-4 h-4 rounded-full bg-surface-1 border-2 border-primary z-10" />
                    <div className="p-3 bg-surface-2 rounded border border-border text-xs">
                      <p className="text-text-primary font-medium mb-1">System Action</p>
                      <p className="text-text-muted">Activity recorded by automated workflow.</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex gap-3 mt-auto pt-6">
              <SOCButton variant="primary" className="flex-1">Update Status</SOCButton>
              <SOCButton variant="secondary" className="flex-1">Assign To Me</SOCButton>
            </div>
          </div>
        )}
      </SOCDrawer>
    </DashboardLayout>
  );
}
