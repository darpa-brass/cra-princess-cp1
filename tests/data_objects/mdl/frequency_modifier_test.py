"""
frequency_modifier_test.py

This program contains code to test frequency_modifier.py.
Author: Tameem Samawi (tsamawi@cra.com)
"""
import sys
import unittest
from general_test_data import GeneralTestData
from frequency_modifier_test_data import FrequencyModifierTestData
from orientdb_utils import import_mdl
from frequency_modifier import FrequencyModifier
from brass_api.orientdb.orientdb_helper import BrassOrientDBHelper


class FrequencyModifierTest(unittest.TestCase):
    def setUp(self):
        import_mdl(GeneralTestData.database_name,
                   GeneralTestData.config_file,
                   GeneralTestData.mdl_file)
        self.orientdb_helper = BrassOrientDBHelper(
            database_name=GeneralTestData.database_name,
            config_file=GeneralTestData.config_file)
        self.orientdb_helper.open_database(over_write=False)
        self.frequency = FrequencyModifier(
            self.orientdb_helper, FrequencyModifierTestData.value)

    def tearDown(self):
        self.orientdb_helper.close_database()

    def test_adjust_frequency(self):
        self.frequency.adjust_frequency()

        valid = False
        txop_nodes = self.orientdb_helper.get_nodes_by_type('TxOp')
        for node in txop_nodes:
            if int(node.CenterFrequencyHz) == FrequencyModifierTestData.value:
                valid = True
            else:
                valid = False
                break

        self.assertTrue(valid)

    def test_adjust_frequency_no_nodes(self):
        txop_nodes = self.orientdb_helper.get_nodes_by_type('TxOp')
        txop_rids = []
        for node in txop_nodes:
            txop_rids.append(node._rid)

        # There are 6 TxOp nodes in Scenario 1's MDL file, which is what is in
        # the test database
        self.assertEqual(len(txop_rids), 6)

        self.orientdb_helper.delete_nodes_by_rid(txop_rids)

        try:
            self.frequency.adjust_frequency()
        except Exception:
            self.fail(
                'Adjusting frequency with 0 TxOp nodes raised an exception unexpectedly')
