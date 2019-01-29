"""

mdl_id_test.py

Module to test mdl_id.py
Author: Tameem Samawi (tsamawi@cra.com)
"""


import unittest
from cp1.data_objects.mdl.mdl_id import MdlId
from cp1.data_objects.mdl.id_set import IdSet
from cp1.common.exception_class import MdlIdInitializationError


class MdlIdTest(unittest.TestCase):
    def setUp(self):
        IdSet().ids.clear()

    def test_valid_id(self):
        id_ = 'Channel 1'
        mdl_id = MdlId(id_)

        self.assertEqual(id_, mdl_id.value)

    def test_invalid_id_type(self):
        self.assertRaises(MdlIdInitializationError, MdlId, 1)

    def test_invalid_id_duplicate(self):
        id_ = 'Channel 1'
        mdl_id = MdlId(id_)

        self.assertRaises(MdlIdInitializationError, MdlId, id_)
