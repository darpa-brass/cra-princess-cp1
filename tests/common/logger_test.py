import unittest
from cra.utils.logger import Logger


class LoggerTest(unittest.TestCase):
    def test_is_singleton(self):
        log1 = Logger()
        log2 = Logger()

        self.assertEqual(log1, log2)
