import React, { useEffect, useState } from 'react';
import { History, ShieldCheck, Lock } from 'lucide-react';
import Table from '../../components/ui/Table';
import Badge from '../../components/ui/Badge';
import LoadingState from '../../components/ui/LoadingState';
import { mockAuditLogs } from '../../data/auditLogs';

export const AdminAuditPage = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    setTimeout(() => {
      setLogs(mockAuditLogs);
      setLoading(false);
    }, 300);
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between border-b border-purple-900/30 pb-4">
        <div>
          <h1 className="text-2xl font-extrabold text-white font-mono-id tracking-tight">
            ADMINISTRATION • IMMUTABLE AUDIT LOGS
          </h1>
          <p className="text-xs text-purple-300/70 font-mono-id mt-1">
            Immutable digital ledger recording officer actions, data intake events, and access requests
          </p>
        </div>

        <Badge status="ACTIVE" size="md">CRYPTOGRAPHIC HASH VERIFIED</Badge>
      </div>

      {loading ? (
        <LoadingState message="Verifying cryptographic audit hashes..." />
      ) : (
        <Table
          headers={[
            'Timestamp',
            'Officer ID',
            'Officer Name',
            'Action Type',
            'Resource Target',
            'IP Address',
            'Status',
            'Details'
          ]}
        >
          {logs.map((log) => (
            <tr key={log.id} className="hover:bg-purple-900/20 font-mono-id text-xs">
              <td className="px-4 py-3.5 text-cyan-300 font-bold">{log.timestamp}</td>
              <td className="px-4 py-3.5 text-purple-200">{log.user_id}</td>
              <td className="px-4 py-3.5 font-semibold text-purple-100">{log.user_name}</td>
              <td className="px-4 py-3.5 text-cyan-400 font-bold">{log.action}</td>
              <td className="px-4 py-3.5 text-purple-300">{log.resource}</td>
              <td className="px-4 py-3.5 text-purple-400/60">{log.ip_address}</td>
              <td className="px-4 py-3.5">
                <Badge status={log.status} size="sm" />
              </td>
              <td className="px-4 py-3.5 text-purple-300/80 truncate max-w-[200px]">
                {log.details}
              </td>
            </tr>
          ))}
        </Table>
      )}
    </div>
  );
};

export default AdminAuditPage;
