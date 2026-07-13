import { Navigate, Outlet } from 'react-router-dom';
import { useAppSelector } from '@/hooks/redux';

export function ProtectedRoute() {
  const isAuthenticated = useAppSelector((s) => s.auth.isAuthenticated);

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}
