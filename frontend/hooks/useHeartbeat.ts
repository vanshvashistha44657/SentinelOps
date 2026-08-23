import { useEffect } from 'react';
import { useAuthStore } from '@/store/useAuthStore';
import api from '@/lib/api';

export const useHeartbeat = () => {
  const { token } = useAuthStore();

  useEffect(() => {
    if (!token) return;

    const interval = setInterval(() => {
      api.post('/auth/heartbeat').catch(console.error);
    }, 60000);

    return () => clearInterval(interval);
  }, [token]);
};
