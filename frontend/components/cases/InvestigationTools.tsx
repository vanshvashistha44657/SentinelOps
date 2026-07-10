"use client";
import React from 'react';
import { cn } from '@/lib/utils';
import { SOCBadge } from '@/components/soc-ui';

interface EvidenceItem {
  id: string;
  type: 'IP' | 'DOMAIN' | 'URL' | 'HASH' | 'HOST' | 'USER';
  value: string;
  riskScore: number;
  timestamp: string;
}

export const EvidenceCard = ({ item }: { item: EvidenceItem }) => {
  const getIcon = () => {
    switch (item.type) {
      case 'IP': return '🌐';
      case 'DOMAIN': return '🔗';
      case 'URL': return '📄';
      case 'HASH': return '🆔';
      case 'HOST': return '💻';
      case 'USER': return '👤';
      default: return '🔍';
    }
  };

  const getRiskColor = (score: number) => {
    if (score >= 80) return 'text-critical';
    if (score >= 50) return 'text-warning';
    return 'text-success';
  };

  return (
    <div className="p-3 bg-surface-3 rounded-lg border border-border group hover:border-primary/50 transition-all cursor-pointer">
      <div className="flex justify-between items-start mb-2">
        <span className="text-lg">{getIcon()}</span>
        <span className={cn("text-[10px] font-bold", getRiskColor(item.riskScore))}>
          SCORE: {item.riskScore}
        </span>
      </div>
      <div className="text-xs font-mono text-text-primary truncate mb-1">{item.value}</div>
      <div className="text-[10px] text-text-muted uppercase tracking-tighter">{item.type}</div>
    </div>
  );
};

interface TimelineEvent {
  id: string;
  type: 'USER' | 'SYSTEM' | 'COMMENT';
  title: string;
  description: string;
  timestamp: string;
}

export const InvestigationTimeline = ({ events }: { events: TimelineEvent[] }) => {
  return (
    <div className="space-y-4 relative before:absolute before:left-2 before:top-2 before:bottom-2 before:w-px before:bg-border">
      {events.map((event) => (
        <div key={event.id} className="pl-6 relative">
          <div className={cn(
            "absolute left-0 top-1 w-4 h-4 rounded-full border-2 border-surface-1 z-10",
            event.type === 'USER' ? "bg-primary" : 
            event.type === 'SYSTEM' ? "bg-info" : "bg-success"
          )} />
          <div className="p-3 bg-surface-2 rounded border border-border text-xs">
            <div className="flex justify-between items-center mb-1">
              <span className="font-semibold text-text-primary">{event.title}</span>
              <span className="text-[10px] text-text-muted">{event.timestamp}</span>
            </div>
            <p className="text-text-secondary">{event.description}</p>
          </div>
        </div>
      ))}
    </div>
  );
};
