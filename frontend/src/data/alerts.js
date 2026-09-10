export const mockAlerts = [
  {
    id: "ALT-9001",
    title: "High-Risk Entity Cross-Case Match",
    type: "CROSS_CASE_MATCH",
    severity: "CRITICAL",
    confidence: 0.94,
    case_id: "C-1024",
    target_entity: "Raj Kumar",
    target_entity_id: "person:raj-kumar",
    timestamp: "10 mins ago",
    status: "REQUIRES_REVIEW",
    summary: "Raj Kumar (Operation Alpha C-1024) matched with high confidence (92%) to R. Kumar (Drug Trafficking Network C-1041).",
    why_flagged: [
      "Identical primary contact phone number (+91-98XXXXXX21) detected across separate case CDR logs.",
      "Shared freight truck registration PB10XX1234 registered under Northline Logistics.",
      "High geographical co-location between Ludhiana and Amritsar transport depots within a 48-hour window.",
      "Financial wire transfer overlap between corporate accounts ACCT-2048 and ACCT-9011.",
      "Network centrality degree indicator exceeding 94th percentile across active Punjab cases."
    ],
    recommended_action: "Initiate joint case review and approve cross-jurisdictional entity unification."
  },
  {
    id: "ALT-9002",
    title: "Suspicious High-Velocity Wire Transfer",
    type: "UNUSUAL_TRANSACTION",
    severity: "HIGH",
    confidence: 0.91,
    case_id: "C-1024",
    target_entity: "ACCT-2048",
    target_entity_id: "fin:acct-2048",
    timestamp: "1 hour ago",
    status: "UNREAD",
    summary: "Single RTGS wire transfer of ₹14,50,000 executed outside regular commercial banking window.",
    why_flagged: [
      "Transaction amount 450% above historical average for ACCT-2048.",
      "Originating account linked to flagged shell entity Northline Logistics.",
      "Destination account ACCT-9011 opened within 14 days of transfer."
    ],
    recommended_action: "Request bank transaction audit trail from Financial Intelligence Unit."
  },
  {
    id: "ALT-9003",
    title: "Night Cargo Transport Anomaly",
    type: "NETWORK_CLUSTER",
    severity: "HIGH",
    confidence: 0.88,
    case_id: "C-1024",
    target_entity: "PB10XX1234",
    target_entity_id: "veh:pb10xx1234",
    timestamp: "3 hours ago",
    status: "UNDER_REVIEW",
    summary: "Vehicle PB10XX1234 detected at Focal Point Warehouse during unauthorized hours.",
    why_flagged: [
      "ANPR camera capture at 23:15 coincide with phone ping from +91-98XXXXXX21.",
      "Surveillance feed indicates 3 heavy vehicles entering unlit facility."
    ],
    recommended_action: "Dispatch field reconnaissance unit to verify warehouse occupant status."
  },
  {
    id: "ALT-9004",
    title: "Cross-State Freight Border Crossing",
    type: "REPEATED_ASSOCIATION",
    severity: "MEDIUM",
    confidence: 0.83,
    case_id: "C-1102",
    target_entity: "Gurugram Logistics Depot",
    target_entity_id: "loc:gurugram",
    timestamp: " Yesterday",
    status: "RESOLVED",
    summary: "Freight movement originating in Ludhiana crossed Punjab-Haryana border without complete e-way manifest.",
    why_flagged: [
      "Toll plaza camera failed to match physical vehicle chassis to registered carrier."
    ],
    recommended_action: "Flag carrier license for state toll inspection."
  }
];
