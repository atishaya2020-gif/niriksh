import React from 'react';
import { Navigate } from 'react-router-dom';
import authService from '../../services/authService';
import { hasPermission } from '../../config/permissions';

export const RoleGuard = ({ permission, children }) => {
  const user = authService.getCurrentUser();
  const userRole = user?.role;

  if (permission && !hasPermission(userRole, permission)) {
    return <Navigate to="/access-denied" replace />;
  }

  return children;
};

export default RoleGuard;
