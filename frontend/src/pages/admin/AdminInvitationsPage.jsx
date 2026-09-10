import React, { useState } from 'react';
import { KeyRound, Plus, Copy, CheckCircle2 } from 'lucide-react';
import GlassCard from '../../components/ui/GlassCard';
import Button from '../../components/ui/Button';
import Input from '../../components/ui/Input';
import Table from '../../components/ui/Table';
import Badge from '../../components/ui/Badge';
import Toast from '../../components/ui/Toast';

export const AdminInvitationsPage = () => {
  const [tokens, setTokens] = useState([
    { id: 'INV-1', code: 'NIRIKSH-PRO-2026', role: 'SENIOR_INVESTIGATOR', state: 'Punjab', status: 'ACTIVE', created: '10 Mar 2025' },
    { id: 'INV-2', code: 'NIRIKSH-PB-9912', role: 'INVESTIGATOR', state: 'Punjab', status: 'ACTIVE', created: '12 Mar 2025' },
    { id: 'INV-3', code: 'NIRIKSH-HR-3321', role: 'STATE_OFFICER', state: 'Haryana', status: 'EXPIRED', created: '01 Jan 2025' }
  ]);

  const [toast, setToast] = useState('');

  const generateToken = () => {
    const newCode = `NIRIKSH-AUTH-${Math.floor(1000 + Math.random() * 9000)}`;
    const newToken = {
      id: `INV-${tokens.length + 1}`,
      code: newCode,
      role: 'INVESTIGATOR',
      state: 'Punjab',
      status: 'ACTIVE',
      created: 'Just now'
    };
    setTokens((prev) => [newToken, ...prev]);
    setToast(`Generated invitation token: ${newCode}`);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-purple-900/30 pb-4">
        <div>
          <h1 className="text-2xl font-extrabold text-white font-mono-id tracking-tight">
            ADMINISTRATION • INVITATION TOKENS
          </h1>
          <p className="text-xs text-purple-300/70 font-mono-id mt-1">
            Generate secure invitation token keys for government officer signup verification
          </p>
        </div>

        <Button variant="cyan" icon={Plus} onClick={generateToken}>
          Generate New Token Code
        </Button>
      </div>

      <Table headers={['Token Code', 'Assigned Role', 'Jurisdiction State', 'Status', 'Created Date', 'Action']}>
        {tokens.map((t) => (
          <tr key={t.id} className="hover:bg-purple-900/20 font-mono-id text-xs">
            <td className="px-4 py-3.5 font-bold text-cyan-300">{t.code}</td>
            <td className="px-4 py-3.5 text-purple-200">{t.role}</td>
            <td className="px-4 py-3.5 text-purple-300">{t.state}</td>
            <td className="px-4 py-3.5">
              <Badge status={t.status} size="sm" />
            </td>
            <td className="px-4 py-3.5 text-purple-400/60">{t.created}</td>
            <td className="px-4 py-3.5">
              <Button
                variant="secondary"
                size="sm"
                icon={Copy}
                onClick={() => {
                  navigator.clipboard.writeText(t.code);
                  setToast(`Copied ${t.code} to clipboard.`);
                }}
              >
                Copy
              </Button>
            </td>
          </tr>
        ))}
      </Table>

      {toast && <Toast type="success" message={toast} onClose={() => setToast('')} />}
    </div>
  );
};

export default AdminInvitationsPage;
