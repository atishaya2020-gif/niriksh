export const mockEntities = [
  // PERSONS
  {
    id: "person:raj-kumar",
    name: "Raj Kumar",
    type: "PERSON",
    risk: "HIGH",
    confidence: 0.94,
    primary_case: "C-1024",
    cases: ["C-1024", "C-1041", "C-1088"],
    phone: "+91-98XXXXXX21",
    location: "Ludhiana",
    vehicle: "PB10XX1234",
    account: "ACCT-2048",
    source: "FIR / CDR / Bank Statement Analysis",
    last_seen: "14 Apr 2025 - Ludhiana Industrial Area",
    potential_matches: [
      {
        id: "person:r-kumar",
        name: "R. Kumar",
        confidence: 0.92,
        matching_factors: [
          "Name phonetic similarity (95%)",
          "Phone number coincidence (+91-98XXXXXX21)",
          "Overlapping location footprint (Ludhiana)",
          "Shared vehicle registration PB10XX1234",
          "Appearance in Case C-1041"
        ]
      }
    ],
    metadata: {
      aliases: ["Rajesh Kumar", "R.K. Transport Operator"],
      role: "Suspected Logistics Coordinator",
      national_id_hash: "8894-XXXX-1102"
    }
  },
  {
    id: "person:amit-verma",
    name: "Amit Verma",
    type: "PERSON",
    risk: "MEDIUM",
    confidence: 0.88,
    primary_case: "C-1024",
    cases: ["C-1024", "C-1102"],
    phone: "+91-98XXXXXX88",
    location: "Gurugram",
    vehicle: "HR26YY5678",
    account: "ACCT-9011",
    source: "Financial Audit Report",
    last_seen: "10 Apr 2025 - Cyber Hub Gurugram",
    metadata: { role: "Financial Account Holder" }
  },
  {
    id: "person:neha-singh",
    name: "Neha Singh",
    type: "PERSON",
    risk: "LOW",
    confidence: 0.81,
    primary_case: "C-1024",
    cases: ["C-1024"],
    phone: "+91-97XXXXXX55",
    location: "Ludhiana",
    account: "ACCT-4402",
    source: "Surveillance Log",
    last_seen: "08 Apr 2025 - Ludhiana",
    metadata: { role: "Corporate Secretary" }
  },
  {
    id: "person:r-kumar",
    name: "R. Kumar",
    type: "PERSON",
    risk: "HIGH",
    confidence: 0.92,
    primary_case: "C-1041",
    cases: ["C-1041"],
    phone: "+91-98XXXXXX21",
    location: "Amritsar",
    vehicle: "PB10XX1234",
    source: "CDR Deep Analysis",
    last_seen: "12 Apr 2025 - Amritsar Sector 4",
    metadata: { role: "Secondary Alias / Suspect" }
  },
  {
    id: "person:vikramjeet-gill",
    name: "Vikramjeet Gill",
    type: "PERSON",
    risk: "HIGH",
    confidence: 0.89,
    primary_case: "C-1041",
    cases: ["C-1041", "C-1024"],
    phone: "+91-99XXXXXX11",
    location: "Amritsar",
    source: "Intelligence Intercept",
    last_seen: "11 Apr 2025 - Amritsar Border",
    metadata: { role: "Transport Fleet Supervisor" }
  },
  {
    id: "person:sandeep-malhotra",
    name: "Sandeep Malhotra",
    type: "PERSON",
    risk: "MEDIUM",
    confidence: 0.85,
    primary_case: "C-1088",
    cases: ["C-1088"],
    phone: "+91-96XXXXXX44",
    location: "Jalandhar",
    source: "Banking Ledger",
    last_seen: "05 Apr 2025 - Jalandhar Main Branch",
    metadata: { role: "Shell Entity Director" }
  },

  // PHONES
  {
    id: "phone:9826000000",
    name: "+91-98XXXXXX21",
    type: "PHONE",
    risk: "HIGH",
    confidence: 0.96,
    primary_case: "C-1024",
    cases: ["C-1024", "C-1041"],
    source: "Telecom CDR Ingestion",
    last_seen: "Active 2 hours ago",
    metadata: { provider: "Airtel Punjab", call_count_30d: 412 }
  },
  {
    id: "phone:9811122233",
    name: "+91-98XXXXXX88",
    type: "PHONE",
    risk: "MEDIUM",
    confidence: 0.90,
    primary_case: "C-1024",
    cases: ["C-1024"],
    source: "CDR Log",
    last_seen: "Yesterday 18:40",
    metadata: { provider: "Jio Haryana", call_count_30d: 189 }
  },
  {
    id: "phone:9755566677",
    name: "+91-97XXXXXX55",
    type: "PHONE",
    risk: "LOW",
    confidence: 0.84,
    primary_case: "C-1024",
    cases: ["C-1024"],
    source: "CDR Log",
    last_seen: "10 Apr 2025",
    metadata: { provider: "Vi Punjab" }
  },

  // LOCATIONS
  {
    id: "loc:ludhiana",
    name: "Ludhiana Industrial Freight Hub",
    type: "LOCATION",
    risk: "HIGH",
    confidence: 0.95,
    primary_case: "C-1024",
    cases: ["C-1024", "C-1041", "C-1088"],
    source: "GPS & Cell Tower Triangulation",
    last_seen: "Continuous monitoring",
    metadata: { coordinates: "30.9010° N, 75.8573° E", risk_factor: "High Transit Frequency" }
  },
  {
    id: "loc:amritsar",
    name: "Amritsar Freight Terminal",
    type: "LOCATION",
    risk: "CRITICAL",
    confidence: 0.97,
    primary_case: "C-1041",
    cases: ["C-1041"],
    source: "Border Patrol Surveillance",
    last_seen: "14 Apr 2025",
    metadata: { coordinates: "31.6340° N, 74.8723° E" }
  },
  {
    id: "loc:gurugram",
    name: "Gurugram Logistics Depot",
    type: "LOCATION",
    risk: "MEDIUM",
    confidence: 0.88,
    primary_case: "C-1102",
    cases: ["C-1102", "C-1024"],
    source: "Toll Gate Camera Log",
    last_seen: "12 Apr 2025",
    metadata: { coordinates: "28.4595° N, 77.0266° E" }
  },
  {
    id: "loc:warehouse",
    name: "Focal Point Warehouse 12B",
    type: "LOCATION",
    risk: "HIGH",
    confidence: 0.93,
    primary_case: "C-1024",
    cases: ["C-1024"],
    source: "Surveillance Observation",
    last_seen: "09 Apr 2025 23:15",
    metadata: { notes: "Site of verified night meetings" }
  },

  // VEHICLES
  {
    id: "veh:pb10xx1234",
    name: "PB10XX1234 (Freight Heavy Truck)",
    type: "VEHICLE",
    risk: "HIGH",
    confidence: 0.94,
    primary_case: "C-1024",
    cases: ["C-1024", "C-1041"],
    source: "ANPR Highway Camera",
    last_seen: "14 Apr 2025 - NH44 Highway",
    metadata: { make: "Tata Prima 4928", owner: "Northline Logistics" }
  },
  {
    id: "veh:hr26yy5678",
    name: "HR26YY5678 (Commercial SUV)",
    type: "VEHICLE",
    risk: "MEDIUM",
    confidence: 0.89,
    primary_case: "C-1102",
    cases: ["C-1102", "C-1024"],
    source: "Toll Plaza Feed",
    last_seen: "13 Apr 2025",
    metadata: { make: "Mahindra Scorpio-N" }
  },

  // FINANCIAL ACCOUNTS
  {
    id: "fin:acct-2048",
    name: "ACCT-2048 (Northline Commercial)",
    type: "FINANCIAL_ACCOUNT",
    risk: "CRITICAL",
    confidence: 0.96,
    primary_case: "C-1024",
    cases: ["C-1024", "C-1088"],
    source: "FIU Suspicious Transaction Report",
    last_seen: "15 Apr 2025",
    metadata: { bank: "State Bank of India", balance_tier: "High Velocity" }
  },
  {
    id: "fin:acct-9011",
    name: "ACCT-9011 (Apex Trade Escrow)",
    type: "FINANCIAL_ACCOUNT",
    risk: "HIGH",
    confidence: 0.91,
    primary_case: "C-1024",
    cases: ["C-1024"],
    source: "Bank Wire Transfer Log",
    last_seen: "11 Apr 2025",
    metadata: { bank: "HDFC Bank" }
  },
  {
    id: "fin:acct-4402",
    name: "ACCT-4402 (Personal Savings)",
    type: "FINANCIAL_ACCOUNT",
    risk: "LOW",
    confidence: 0.82,
    primary_case: "C-1024",
    cases: ["C-1024"],
    source: "Audit Report",
    last_seen: "08 Apr 2025",
    metadata: { bank: "ICICI Bank" }
  },

  // ORGANIZATIONS
  {
    id: "org:northline",
    name: "Northline Logistics Pvt Ltd",
    type: "ORGANIZATION",
    risk: "HIGH",
    confidence: 0.95,
    primary_case: "C-1024",
    cases: ["C-1024", "C-1041", "C-1102"],
    source: "ROC Registrar & GST Filing",
    last_seen: "Active Corporate Entity",
    metadata: { gst_status: "Flagged", reg_number: "CIN-U60231PB2021PTC" }
  },
  {
    id: "org:apex",
    name: "Apex Global Trade Corp",
    type: "ORGANIZATION",
    risk: "MEDIUM",
    confidence: 0.87,
    primary_case: "C-1088",
    cases: ["C-1088", "C-1024"],
    source: "GST Portal Data",
    last_seen: "Active Shell Entity",
    metadata: { reg_state: "Punjab" }
  },

  // CASES
  {
    id: "case:c-1024",
    name: "Case C-1024 (Operation Alpha)",
    type: "CASE",
    risk: "HIGH",
    confidence: 1.0,
    primary_case: "C-1024",
    cases: ["C-1024"],
    source: "System Core Case Index",
    last_seen: "Active Investigation",
    metadata: { status: "ACTIVE" }
  },

  // EVENTS & TRANSACTIONS
  {
    id: "evt:warehouse-meet",
    name: "Night Cargo Transfer Event",
    type: "EVENT",
    risk: "HIGH",
    confidence: 0.92,
    primary_case: "C-1024",
    cases: ["C-1024"],
    source: "Field Reconnaissance Note",
    last_seen: "09 Apr 2025 23:45",
    metadata: { location: "Ludhiana Warehouse" }
  },
  {
    id: "txn:89042",
    name: "TXN-89042 (₹14,50,000 Transfer)",
    type: "TRANSACTION",
    risk: "CRITICAL",
    confidence: 0.98,
    primary_case: "C-1024",
    cases: ["C-1024", "C-1088"],
    source: "Bank Gateway Wire Log",
    last_seen: "11 Apr 2025 14:22",
    metadata: { amount: "₹14,50,000", mode: "RTGS" }
  },
  {
    id: "txn:91104",
    name: "TXN-91104 (₹4,80,000 Wire)",
    type: "TRANSACTION",
    risk: "MEDIUM",
    confidence: 0.90,
    primary_case: "C-1024",
    cases: ["C-1024"],
    source: "NEFT Ledger",
    last_seen: "13 Apr 2025 11:05",
    metadata: { amount: "₹4,80,000", mode: "NEFT" }
  }
];
