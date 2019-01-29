# """
#
# schedule_modifier_test.py
#
# This program contains code to test schedule_modifier.py.
#
# Author: Tameem Samawi (tsamawi@cra.com)
#
# """
#
# import sys
# import unittest
# sys.path.insert(0, '../../src/scenarios')
# sys.path.insert(0, '../../src/brass_api_src')
# sys.path.insert(0, '../../src/utils')
# from general_test_data import GeneralTestData
# from orientdb_utils import import_mdl
# from schedule_modifier import ScheduleModifier
# from schedule_modifier_test_data import ScheduleModifierTestData
# from brass_api.orientdb.orientdb_helper import BrassOrientDBHelper
#
#
# class ScheduleModifierTest(unittest.TestCase):
#     def setUp(self):
#         import_mdl(
#             GeneralTestData.database_name,
#             GeneralTestData.config_file,
#             GeneralTestData.mdl_file)
#         self.orientdb_helper = BrassOrientDBHelper(
#             database_name=GeneralTestData.database_name,
#             config_file=GeneralTestData.config_file)
#         self.orientdb_helper.open_database(over_write=False)
#         self.new_schedule = [txop1, txop2, txop3, txop4, txop5, txop6]
#         self.schedule = ScheduleModifier(
#             self.orientdb_helper,
#             ScheduleModifierTestData.new_schedule)
#
#     def tearDown(self):
#         self.orientdb_helper.close_database()
#
#     def test_adjust_schedule_passes(self):
#         self.schedule.modify_schedule()
#
#         valid = False
#         i = 0
#         db_txop = self.orientdb_helper.run_query('SELECT FROM TxOp ORDER BY StartUSec asc')
#
#         for txop in db_txop:
#             if self.txop_equals(txop, self.new_schedule[i]):
#                 valid = True
#             else:
#                 valid = False
#                 break
#             i += 1
#
#         self.assertTrue(valid)
#
#     def test_adjust_schedule_fails(self):
#         self.schedule.modify_schedule()
#         txop_timeout = 255
#         center_frequency_hz = 4919500000
#         txop1 = TxOp(StartUSec=0, StopUSec=11500, TxOpTimeout=txop_timeout, CenterFrequencyHz=center_frequency_hz, link_direction='up')
#         txop2 = TxOp(StartUSec=12500, StopUSec=24000, TxOpTimeout=txop_timeout, CenterFrequencyHz=center_frequency_hz, link_direction='down')
#         txop3 = TxOp(StartUSec=25000, StopUSec=48000, TxOpTimeout=txop_timeout, CenterFrequencyHz=center_frequency_hz, link_direction='up')
#         txop4 = TxOp(StartUSec=49000, StopUSec=74000, TxOpTimeout=txop_timeout, CenterFrequencyHz=center_frequency_hz, link_direction='down')
#         txop5 = TxOp(StartUSec=75000, StopUSec=86500, TxOpTimeout=txop_timeout, CenterFrequencyHz=center_frequency_hz, link_direction='up')
#         txop6 = TxOp(StartUSec=87500, StopUSec=100000, TxOpTimeout=txop_timeout, CenterFrequencyHz=center_frequency_hz, link_direction='down')
#
#         new_schedule = [txop1, txop2, txop3, txop4, txop5, txop6]
#
#         valid = False
#         i = 0
#         txop_nodes = self.orientdb_helper.run_query('SELECT FROM TxOp ORDER BY StartUSec asc')
#
#         for txop in txop_nodes:
#             if self.txop_equals(txop, new_schedule[i]):
#                 valid = True
#             else:
#                 valid = False
#                 break
#             i += 1
#
#         self.assertFalse(valid)
#
#     def txop_equals(self, db_txop, txop):
#         return (int(db_txop.StartUSec) == txop.StartUSec
#                 and int(db_txop.StopUSec) == txop.StopUSec
#                 and int(db_txop.TxOpTimeout) == txop.TxOpTimeout
#                 and int(db_txop.CenterFrequencyHz) == txop.CenterFrequencyHz
#                 and self.link_direction_equals(db_txop, txop))
#
#     def link_direction_equals(self, db_txop, txop):
#         radio_links = self.orientdb_helper.get_connected_nodes(targetNode_rid=db_txop._rid, direction='out', filterdepth=1)
#
#         if len(radio_links) is 0:
#             return False
#
#         radio_link = radio_links[0]
#         if radio_link.Name == 'GndRadio_to_TA' and txop.link_direction == 'up':
#             return True
#         elif radio_link.Name == 'TA_to_GndRadio' and txop.link_direction == 'down':
#             return True
#         return False
