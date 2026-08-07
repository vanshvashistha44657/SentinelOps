"use client";
import { useState } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import { cn } from '@/lib/utils';
import { useCases, useCaseNotes, useCaseEvidence, useAddCaseNote, useAddCaseEvidence } from '@/hooks/useData';
import { SOCTable, SOCBadge, SOCButton, SOCCard, SOCCardHeader, SOCCardContent, SOCInput } from '@/components/soc-ui';
import { SOCDrawer } from '@/components/soc-drawer';
import { InvestigationTimeline, EvidenceCard } from '@/components/cases/InvestigationTools';
import { Search, Filter, Plus, ShieldAlert, Clock, MessageSquare, Paperclip, AlertCircle, AlertTriangle } from 'lucide-react';

export default function CasesPage() {
  const [params] = useState({ page: 1, size: 100 });
  const { data: caseResponse, isLoading } = useCases(params);
  const [selectedCase, setSelectedCase] = useState<any>(null);
  const { data: notes, refetch: refetchNotes } = useCaseNotes(selectedCase?.id || '');
  const { data: evidence, refetch: refetchEvidence } = useCaseEvidence(selectedCase?.id || '');
  
  const addNote = useAddCaseNote();
  const addEvidence = useAddCaseEvidence();
  const [noteContent, setNoteContent] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  const cases = caseResponse?.items || [];
  const filteredCases = cases?.filter((c: any) => 
    c.title.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  const columns = [
    { label: 'ID', accessor: 'id' },
    { label: 'Case Title', accessor: 'title' },
    { label: 'Status', accessor: 'status' },
    { label: 'Priority', accessor: 'priority' },
  ];

  if (isLoading) return <DashboardLayout>Loading...</DashboardLayout>;

  return (
    <DashboardLayout>
      <div className="flex flex-col gap-6">
        {/* ... (header and search remain the same) */}
        <header className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-text-primary tracking-tight">Case Management</h1>
            <p className="text-text-secondary text-sm">Centralized investigation and resolution hub</p>
          </div>
          <SOCButton variant="primary" size="sm" className="flex items-center gap-2">
            <Plus size={14} /> New Case
          </SOCButton>
        </header>
        
        {/* ... (table section remains same) */}
        <SOCCard>
          <SOCCardContent className="p-0">
            <SOCTable 
              headers={columns} 
              data={filteredCases}
              onRowClick={setSelectedCase}
              renderCell={(item: any, col: string) => {
                if (col === 'status') return <SOCBadge variant="info">{item.status}</SOCBadge>;
                if (col === 'priority') return <SOCBadge variant={item.priority === 'HIGH' ? 'warning' : 'info'}>{item.priority}</SOCBadge>;
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
            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 bg-surface-3 rounded-lg border border-border">
                <p className="text-[10px] text-text-secondary uppercase mb-1">Status</p>
                <p className="text-sm font-medium text-text-primary">{selectedCase.status}</p>
              </div>
              <div className="p-3 bg-surface-3 rounded-lg border border-border">
                <p className="text-[10px] text-text-secondary uppercase mb-1">Priority</p>
                <p className="text-sm font-medium text-text-primary">{selectedCase.priority}</p>
              </div>
            </div>

            <section>
              <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
                <ShieldAlert size={16} className="text-primary" /> Evidence
              </h3>
              <div className="grid grid-cols-2 gap-3 mb-2">
                {evidence?.map((ev: any) => (
                  <EvidenceCard key={ev.id} item={{ id: ev.id, type: ev.type, value: ev.value, riskScore: 50, timestamp: ev.created_at }} />
                ))}
              </div>
            </section>
            
            <section>
              <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
                <Paperclip size={16} className="text-primary" /> Attachments
              </h3>
              <div className="p-4 border-2 border-dashed border-border rounded-lg text-center text-xs text-text-muted">
                Drag and drop files to upload
              </div>
            </section>

            <section>
              <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
                <Clock size={16} className="text-primary" /> Timeline / Notes
              </h3>
              <InvestigationTimeline events={notes?.map((n: any) => ({
                id: n.id, type: 'COMMENT', title: 'Analyst Note', description: n.content, timestamp: new Date(n.created_at).toLocaleTimeString()
              })) || []} />
              
              <div className="flex gap-2 mt-2">
                <SOCInput value={noteContent} onChange={(e) => setNoteContent(e.target.value)} placeholder="Add note..." />
                <SOCButton onClick={() => addNote.mutate({ caseId: selectedCase.id, note: { content: noteContent } }, { onSuccess: () => setNoteContent('') })}>Add</SOCButton>
              </div>
            </section>
          </div>
        )}
      </SOCDrawer>
    </DashboardLayout>
  );
}
