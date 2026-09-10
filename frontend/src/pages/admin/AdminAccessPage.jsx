import React from 'react';
import { ShieldCheck, Check, X } from 'lucide-react';
import GlassCard from '../../components/ui/GlassCard';
import Table from '../../components/ui/Table';
import { ROLES, PERMISSIONS, ROLE_PERMISSIONS } from '../../config/permissions';

export const AdminAccessPage = () => {
  const rolesList = Object.keys(ROLES);
  const permissionsList = Object.keys(PERMISSIONS);

  return (
    <div className="space-y-6">
      <div className="border-b border-purple-900/30 pb-4">
        <h1 className="text-2xl font-extrabold text-white font-mono-id tracking-tight">
          ADMINISTRATION • ACCESS CONTROL MATRIX
        </h1>
        <p className="text-xs text-purple-300/70 font-mono-id mt-1">
          Role-Based Access Control (RBAC) permission definitions and route enforcement rules
        </p>
      </div>

      <Table headers={['Permission Name', ...rolesList]}>
        {permissionsList.map((permKey) => (
          <tr key={permKey} className="hover:bg-purple-900/20 font-mono-id text-xs">
            <td className="px-4 py-3 font-bold text-cyan-300">{permKey}</td>
            {rolesList.map((roleKey) => {
              const hasPerm = (ROLE_PERMISSIONS[roleKey] || []).includes(PERMISSIONS[permKey]);
              return (
                <td key={roleKey} className="px-4 py-3 text-center">
                  {hasPerm ? (
                    <span className="inline-flex p-1 bg-emerald-950/80 rounded border border-emerald-500/40 text-emerald-400">
                      <Check className="w-3.5 h-3.5" />
                    </span>
                  ) : (
                    <span className="inline-flex p-1 bg-slate-950 rounded border border-purple-900/30 text-purple-400/40">
                      <X className="w-3.5 h-3.5" />
                    </span>
                  )}
                </td>
              );
            })}
          </tr>
        ))}
      </Table>
    </div>
  );
};

export default AdminAccessPage;
