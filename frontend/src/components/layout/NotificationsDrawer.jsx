import React from 'react';
import { Link } from 'react-router-dom';
import { Bell, CheckCheck, Radio, ShieldAlert, FileText } from 'lucide-react';
import Drawer from '../ui/Drawer';
import { mockNotifications } from '../../data/notifications';

export const NotificationsDrawer = ({ isOpen, onClose }) => {
  return (
    <Drawer
      isOpen={isOpen}
      onClose={onClose}
      title="SYSTEM NOTIFICATIONS"
      subtitle="Real-Time Investigation Alerts & Requests"
    >
      <div className="space-y-4">
        <div className="flex items-center justify-between pb-2 border-b border-purple-900/30">
          <span className="text-xs font-mono-id text-purple-300/70">
            {mockNotifications.length} Active System Notices
          </span>
          <button className="text-xs text-cyan-400 hover:underline flex items-center gap-1 font-mono-id cursor-pointer">
            <CheckCheck className="w-3.5 h-3.5" /> Mark all read
          </button>
        </div>

        <div className="space-y-2.5">
          {mockNotifications.map((ntf) => (
            <Link
              key={ntf.id}
              to={ntf.link}
              onClick={onClose}
              className={`block p-3 rounded-xl border transition-all ${
                !ntf.read
                  ? 'bg-purple-950/50 border-purple-500/40 shadow-sm shadow-purple-900/40'
                  : 'bg-slate-950/40 border-purple-900/20 text-purple-300/70'
              }`}
            >
              <div className="flex items-start gap-3">
                <div className="p-2 bg-purple-900/50 rounded-lg text-purple-300 mt-0.5">
                  {ntf.type === 'ALERT' ? (
                    <Radio className="w-4 h-4 text-red-400" />
                  ) : ntf.type === 'ACCESS' ? (
                    <ShieldAlert className="w-4 h-4 text-amber-400" />
                  ) : (
                    <FileText className="w-4 h-4 text-cyan-400" />
                  )}
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <h5 className="text-xs font-bold text-purple-100">{ntf.title}</h5>
                    <span className="text-[10px] font-mono-id text-purple-400/60">
                      {ntf.timestamp}
                    </span>
                  </div>
                  <p className="text-xs text-purple-300/80 mt-1 font-mono-id line-clamp-2">
                    {ntf.message}
                  </p>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </Drawer>
  );
};

export default NotificationsDrawer;
