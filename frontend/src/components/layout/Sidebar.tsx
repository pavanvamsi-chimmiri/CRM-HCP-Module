import { NavLink } from 'react-router-dom';
import {
  Activity,
  ClipboardList,
  History,
  LayoutDashboard,
  LogOut,
  Settings,
  Stethoscope,
} from 'lucide-react';
import { cn } from '@/utils';
import { useAppDispatch, useAppSelector } from '@/hooks/redux';
import { logout } from '@/store/slices/authSlice';

const navItems = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/log-interaction', icon: ClipboardList, label: 'Log Interaction' },
  { to: '/history', icon: History, label: 'History' },
  { to: '/settings', icon: Settings, label: 'Settings' },
];

export function Sidebar() {
  const dispatch = useAppDispatch();
  const user = useAppSelector((s) => s.auth.user);

  return (
    <aside className="fixed inset-y-0 left-0 z-30 flex w-64 flex-col border-r border-brand-100 bg-white">
      <div className="flex h-16 items-center gap-3 border-b border-brand-100 px-6">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand-600">
          <Stethoscope className="h-5 w-5 text-white" />
        </div>
        <div>
          <h1 className="text-sm font-bold text-brand-900">HCP CRM</h1>
          <p className="text-xs text-slate-500">Medical Sales</p>
        </div>
      </div>

      <nav className="flex-1 space-y-1 px-3 py-4">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-brand-50 text-brand-700'
                  : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
              )
            }
          >
            <Icon className="h-5 w-5" />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="border-t border-brand-100 p-4">
        <div className="mb-3 flex items-center gap-3 rounded-lg bg-brand-50 px-3 py-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-600 text-xs font-bold text-white">
            {user?.full_name?.charAt(0) || 'U'}
          </div>
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium text-slate-900">{user?.full_name}</p>
            <p className="truncate text-xs text-slate-500">{user?.email}</p>
          </div>
        </div>
        <button
          onClick={() => dispatch(logout())}
          className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm text-slate-600 transition-colors hover:bg-red-50 hover:text-red-600"
        >
          <LogOut className="h-4 w-4" />
          Sign Out
        </button>
      </div>
    </aside>
  );
}

export function MobileHeader() {
  return (
    <header className="flex h-14 items-center gap-2 border-b border-brand-100 bg-white px-4 lg:hidden">
      <Activity className="h-5 w-5 text-brand-600" />
      <span className="font-semibold text-brand-900">HCP CRM</span>
    </header>
  );
}
