"use client";
import { useState } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import { useThreatIndicators, useCreateThreatIndicator, useDeleteThreatIndicator } from '@/hooks/useData';
import { SOCTable, SOCBadge, SOCButton, SOCCard, SOCCardHeader, SOCCardContent, SOCInput } from '@/components/soc-ui';
import { Plus, Trash2, ShieldAlert } from 'lucide-react';

export default function ThreatIntelligencePage() {
  const { data: indicators } = useThreatIndicators();
  const createIndicator = useCreateThreatIndicator();
  const deleteIndicator = useDeleteThreatIndicator();
  
  const [value, setValue] = useState('');
  const [type, setType] = useState('IPV4');

  return (
    <DashboardLayout>
      <div className="flex flex-col gap-6">
        <header>
          <h1 className="text-2xl font-bold text-text-primary tracking-tight">Threat Intelligence</h1>
        </header>

        <div className="flex gap-2">
          <SOCInput value={value} onChange={(e) => setValue(e.target.value)} placeholder="Indicator value (e.g., 1.1.1.1)..." />
          <SOCButton onClick={() => createIndicator.mutate({ type, value, severity: 'HIGH', source: 'INTERNAL' })}>Add Indicator</SOCButton>
        </div>

        <SOCCard>
          <SOCCardHeader title="Threat Indicators (IOCs)" />
          <SOCCardContent className="p-0">
            <SOCTable 
                headers={[{label: 'Value', accessor: 'value'}, {label: 'Type', accessor: 'type'}, {label: 'Severity', accessor: 'severity'}, {label: 'Actions', accessor: 'actions'}]}
                data={indicators || []}
                renderCell={(item: any, col: string) => {
                    if (col === 'severity') return <SOCBadge variant={item.severity === 'CRITICAL' ? 'critical' : 'warning'}>{item.severity}</SOCBadge>;
                    if (col === 'actions') return <SOCButton variant="secondary" size="xs" onClick={() => deleteIndicator.mutate(item.id)}><Trash2 size={12}/></SOCButton>;
                    return item[col];
                }}
            />
          </SOCCardContent>
        </SOCCard>
      </div>
    </DashboardLayout>
  );
}
