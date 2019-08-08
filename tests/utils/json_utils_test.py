import unittest
import os
from cra.utils.file_utils.json_utils import create_mdl_bandwidth_set, file_to_json
from json_utils_test_data import JsonUtilsTestData
from cra.scenarios.common.constants import Constants
from cra.scenarios.mdl_data.mdl_bandwidth_rate import MDLBandwidthRate
from cra.scenarios.mdl_data.mdl_bandwidth_set import MDLBandwidthSet


class JsonUtilsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_file_name = 'test.json'

    def create_sample_json_file(self):
        self.f = open(self.test_file_name, 'w+')
        self.f.write('''{{
                                "voice": {{
                                            "{0}": "{1}",
                                            "{2}": {3},
                                            "{4}": "{5}",
                                            "{6}": {7}
                                         }},
                                "safety": {{
                                            "{8}": "{9}",
                                            "{10}": {11},
                                            "{12}": "{13}",
                                            "{14}": {15}
                                           }},
                               "bulk": {{
                                            "{16}": "{17}",
                                            "{18}": {19},
                                            "{20}": "{21}",
                                            "{22}": {23}
                                         }},
                                "rfnm": {{
                                            "{24}": "{25}",
                                            "{26}": {27},
                                            "{28}": "{29}",
                                            "{30}": {31}
                                           }}
                                }}'''.format(Constants.radioA_to_radioB_id_key, JsonUtilsTestData.voice_radioA_to_radioB_id,
                                             Constants.radioA_to_radioB_value_key, JsonUtilsTestData.voice_radioA_to_radioB_value,
                                             Constants.radioB_to_radioA_id_key, JsonUtilsTestData.voice_radioB_to_radioA_id,
                                             Constants.radioB_to_radioA_value_key, JsonUtilsTestData.voice_radioB_to_radioA_value,
                                             Constants.radioA_to_radioB_id_key, JsonUtilsTestData.safety_radioA_to_radioB_id,
                                             Constants.radioA_to_radioB_value_key, JsonUtilsTestData.safety_radioA_to_radioB_value,
                                             Constants.radioB_to_radioA_id_key, JsonUtilsTestData.safety_radioB_to_radioA_id,
                                             Constants.radioB_to_radioA_value_key, JsonUtilsTestData.safety_radioB_to_radioA_value,
                                             Constants.radioA_to_radioB_id_key, JsonUtilsTestData.bulk_radioA_to_radioB_id,
                                             Constants.radioA_to_radioB_value_key, JsonUtilsTestData.bulk_radioA_to_radioB_value,
                                             Constants.radioB_to_radioA_id_key, JsonUtilsTestData.bulk_radioB_to_radioA_id,
                                             Constants.radioB_to_radioA_value_key, JsonUtilsTestData.bulk_radioB_to_radioA_value,
                                             Constants.radioA_to_radioB_id_key, JsonUtilsTestData.rfnm_radioA_to_radioB_id,
                                             Constants.radioA_to_radioB_value_key, JsonUtilsTestData.rfnm_radioA_to_radioB_value,
                                             Constants.radioB_to_radioA_id_key, JsonUtilsTestData.rfnm_radioB_to_radioA_id,
                                             Constants.radioB_to_radioA_value_key, JsonUtilsTestData.rfnm_radioB_to_radioA_value))
        self.f.close()

    def setUp(self):
        self.create_sample_json_file()
        self.bandwidth_map = file_to_json(self.test_file_name)

    def tearDown(self):
        os.remove(self.test_file_name)

    def test_file_to_json(self):
        self.assertEqual(JsonUtilsTestData.voice_radioA_to_radioB_id, self.bandwidth_map['voice'][Constants.radioA_to_radioB_id_key])
        self.assertEqual(JsonUtilsTestData.voice_radioA_to_radioB_value, self.bandwidth_map['voice'][Constants.radioA_to_radioB_value_key])
        self.assertEqual(JsonUtilsTestData.voice_radioB_to_radioA_id, self.bandwidth_map['voice'][Constants.radioB_to_radioA_id_key])
        self.assertEqual(JsonUtilsTestData.voice_radioB_to_radioA_value, self.bandwidth_map['voice'][Constants.radioB_to_radioA_value_key])

        self.assertEqual(JsonUtilsTestData.safety_radioA_to_radioB_id, self.bandwidth_map['safety'][Constants.radioA_to_radioB_id_key])
        self.assertEqual(JsonUtilsTestData.safety_radioA_to_radioB_value, self.bandwidth_map['safety'][Constants.radioA_to_radioB_value_key])
        self.assertEqual(JsonUtilsTestData.safety_radioB_to_radioA_id, self.bandwidth_map['safety'][Constants.radioB_to_radioA_id_key])
        self.assertEqual(JsonUtilsTestData.safety_radioB_to_radioA_value, self.bandwidth_map['safety'][Constants.radioB_to_radioA_value_key])

        self.assertEqual(JsonUtilsTestData.bulk_radioA_to_radioB_id, self.bandwidth_map['bulk'][Constants.radioA_to_radioB_id_key])
        self.assertEqual(JsonUtilsTestData.bulk_radioA_to_radioB_value, self.bandwidth_map['bulk'][Constants.radioA_to_radioB_value_key])
        self.assertEqual(JsonUtilsTestData.bulk_radioB_to_radioA_id, self.bandwidth_map['bulk'][Constants.radioB_to_radioA_id_key])
        self.assertEqual(JsonUtilsTestData.bulk_radioB_to_radioA_value, self.bandwidth_map['bulk'][Constants.radioB_to_radioA_value_key])
    
        self.assertEqual(JsonUtilsTestData.rfnm_radioA_to_radioB_id, self.bandwidth_map['rfnm'][Constants.radioA_to_radioB_id_key])
        self.assertEqual(JsonUtilsTestData.rfnm_radioA_to_radioB_value, self.bandwidth_map['rfnm'][Constants.radioA_to_radioB_value_key])
        self.assertEqual(JsonUtilsTestData.rfnm_radioB_to_radioA_id, self.bandwidth_map['rfnm'][Constants.radioB_to_radioA_id_key])
        self.assertEqual(JsonUtilsTestData.rfnm_radioB_to_radioA_value, self.bandwidth_map['rfnm'][Constants.radioB_to_radioA_value_key])

    def test_mdl_bandwidth_value_keys(self):
        key_match = False
        i = 0

        for key in self.bandwidth_map.keys():
            if Constants.mdl_bandwidth_types [i] == key:
                key_match = True
                i += 1
            else:
                key_match = False
                break

        self.assertTrue(key_match)

    def test_create_mdl_bandwidth_set(self):
        actual = create_mdl_bandwidth_set(self.bandwidth_map)

        voice = MDLBandwidthRate(JsonUtilsTestData.voice_radioA_to_radioB_id, JsonUtilsTestData.voice_radioA_to_radioB_value,
                                 JsonUtilsTestData.voice_radioB_to_radioA_id, JsonUtilsTestData.voice_radioB_to_radioA_value)
        safety = MDLBandwidthRate(JsonUtilsTestData.safety_radioA_to_radioB_id, JsonUtilsTestData.safety_radioA_to_radioB_value,
                                 JsonUtilsTestData.safety_radioB_to_radioA_id, JsonUtilsTestData.safety_radioB_to_radioA_value)
        bulk = MDLBandwidthRate(JsonUtilsTestData.bulk_radioA_to_radioB_id, JsonUtilsTestData.bulk_radioA_to_radioB_value,
                                 JsonUtilsTestData.bulk_radioB_to_radioA_id, JsonUtilsTestData.bulk_radioB_to_radioA_value)
        rfnm = MDLBandwidthRate(JsonUtilsTestData.rfnm_radioA_to_radioB_id, JsonUtilsTestData.rfnm_radioA_to_radioB_value,
                                 JsonUtilsTestData.rfnm_radioB_to_radioA_id, JsonUtilsTestData.rfnm_radioB_to_radioA_value)
        expected = MDLBandwidthSet(voice, safety, bulk, rfnm)

        self.assertEqual(expected.voice.radioA_to_radioB_id, actual.voice.radioA_to_radioB_id)
        self.assertEqual(expected.voice.radioA_to_radioB_value, actual.voice.radioA_to_radioB_value)
        self.assertEqual(expected.voice.radioB_to_radioA_id, actual.voice.radioB_to_radioA_id)
        self.assertEqual(expected.voice.radioB_to_radioA_value, actual.voice.radioB_to_radioA_value)

        self.assertEqual(expected.safety.radioA_to_radioB_id, actual.safety.radioA_to_radioB_id)
        self.assertEqual(expected.safety.radioA_to_radioB_value, actual.safety.radioA_to_radioB_value)
        self.assertEqual(expected.safety.radioB_to_radioA_id, actual.safety.radioB_to_radioA_id)
        self.assertEqual(expected.safety.radioB_to_radioA_value, actual.safety.radioB_to_radioA_value)

        self.assertEqual(expected.bulk.radioA_to_radioB_id, actual.bulk.radioA_to_radioB_id)
        self.assertEqual(expected.bulk.radioA_to_radioB_value, actual.bulk.radioA_to_radioB_value)
        self.assertEqual(expected.bulk.radioB_to_radioA_id, actual.bulk.radioB_to_radioA_id)
        self.assertEqual(expected.bulk.radioB_to_radioA_value, actual.bulk.radioB_to_radioA_value)

        self.assertEqual(expected.rfnm.radioA_to_radioB_id, actual.rfnm.radioA_to_radioB_id)
        self.assertEqual(expected.rfnm.radioA_to_radioB_value, actual.rfnm.radioA_to_radioB_value)
        self.assertEqual(expected.rfnm.radioB_to_radioA_id, actual.rfnm.radioB_to_radioA_id)
        self.assertEqual(expected.rfnm.radioB_to_radioA_value, actual.rfnm.radioB_to_radioA_value)

