"""bandwidth_processor.py

Generates new bandwidth rates based on available bandwidth and ratio of bandwidth going up
and bandwidth going down for each of the four types of bandwidth: voice, safety, bulk and RFNM.
Output of this class is used to update the Rate children ServiceLevelProfile elements of MDL files,
which is where bandwidth allocation is specified.
A file containing ServiceLevelProfile IDs can be found under cp1/conf/mdl_ids.json. Below are the SLP identifiers provided by SwRI::
    voice: SLP_1_20
    safety: SLP_1_301
    bulk: SLP_1_40
    RFNM: SLP_1_10

i.e. constraints_object.goal_throughput_bulk = Kbps(75), up_ratio = 0.25
In this case, the output of :func:`ProcessBandwidth.process() <cp1.processing.process_bandwidth.process>` should be used in conjunction with
:func:`OrientDBStorage.update_bandwidth <cp1.utils.OrientDBStorage.update_bandwidth` to edit the following MDL elements::
     <ServiceLevelProfile ID = TA1_to_GndGrp1_SLP_1_40>
        .
            .
                .
                <Rate>56250</Rate>
                .
            .
        .
     </ServiceLevelProfile>
     <ServiceLevelProfile ID = GR1_to_TA1_SLP_1_40>
          .
              .
                  .
                  <Rate>18750</Rate>
                  .
              .
          .
     </ServiceLevelProfile>

Author: Tameem Samawi (tsamawi@cra.com)
"""
from cp1.data_objects.processing.schedule import Schedule
from cp1.data_objects.mdl.microseconds import Microseconds
from cp1.data_objects.mdl.kbps import Kbps
from cp1.data_objects.processing.constraints_object import ConstraintsObject
import os
import json


class BandwidthProcessor:
    def __init__(self, constraints_object, bandwidth_file, up_ratio):
        """
        Constructor

        :param ConstraintsObject constraints_object: The set of constraints on the schedule including the list of candidate TAs,
                                   available frequencies and new amount of available bandwidth
        :param str bandwidth_file: The path to the bandwidth ids file
        :param int up_ratio: The percentage of bandwidth that should be allocated to Ground to TA. Leftover bandwidth
                         is allocated to TA to Ground
        """
        self.constraints_object = constraints_object
        self.bandwidth_file = bandwidth_file
        self.up_ratio = up_ratio
        self.down_ratio = 1 - up_ratio

        self.process()

    def process(self):
        # Create these values in a loop
        """
        Creates a dictionary of bandwidth keys/values based on TAs.
        The keys in this dictionary represent MDL ServiveLevelProfile (SLP) IDs, which
        are the elements that contain information on transmission rates for each
        of the four types of communication: safety, voice, bulk and RFNM
        The values in this dictionary are ints representing the bit per second rates for a specific
        transmission type and direction.
        i.e. {'TA1_to_GndGrp1_SLP_1_20': 75000} indicates that of the total available bandwidth from
        TA1 to Ground, 75000 bits per second of that bandwidth should be allocated to voice radio
        communications.

        The rate of a specific bandwidth value is determined by the ratio of bandwidth allocated to
        Ground to TA (up_ratio) and TA to Ground (down_ratio) communications.

        The ServiveLevelProfile element in an MDL file is identifiable by the constants provided in
        the bandwidth_file. For each of these constants we need to append information on which TA
        and which Ground station are communicating to one another for the IDs to be valid.
        i.e. TA1_to_GndGrp1_SLP_1_301 represents the bandwidth transmission rate for all safety radio
        communications from TA1 to Ground.

        :returns dict<str, int> schedule:
        """
        new_rates = []

        voice_up = int(
            self.constraints_object.goal_throughput_voice.rate.to_bits_per_second() * self.up_ratio)
        voice_down = int(
            self.constraints_object.goal_throughput_voice.rate.to_bits_per_second() * self.down_ratio)

        safety_up = int(
            self.constraints_object.goal_throughput_safety.rate.to_bits_per_second() * self.up_ratio)
        safety_down = int(
            self.constraints_object.goal_throughput_safety.rate.to_bits_per_second() * self.down_ratio)

        bulk_up = int(
            self.constraints_object.goal_throughput_bulk.rate.to_bits_per_second() * self.up_ratio)
        bulk_down = int(
            self.constraints_object.goal_throughput_bulk.rate.to_bits_per_second() * self.down_ratio)

        data_file = open(self.bandwidth_file, 'r')
        configMap = json.load(data_file)

        ground_from = configMap['Ground ID']['from']
        ground_to = configMap['Ground ID']['to']
        voice = configMap['Transmission ServiceLevelProfile IDs']['voice']
        safety = configMap['Transmission ServiceLevelProfile IDs']['safety']
        bulk = configMap['Transmission ServiceLevelProfile IDs']['bulk']

        data_file.close()

        voice_up = ground_from + '_to_' + ta.id + '_' + voice
        voice_down = ta.id + '_to_' + ground_to + '_' + voice

        safety_up = ground_from + '_to_' + ta.id + '_' + safety
        safety_down = ta.id + '_to_' + ground_to + '_' + safety

        bulk_up = ground_from + '_to_' + ta.id + '_' + bulk
        bulk_down = ta.id + '_to_' + ground_to + '_' + bulk

        for ta in self.constraints_object.candidate_tas:
            slp_ids = self.generate_slp_id(ta)

            new_rates.append(
                (slp_ids.get('voice_up'), rate_values.get('voice_up')))
            new_rates.append((slp_ids.get('voice_down'),
                              rate_values.get('voice_down')))

            new_rates.append(
                (slp_ids.get('safety_up'), rate_values.get('safety_up')))
            new_rates.append((slp_ids.get('safety_down'),
                              rate_values.get('safety_down')))

            new_rates.append(
                (slp_ids.get('bulk_up'), rate_values.get('bulk_up')))
            new_rates.append(
                (slp_ids.get('bulk_down'), rate_values.get('bulk_down')))
