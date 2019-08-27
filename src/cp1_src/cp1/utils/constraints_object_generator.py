"""constraints_object_generator.py

Generates ConstraintsObjects based on config file parameters.
Author: Tameem Samawi (tsamawi@cra.com)
"""
import json
import numpy
import random

from cp1.utils.decorators.timedelta import timedelta

from cp1.data_objects.processing.constraints_object import ConstraintsObject
from cp1.data_objects.processing.channel import Channel
from cp1.data_objects.processing.ta import TA
from cp1.data_objects.mdl.frequency import Frequency
from cp1.data_objects.mdl.kbps import Kbps
from cp1.data_objects.mdl.txop_timeout import TxOpTimeout
from cp1.data_objects.processing.prf import PRF


class ConstraintsObjectGenerator():
    @staticmethod
    def generate(config):
        """Generates a ConstraintsObject within the parameters specified by a ConfigurationObject

        :param ConfigurationObject config: The Configuration for an instance of a challenge problem
        :returns ConstraintsObject:
        """
        constraints_object_list = []

        if config.testing == 1:
            channel_list = []
            for i in range(config.testing_num_channels):
                channel = Channel(frequency=Frequency(4919500000 + i*100000),
                                    capacity=Kbps(config.testing_channel_capacity))
                channel_list.append(channel)

            ta_list = []
            for i in range(config.testing_num_tas):
                eligible_frequency_list = []
                for j in range(config.testing_eligible_frequencies[i]):
                    eligible_frequency_list.append(channel_list[j].frequency)

                ta = TA(id_='TA{0}'.format(i),
                minimum_voice_bandwidth=Kbps(int(config.testing_total_min_bw[i])/2),
                minimum_safety_bandwidth=Kbps(int(config.testing_total_min_bw[i])/2),
                latency=timedelta(microseconds=1000*int(config.testing_latency[i])),
                scaling_factor=config.testing_scaling_factor[i],
                c=config.testing_c[i],
                eligible_frequencies=eligible_frequency_list)

                ta_list.append(ta)

            testing_constraints_object = ConstraintsObject(
                        id_='TestingConstraintsObject',
                        candidate_tas=ta_list,
                        channels=channel_list,
                        seed='timestamp',
                        goal_throughput_bulk=config.goal_throughput_bulk,
                        goal_throughput_voice=config.goal_throughput_voice,
                        goal_throughput_safety=config.goal_throughput_safety,
                        guard_band=timedelta(microseconds=1000*int(config.guard_band)),
                        epoch=timedelta(microseconds=1000*int(config.epoch)),
                        txop_timeout=TxOpTimeout(config.txop_timeout))

            constraints_object_list.append(testing_constraints_object)

        else:
            seed = 'timestamp'
            for x in range(1, config.instances[0] + 1):
                if len(config.instances) == 2:
                    seed = config.instances[1] + x
                    numpy.random.seed(seed)
                    random.seed(seed)

                channels = ConstraintsObjectGenerator._generate_channels(config)
                candidate_tas = ConstraintsObjectGenerator._generate_tas(config, channels)

                constraints_object = ConstraintsObject(id_ = 'ConstraintsObject{0}'.format(x+1),
                candidate_tas=candidate_tas,
                channels=channels,
                seed=seed,
                goal_throughput_bulk=Kbps(config.goal_throughput_bulk),
                goal_throughput_voice=Kbps(config.goal_throughput_voice),
                goal_throughput_safety=Kbps(config.goal_throughput_safety),
                guard_band=timedelta(microseconds=1000*int(config.guard_band)),
                epoch=timedelta(microseconds=1000*int(config.epoch)),
                txop_timeout=TxOpTimeout(config.txop_timeout)
                )

                constraints_object_list.append(constraints_object)

        return constraints_object_list

    @staticmethod
    def _generate_channels(config):
        """Generates a set amount of Channels in the range of data provided by data_file.

        :param ConfigurationObject config: The Configuration for an instance of a challenge problem
        :returns [<Channel>] channels: A list of channels generated from config
        """
        channels = []
        for i in range(0, config.num_channels):
            base_frequency = config.frequency[0]
            frequency_incrementation = config.frequency[1]
            capacity = PRF(config.capacity)
            channels.append(Channel(
                frequency=Frequency(base_frequency +
                                    (i * frequency_incrementation)),
                capacity=Kbps(capacity.evaluate())))
        return channels

    @staticmethod
    def _generate_tas(config, channels):
        """Generates a set amount of TAs in the range of data provided by parameters.
        TA IDs start at 1
        Note that eligible frequencies is a list of Kbps values

        :param ConfigurationObject config: The Configuration for an instance of a challenge problem
        :returns [<TA>] tas: A list of TAs generated from config
        """
        tas = []
        for x in range(config.num_tas):
            safety = PRF(config.safety)
            voice = PRF(config.voice)
            latency = PRF(config.latency)
            scaling_factor = PRF(config.scaling_factor)
            c = PRF(config.c)
            eligible_frequencies = PRF(config.eligible_frequencies)

            tas.append(TA(
                id_='TA{0}'.format(x + 1),
                minimum_voice_bandwidth=Kbps(voice.evaluate()),
                minimum_safety_bandwidth=Kbps(safety.evaluate()),
                latency=timedelta(microseconds=1000*int(latency.evaluate())),
                scaling_factor=scaling_factor.evaluate(),
                c=c.evaluate(),
                eligible_frequencies = list(map(lambda x: x.frequency, random.sample(channels, eligible_frequencies.evaluate())))))
        return tas
