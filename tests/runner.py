import unittest

# import test module
import scenarios.optimization.optimization_result_test

# initialize the test suite
loader = unittest.TestLoader()
suite = unittest.TestSuite()

# add tests to the suite
suite.addTests(loader.loadTestsFromModule(optimization_result_test))


# initialize and execute a runner
runner = unittest.TextTestRunner(verbosity=3)
result = runner.run(suite)