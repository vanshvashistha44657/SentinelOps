"use client";
import React from 'react';
import { SOCCard, SOCCardHeader, SOCCardContent, SOCBadge, SOCButton } from '@/components/soc-ui';
import { MoreVertical, User, Clock } from 'lucide-react';
import { cn } from '@/lib/utils';

interface KanbanIncident {
  id: string;
  title: string;
  status: string;
  severity: string;
  owner?: string;
  updated_at: string;
}

interface KanbanColumnProps {
  status: string;
  incidents: KanbanIncident[];
  onIncidentClick: (incident: KanbanIncident) => void;
}

const KanbanColumn = ({ status, incidents, onIncidentClick }: KanbanColumnProps) => {
  return (
    <div className="flex flex-col gap-4 min-w-[300px]">
      <div className="flex items-center justify-between px-1">
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-semibold text-text-primary uppercase tracking-wider">{status}</h3>
          <span className="text-xs text-text-muted bg-surface-3 px-2 py-0.5 rounded-full">{incidents.length}</span>
        </div>
        <button className="text-text-muted hover:text-text-primary transition-colors">
          <MoreVertical size={16} />
        </button>
      </div>
      
      <div className="flex flex-col gap-3 min-h-[200px]">
        {incidents.map((incident) => (
          <SOCCard 
            key={incident.id} 
            className="cursor-pointer hover:border-primary/50 transition-all group"
            onClick={() => onIncidentClick(incident)}
          >
            <SOCCardContent className="p-4">
              <div className="flex justify-between items-start mb-3">
                <SOCBadge variant={getSeverityVariant(incident.severity)}>{incident.severity}</SOCBadge>
                <span className="text-[10px] text-text-muted flex items-center gap-1">
                  <Clock size={10} /> {new Date(incident.updated_at).toLocaleDateString()}
                </span>
              </div>
              
              <h4 className="text-sm font-medium text-text-primary mb-4 line-clamp-2 group-hover:text-primary transition-colors">
                {incident.title}
              </h4>
              
              <div className="flex items-center justify-between mt-auto pt-3 border-t border-border/50">
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 rounded-full bg-surface-3 flex items-center justify-center text-[10px] font-bold text-text-secondary border border-border">
                    {incident.owner ? incident.owner.charAt(0).toUpperCase() : '?'}
                  </div>
                  <span className="text-xs text-text-secondary truncate max-w-[80px]">
                    {incident.owner || 'Unassigned'}
                  </span>
                </div>
                <button className="p-1 text-text-muted hover:text-text-primary opacity-0 group-hover:opacity-100 transition-opacity">
                  <MoreVertical size={14} />
                </button>
              </div>
            </SOCCardContent>
          </SOCCard>
        ))}
      </div>
    </div>
  );
};

const getSeverityVariant = (severity: string) => {
  switch (severity.toUpperCase()) {
    case 'CRITICAL': return 'critical';
    case 'HIGH': return 'warning';
    case 'MEDIUM': return 'info';
    default: return 'info';
  }
};

export const IncidentKanban = ({ 
  incidents, 
  onIncidentClick 
}: { 
  incidents: any[]; 
  onIncidentClick: (incident: any) => void 
}) => {
  const statuses = ['OPEN', 'INVESTIGATING', 'CONTAINED', 'CLOSED'];

  return (
    <div className="flex gap-6 overflow-x-auto pb-4 scrollbar-thin scrollbar-thumb-surface-3 scrollbar-track-transparent">
      {statuses.map(status => (
        <KanbanColumn 
          key={status} 
          status={status} 
          incidents={incidents.filter(i => i.status === status)} 
          onIncidentClick={onIncidentClick}
        />
      ))}
    </div>
  );
};
