# """
#
# optimize_performer_test.py
#
# This program contains code to test optimize_performer.py.
#
# Author: Tameem Samawi (tsamawi@cra.com)
#
# """
#
# import unittest
# import sys
# sys.path.insert(0, '../../src/scenarios')
# sys.path.insert(0, '../../src/brass_api_src')
# from optimize_performer import OptimizePerformer
# from brass_api.orientdb.orientdb_helper import BrassOrientDBHelper
# from general_test_data import GeneralTestData
#
#
# class RunOptimizerTest(unittest.TestCase):
#     def setUp(self):
#         self.orientdb_helper = BrassOrientDBHelper('test', '../../conf/cra_config.json')
#         self.optimize_performer = OptimizePerformer('test', '../../conf/cra_config.json',
#                                                     '../../examples/mdl_files/scenario_1/BRASS_Scenario1_BeforeAdaptation.xml',
#                                                     '../output/RunOptimizerTestOutput.xml')
#         self.orientdb_helper.open_database()
#
#     def tearDown(self):
#         self.orientdb_helper.close_database()
#
#     def test_modify_mdl(self):
#         self.optimize_performer.modify_mdl()
#         # What would we even test here? that the export works?
#
#
