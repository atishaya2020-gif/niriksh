import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Search,
  Bell,
  User,
  LogOut,
  Settings,
  Shield,
  Globe,
  ChevronDown
} from 'lucide-react';
import Breadcrumbs from './Breadcrumbs';
import authService from '../../services/authService';

export const Navbar = ({
  currentUser,
  setCurrentUser,
  onOpenSearch,
  onOpenNotifications,
  onOpenCrossState,
  unreadCount = 2
}) => {
  const [profileOpen, setProfileOpen] = useState(false);
  const navigate = useNavigate();

  const handleLogout = async () => {
    await authService.logout();
    navigate('/login');
  };

  return (
    <header className="sticky top-0 z-30 h-16 glass-panel border-b border-purple-500/30 bg-slate-950/80 backdrop-blur-xl px-4 sm:px-6 flex items-center justify-between">
      {/* Left: Breadcrumbs & Mobile Brand */}
      <div className="flex items-center gap-4">
        <Breadcrumbs />
      </div>

      {/* Right: Search, State, Role, Notifications & User */}
      <div className="flex items-center gap-3">
        {/* Global Search Button Trigger */}
        <button
          onClick={onOpenSearch}
          className="flex items-center gap-2 px-3 py-1.5 bg-slate-900/80 hover:bg-purple-950/60 border border-purple-500/30 rounded-xl text-xs text-purple-300 hover:text-white transition-all cursor-pointer font-mono-id"
        >
          <Search className="w-3.5 h-3.5 text-purple-400" />
          <span className="hidden sm:inline">Search (Ctrl + K)</span>
        </button>

        {/* Current State Switcher */}
        <button
          onClick={onOpenCrossState}
          className="flex items-center gap-1.5 px-2.5 py-1.5 bg-purple-950/60 hover:bg-purple-900/70 border border-purple-500/30 rounded-xl text-xs font-mono-id text-purple-200 cursor-pointer transition-all"
          title="Switch Active Investigation State"
        >
          <Globe className="w-3.5 h-3.5 text-cyan-400" />
          <span className="font-bold">{currentUser?.state || 'Punjab'}</span>
          <ChevronDown className="w-3 h-3 text-purple-400" />
        </button>

        <div className="hidden lg:flex items-center gap-1.5 px-2 py-1 bg-slate-900/70 border border-purple-900/40 rounded-xl text-[11px] font-mono-id">
          <Shield className="w-3.5 h-3.5 text-purple-400" />
          <span className="text-purple-200 font-semibold text-xs">{currentUser?.role || 'USER'}</span>
        </div>

        {/* Notifications Drawer Button */}
        <button
          onClick={onOpenNotifications}
          className="relative p-2 text-purple-300 hover:text-white hover:bg-purple-900/40 rounded-xl border border-purple-500/20 transition-all cursor-pointer"
          title="Notifications"
        >
          <Bell className="w-4 h-4" />
          {unreadCount > 0 && (
            <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-cyan-500 text-slate-950 text-[10px] font-extrabold flex items-center justify-center font-mono-id shadow-sm shadow-cyan-400">
              {unreadCount}
            </span>
          )}
        </button>

        {/* User Profile Menu */}
        <div className="relative">
          <button
            onClick={() => setProfileOpen(!profileOpen)}
            className="flex items-center gap-2 p-1.5 bg-purple-950/40 hover:bg-purple-900/60 border border-purple-500/30 rounded-xl cursor-pointer transition-all"
          >
            <div className="w-7 h-7 rounded-lg bg-gradient-to-tr from-purple-600 to-cyan-500 flex items-center justify-center font-mono-id text-white font-bold text-xs shadow-sm">
               {currentUser?.username?.slice(0, 3).toUpperCase() || 'USR'}
            </div>
            <span className="hidden md:inline text-xs font-semibold text-purple-100 font-mono-id">
               {currentUser?.username || 'User'}
            </span>
            <ChevronDown className="w-3 h-3 text-purple-400" />
          </button>

          {/* Profile Dropdown */}
          {profileOpen && (
            <div
              className="absolute right-0 mt-2 w-56 glass-panel border border-purple-500/40 shadow-2xl rounded-xl p-2 z-50 space-y-1"
              onMouseLeave={() => setProfileOpen(false)}
            >
              <div className="px-3 py-2 border-b border-purple-900/40">
                 <p className="text-xs font-bold text-purple-100">{currentUser?.username}</p>
                 <p className="text-[10px] font-mono-id text-purple-400/80 mt-0.5">
                   User {currentUser?.id} • {currentUser?.role}
                 </p>
              </div>

              <Link
                to="/profile"
                onClick={() => setProfileOpen(false)}
                className="flex items-center gap-2 px-3 py-2 text-xs text-purple-200 hover:bg-purple-900/40 rounded-lg transition-colors"
              >
                <User className="w-4 h-4 text-purple-400" /> Official Profile
              </Link>
              <Link
                to="/settings"
                onClick={() => setProfileOpen(false)}
                className="flex items-center gap-2 px-3 py-2 text-xs text-purple-200 hover:bg-purple-900/40 rounded-lg transition-colors"
              >
                <Settings className="w-4 h-4 text-purple-400" /> Platform Settings
              </Link>

              <button
                onClick={handleLogout}
                className="w-full flex items-center gap-2 px-3 py-2 text-xs text-red-400 hover:bg-red-950/50 rounded-lg transition-colors cursor-pointer text-left font-mono-id"
              >
                <LogOut className="w-4 h-4" /> Sign Out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Navbar;
