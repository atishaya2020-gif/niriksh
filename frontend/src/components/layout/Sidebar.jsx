import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  FolderKanban,
  FileSpreadsheet,
  Network,
  Users,
  Bell,
  FileCode2,
  FileText,
  ShieldCheck,
  KeyRound,
  History,
  Radio,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  Layers
} from 'lucide-react';
import transparentLogo from '../../assets/niriksh-logo.png';
import { hasPermission, PERMISSIONS } from '../../config/permissions';

export const Sidebar = ({ collapsed, setCollapsed, userRole }) => {
  const mainNav = [
    { label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { label: 'Cases', path: '/cases', icon: FolderKanban },
    { label: 'Data Intake', path: '/data-intake', icon: FileSpreadsheet, highlight: true },
    { label: 'Entities', path: '/entities', icon: Users },
    { label: 'Network Analysis', path: '/network', icon: Network },
    { label: 'Alerts', path: '/alerts', icon: Radio },
    { label: 'Evidence', path: '/evidence', icon: FileCode2 },
    { label: 'Reports', path: '/reports', icon: FileText },
    { label: 'Notifications', path: '/notifications', icon: Bell }
  ];

  const adminNav = [
    { label: 'Users', path: '/admin/users', icon: Users, perm: PERMISSIONS.MANAGE_USERS },
    { label: 'Access Control', path: '/admin/access-control', icon: ShieldCheck, perm: PERMISSIONS.MANAGE_ROLES },
    { label: 'Invitations', path: '/admin/invitations', icon: KeyRound, perm: PERMISSIONS.MANAGE_USERS },
    { label: 'Audit Logs', path: '/admin/audit-logs', icon: History, perm: PERMISSIONS.VIEW_AUDIT_LOGS }
  ];

  const filteredAdminNav = adminNav.filter((item) => hasPermission(userRole, item.perm));

  return (
    <aside
      className={`fixed top-0 left-0 bottom-0 z-40 flex flex-col glass-panel border-r border-purple-500/30 bg-slate-950/90 backdrop-blur-xl transition-all duration-300 ${
        collapsed ? 'w-20' : 'w-64'
      }`}
    >
      {/* Header / Brand */}
      <div className="flex items-center justify-between p-4 border-b border-purple-900/40">
        <NavLink to="/dashboard" className="flex items-center gap-3 overflow-hidden">
          <img
            src={transparentLogo}
            alt="NIRIKSH Logo"
            className="w-9 h-9 object-contain drop-shadow-[0_0_8px_rgba(139,92,246,0.6)]"
          />
          {!collapsed && (
            <div className="flex flex-col">
              <span className="text-lg font-black tracking-wider text-transparent bg-clip-text bg-gradient-to-r from-purple-200 via-purple-300 to-cyan-300 font-mono-id">
                NIRIKSH
              </span>
              <span className="text-[9px] font-mono-id text-purple-400/80 tracking-tight">
                CYBER COMMAND
              </span>
            </div>
          )}
        </NavLink>

        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-1.5 text-purple-400 hover:text-purple-100 hover:bg-purple-900/40 rounded-lg transition-colors cursor-pointer"
        >
          {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>

      {/* Navigation List */}
      <div className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
        <div>
          {!collapsed && (
            <p className="px-3 mb-2 text-[10px] font-bold uppercase tracking-widest text-purple-400/60 font-mono-id">
              Investigation Suite
            </p>
          )}
          <nav className="space-y-1">
            {mainNav.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium transition-all ${
                      isActive
                        ? 'bg-purple-600/90 text-white font-semibold shadow-lg shadow-purple-900/60 border border-purple-400/40'
                        : 'text-purple-300/70 hover:text-purple-100 hover:bg-purple-900/30'
                    } ${item.highlight && !collapsed ? 'border border-cyan-500/30 bg-cyan-950/20' : ''}`
                  }
                  title={collapsed ? item.label : undefined}
                >
                  <Icon className="w-4 h-4 flex-shrink-0" />
                  {!collapsed && (
                    <span className="truncate flex-1">{item.label}</span>
                  )}
                  {!collapsed && item.highlight && (
                    <Sparkles className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
                  )}
                </NavLink>
              );
            })}
          </nav>
        </div>

        {filteredAdminNav.length > 0 && (
          <div className="pt-2 border-t border-purple-900/30">
            {!collapsed && (
              <p className="px-3 mb-2 text-[10px] font-bold uppercase tracking-widest text-purple-400/60 font-mono-id">
                Administration
              </p>
            )}
            <nav className="space-y-1">
              {filteredAdminNav.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    className={({ isActive }) =>
                      `flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium transition-all ${
                        isActive
                          ? 'bg-purple-600/90 text-white font-semibold shadow-lg shadow-purple-900/60 border border-purple-400/40'
                          : 'text-purple-300/70 hover:text-purple-100 hover:bg-purple-900/30'
                      }`
                    }
                    title={collapsed ? item.label : undefined}
                  >
                    <Icon className="w-4 h-4 flex-shrink-0" />
                    {!collapsed && <span className="truncate">{item.label}</span>}
                  </NavLink>
                );
              })}
            </nav>
          </div>
        )}
      </div>

      {/* Footer Banner */}
      {!collapsed && (
        <div className="p-3 m-3 bg-purple-950/50 border border-purple-500/20 rounded-xl text-center">
          <span className="text-[10px] font-mono-id text-purple-300/70 block">
            DEMO MODE • SYNTHETIC DATA
          </span>
          <span className="text-[9px] font-mono-id text-cyan-400 font-bold block mt-0.5">
            SIH 2026 PROTOTYPE
          </span>
        </div>
      )}
    </aside>
  );
};

export default Sidebar;
