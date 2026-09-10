import { apiGet } from './api';

import {
  backendGraphToCytoscape
} from '../utils/graphTransform';

export const networkService = {

  getGraph:
    async (caseId) => {

      const id =
        Number(caseId);

      if (
        !Number.isInteger(id) ||
        id <= 0
      ) {
        throw new Error(
          'Select a valid case.'
        );
      }

      const response =
        await apiGet(
          `/network/${id}`
        );

      const data =
        response?.data ||
        response;

      const network =
        data?.network ||
        {};

      return {

        nodes:
          (network.nodes || [])
            .map(
              (node) => ({
                id:
                  node.id,

                name:
                  node.label ||
                  node.id,

                label:
                  node.label ||
                  node.id,

                type:
                  node.type ||
                  'UNKNOWN',

                risk:
                  node.risk ||
                  'LOW',

                risk_score:
                  node.risk_score ||
                  0,

                confidence:
                  0.85,

                metadata:
                  node.metadata ||
                  {},

                source:
                  'Graph Database',

                cases: [],

                potential_matches: []
              })
            ),

        edges:
          (network.edges || [])
            .map(
              (edge, index) => ({
                id:
                  edge.id ||
                  `edge-${index}`,

                source:
                  edge.source,

                target:
                  edge.target,

                type:
                  (
                    edge.relationship_type ||
                    'CONNECTED_TO'
                  ).toUpperCase(),

                label:
                  edge.relationship_type ||
                  'Connected',

                confidence:
                  edge.confidence ||
                  0.85,

                evidence_id:
                  null,

                timestamp:
                  null,

                why_detected:
                  edge.reason ||
                  'Connection detected.'
              })
            ),

        _raw:
          data
      };
    },

  getCytoscapeElements:
    async (caseId) => {

      const graph =
        await networkService.getGraph(
          caseId
        );

      return backendGraphToCytoscape(
        graph
      );
    },

  simulateDisruption:
    async (
      caseId,
      targetEntityId
    ) => {

      const id =
        Number(caseId);

      if (
        !Number.isInteger(id) ||
        id <= 0
      ) {
        throw new Error(
          'Invalid case ID.'
        );
      }

      if (!targetEntityId) {
        throw new Error(
          'Select an entity.'
        );
      }

      return apiGet(
        `/network/${id}/simulate`,
        {
          target_entity_id:
            targetEntityId
        }
      );
    }
};

export default networkService;