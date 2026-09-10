import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Bell, CheckCheck, Radio, ShieldAlert, FileText } from 'lucide-react';
import GlassCard from '../components/ui/GlassCard';
import Button from '../components/ui/Button';
import notificationService from '../services/notificationService';

export const NotificationsPage = () => {
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    const loadNtf = async () => {
      const data = await notificationService.getNotifications();
      setNotifications(data);
    };
    loadNtf();
  }, []);

  const handleMarkAll = async () => {
    await notificationService.markAllAsRead();
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between border-b border-purple-900/30 pb-4">
        <div>
          <h1 className="text-2xl font-extrabold text-white font-mono-id tracking-tight">
            SYSTEM NOTIFICATIONS & ALERTS
          </h1>
          <p className="text-xs text-purple-300/70 font-mono-id mt-1">
            Real-time notifications log for cross-case matches, data intake, and access requests
          </p>
        </div>

        <Button variant="outline" size="sm" icon={CheckCheck} onClick={handleMarkAll}>
          Mark All As Read
        </Button>
      </div>

      <div className="space-y-3">
        {notifications.map((ntf) => (
          <GlassCard key={ntf.id} hoverEffect className="p-4">
            <div className="flex items-start justify-between gap-4">
              <div className="flex items-start gap-3">
                <div className="p-2.5 bg-purple-950/80 border border-purple-500/30 rounded-xl text-purple-300">
                  {ntf.type === 'ALERT' ? (
                    <Radio className="w-5 h-5 text-red-400" />
                  ) : ntf.type === 'ACCESS' ? (
                    <ShieldAlert className="w-5 h-5 text-amber-400" />
                  ) : (
                    <FileText className="w-5 h-5 text-cyan-400" />
                  )}
                </div>
                <div>
                  <h4 className="text-sm font-bold text-purple-100">{ntf.title}</h4>
                  <p className="text-xs font-mono-id text-purple-200 mt-1">{ntf.message}</p>
                  <span className="text-[10px] font-mono-id text-purple-400/60 block mt-2">
                    {ntf.timestamp}
                  </span>
                </div>
              </div>

              <Link to={ntf.link}>
                <Button variant="secondary" size="sm">
                  View Detail →
                </Button>
              </Link>
            </div>
          </GlassCard>
        ))}
      </div>
    </div>
  );
};

export default NotificationsPage;
