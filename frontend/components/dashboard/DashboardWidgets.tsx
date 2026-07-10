"use client";
import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { SOCCard, SOCCardHeader, SOCCardContent } from '@/components/soc-ui';
import { Activity, ShieldAlert, AlertTriangle, ShieldCheck } from 'lucide-react';

interface KPIProps {
  title: string;
  value: string | number;
  trend: number;
  icon: React.ElementType;
  variant: 'critical' | 'warning' | 'info' | 'success';
}

export const KPICard = ({ title, value, trend, icon: Icon, variant }: KPIProps) => {
  const variants = {
    critical: "text-critical",
    warning: "text-warning",
    info: "text-info",
    success: "text-success",
  };
  
  return (
    <SOCCard className="relative overflow-hidden group">
      <div className={cn("absolute top-0 left-0 w-1 h-full bg-current", variants[variant])} />
      <SOCCardContent className="flex items-center justify-between p-6">
        <div>
          <p className="text-xs font-medium text-text-secondary uppercase tracking-wider mb-1">{title}</p>
          <div className="text-3xl font-bold text-text-primary">{value}</div>
          <div className={cn("text-xs mt-2 flex items-center gap-1", trend > 0 ? "text-critical" : "text-success")}>
            {trend > 0 ? "↑" : "↓"} {Math.abs(trend)}% <span className="text-text-muted">vs last 24h</span>
          </div>
        </div>
        <div className={cn("p-3 rounded-lg bg-surface-3 group-hover:scale-110 transition-transform", variants[variant])}>
          <Icon size={24} />
        </div>
      </SOCCardContent>
    </SOCCard>
  );
};

export const AlertTrendChart = ({ data }: { data: any[] }) => (
  <SOCCard className="h-full">
    <SOCCardHeader title="Alert Volume Trend" />
    <SOCCardContent className="h-[300px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data}>
          <defs>
            <linearGradient id="colorAlerts" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
          <XAxis 
            dataKey="name" 
            stroke="#64748b" 
            fontSize={12} 
            tickLine={false} 
            axisLine={false} 
          />
          <YAxis 
            stroke="#64748b" 
            fontSize={12} 
            tickLine={false} 
            axisLine={false} 
          />
          <Tooltip 
            contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
            itemStyle={{ color: '#f8fafc' }}
          />
          <Area 
            type="monotone" 
            dataKey="alerts" 
            stroke="#3b82f6" 
            fillOpacity={1} 
            fill="url(#colorAlerts)" 
            strokeWidth={2}
          />
        </AreaChart>
      </ResponsiveContainer>
    </SOCCardContent>
  </SOCCard>
);

export const RecentActivityFeed = ({ activities }: { activities: any[] }) => (
  <SOCCard className="h-full">
    <SOCCardHeader title="Live Security Feed" />
    <SOCCardContent className="p-0">
      <div className="divide-y divide-border">
        {activities.map((activity, i) => (
          <div key={i} className="p-4 hover:bg-surface-3 transition-colors flex gap-4 items-start">
            <div className={cn("mt-1 w-2 h-2 rounded-full shrink-0", 
              activity.severity === 'CRITICAL' ? "bg-critical" : 
              activity.severity === 'HIGH' ? "bg-warning" : "bg-info"
            )} />
            <div className="flex-1 min-w-0">
              <div className="flex justify-between items-baseline gap-2">
                <p className="text-sm font-medium text-text-primary truncate">{activity.title}</p>
                <span className="text-[10px] text-text-muted whitespace-nowrap">{activity.timestamp}</span>
              </div>
              <p className="text-xs text-text-secondary truncate">{activity.description}</p>
            </div>
          </div>
        ))}
      </div>
    </SOCCardContent>
  </SOCCard>
);

import { cn } from '@/lib/utils';
