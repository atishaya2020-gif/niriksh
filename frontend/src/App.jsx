import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

// Layout
import DashboardLayout from './components/layout/DashboardLayout';

// Auth & Guards
import ProtectedRoute from './components/auth/ProtectedRoute';
import RoleGuard from './components/auth/RoleGuard';
import { PERMISSIONS } from './config/permissions';

// Public Pages
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import AccessDeniedPage from './pages/AccessDeniedPage';

// Protected Pages
import DashboardPage from './pages/DashboardPage';
import CasesPage from './pages/CasesPage';
import CaseDetailsPage from './pages/CaseDetailsPage';
import DataIntakePage from './pages/DataIntakePage';
import EntitiesPage from './pages/EntitiesPage';
import EntityDetailsPage from './pages/EntityDetailsPage';
import NetworkPage from './pages/NetworkPage';
import DisruptionPage from './pages/DisruptionPage';
import AlertsPage from './pages/AlertsPage';
import EvidencePage from './pages/EvidencePage';
import ReportsPage from './pages/ReportsPage';
import NotificationsPage from './pages/NotificationsPage';
import ProfilePage from './pages/ProfilePage';
import SettingsPage from './pages/SettingsPage';

// Admin Pages
import AdminUsersPage from './pages/admin/AdminUsersPage';
import AdminAccessPage from './pages/admin/AdminAccessPage';
import AdminInvitationsPage from './pages/admin/AdminInvitationsPage';
import AdminAuditPage from './pages/admin/AdminAuditPage';

export function App() {
  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route path="/access-denied" element={<AccessDeniedPage />} />

        {/* Protected Dashboard Shell */}
        <Route
          element={
            <ProtectedRoute>
              <DashboardLayout />
            </ProtectedRoute>
          }
        >
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/investigations" element={<CasesPage />} />
          <Route path="/cases" element={<CasesPage />} />
          <Route path="/cases/:caseId" element={<CaseDetailsPage />} />
          <Route path="/data-intake" element={<DataIntakePage />} />
          <Route path="/entities" element={<EntitiesPage />} />
          <Route path="/entities/:entityId" element={<EntityDetailsPage />} />
          <Route path="/network" element={<NetworkPage />} />
          <Route path="/network/disruption" element={<DisruptionPage />} />
          <Route path="/alerts" element={<AlertsPage />} />
          <Route path="/evidence" element={<EvidencePage />} />
          <Route path="/reports" element={<ReportsPage />} />
          <Route path="/notifications" element={<NotificationsPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/settings" element={<SettingsPage />} />

          {/* Admin Routes with Role Guards */}
          <Route
            path="/admin/users"
            element={
              <RoleGuard permission={PERMISSIONS.MANAGE_USERS}>
                <AdminUsersPage />
              </RoleGuard>
            }
          />
          <Route
            path="/admin/access-control"
            element={
              <RoleGuard permission={PERMISSIONS.MANAGE_ROLES}>
                <AdminAccessPage />
              </RoleGuard>
            }
          />
          <Route
            path="/admin/invitations"
            element={
              <RoleGuard permission={PERMISSIONS.MANAGE_USERS}>
                <AdminInvitationsPage />
              </RoleGuard>
            }
          />
          <Route
            path="/admin/audit-logs"
            element={
              <RoleGuard permission={PERMISSIONS.VIEW_AUDIT_LOGS}>
                <AdminAuditPage />
              </RoleGuard>
            }
          />
        </Route>

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
