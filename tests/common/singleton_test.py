import unittest
from cra.utils.singleton import Singleton


class MyClass(metaclass=Singleton):
    def __init__(self, x):
        self.x = x


class SingletonTest(unittest.TestCase):
    def test_singletons_are_equal(self):
        foo_1 = MyClass(10)
        foo_2 = MyClass(20)

        self.assertEqual(foo_1.x, foo_2.x)
