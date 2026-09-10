/**
 * Converts backend network graph schema to Cytoscape.js compatible elements format.
 */
export const backendGraphToCytoscape = (backendGraph) => {
  if (!backendGraph || !backendGraph.nodes) return [];

  const cytoscapeNodes = backendGraph.nodes.map((node) => ({
    data: {
      id: node.id,
      label: node.name || node.label || node.id,
      type: node.type ? node.type.toUpperCase() : 'UNKNOWN',
      risk: node.risk || 'LOW',
      confidence: node.confidence || 0.8,
      cases: node.cases || [],
      phone: node.phone || null,
      location: node.location || null,
      vehicle: node.vehicle || null,
      account: node.account || null,
      source: node.source || 'Ingestion Service',
      last_seen: node.last_seen || null,
      potential_matches: node.potential_matches || [],
      metadata: node.metadata || {}
    }
  }));

  const cytoscapeEdges = (backendGraph.edges || []).map((edge) => ({
    data: {
      id: edge.id,
      source: edge.source,
      target: edge.target,
type: (edge.type || edge.relationship_type || 'CONNECTED_TO').toUpperCase(),
       label: edge.label || edge.relationship_type || edge.type || 'Connected',
       confidence: edge.confidence || 0.85,
       evidence_id: edge.evidence_id || null,
       timestamp: edge.timestamp || null,
       why_detected: edge.why_detected || edge.reason || 'Co-occurrence in investigation records.'
    }
  }));

  return [...cytoscapeNodes, ...cytoscapeEdges];
};

export const getNodeColor = (type, risk) => {
  if (risk === 'CRITICAL') return '#EF4444';
  
  switch (type) {
    case 'PERSON':
      return '#8B5CF6'; // purple
    case 'PHONE':
      return '#A855F7'; // bright violet
    case 'LOCATION':
      return '#22D3EE'; // cyan
    case 'VEHICLE':
      return '#F97316'; // orange
    case 'FINANCIAL_ACCOUNT':
      return '#2DD4BF'; // teal
    case 'ORGANIZATION':
      return '#38BDF8'; // blue
    case 'CASE':
      return '#C084FC'; // light purple
    case 'EVENT':
      return '#EAB308'; // yellow
    case 'TRANSACTION':
      return '#EC4899'; // pink
    default:
      return '#94A3B8';
  }
};
