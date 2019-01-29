import unittest
from unittest.mock import patch
from cra.scenarios.common.exception_class import NodeNotFoundException
import cra.utils.orientdb_utils as orientdb_utils


class MockPyorientNode:
    def __init__(self, ID, _class, _rid):
        self.ID = ID
        self._class = _class
        self._rid = _rid


class OrientDBUtilsTest(unittest.TestCase):
    def setUp(self):
        self.mock_id = 'TA1'
        self.mock_class = 'Rate'
        self.mock_rid = 'rid'

        self.mock_pyorient_node = MockPyorientNode(self.mock_id, self.mock_class, self.mock_rid)

    @patch('brass_api.orientdb.orientdb_helper.BrassOrientDBHelper')
    def test_get_rate_node(self, MockBrassOrientDBHelper):
        orientdb_helper = MockBrassOrientDBHelper()
        orientdb_helper.get_nodes_by_type.return_value = [self.mock_pyorient_node]
        orientdb_helper.get_connected_nodes.return_value = [self.mock_pyorient_node]

        actual = orientdb_utils.get_rate_node(orientdb_helper, self.mock_id)
        self.assertEqual(self.mock_pyorient_node, actual)

    @patch('brass_api.orientdb.orientdb_helper.BrassOrientDBHelper')
    def test_get_rate_node_missing_slp_node(self, MockBrassOrientDBHelper):
        invalid_mock_id = 'foo'

        orientdb_helper = MockBrassOrientDBHelper()
        orientdb_helper.get_nodes_by_type.return_value = [self.mock_pyorient_node]
        orientdb_helper.get_connected_nodes.return_value = [self.mock_pyorient_node]

        self.assertRaises(NodeNotFoundException, orientdb_utils.get_rate_node, orientdb_helper, invalid_mock_id)

    @patch('brass_api.orientdb.orientdb_helper.BrassOrientDBHelper')
    def test_get_rate_node_missing_rate_nodes(self, MockBrassOrientDBHelper):
        invalid_mock_class = 'foo'
        mock_pyorient_node = MockPyorientNode(self.mock_id, invalid_mock_class, self.mock_rid)

        orientdb_helper = MockBrassOrientDBHelper()
        orientdb_helper.get_nodes_by_type.return_value = [self.mock_pyorient_node]
        orientdb_helper.get_connected_nodes.return_value = [mock_pyorient_node]

        self.assertRaises(NodeNotFoundException, orientdb_utils.get_rate_node, orientdb_helper, self.mock_id)
