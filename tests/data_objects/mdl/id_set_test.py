"""
id_set_test.py

Module to test id_set
Author: Tameem Samawi (tsamawi@cra.com)
"""
import unittest
from cp1.data_objects.mdl.id_set import IdSet


class IdSetTest(unittest.TestCase):
    def test_is_same_instance(self):
        set1 = IdSet()
        set2 = IdSet()

        self.assertTrue(set1 is set2)

    def test_adds_to_both_instances(self):
        set1 = IdSet()
        set2 = IdSet()
        set1.ids.add('foo')

        self.assertTrue('foo' in set2.ids)
