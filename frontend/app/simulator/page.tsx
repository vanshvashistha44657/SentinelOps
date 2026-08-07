"use client";
import { useState } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import { SOCButton, SOCCard, SOCCardHeader, SOCCardContent } from '@/components/soc-ui';
import { useRunAttack } from '@/hooks/useData';
import { Play, AlertTriangle } from 'lucide-react';

export default function SimulatorPage() {
  const runAttack = useRunAttack();
  const [status, setStatus] = useState<string | null>(null);

  const attacks = [
    { id: 'brute_force', name: 'Brute Force Login' },
    { id: 'powershell_execution', name: 'PowerShell Execution' }
  ];

  const handleAttack = (type: string) => {
    setStatus(`Running attack: ${type}...`);
    runAttack.mutate(type, {
      onSuccess: () => setStatus(`Attack ${type} simulated successfully!`),
      onError: () => setStatus(`Failed to simulate ${type}`)
    });
  };

  return (
    <DashboardLayout>
      <div className="flex flex-col gap-6">
        <header>
          <h1 className="text-2xl font-bold text-text-primary tracking-tight">Attack Simulation Center</h1>
        </header>

        <div className="grid grid-cols-2 gap-6">
          <SOCCard>
            <SOCCardHeader title="Available Attacks" />
            <SOCCardContent className="flex flex-col gap-4">
              {attacks.map(attack => (
                <div key={attack.id} className="flex justify-between items-center p-3 bg-surface-2 rounded border border-border">
                  <span>{attack.name}</span>
                  <SOCButton size="sm" onClick={() => handleAttack(attack.id)} className="flex items-center gap-2">
                    <Play size={14}/> Run
                  </SOCButton>
                </div>
              ))}
              {status && <div className="text-sm text-info mt-2">{status}</div>}
            </SOCCardContent>
          </SOCCard>

          <SOCCard>
            <SOCCardHeader title="Simulation Activity" />
            <SOCCardContent>
                <div className="text-sm text-text-muted">Monitor the dashboard for incoming events from simulated attacks.</div>
                <div className="mt-4 flex items-center gap-2 text-warning"><AlertTriangle size={16}/> Ensure detection rules are active.</div>
            </SOCCardContent>
          </SOCCard>
        </div>
      </div>
    </DashboardLayout>
  );
}
