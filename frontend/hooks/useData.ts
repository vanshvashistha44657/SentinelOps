import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api';

// Operational Data Hooks
export const useAlerts = () => useQuery({ queryKey: ['alerts'], queryFn: () => api.get('/alerts/').then(res => res.data) });
export const useIncidents = () => useQuery({ queryKey: ['incidents'], queryFn: () => api.get('/incidents/').then(res => res.data) });
export const useCases = () => useQuery({ queryKey: ['cases'], queryFn: () => api.get('/cases/').then(res => res.data) });

// New Operational Hooks
export const useDetectionRules = () => useQuery({ queryKey: ['detection-rules'], queryFn: () => api.get('/detection/rules').then(res => res.data) });
export const useThreatHunting = () => useQuery({ queryKey: ['hunting'], queryFn: () => api.get('/hunting/').then(res => res.data) });
export const useIOCs = () => useQuery({ queryKey: ['iocs'], queryFn: () => api.get('/iocs/').then(res => res.data) });
export const useThreatIntel = () => useQuery({ queryKey: ['threat-intel'], queryFn: () => api.get('/threat-intel/').then(res => res.data) });
export const useReports = () => useQuery({ queryKey: ['reports'], queryFn: () => api.get('/reports/').then(res => res.data) });
export const useAdminUsers = () => useQuery({ queryKey: ['admin-users'], queryFn: () => api.get('/admin/users').then(res => res.data) });
