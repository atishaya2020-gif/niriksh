export const PROCESS_STAGES = [
  { id: "stage_01", step: "01", name: "DATA RECEIVED", desc: "Verifying digital signature and file integrity" },
  { id: "stage_02", step: "02", name: "DATA CLEANING", desc: "Normalizing text formatting, OCR cleaning & tokenization" },
  { id: "stage_03", step: "03", name: "ENTITY EXTRACTION", desc: "Extracting names, phones, locations, accounts & vehicles" },
  { id: "stage_04", step: "04", name: "ENTITY MATCHING", desc: "Cross-referencing entities against active system database" },
  { id: "stage_05", step: "05", name: "RELATIONSHIP DETECTION", desc: "Inferring co-occurrences, CDR logs, and financial flows" },
  { id: "stage_06", step: "06", name: "GRAPH CONSTRUCTION", desc: "Building Cytoscape graph topology & node positioning" },
  { id: "stage_07", step: "07", name: "NETWORK ANALYSIS", desc: "Calculating centrality scores, degree distribution & hubs" },
  { id: "stage_08", step: "08", name: "RISK ANALYSIS", desc: "Evaluating anomaly patterns & generating Explainable AI alerts" },
  { id: "stage_09", step: "09", name: "INVESTIGATOR REVIEW", desc: "Finalizing network graph reveal for analyst validation" }
];

export const mockProcessingResults = {
  records_processed: 1248,
  entities_extracted: 342,
  potential_matches: 87,
  relationships_detected: 516,
  high_risk_indicators: 14,
  review_required: 23
};
