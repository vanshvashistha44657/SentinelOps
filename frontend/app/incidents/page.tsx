"use client";
import { useState } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import { cn } from '@/lib/utils';
import { useIncidents, useUpdateIncident } from '@/hooks/useData';
import { SOCTable, SOCBadge, SOCButton, SOCCard, SOCCardHeader, SOCCardContent } from '@/components/soc-ui';
import { IncidentKanban } from '@/components/dashboard/IncidentKanban';
import { SOCDrawer } from '@/components/soc-drawer';
import { Search, Download, Filter } from 'lucide-react';

export default function IncidentsPage() {
  const [params] = useState({ page: 1, size: 100 });
  const { data: incidentResponse, isLoading } = useIncidents(params);
  const updateIncident = useUpdateIncident();
  const [view, setView] = useState<'table' | 'kanban'>('table');
  const [selectedIncident, setSelectedIncident] = useState<any>(null);
  const [searchTerm, setSearchTerm] = useState('');

  const incidents = incidentResponse?.items || [];

  const filteredIncidents = incidents?.filter((inc: any) => 
    inc.title.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  const columns = [
    { label: 'Title', accessor: 'title' },
    { label: 'Status', accessor: 'status' },
    { label: 'Severity', accessor: 'severity' },
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
            <SOCButton variant="secondary" size="sm">Export CSV</SOCButton>
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
        </div>

        {view === 'table' ? (
          <SOCCard>
            <SOCCardHeader title="Incidents List" />
            <SOCCardContent className="p-0">
              <SOCTable 
                headers={columns} 
                data={filteredIncidents}
                onRowClick={setSelectedIncident}
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
            <h2 className="text-xl font-bold text-text-primary">{selectedIncident.title}</h2>
            <div className="flex gap-3">
              <SOCButton 
                variant="primary" 
                onClick={() => updateIncident.mutate({ id: selectedIncident.id, update: { status: 'UNDER_INVESTIGATION' } })}
              >
                Investigate
              </SOCButton>
              <SOCButton 
                variant="secondary" 
                onClick={() => updateIncident.mutate({ id: selectedIncident.id, update: { status: 'RESOLVED' } })}
              >
                Resolve
              </SOCButton>
            </div>
          </div>
        )}
      </SOCDrawer>
    </DashboardLayout>
  );
}
