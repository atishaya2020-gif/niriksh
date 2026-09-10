import React, { useEffect, useState } from 'react';
import { Users, Shield, UserCheck, UserX, Ban, RotateCcw } from 'lucide-react';
import Table from '../../components/ui/Table';
import Button from '../../components/ui/Button';
import Badge from '../../components/ui/Badge';
import Toast from '../../components/ui/Toast';
import LoadingState from '../../components/ui/LoadingState';
import userService from '../../services/userService';

export const AdminUsersPage = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState('');

  useEffect(() => {
    const loadUsers = async () => {
      setLoading(true);
      const data = await userService.getUsers();
      setUsers([...data]);
      setLoading(false);
    };
    loadUsers();
  }, []);

  const handleAction = async (userId, newStatus, actionName) => {
    await userService.updateUserStatus(userId, newStatus);
    setUsers((prev) =>
      prev.map((u) => (u.id === userId || u.employee_id === userId ? { ...u, status: newStatus } : u))
    );
    setToast(`User ${userId} status updated to ${actionName}.`);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-purple-900/30 pb-4">
        <div>
          <h1 className="text-2xl font-extrabold text-white font-mono-id tracking-tight">
            ADMINISTRATION • USER MANAGEMENT
          </h1>
          <p className="text-xs text-purple-300/70 font-mono-id mt-1">
            Authorize government personnel accounts, assign RBAC roles, and manage access statuses
          </p>
        </div>
      </div>

      {loading ? (
        <LoadingState message="Loading system user registry..." />
      ) : (
        <Table
          headers={[
            'Officer Name',
            'Employee ID',
            'Department',
            'System Role',
            'State',
            'Status',
            'Last Active',
            'Management Actions'
          ]}
        >
          {users.map((u) => (
            <tr key={u.id} className="hover:bg-purple-900/30 transition-colors">
              <td className="px-4 py-3.5 font-semibold text-purple-100">{u.name}</td>
              <td className="px-4 py-3.5 font-mono-id font-bold text-cyan-300">{u.employee_id}</td>
              <td className="px-4 py-3.5 text-xs font-mono-id text-purple-200">{u.department}</td>
              <td className="px-4 py-3.5 text-xs font-mono-id font-bold text-yellow-400">{u.role}</td>
              <td className="px-4 py-3.5 text-xs font-mono-id text-purple-300">{u.state}</td>
              <td className="px-4 py-3.5">
                <Badge status={u.status} size="sm" />
              </td>
              <td className="px-4 py-3.5 text-xs font-mono-id text-purple-400/60">{u.last_active}</td>
              <td className="px-4 py-3.5 flex items-center gap-2">
                {u.status !== 'ACTIVE' && (
                  <Button
                    variant="cyan"
                    size="sm"
                    onClick={() => handleAction(u.id, 'ACTIVE', 'ACTIVE')}
                  >
                    Approve / Restore
                  </Button>
                )}
                {u.status === 'ACTIVE' && (
                  <>
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => handleAction(u.id, 'SUSPENDED', 'SUSPENDED')}
                    >
                      Suspend
                    </Button>
                    <Button
                      variant="danger"
                      size="sm"
                      onClick={() => handleAction(u.id, 'BLOCKED', 'BLOCKED')}
                    >
                      Block
                    </Button>
                  </>
                )}
              </td>
            </tr>
          ))}
        </Table>
      )}

      {toast && <Toast type="success" message={toast} onClose={() => setToast('')} />}
    </div>
  );
};

export default AdminUsersPage;
