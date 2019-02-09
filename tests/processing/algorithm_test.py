import unittest
from cp1.processing.algorithm import Algorithm
from cp1.data_objects.constraints.ta import TA
from cp1.data_objects.mdl.kbps import Kbps
from cp1.data_objects.mdl.mdl_id import MdlId
from cp1.data_objects.mdl.milliseconds import Milliseconds
from cp1.data_objects.mdl.frequency import Frequency
from cp1.data_objects.mdl.txop_timeout import TxOpTimeout
from cp1.data_objects.mdl.txop import TxOp


class AlgorithmTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ta_1 = TA(id_=MdlId('TA1'), minimum_voice_bandwidth=Kbps(25),
                      minimum_safety_bandwidth=Kbps(25), scaling_factor=1,
                      c=0.5, utility_threshold=65)
        cls.ta_2 = TA(id_=MdlId('TA2'), minimum_voice_bandwidth=Kbps(25),
                      minimum_safety_bandwidth=Kbps(15), scaling_factor=1,
                      c=0.5, utility_threshold=55)
        cls.ta_3 = TA(id_=MdlId('TA3'), minimum_voice_bandwidth=Kbps(15),
                      minimum_safety_bandwidth=Kbps(15), scaling_factor=1,
                      c=0.5, utility_threshold=40)
        cls.ta_4 = TA(id_=MdlId('TA4'), minimum_voice_bandwidth=Kbps(10),
                      minimum_safety_bandwidth=Kbps(5), scaling_factor=1,
                      c=0.5, utility_threshold=35)
        cls.ta_5 = TA(id_=MdlId('TA5'), minimum_voice_bandwidth=Kbps(10),
                      minimum_safety_bandwidth=Kbps(5), scaling_factor=1,
                      c=0.5, utility_threshold=35)

        self.channel_1 = Channel(name=MdlId('Channel_1'), frequency=Frequency(4919500000),
                                 timeout=TxOpTimeout(255))


    def test_valid_schedule(self):
        constraints_object = ConstraintsObject(candidate_tas=[self.ta_1,
                                                              self.ta_2,
                                                              self.ta_3,
                                                              self.ta_4,
                                                              self.ta_5],
                                               goal_throughput_bulk=150,
                                               goal_throughput_voice=100,
                                               goal_throughput_safety=100,
                                               latency=Milliseconds(50),
                                               guard_band=Milliseconds(1),
                                               epoch=Milliseconds(100),
                                               channel=self.channel_1)

        algorithm = Algorithm(constraints_object=constraints_object)

        new_schedule = algorithm.optimize()

    #TODO
    def test_empty_constraints(self):
        return

    #TODO
    def test_only_one_ta_fits(self):
        return

    #TODO
    def test_all_tas_fit(self):
        return

    #TODO
    def test_tas_require_0_bandwidth(self):
        return

    #TODO
    def test_no_tas_fit(self):
        return

    #TODO
    def test_latency_not_factor_of_epoch(self):
        return

    #TODO
    def test_latency_equals_epoch(self):
        return

    #TODO
    def test_epoch_less_than_latency(self):
        return

    #TODO
    def test_guard_band_of_0(self):
        return

    #TODO
    def test_guard_band_of_10(self):
        return
