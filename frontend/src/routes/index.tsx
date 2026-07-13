import React, { useEffect, useState } from 'react';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AppLayout } from '@/components/layout/AppLayout';
import { ProtectedRoute } from '@/routes/ProtectedRoute';
import { LoginPage, RegisterPage } from '@/pages/LoginPage';
import { DashboardPage } from '@/pages/DashboardPage';
import { LogInteractionPage } from '@/pages/LogInteractionPage';
import { HistoryPage } from '@/pages/HistoryPage';
import { SettingsPage } from '@/pages/SettingsPage';
import { useAppDispatch, useAppSelector } from '@/hooks/redux';
import { setUser } from '@/store/slices/authSlice';
import { authApi } from '@/services/api/auth';
import { PageLoader } from '@/components/ui/LoadingSpinner';

function AuthInitializer({ children }: { children: React.ReactNode }) {
  const dispatch = useAppDispatch();
  const isAuthenticated = useAppSelector((s) => s.auth.isAuthenticated);
  const user = useAppSelector((s) => s.auth.user);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    const init = async () => {
      if (isAuthenticated && !user) {
        try {
          const me = await authApi.getMe();
          dispatch(setUser(me));
        } catch {
          localStorage.removeItem('access_token');
        }
      }
      setIsReady(true);
    };
    init();
  }, [dispatch, isAuthenticated, user]);

  if (!isReady) return <PageLoader />;
  return <>{children}</>;
}

export function AppRoutes() {
  const isAuthenticated = useAppSelector((s) => s.auth.isAuthenticated);

  return (
    <BrowserRouter>
      <AuthInitializer>
        <Routes>
          <Route
            path="/login"
            element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <LoginPage />}
          />
          <Route
            path="/register"
            element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <RegisterPage />}
          />

          <Route element={<ProtectedRoute />}>
            <Route element={<AppLayout />}>
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/log-interaction" element={<LogInteractionPage />} />
              <Route path="/log-interaction/:id" element={<LogInteractionPage />} />
              <Route path="/history" element={<HistoryPage />} />
              <Route path="/settings" element={<SettingsPage />} />
            </Route>
          </Route>

          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </AuthInitializer>

      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#fff',
            color: '#1e293b',
            border: '1px solid #dbeafe',
            borderRadius: '0.75rem',
            fontSize: '0.875rem',
          },
          success: {
            iconTheme: { primary: '#2563eb', secondary: '#fff' },
          },
          error: {
            iconTheme: { primary: '#dc2626', secondary: '#fff' },
          },
        }}
      />
    </BrowserRouter>
  );
}
