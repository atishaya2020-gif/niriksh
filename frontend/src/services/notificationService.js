import {
  apiGet,
  apiPatch
} from './api';

const mapAlertToNotification = (
  alert
) => {

  const closed =
    alert.status === 'RESOLVED' ||
    alert.status === 'DISMISSED';

  return {
    id:
      `ALERT-${alert.id}`,

    type:
      'ALERT',

    title:
      alert.alert_type ||
      'Risk Alert',

    message:
      alert.reason ||
      `${alert.risk_level || 'UNKNOWN'} risk detected`,

    timestamp:
      alert.created_at
        ? new Date(
            alert.created_at
          ).toLocaleString()
        : 'Unknown',

    read:
      closed,

    link:
      alert.case_id
        ? `/cases/${alert.case_id}`
        : '/alerts',

    alert_id:
      alert.id,

    case_id:
      alert.case_id,

    risk_level:
      alert.risk_level,

    risk_score:
      alert.risk_score,

    confidence:
      alert.confidence
  };
};

export const notificationService = {

  getNotifications:
    async () => {

      const response =
        await apiGet('/alerts');

      const alerts =
        response?.data?.alerts ||
        response?.alerts ||
        [];

      return alerts.map(
        mapAlertToNotification
      );
    },

  markAsRead:
    async (id) => {

      const alertId =
        String(id).replace(
          'ALERT-',
          ''
        );

      return apiPatch(
        `/alerts/${alertId}/status?status=RESOLVED`
      );
    },

  markAllAsRead:
    async () => {

      const response =
        await apiGet('/alerts');

      const alerts =
        response?.data?.alerts ||
        response?.alerts ||
        [];

      const active =
        alerts.filter(
          (alert) =>
            alert.status !==
              'RESOLVED' &&
            alert.status !==
              'DISMISSED'
        );

      await Promise.all(
        active.map(
          (alert) =>
            apiPatch(
              `/alerts/${alert.id}/status?status=RESOLVED`
            )
        )
      );

      return {
        success: true
      };
    }
};

export default notificationService;