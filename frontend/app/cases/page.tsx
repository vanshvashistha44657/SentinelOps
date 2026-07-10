"use client";
import { useState } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import { cn } from '@/lib/utils';
import { useCases } from '@/hooks/useData';
import { SOCTable, SOCBadge, SOCButton, SOCCard, SOCCardHeader, SOCCardContent } from '@/components/soc-ui';
import { SOCDrawer } from '@/components/soc-drawer';
import { InvestigationTimeline, EvidenceCard } from '@/components/cases/InvestigationTools';
import { Search, Filter, Download, Plus, ShieldAlert, Clock, User, Link as LinkIcon, MessageSquare } from 'lucide-react';

export default function CasesPage() {
  const { data: cases, isLoading } = useCases();
  const [selectedCase, setSelectedCase] = useState<any>(null);
  const [searchTerm, setSearchTerm] = useState('');

  const filteredCases = cases?.filter((c: any) => 
    c.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.id.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  const columns = [
    { label: 'ID', accessor: 'id' },
    { label: 'Case Title', accessor: 'title' },
    { label: 'Status', accessor: 'status', renderCell: (val: string) => <SOCBadge variant="info">{val}</SOCBadge> },
    { label: 'Priority', accessor: 'priority', renderCell: (val: string) => <SOCBadge variant={val === 'HIGH' ? 'warning' : 'info'}>{val}</SOCBadge> },
    { label: 'Owner', accessor: 'owner' },
  ];

  if (isLoading) return <DashboardLayout>Loading...</DashboardLayout>;

  // Mock data for investigation drawer to demonstrate functionality
  const mockEvidence = [
    { id: '1', type: 'IP' as const, value: '192.168.1.105', riskScore: 85, timestamp: '2024-07-10 10:00' },
    { id: '2', type: 'DOMAIN' as const, value: 'malicious-site.com', riskScore: 92, timestamp: '2024-07-10 10:05' },
    { id: '3', type: 'USER' as const, value: 'admin_service', riskScore: 40, timestamp: '2024-07-10 10:10' },
  ];

  const mockTimeline = [
    { id: 't1', type: 'SYSTEM' as const, title: 'Alert Ingested', description: 'Automated ingestion from SentinelOne', timestamp: '10:00:05' },
    { id: 't2', type: 'USER' as const, title: 'Case Created', description: 'Created by Analyst Sarah Jenkins', timestamp: '10:05:22' },
    { id: 't3', type: 'COMMENT' as const, title: 'Note Added', description: 'Initial triage complete. Scanning endpoints.', timestamp: '10:15:00' },
  ];

  return (
    <DashboardLayout>
      <div className="flex flex-col gap-6">
        <header className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-text-primary tracking-tight">Case Management</h1>
            <p className="text-text-secondary text-sm">Centralized investigation and resolution hub</p>
          </div>
          <div className="flex gap-3">
            <button className="soc-btn-secondary text-xs flex items-center gap-2">
              <Download size={14} /> Export
            </button>
            <button className="soc-btn-primary text-xs flex items-center gap-2">
              <Plus size={14} /> New Case
            </button>
          </div>
        </header>

        <div className="flex gap-4 items-center">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" size={16} />
            <input 
              type="text" 
              placeholder="Search cases, IDs, owners..." 
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
          <SOCCardHeader title="Active Investigations" />
          <SOCCardContent className="p-0">
            <SOCTable 
              headers={columns} 
              data={filteredCases}
              renderCell={(item: any, col: string) => {
                if (col === 'status') return <SOCBadge variant="info">{item[col]}</SOCBadge>;
                if (col === 'priority') return <SOCBadge variant={item[col] === 'HIGH' ? 'warning' : 'info'}>{item[col]}</SOCBadge>;
                return item[col];
              }}
            />
          </SOCCardContent>
        </SOCCard>
      </div>

      <SOCDrawer 
        isOpen={!!selectedCase} 
        onClose={() => setSelectedCase(null)} 
        title={`Investigation: ${selectedCase?.id || ''}`}
      >
        {selectedCase && (
          <div className="flex flex-col gap-6">
            {/* Case Overview */}
            <div className="space-y-4">
              <div className="flex justify-between items-start">
                <div className="space-y-1">
                  <h2 className="text-xl font-bold text-text-primary">{selectedCase.title}</h2>
                  <div className="flex items-center gap-2 text-xs text-text-muted">
                    <span className="bg-surface-3 px-2 py-0.5 rounded">CASE-${selectedCase.id.slice(0,8).toUpperCase()}</span>
                    <span>•</span>
                    <span className="flex items-center gap-1"><Clock size={12} /> Opened {new Date().toLocaleString()}</span>
                  </div>
                </div>
                <SOCBadge variant="critical">CRITICAL</SOCBadge>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div className="p-3 bg-surface-3 rounded-lg border border-border">
                  <p className="text-[10px] text-text-secondary uppercase mb-1">Status</p>
                  <p className="text-sm font-medium text-text-primary">INVESTIGATING</p>
                </div>
                <div className="p-3 bg-surface-3 rounded-lg border border-border">
                  <p className="text-[10px] text-text-secondary uppercase mb-1">Owner</p>
                  <p className="text-sm font-medium text-text-primary">Sarah Jenkins</p>
                </div>
                <div className="p-3 bg-surface-3 rounded-lg border border-border">
                  <p className="text-[10px] text-text-secondary uppercase mb-1">SLA</p>
                  <p className="text-sm font-medium text-critical">02:45:12</p>
                </div>
              </div>
            </div>

            {/* Investigation Tabs/Sections */}
            <div className="space-y-6">
              <section>
                <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
                  <ShieldAlert size={16} className="text-primary" /> Evidence Management
                </h3>
                <div className="grid grid-cols-3 gap-3">
                  {mockEvidence.map(ev => (
                    <EvidenceCard key={ev.id} item={ev} />
                  ))}
                </div>
              </section>

              <section>
                <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
                  <Clock size={16} className="text-primary" /> Investigation Timeline
                </h3>
                <InvestigationTimeline events={mockTimeline} />
              </section>

              <section>
                <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
                  <LinkIcon size={16} className="text-primary" /> Related Objects
                </h3>
                <div className="space-y-2">
                  <div className="p-3 bg-surface-2 rounded-lg border border-border flex items-center justify-between text-xs">
                    <div className="flex items-center gap-3">
                      <ShieldAlert size={14} className="text-warning" />
                      <span className="text-text-primary">Alert: Unusual PowerShell Execution</span>
                    </div>
                    <SOCBadge variant="info">Linked</SOCBadge>
                  </div>
                  <div className="p-3 bg-surface-2 rounded-lg border border-border flex items-center justify-between text-xs">
                    <div className="flex items-center gap-3">
                      <User size={14} className="text-info" />
                      <span className="text-text-primary">User: jdoe_admin</span>
                    </div>
                    <SOCBadge variant="info">Related</SOCBadge>
                  </div>
                </div>
              </section>

              <section>
                <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
                  <MessageSquare size={16} className="text-primary" /> Analyst Workspace
                </h3>
                <div className="space-y-3">
                  <div className="p-3 bg-surface-2 rounded-lg border border-border text-xs italic text-text-secondary">
                    "Initial triage complete. Scanning endpoints..."
                  </div>
                  <textarea 
                    className="soc-input w-full h-24 text-xs resize-none" 
                    placeholder="Add a note or comment..."
                  />
                </div>
              </section>
            </div>

            <div className="flex gap-3 mt-auto pt-6">
              <SOCButton variant="primary" className="flex-1">Update Case</SOCButton>
              <SOCButton variant="secondary" className="flex-1">Close Case</SOCButton>
            </div>
          </div>
        )}
      </SOCDrawer>
    </DashboardLayout>
  );
}
