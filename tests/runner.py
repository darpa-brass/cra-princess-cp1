import unittest

# Discover and run tests
suite = unittest.TestLoader().discover('.', '*_test.py')
unittest.TextTestRunner(verbosity=3).run(suite)
