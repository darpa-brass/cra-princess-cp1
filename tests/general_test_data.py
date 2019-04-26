"""

general_test_data.py

This program contains test database connection information, a mock pyorient node class for mocking.

Author: Tameem Samawi (tsamawi@cra.com)

"""
from cra.utils.json_utils import file_to_json


class GeneralTestData:
    test_conf = file_to_json('../../../../../conf/local_db_config.json')
    database_name = test_conf['testing']['database_name']
    config_file = test_conf['testing']['config_file']
    mdl_file = test_conf['testing']['mdl_file_path']


class MockPyOrientNode:
    def __init__(self, _class):
        self._class = _class
