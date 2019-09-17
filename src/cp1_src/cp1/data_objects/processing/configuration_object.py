"""configuration_object.py

Class to process all configuration settings for a Challenge Problem instance
Author: Tameem Samawi (tsamawi@cra.com)
"""
from cp1.common.exception_class import ConfigFileException
from cp1.utils.decorators.timedelta import timedelta
import json


class ConfigurationObject:
    def __init__(self, config_file):
        """Constructor
        Extracts data from config_file and validates format

        :raises ConfigFileException:
        """
        with open(config_file, 'r') as f:
            data = json.load(f)

            try:
                self.num_tas = data['Constraints']['candidate_tas']['num']
                self.eligible_frequencies = data['Constraints']['candidate_tas']['eligible_frequencies']
                self.voice = data['Constraints']['candidate_tas']['voice_bandwidth']
                self.safety = data['Constraints']['candidate_tas']['safety_bandwidth']
                self.latency = data['Constraints']['candidate_tas']['latency']
                self.scaling_factor = data['Constraints']['candidate_tas']['scaling_factor']
                self.c = data['Constraints']['candidate_tas']['c']

                self.testing_num_tas = data['Testing']['TAs']['num']
                self.testing_eligible_frequencies = data['Testing']['TAs']['eligible_frequencies']
                self.testing_total_min_bw = data['Testing']['TAs']['total_min_bw']
                self.testing_latency = data['Testing']['TAs']['latency']
                self.testing_scaling_factor = data['Testing']['TAs']['scaling_factor']
                self.testing_c = data['Testing']['TAs']['c']

                self.testing_num_channels = data['Testing']['Channels']['num']
                self.testing_channel_capacity = data['Testing']['Channels']['capacity']
                self.testing_seed = data['Testing']['Seed']

                self.num_channels = data['Constraints']['channels']['num']
                self.frequency = data['Constraints']['channels']['frequency']
                self.capacity = data['Constraints']['channels']['capacity']

                self.guard_band = data['Constraints']['guard_band']
                self.epoch = data['Constraints']['epoch']
                self.txop_timeout = data['Constraints']['txop_timeout']
                self.goal_throughput_bulk = data['Constraints']['goal_throughput_bulk']
                self.goal_throughput_voice = data['Constraints']['goal_throughput_voice']
                self.goal_throughput_safety = data['Constraints']['goal_throughput_safety']

                self.accuracy_epsilons = data['Algorithms']['Discretizers']['Accuracy']['epsilons']
                self.bandwidth_discs = data['Algorithms']['Discretizers']['Bandwidth']['discs']
                self.value_discs = data['Algorithms']['Discretizers']['Value']['discs']

                self.cbc = data['Algorithms']['Optimizers']['CBC']
                self.gurobi = data['Algorithms']['Optimizers']['Gurobi']
                self.greedy = data['Algorithms']['Optimizers']['Greedy']
                self.dynamic = data['Algorithms']['Optimizers']['Dynamic']

                self.conservative = data['Algorithms']['Schedulers']['Conservative']
                self.hybrid = data['Algorithms']['Schedulers']['Hybrid']

                self.perturb = data['Perturbations']['perturb']
                self.num_tas_to_reconsider = data['Perturbations']['num_tas_to_reconsider']
                self.increase_ta_min_bw = data['Perturbations']['increase_ta_min_bw']
                self.drop_channel = data['Perturbations']['drop_channel']
                self.change_channel_capacity = data['Perturbations']['change_channel_capacity']

                self.testing = data['Miscellaneous']['testing']
                self.orientdb = data['Miscellaneous']['orientdb']
                self.clear = data['Miscellaneous']['clear']
                self.visualize = data['Miscellaneous']['visualize']
                self.instances = data ['Miscellaneous']['instances']

            except Exception as ex:
                raise ConfigFileException(ex, 'ConfigurationObject.__init__')

            self.validate()

    def validate(self):
        """Runs a set of private validation methods on the configuration object to
           ensure that the configurations file passed in is valid.

        :raises ConfigFileException:
        """
        self._validate_num('num_tas', self.num_tas)
        self._validate_distribution_schema('eligible_frequencies', self.eligible_frequencies)
        self._validate_eligible_frequencies()
        self._validate_distribution_schema('voice_bandwidth', self.voice)
        self._validate_distribution_schema('safety_bandwidth', self.safety)
        self._validate_distribution_schema('latency', self.latency)
        self._validate_distribution_schema('scaling_factor', self.scaling_factor)
        self._validate_distribution_schema('c', self.c)

        self._validate_num('num_channels', self.num_channels)
        self._validate_base_freq()
        self._validate_distribution_schema('capacity', self.capacity)

        self._validate_discs('bandwidth_discs', self.bandwidth_discs)
        self._validate_discs('value_discs', self.value_discs)
        self._validate_accuracy_discs('accuracy_epsilons', self.accuracy_epsilons)

        self._validate_01_field('CBC', self.cbc)
        self._validate_01_field('Gurobi', self.gurobi)
        self._validate_01_field('Greedy', self.greedy)
        self._validate_01_field('Dynamic', self.dynamic)

        self._validate_01_field('Conservative', self.conservative)
        self._validate_01_field('Hybrid', self.hybrid)

        self._validate_01_field('orientdb', self.orientdb)
        self._validate_01_field('clear', self.clear)
        self._validate_01_field('visualize', self.visualize)
        self._validate_visualize()
        self._validate_instances()

    def _validate_distribution_schema(self, prop, val):
        """Validates the format of a PRF object as read in from a json file.

        :raises ConfigFileException:
        """
        for x in val:
            if len(x) != 2:
                raise ConfigFileException(
                    'The format of each field must be [int/float, [int/float(, int/float)]] where paranthesized values are optional.'.format(
                        prop,
                        x[1]),
                    'ConfigurationObject._validate_distribution_schema')
            elif not 1 <= len(x[1]) <= 2:
                raise ConfigFileException(
                    '{0} ({1}) distribution must contain 1 or 2 values.'.format(
                        prop,
                        x[1]),
                    'ConfigurationObject._validate_distribution_schema')
            elif not isinstance(x[0], (int, float)) or not all(isinstance(y, (int, float)) for y in x[1]):
                raise ConfigFileException(
                    '{0} ({1}) distribution and percentage must only contain ints or floats.'.format(
                        prop,
                        x),
                    'ConfigurationObject._validate_distribution_schema')
            elif x[0] < 0:
                raise ConfigFileException(
                    '{0} ({1}) percentage must be >= 0.'.format(
                        prop,
                        x[0]),
                    'ConfigurationObject._validate_distribution_schema')
            elif not all(y >= 0 for y in x[1]):
                raise ConfigFileException(
                    '{0} ({1}) distribution must contain values >= 0.'.format(
                        prop,
                        x[1]),
                    'ConfigurationObject._validate_distribution_schema')

    def _validate_accuracy_discs(self, prop, val):
        """Validates that the set of floats passed in the accuracy discretization
        field of the config file are all between 0 and 1.

        :param str prop: The property name, i.e. accuracy_epsilons
        :param [int] val: The array of epsilon values
        """
        if not all(isinstance(x, (int, float)) for x in val):
            raise ConfigFileException(
                    '{0}:{1} must be an array of ints'.format(
                    prop, val),
                    'ConfigurationObject._validate_accuracy_discs'
                    )
        for x in val:
            if x < 0 or x >= 1:
                raise ConfigFileException(
                    '{0}:{1} must contain values in the range (0, 1]'.format(
                    prop, val)
                    )

    def _validate_discs(self, prop, val):
        """Validates the discretization values passed into the Bandwidth and Value
           discretization fields.

        :param str prop: The name of the property, i.e. bandwidth_discs
        :param [int] val: The value of this field
        :raises ConfigFileException:
        """
        if not all(isinstance(x, int) for x in val):
            raise ConfigFileException(
                    '{0}:{1} must be an array of ints'.format(
                    prop, val),
                    'ConfigurationObject._validate_discs'
                    )

        for x in val:
            if x < 0:
                raise ConfigFileException(
                        '{0}:{1} must only contain positive ints'.format(
                        prop, val),
                        'ConfigurationObject._validate_discs'
                        )

    def _validate_01_field(self, prop, val):
        """Validates that any field which should contain a 1 or 0 does indeed.

        :param str prop: The name of the property, i.e. Dynamic
        :param str val: The value of this field
        :raises ConfigFileException:
        """
        if not isinstance(val, int) or val not in [0, 1]:
            raise ConfigFileException(
                    '{0}:{1} must have a value of 0 or 1'.format(
                    prop, val),
                    'ConfigurationObject._validate_01_field'
                    )

    def _validate_instances(self):
        """Validates that the instances field is properly formatted

        :raises ConfigFileException:
        """
        if not all(isinstance(x, int) for x in self.instances):
            raise ConfigFileException(
                    'instances must be a list of ints: {0}'.format(
                    self.instances),
                    'ConfigurationObject._validate_instances'
                        )
        if len(self.instances) > 2:
            raise ConfigFileException(
                    'instances must not have more than 2 values: {0}'.format(
                        self.instances),
                    'ConfigurationObject._validate_instances')
        if self.instances[0] < 0:
            raise ConfigFileException(
                    'instances first entry must be positive: {0}'.format(
                    self.instances),
                    'ConfigurationObject._validate_instances'
                    )

    def _validate_num(self, prop, val):
        """Validates that the number of objects to generate is correctly formatted.

        prop begin with `num_`
        val be an int

        :raises InvalidNumToGenerateException:
        """
        if prop[:4] != 'num_':
            raise ConfigFileException(
                '{0} must start with \'num_\''.format(
                    prop),
                'ConfigurationObject._validate_num')
        if not isinstance(val, int):
            raise ConfigFileException(
                '{0} ({1}) must be an int'.format(
                    prop,
                    val),
                'ConfigurationObject._validate_num')

        if val < 1:
            raise ConfigFileException(
                '{0} ({1}) must be >= 1'.format(
                    prop,
                    val),
                'ConfigurationObject._validate_num')

    def _validate_visualize(self):
        """Sets visualize to 0 if orientdb is 0
        """
        if self.orientdb == 0:
            self.visualize = 0

    def _validate_seeds(self, seeds):
        """Validates that the seeds field is correctly formatted.

        Examples:
            ['timestamp', 4]
                4 randomly seeded ConstraintsObjects
            [0, 10]
                10 ConstraintsObjects seeded from 0 to 10 inclusive

        :param [int|str, int] seeds: The seeds to use for the random number
        """
        if not seeds == "timestamp":
            if not len(seeds[1]) == 2:
                raise ConfigFileException(
                    'seeds ({0}) distribution must contain 2 ints'.format(
                        seeds),
                    'ConfigurationObject._validate_seeds')
            elif not all(isinstance(x, int) for x in seeds):
                raise ConfigFileException(
                    'seeds ({0}) distribution must be of type int'.format(
                        seeds),
                    'ConfigurationObject._validate_seeds')

    def _validate_base_freq(self):
        """Validates that the base frequency is not < 0 and frequency incrementation is an int
        :raises ConfigFileException:
        """
        if not isinstance(self.frequency[0], int) or self.frequency[0] < 0:
            raise ConfigFileException(
                'Base Frequency ({0}) must be an int greater than 0'.format(self.frequency[0]),
                'ConfigurationObject._validate_base_freq')
        if not isinstance(self.frequency[1], int):
            raise ConfigFileException(
                'Frequency increment ({0}) must be an int'.format(self.frequency[1]),
                'ConfigurationObject._validate_base_freq')

    def _validate_eligible_frequencies(self):
        """Validates that the number of eligible channels does not exceed num channels
        """
        for eligible_channel in self.eligible_frequencies:
            eligible_channel_list = eligible_channel[1]
            for num in eligible_channel_list:
                if num > self.num_channels:
                    raise ConfigFileException('There cannot be more eligible_frequencies ({0}) than total channels ({1})'.format(num, self.num_channels))
