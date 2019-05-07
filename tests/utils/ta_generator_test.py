import unittest
from cp1.utils.ta_generator import TAGenerator
from cp1.data_objects.mdl.kbps import Kbps
from cp1.data_objects.mdl.id_set import IdSet
from cp1.common.exception_class import TAGeneratorRangeException
from cp1.common.exception_class import TAGeneratorInitializationException


class TAGeneratorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out_of_bounds_upper_voice = 201
        cls.out_of_bounds_upper_safety = 101
        cls.out_of_bounds_lower_scaling_factor = -1
        cls.out_of_bounds_upper_scaling_factor = 11
        cls.out_of_bounds_lower_c = -1
        cls.out_of_bounds_upper_c = 1.1
        cls.out_of_bounds_lower_min_value = -1
        cls.out_of_bounds_upper_min_value = 101

    def setUp(self):
        id_set = IdSet()
        id_set.ids.clear()

    def test_generates_correct_amount_of_tas(self):
        generator = TAGenerator(lower_minimum_voice_bandwidth=Kbps(20),
                                upper_minimum_voice_bandwidth=Kbps(100),
                                lower_minimum_safety_bandwidth=Kbps(5),
                                upper_minimum_safety_bandwidth=Kbps(50),
                                lower_scaling_factor=1,
                                upper_scaling_factor=5,
                                lower_c=0.03,
                                upper_c=0.08,
                                lower_min_value=30,
                                upper_min_value=70)
        num_tas = 100
        ta_list = generator.generate(num_tas)

        self.assertEqual(len(ta_list), num_tas)

    def test_out_of_bounds_upper_minimum_voice(self):
        self.assertRaises(TAGeneratorRangeException, TAGenerator, Kbps(0), Kbps(self.out_of_bounds_upper_voice),
                          Kbps(0), Kbps(50), 1, 2, 3, 4, 5, 6)

    def test_out_of_bounds_upper_minimum_safety(self):
        self.assertRaises(TAGeneratorRangeException, TAGenerator, Kbps(0), Kbps(1),
                          Kbps(0), Kbps(self.out_of_bounds_upper_safety), 1, 2, 3, 4, 5, 6)

    def test_out_of_bounds_lower_scaling_factor(self):
        self.assertRaises(TAGeneratorRangeException, TAGenerator, Kbps(0), Kbps(1),
                          Kbps(0), Kbps(50), self.out_of_bounds_lower_scaling_factor, 2, 3, 4, 5, 6)

    def test_out_of_bounds_upper_scaling_factor(self):
        self.assertRaises(TAGeneratorRangeException, TAGenerator, Kbps(0), Kbps(1),
                          Kbps(0), Kbps(50), 1, self.out_of_bounds_upper_scaling_factor, 3, 4, 5, 6)

    def test_out_of_bounds_lower_c(self):
        self.assertRaises(TAGeneratorRangeException, TAGenerator, Kbps(0), Kbps(1),
                          Kbps(0), Kbps(50), 1, 2, self.out_of_bounds_lower_c, 4, 5, 6)

    def test_out_of_bounds_upper_c(self):
        self.assertRaises(TAGeneratorRangeException, TAGenerator, Kbps(0), Kbps(1),
                          Kbps(0), Kbps(50), 1, 2, 3, self.out_of_bounds_upper_c, 5, 6)

    def test_out_of_bounds_lower_min_value(self):
        self.assertRaises(TAGeneratorRangeException, TAGenerator, Kbps(0), Kbps(1),
                          Kbps(0), Kbps(50), 1, 2, 3, 4, self.out_of_bounds_lower_min_value, 6)

    def test_out_of_bounds_upper_min_value(self):
        self.assertRaises(TAGeneratorRangeException, TAGenerator, Kbps(0), Kbps(1),
                          Kbps(0), Kbps(50), 1, 2, 3, 4, 5, self.out_of_bounds_upper_min_value)

    def test_upper_minimum_voice_bandwidth_incorrect_type(self):
        self.assertRaises(TAGeneratorInitializationException, TAGenerator, Kbps(0), 'foo',
                          Kbps(0), Kbps(50), 1, 2, 3, 4, 5, 6)

    def test_lower_minimum_safety_bandwidth_incorrect_type(self):
        self.assertRaises(TAGeneratorInitializationException, TAGenerator, Kbps(0), Kbps(1),
                          'foo', Kbps(50), 1, 2, 3, 4, 5, 6)

    def test_upper_minimum_safety_bandwidth_incorrect_type(self):
        self.assertRaises(TAGeneratorInitializationException, TAGenerator, Kbps(0), Kbps(1),
                          Kbps(0), 'foo', 1, 2, 3, 4, 5, 6)

    def test_lower_scaling_factor_incorrect_type(self):
        self.assertRaises(TAGeneratorInitializationException, TAGenerator, Kbps(0), Kbps(1),
                          Kbps(0), Kbps(50), 'foo', 2, 3, 4, 5, 6)

    def test_upper_scaling_factor_incorrect_type(self):
        self.assertRaises(TAGeneratorInitializationException, TAGenerator, Kbps(0), Kbps(1),
                          Kbps(0), Kbps(50), 1, 'foo', 3, 4, 5, 6)

    def test_lower_c_incorrect_type(self):
        self.assertRaises(TAGeneratorInitializationException, TAGenerator, Kbps(0), Kbps(1),
                          Kbps(0), Kbps(50), 1, 2, 'foo', 4, 5, 6)

    def test_upper_c_incorrect_type(self):
        self.assertRaises(TAGeneratorInitializationException, TAGenerator, Kbps(0), Kbps(1),
                          Kbps(0), Kbps(50), 1, 2, 3, 'foo', 5, 6)

    def test_lower_min_value_incorrect_type(self):
        self.assertRaises(TAGeneratorInitializationException, TAGenerator, Kbps(0), Kbps(1),
                          Kbps(0), Kbps(50), 1, 2, 3, 4, 'foo', 6)

    def test_upper_min_value_incorrect_type(self):
        self.assertRaises(TAGeneratorInitializationException, TAGenerator, Kbps(0), Kbps(1),
                          Kbps(0), Kbps(50), 1, 2, 3, 4, 5, 'foo')
