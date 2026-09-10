export const mockNotifications = [
  {
    id: "NTF-001",
    title: "New High-Risk Entity Match Detected",
    message: "Raj Kumar matched with R. Kumar across Case C-1024 and C-1041 (92% confidence).",
    timestamp: "10 mins ago",
    type: "ALERT",
    read: false,
    link: "/entities/person:raj-kumar"
  },
  {
    id: "NTF-002",
    title: "Data Intake Pipeline Completed",
    message: "FIR_Ludhiana_Report_2025.pdf processed successfully. 342 entities extracted and graph updated.",
    timestamp: "45 mins ago",
    type: "PROCESSING",
    read: false,
    link: "/data-intake"
  },
  {
    id: "NTF-003",
    title: "Cross-State Access Request Pending Approval",
    message: "Officer EMP005 requested access to Punjab intelligence records for Case C-1102.",
    timestamp: "2 hours ago",
    type: "ACCESS",
    read: true,
    link: "/admin/access-control"
  },
  {
    id: "NTF-004",
    title: "Suspicious Financial Transfer Alert",
    message: "₹14,50,000 RTGS wire transfer flagged under Case C-1024.",
    timestamp: "4 hours ago",
    type: "ALERT",
    read: true,
    link: "/alerts"
  }
];
