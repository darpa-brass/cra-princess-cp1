import sys
sys.path.insert(0, '../../')
from general_test_data import GeneralTestData
import unittest
from cra.scenarios.optimization.optimization_result import OptimizationResult
from cra.scenarios.mdl_data.mdl_frequency import MDLFrequency
from cra.scenarios.mdl_data.mdl_txop import TxOp
from cra.scenarios.optimization.store_result import StoreResult
from cra.utils.logger import Logger
from optimization_result_test_data import OptimizationResultTestData
from unittest.mock import patch
from brass_api.orientdb.orientdb_helper import BrassOrientDBHelper
from general_test_data import GeneralTestData

from functools import reduce

#logger =Logger().logger


class StoreResultTest(unittest.TestCase):
    @patch('brass_api.orientdb.orientdb_helper.BrassOrientDBHelper')
    def test_update_frequency(self, MockBrassOrientDBHelper):
        # Setup testing variables
        new_frequency_value = 1200
        new_frequency = MDLFrequency(new_frequency_value)

        # Setup mocking return values and mocked functions
        mock_txop_list = [TxOp(start_usec=0, stop_usec=10500, center_frequency_hz=MDLFrequency(1000), txop_timeout=255, _rid='1'),
                          TxOp(start_usec=12000, stop_usec=25000, center_frequency_hz=MDLFrequency(1000), txop_timeout=255, _rid='2')]

        def mock_update_node(a, b):
            for txop in mock_txop_list:
                txop.center_frequency_hz = new_frequency

        # Setup mocking object
        orientdb_helper = MockBrassOrientDBHelper()
        orientdb_helper.get_nodes_by_type.return_value = mock_txop_list
        orientdb_helper.update_node.side_effect = mock_update_node

        # Perform frequency modification
        store_result = StoreResult(orientdb_helper)
        store_result.update_frequency(new_frequency)

        for txop in mock_txop_list:
            self.assertEqual(txop.center_frequency_hz.value, new_frequency_value)

    @patch('brass_api.orientdb.orientdb_helper.BrassOrientDBHelper')
    def test_update_frequency_invalid_frequency(self, MockBrassOrientDBHelper):
        orientdb_helper = MockBrassOrientDBHelper()
        store_result = StoreResult(orientdb_helper)

        self.assertRaises(ValueError, store_result.update_frequency, 'Should be an instance of MDLFrequency')

    @patch('brass_api.orientdb.orientdb_helper.BrassOrientDBHelper')
    def test_update_schedule(self, MockBrassOrientDBHelper):
        class MockRadioLink:
            def __init__(self, ID):
                self.ID = ID

        # Mocked methods
        def mock_get_nodes_by_type(_type):
            if _type == 'TxOp':
                return [TxOp(start_usec=0, stop_usec=10500, center_frequency_hz=MDLFrequency(1000), txop_timeout=255, _rid='1'),
                 TxOp(start_usec=12000, stop_usec=25000, center_frequency_hz=MDLFrequency(1000), txop_timeout=255, _rid='2')]

            elif _type == 'RadioLink':
                return [MockRadioLink('A'), MockRadioLink('B'), MockRadioLink('C')]
            else:
                return None

        # Configure mocking object
        orientdb_helper = MockBrassOrientDBHelper()
        orientdb_helper.get_nodes_by_type.side_effect = mock_get_nodes_by_type
        orientdb_helper.get_child_nodes.side_effect = mock_get_child_nodes
        orientdb_helper.update_node.side_effect = mock_update_node
        orientdb_helper.create_node.side_effect = mock_create_node
        orientdb_helper.set_containment_relationship.return_value = None
        orientdb_helper.delete_nodes_by_rid.return_value = None


    # @patch('brass_api.orientdb.orientdb_helper.BrassOrientDBHelper')
    # def test_update_schedule(self, MockBrassOrientDBHelper):
    #     (OptimizationResultTestData.valid_mdl_schedule,
    #      OptimizationResultTestData.valid_mdl_bandwidth_set,
    #      OptimizationResultTestData.valid_mdl_frequency)

# TODO Is it enough to just test that our update_frequency method makes calls to the database?
# The actual call to update node does not pass in a txop list.

