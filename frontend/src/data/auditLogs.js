export const mockAuditLogs = [
  {
    id: "LOG-901",
    timestamp: "15 Apr 2025 14:12:05",
    user_id: "EMP001",
    user_name: "Vikramaditya Singh",
    role: "SENIOR_INVESTIGATOR",
    action: "DATA_INGESTION_START",
    resource: "Data Intake File: FIR_Ludhiana_Report_2025.pdf",
    ip_address: "10.14.22.109",
    status: "SUCCESS",
    details: "Initiated 9-stage analysis pipeline for Case C-1024."
  },
  {
    id: "LOG-902",
    timestamp: "15 Apr 2025 14:13:30",
    user_id: "EMP001",
    user_name: "Vikramaditya Singh",
    role: "SENIOR_INVESTIGATOR",
    action: "NETWORK_GRAPH_VIEW",
    resource: "Network Topology - Case C-1024",
    ip_address: "10.14.22.109",
    status: "SUCCESS",
    details: "Loaded Cytoscape interactive graph view (32 nodes, 58 edges)."
  },
  {
    id: "LOG-903",
    timestamp: "15 Apr 2025 13:45:12",
    user_id: "EMP002",
    user_name: "Ananya Sharma",
    role: "ANALYST",
    action: "ENTITY_PROFILE_ACCESS",
    resource: "Entity ID: person:raj-kumar",
    ip_address: "10.14.22.115",
    status: "SUCCESS",
    details: "Reviewed potential match indicators with R. Kumar."
  },
  {
    id: "LOG-904",
    timestamp: "15 Apr 2025 11:20:00",
    user_id: "EMP005",
    user_name: "Amitabh Verma",
    role: "STATE_OFFICER",
    action: "CROSS_STATE_ACCESS_REQUEST",
    resource: "Target State: Punjab (Case C-1024)",
    ip_address: "10.20.08.44",
    status: "PENDING",
    details: "Requested 7-day read-only access for cross-state coordination."
  },
  {
    id: "LOG-905",
    timestamp: "14 Apr 2025 17:05:44",
    user_id: "EMP003",
    user_name: "Rajesh Guard",
    role: "SUPER_ADMIN",
    action: "USER_STATUS_UPDATE",
    resource: "User ID: EMP005",
    ip_address: "10.10.01.01",
    status: "SUCCESS",
    details: "Updated user account status to SUSPENDED."
  }
];
