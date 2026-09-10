# NIRIKSH: AI-Powered Criminal Network Analysis System
> **Tagline**: Secure Investigation Intelligence Platform  
> **Smart India Hackathon 2026 Prototype**

---

## 🚀 Overview

**NIRIKSH** is a futuristic cyber investigation intelligence command center designed to transform disconnected criminal investigation records (FIRs, CDR telecom logs, financial transactions, surveillance feeds, and intelligence notes) into an interactive, explainable, and multi-jurisdictional network topology graph.

Built with an **Apple-level futuristic dark visual design system**, NIRIKSH features glassmorphic floating panels, cyber radial purple glows, real-time Cytoscape.js graph rendering, automated 9-stage ingestion pipelines, explainable AI anomaly detection, network disruption modeling, and role-based access control (RBAC).

---

## ✨ Key Features

1. **Futuristic Command Center UI**: Custom-tailored dark glassmorphic design system using `#05040A` deep navy backgrounds, vibrant purple glows (`#7C3AED`, `#8B5CF6`), cyber cyan accents (`#22D3EE`), and custom typography (`Inter` + `JetBrains Mono`).
2. **Main SIH Demo Flow — Data Intake to Automatic Inline Graph**:
   - Multi-source dropzone (PDF, CSV, JSON, TXT).
   - Animated 9-stage processing pipeline (Data Received, Cleaning, Entity Extraction, Entity Matching, Relationship Detection, Graph Construction, Network Analysis, Risk Analysis, Investigator Review).
   - **Automatic Graph Reveal**: Seamless inline Cytoscape.js network graph reveal directly on the Data Intake page upon completion.
3. **Interactive Cytoscape.js Network Analysis**:
   - 30+ interconnected synthetic entity nodes across 9 entity types (Person, Phone, Location, Vehicle, Financial Account, Organization, Case, Event, Transaction).
   - Zoom, Pan, Fit, Reset, Node Focus, Type & Risk filtering, Neighborhood highlighting, and sliding side drawers.
4. **Network Disruption Simulator**:
   - Mathematical graph simulation modeling before and after metrics (network density, connected components, remaining high-risk links) upon removing key entities (e.g. `Raj Kumar`).
5. **Entity Resolution & Matching**:
   - Detailed profile for primary subject `Raj Kumar` (`person:raj-kumar`) with automated candidate match resolution against `R. Kumar` (92% confidence matching factors: name similarity, phone coincidence, location overlap, vehicle sharing).
6. **Explainable AI Alerts**:
   - Interactive risk indicators featuring a dedicated *"Why was this flagged?"* drawer explaining automated risk factors with confidence scores and human-in-the-loop verification disclaimers.
7. **Role-Based Access Control (RBAC)**:
   - Supports 7 system roles (`SUPER_ADMIN`, `ADMIN`, `SENIOR_INVESTIGATOR`, `INVESTIGATOR`, `ANALYST`, `STATE_OFFICER`, `VIEWER`) with route protection and dynamic sidebar navigation.
8. **Inter-State Coordination**:
   - Cross-state intelligence access request modals for multi-jurisdictional case collaboration (e.g. Punjab to Haryana/Delhi).

---

## 🛠️ Tech Stack

- **Core UI**: React 19, Vite, React Router DOM v7
- **Styling**: Tailwind CSS v4, Custom CSS Glassmorphism Tokens
- **Graph Visualization**: Cytoscape.js (`cytoscape`)
- **Data Visualization**: Recharts (`recharts`)
- **Iconography**: Lucide React (`lucide-react`)
- **HTTP Layer**: Axios (`axios`) with mock service boundaries

---

## 📁 Project Structure

```
niriksh-frontend/
├── public/
├── scripts/
│   └── process-logo.js         # Logo background transparency stripper
├── src/
│   ├── assets/
│   │   └── niriksh-logo.png    # Transparent NIRIKSH logo
│   ├── components/
│   │   ├── auth/               # ProtectedRoute & RoleGuard
│   │   ├── layout/             # Shell, Sidebar, Navbar, Drawers, Modals
│   │   └── ui font/            # Reusable Primitives (GlassCard, Button, Badge, Modal, etc.)
│   ├── config/
│   │   ├── env.js              # API & Mock data configuration
│   │   └── permissions.js      # RBAC permission matrix
│   ├── data/                   # Shared synthetic datasets
│   │   ├── users.js
│   │   ├── cases.js            # Includes primary demo case C-1024
│   │   ├── entities.js         # Includes Raj Kumar & 30+ nodes
│   │   ├── relationships.js
│   │   ├── alerts.js
│   │   ├── evidence.js
│   │   ├── notifications.js
│   │   ├── reports.js
│   │   ├── auditLogs.js
│   │   ├── crossStateRequests.js
│   │   └── processingJobs.js
│   ├── pages/                  # Command Center Views
│   │   ├── admin/              # User Mgmt, RBAC Matrix, Tokens, Audit Logs
│   │   ├── LandingPage.jsx
│   │   ├── LoginPage.jsx
│   │   ├── SignupPage.jsx
│   │   ├── DashboardPage.jsx
│   │   ├── CasesPage.jsx
│   │   ├── CaseDetailsPage.jsx
│   │   ├── DataIntakePage.jsx  # 9-Stage Pipeline + Auto Graph Reveal
│   │   ├── NetworkPage.jsx     # Cytoscape Graph Canvas
│   │   ├── DisruptionPage.jsx  # Graph Disruption Model
│   │   ├── EntitiesPage.jsx
│   │   ├── EntityDetailsPage.jsx # Entity Profile & Matching
│   │   ├── AlertsPage.jsx      # Explainable AI
│   │   ├── EvidencePage.jsx
│   │   ├── ReportsPage.jsx
│   │   ├── NotificationsPage.jsx
│   │   ├── ProfilePage.jsx
│   │   └── SettingsPage.jsx
│   ├── services/               # Isolated Mock Service Layer
│   ├── utils/                  # Cytoscape schema converters & ID helpers
│   ├── App.jsx                 # Main Routing Configuration
│   ├── main.jsx
│   └── index.css               # Design System Tokens
├── package.json
└── README.md
```

---

## 🔑 Demo Credentials

To log in to the prototype, use the following synthetic demo credentials:

| Employee ID | Password | Role | State |
| :--- | :--- | :--- | :--- |
| **`EMP001`** | `admin123` | SENIOR_INVESTIGATOR | Punjab |
| **`EMP003`** | `admin123` | SUPER_ADMIN | Delhi |

> *Note: Role switcher in the top Navbar allows instant on-the-fly RBAC testing.*

---

## ⚡ Getting Started

### 1. Installation
```bash
npm install
```

### 2. Run Locally
```bash
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

### 3. Production Build Validation
```bash
npm run build
```

---

## 🛡️ Synthetic Data & Safety Disclaimer

- **Synthetic Data**: All names (`Raj Kumar`, `Amit Verma`), phone numbers (`+91-98XXXXXX21`), registration numbers (`PB10XX1234`), bank account numbers (`ACCT-2048`), locations, and FIR records displayed in this application are 100% synthetic data generated for demonstration purposes.
- **Human-in-the-Loop**: All analytical insights, network linkages, and automated anomaly flags require human investigator confirmation. Detected connections do not establish guilt or legal liability.
- **Prototype Notice**: NIRIKSH is an architectural concept prototype created for the Smart India Hackathon 2026. Production deployment requires backend integration with FastAPI, PostgreSQL, Neo4j, JWT validation, and official government identity verification.
