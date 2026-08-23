import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api';

// Operational Data Hooks
export const useAlerts = (params: any) => useQuery({ 
  queryKey: ['alerts', params], 
  queryFn: async () => {
    const res = await api.get('/alerts/', { params });
    if (Array.isArray(res.data)) {
        return { items: res.data, total: res.data.length, page: 1, size: res.data.length };
    }
    return res.data;
  }
});

export const useUpdateAlert = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { id: string, update: any }) => api.patch(`/alerts/${data.id}`, data.update),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['alerts'] })
  });
};

export const useDeleteAlert = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.delete(`/alerts/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['alerts'] })
  });
};

export const useIncidents = (params: any) => useQuery({ 
  queryKey: ['incidents', params], 
  queryFn: () => api.get('/incidents/', { params }).then(res => res.data) 
});

export const useUpdateIncident = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { id: string, update: any }) => api.patch(`/incidents/${data.id}`, data.update),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['incidents'] })
  });
};

export const useCases = (params: any) => useQuery({ 
  queryKey: ['cases', params], 
  queryFn: () => api.get('/cases/', { params }).then(res => res.data) 
});

export const useCreateCase = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: any) => api.post('/cases/', data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['cases'] })
  });
};

export const useUpdateCase = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { id: string, update: any }) => api.patch(`/cases/${data.id}`, data.update),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['cases'] })
  });
};

// Case Items
export const useCaseNotes = (caseId: string) => useQuery({
  queryKey: ['cases', caseId, 'notes'],
  queryFn: () => api.get(`/cases/${caseId}/notes`).then(res => res.data),
  enabled: !!caseId
});

export const useAddCaseNote = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { caseId: string, note: any }) => api.post(`/cases/${data.caseId}/notes`, data.note),
    onSuccess: (data, variables) => queryClient.invalidateQueries({ queryKey: ['cases', variables.caseId, 'notes'] })
  });
};

export const useCaseEvidence = (caseId: string) => useQuery({
  queryKey: ['cases', caseId, 'evidence'],
  queryFn: () => api.get(`/cases/${caseId}/evidence`).then(res => res.data),
  enabled: !!caseId
});

export const useAddCaseEvidence = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { caseId: string, evidence: any }) => api.post(`/cases/${data.caseId}/evidence`, data.evidence),
    onSuccess: (data, variables) => queryClient.invalidateQueries({ queryKey: ['cases', variables.caseId, 'evidence'] })
  });
};

// Ingestion Hooks
export const useIngestionStatus = () => useQuery({
  queryKey: ['ingestion-status'],
  queryFn: () => api.get('/ingestion/status').then(res => res.data),
  refetchInterval: 10000
});

export const useIngestionStatistics = () => useQuery({
  queryKey: ['ingestion-statistics'],
  queryFn: () => api.get('/ingestion/statistics').then(res => res.data),
  refetchInterval: 30000
});

export const useFailedLogs = () => useQuery({
  queryKey: ['ingestion-failed'],
  queryFn: () => api.get('/ingestion/failed').then(res => res.data)
});

export const useDeleteFailedLog = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.delete(`/ingestion/failed/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['ingestion-failed'] })
  });
};

// Dashboard Hooks
export const useDashboardOverview = () => useQuery({ 
  queryKey: ['dashboard-overview'], 
  queryFn: () => api.get('/dashboard/overview').then(res => res.data),
  refetchInterval: 30000 
});

export const useDashboardCharts = () => useQuery({ 
  queryKey: ['dashboard-charts'], 
  queryFn: () => api.get('/dashboard/charts').then(res => res.data),
  refetchInterval: 60000 
});

export const useDashboardMetrics = () => useQuery({ 
  queryKey: ['dashboard-metrics'], 
  queryFn: () => api.get('/dashboard/metrics').then(res => res.data),
  refetchInterval: 60000 
});

export const useDetectionRules = () => useQuery({ 
  queryKey: ['detection-rules'], 
  queryFn: () => api.get('/detection/rules/').then(res => res.data) 
});

export const useDashboardTop = () => useQuery({ 
  queryKey: ['dashboard-top'], 
  queryFn: () => api.get('/dashboard/top').then(res => res.data),
  refetchInterval: 60000 
});
// Threat Hunting Hooks
export const useThreatHuntingSearch = (query: string, page: number, size: number, enabled: boolean) => useQuery({
  queryKey: ['hunting-search', query, page, size],
  queryFn: () => api.get(`/hunting/search?query=${encodeURIComponent(query)}&page=${page}&size=${size}`).then(res => res.data),
  enabled
});

export const useThreatHuntingHistory = () => useQuery({
  queryKey: ['hunting-history'],
  queryFn: () => api.get('/hunting/history').then(res => res.data)
});

export const useSavedHuntingQueries = () => useQuery({
  queryKey: ['hunting-saved'],
  queryFn: () => api.get('/hunting/saved').then(res => res.data)
});

export const useSaveHuntingQuery = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: any) => api.post('/hunting/', data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['hunting-saved'] })
  });
};

export const useDeleteHuntingQuery = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.delete(`/hunting/saved/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['hunting-saved'] })
  });
};
export const useIOCs = () => useQuery({ queryKey: ['iocs'], queryFn: () => api.get('/iocs/').then(res => res.data) });
// Threat Intelligence Hooks
export const useThreatIndicators = () => useQuery({
  queryKey: ['threat-indicators'],
  queryFn: () => api.get('/threat-intelligence/iocs').then(res => res.data)
});

export const useCreateThreatIndicator = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: any) => api.post('/threat-intelligence/iocs', data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['threat-indicators'] })
  });
};

export const useUpdateThreatIndicator = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { id: string, update: any }) => api.patch(`/threat-intelligence/iocs/${data.id}`, data.update),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['threat-indicators'] })
  });
};

export const useDeleteThreatIndicator = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.delete(`/threat-intelligence/iocs/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['threat-indicators'] })
  });
};
export const useReports = () => useQuery({ queryKey: ['reports'], queryFn: () => api.get('/reports/').then(res => res.data) });
// Admin Hooks
export const useAdminStats = () => useQuery({
  queryKey: ['admin-stats'],
  queryFn: () => api.get('/admin/dashboard/stats').then(res => res.data),
  refetchInterval: 60000
});

export const useAdminUsers = () => useQuery({
  queryKey: ['admin-users'],
  queryFn: () => api.get('/admin/users').then(res => res.data)
});

export const useApproveUser = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (userId: string) => api.post(`/admin/users/${userId}/approve`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin-users'] })
  });
};

export const useRejectUser = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { userId: string, reason: string }) => api.post(`/admin/users/${data.userId}/reject`, null, { params: { reason: data.reason } }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin-users'] })
  });
};

export const useAuditLogs = () => useQuery({
  queryKey: ['admin-audit-logs'],
  queryFn: () => api.get('/admin/audit-logs').then(res => res.data)
});


// Simulator Hooks
export const useRunAttack = () => {
  return useMutation({
    mutationFn: (attackType: string) => api.post(`/simulator/attack/${attackType}`),
  });
};
