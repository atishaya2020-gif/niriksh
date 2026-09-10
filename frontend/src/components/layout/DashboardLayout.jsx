import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Navbar from './Navbar';
import GlobalSearchModal from './GlobalSearchModal';
import NotificationsDrawer from './NotificationsDrawer';
import CrossStateModal from './CrossStateModal';
import authService from '../../services/authService';

export const DashboardLayout = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [currentUser, setCurrentUser] = useState(() => authService.getCurrentUser());
  const [searchOpen, setSearchOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [crossStateOpen, setCrossStateOpen] = useState(false);

  return (
    <div className="min-h-screen bg-[#05040A] text-purple-100 flex flex-col font-sans">
      {/* Sidebar Navigation */}
      <Sidebar
        collapsed={collapsed}
        setCollapsed={setCollapsed}
        userRole={currentUser?.role}
      />

      {/* Main Content Body */}
      <div
        className={`flex-1 flex flex-col transition-all duration-300 ${
          collapsed ? 'ml-20' : 'ml-64'
        }`}
      >
        <Navbar
          currentUser={currentUser}
          setCurrentUser={setCurrentUser}
          onOpenSearch={() => setSearchOpen(true)}
          onOpenNotifications={() => setNotificationsOpen(true)}
          onOpenCrossState={() => setCrossStateOpen(true)}
        />

        <main className="flex-1 p-4 sm:p-6 lg:p-8 overflow-y-auto">
          <Outlet context={{ currentUser }} />
        </main>
      </div>

      {/* Modals & Drawers */}
      <GlobalSearchModal isOpen={searchOpen} onClose={() => setSearchOpen(false)} />
      <NotificationsDrawer
        isOpen={notificationsOpen}
        onClose={() => setNotificationsOpen(false)}
      />
      <CrossStateModal isOpen={crossStateOpen} onClose={() => setCrossStateOpen(false)} />
    </div>
  );
};

export default DashboardLayout;
