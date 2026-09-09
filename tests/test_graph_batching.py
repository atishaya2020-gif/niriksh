import unittest
from unittest.mock import patch

from app.services.graph_service import GraphBatch, create_record_graph


class GraphBatchingTests(unittest.TestCase):
    def test_graph_batch_accumulates_until_flush(self):
        batch = GraphBatch(batch_size=10)
        row = {"record_id": "REC-TEST-001", "category": "Cybercrime", "person_name": "Test Person", "city": "Delhi"}
        with patch("app.services.graph_service.neo4j_client.execute_write_batch") as mock_execute:
            create_record_graph(row, 99, batch)
            mock_execute.assert_not_called()
            batch.flush_all()
            mock_execute.assert_called()
            # Verify at least one call had non-empty rows
            any_non_empty = any(len(call[0][1]) > 0 for call in mock_execute.call_args_list)
            self.assertTrue(any_non_empty)

    def test_graph_batch_flushes_when_threshold_reached(self):
        batch = GraphBatch(batch_size=1)
        row = {"record_id": "REC-TEST-002", "category": "Cybercrime", "person_name": "Test Person", "city": "Delhi"}
        with patch("app.services.graph_service.neo4j_client.execute_write_batch") as mock_execute:
            create_record_graph(row, 99, batch)
            self.assertGreaterEqual(mock_execute.call_count, 1)