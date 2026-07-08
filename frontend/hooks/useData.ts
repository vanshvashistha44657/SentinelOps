import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api';

export const useAlerts = () => useQuery({ queryKey: ['alerts'], queryFn: () => api.get('/alerts/').then(res => res.data) });
export const useIncidents = () => useQuery({ queryKey: ['incidents'], queryFn: () => api.get('/incidents/').then(res => res.data) });
export const useCases = () => useQuery({ queryKey: ['cases'], queryFn: () => api.get('/cases/').then(res => res.data) });
