"use client";
import { useState } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import { useThreatHuntingSearch, useThreatHuntingHistory, useSavedHuntingQueries, useSaveHuntingQuery, useDeleteHuntingQuery } from '@/hooks/useData';
import { SOCTable, SOCButton, SOCCard, SOCCardHeader, SOCCardContent, SOCInput, SOCBadge } from '@/components/soc-ui';
import { Search, Save, Trash2, ChevronRight, ChevronDown } from 'lucide-react';

export default function ThreatHuntingPage() {
  const [query, setQuery] = useState('');
  const [page, setPage] = useState(1);
  const [size] = useState(20);
  const [executeSearch, setExecuteSearch] = useState(false);
  const { data: searchResponse, isLoading: searching } = useThreatHuntingSearch(query, page, size, executeSearch);
  const { data: history } = useThreatHuntingHistory();
  const { data: savedQueries } = useSavedHuntingQueries();
  const saveQuery = useSaveHuntingQuery();
  const deleteQuery = useDeleteHuntingQuery();
  const [expandedRow, setExpandedRow] = useState<string | null>(null);

  const handleSearch = () => {
    setExecuteSearch(true);
  };

  const results = searchResponse?.items || [];

  return (
    <DashboardLayout>
      <div className="flex flex-col gap-6">
        <header>
          <h1 className="text-2xl font-bold text-text-primary tracking-tight">Threat Hunting</h1>
        </header>

        <div className="flex gap-2">
          <SOCInput value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Enter search query (e.g., event_type=login)..." className="flex-1" />
          <SOCButton onClick={handleSearch} className="flex items-center gap-2"><Search size={16}/>Search</SOCButton>
          <SOCButton variant="secondary" onClick={() => saveQuery.mutate({ name: query.substring(0, 20), query })} className="flex items-center gap-2"><Save size={16}/>Save</SOCButton>
        </div>

        <div className="grid grid-cols-4 gap-6">
          <SOCCard className="col-span-3">
            <SOCCardHeader title="Results" />
            <SOCCardContent className="p-0">
              <SOCTable 
                headers={[{ label: 'Timestamp', accessor: 'timestamp' }, { label: 'Event Type', accessor: 'event' }, { label: 'Actions', accessor: 'actions' }]} 
                data={results}
                renderCell={(item: any, col: string) => {
                    if (col === 'actions') return <button onClick={() => setExpandedRow(expandedRow === item.id ? null : item.id)}>{expandedRow === item.id ? <ChevronDown size={16}/> : <ChevronRight size={16}/>}</button>;
                    return item[col];
                }}
              />
              {results.map((r: any) => expandedRow === r.id && (
                  <div key={r.id} className="p-4 bg-surface-2 border-b text-xs font-mono">
                    <pre>{JSON.stringify(r.parsed, null, 2)}</pre>
                  </div>
              ))}
            </SOCCardContent>
          </SOCCard>

          <div className="flex flex-col gap-6">
            <SOCCard>
              <SOCCardHeader title="History" />
              <SOCCardContent>
                {history?.map((h: any) => <div key={h.id} className="text-xs py-1 border-b truncate">{h.query}</div>)}
              </SOCCardContent>
            </SOCCard>

            <SOCCard>
              <SOCCardHeader title="Saved Searches" />
              <SOCCardContent>
                {savedQueries?.map((s: any) => (
                  <div key={s.id} className="flex justify-between text-xs py-1">
                    {s.name}
                    <Trash2 size={14} className="cursor-pointer text-critical" onClick={() => deleteQuery.mutate(s.id)} />
                  </div>
                ))}
              </SOCCardContent>
            </SOCCard>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
