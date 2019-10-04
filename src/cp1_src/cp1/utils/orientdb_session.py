"""orientdb_session.py

Any helper functions that store data in OrientDB.
Author: Tameem Samawi (tsamawi@cra.com)
"""
import re
import sys
from functools import reduce
from collections import defaultdict
from cp1.utils.decorators.timedelta import timedelta

from brass_api.orientdb.orientdb_helper import BrassOrientDBHelper
from brass_api.common.exception_class import BrassException
import brass_api.orientdb.orientdb_sql as sql

from cp1.data_objects.constants.constants import *
from cp1.data_objects.mdl.kbps import Kbps
from cp1.data_objects.mdl.txop import TxOpTimeout
from cp1.data_objects.mdl.frequency import Frequency
from cp1.data_objects.mdl.bandwidth_rate import BandwidthRate
from cp1.data_objects.mdl.bandwidth_types import BandwidthTypes
from cp1.data_objects.processing.ta import TA
from cp1.data_objects.processing.channel import Channel
from cp1.data_objects.processing.constraints_object import ConstraintsObject

from cp1.common.exception_class import NodeNotFoundException
from cp1.common.exception_class import TAsNotFoundException
from cp1.common.exception_class import SystemWideConstraintsNotFoundException
from cp1.common.exception_class import ConstraintsNotFoundException
from cp1.common.exception_class import ChannelsNotFoundException
from cp1.common.exception_class import RadioLinkNotFoundException
from cp1.common.logger import Logger


logger = Logger().logger


class OrientDBSession(BrassOrientDBHelper):
    def __init__(self,  database_name=None, config_file=None, orientdb_client=None, explicit=False):
        self.explicit = explicit
        self.node_count = 0
        self.containment_edge_count = 0
        self.reference_edge_count = 0
        self.node_class_count = 0
        return super(OrientDBSession, self).__init__(database_name, config_file, orientdb_client)


    def store_and_retrieve_constraints(self, constraints_objects):
        """Stores and retrieves constraints in OrientDB.
        This method is just to test storage and retrieval of ConstraintsObjects in OrientDB
        as SwRI has not yet provided actual ConstraintsObjects. Might be used in final code
        depending on how they evaluate.

        :param [<ConstraintsObject>] constraints_objects: The list of ConstraintsObject to store in OrientDB
        :returns [<ConstraintsObject>] orientdb_constraints_objects: The list of ConstraintsObject retrieved from OrientDB. Should match input.
        """
        for constraints_object in constraints_objects:
            self.store_constraints(constraints_object)

        orientdb_constraints_objects = self.retrieve_constraints()
        return orientdb_constraints_objects

    def update_schedule(self, schedules):
        """
        Stores the list of TxOp nodes found in schedule in the MDL file.
        Tries to create TransmissionSchedule and TxOp classes if they don't exist.
        Creates one TransmissionSchedule node for each TA we are interested in scheduling.


        :param [<Schedule>] schedules: A list of schedule objects, one for each channel.
        """
        # The original MDL file we import does not contain any TransmissionSchedule or TxOp
        # elements, so we have to create this class before indexing TransmissionSchedules
        try:
            logger.debug('Attempting to create a TransmissionSchedule class')
            self.create_node_class('TransmissionSchedule')
        except Exception as e:
            logger.debug('{0}'.format(str(e)))
            pass

        try:
            self.create_node_class('TxOp')
        except:
            pass

        try:
            self.delete_nodes_by_class('TransmissionSchedule')
        except:
            pass
        try:
            self.delete_nodes_by_class('TxOp')
        except:
            pass

        radio_links = self.get_nodes_by_type('RadioLink')

        # Construct one list of TxOps from the list of Schedules
        txop_list = []
        for schedule in schedules:
            for txop in schedule.txops:
                txop.start_usec = timedelta(days=txop.start_usec.days, seconds=txop.start_usec.seconds, microseconds=txop.start_usec.microseconds)
                txop.stop_usec = timedelta(days=txop.stop_usec.days, seconds=txop.stop_usec.seconds, microseconds=txop.stop_usec.microseconds)
                txop_list.append(txop)

        # Generate a Dictionary of RadioLinks
        radio_link_rids = defaultdict(list)
        for txop in txop_list:
            if txop.radio_link_id not in radio_link_rids:
                radio_link_rids[txop.radio_link_id].append(txop.center_frequency_hz.value)

        # Match RadioLinks to their corresponding RIDs
        transmission_schedule_rids = {}
        for rl in radio_link_rids:
            i = 0
            found = False
            for orient_record in radio_links:
                if rl == orient_record.ID:
                    radio_link_rids[rl].append(orient_record._rid)
                    transmission_schedule_rid = self.create_node('TransmissionSchedule', {'uid': 'TransmissionSchedule-{0}'.format(i)})
                    transmission_schedule_rids[rl] = transmission_schedule_rid
                    self.set_containment_relationship(parent_rid=orient_record._rid, child_rid=transmission_schedule_rid)
                    found = True
                    i += 1
                    break
            if not found:
                raise RadioLinkNotFoundException('Unable to find RadioLink ({0}) in OrientDB database'.format(rl), 'OrientDBSession.update_schedule')

        # Create TxOp objects in OrientDB and connect them to RadioLinks
        i = 0
        for txop in txop_list:
            txop_properties = {
                'StartUSec': txop.start_usec.get_microseconds(),
                'StopUSec': txop.stop_usec.get_microseconds(),
                'TxOpTimeout': txop.txop_timeout.value,
                'CenterFrequencyHz': txop.center_frequency_hz.value,
                'uid': 'TxOp-{0}'.format(i)
                }

            txop_rid = self.create_node('TxOp', txop_properties)
            self.set_containment_relationship(parent_rid=transmission_schedule_rids[txop.radio_link_id], child_rid=txop_rid)
            i += 1

        self._update_ran(radio_link_rids)

    def store_constraints(self, constraints_object):
        """Stores a ConstraintsObject in the OrientDB database

        :param ConstraintsObject constraints_object: The ConstraintsObject to store in the database
        """
        try:
            self.create_node_class('TA')
        except:
            pass
        try:
            self.create_node_class('Channel')
        except:
            pass
        try:
            self.create_node_class('Constraints')
        except:
            pass

        constraints_object_properties = {
            'id': constraints_object.id_,
            'constraint_type': 'System Wide Constraint',
            'goal_throughput_bulk': constraints_object.goal_throughput_bulk.value,
            'goal_throughput_voice': constraints_object.goal_throughput_voice.value,
            'goal_throughput_safety': constraints_object.goal_throughput_safety.value,
            'guard_band': constraints_object.guard_band.get_milliseconds(),
            'epoch': constraints_object.epoch.get_milliseconds(),
            'txop_timeout': constraints_object.txop_timeout.value,
            'seed': constraints_object.seed
        }
        constraints_object.rid = self.create_node('Constraints', constraints_object_properties)

        # Create Channels and TAs
        for channel in constraints_object.channels:
            self.create_channel(channel)
        for ta in constraints_object.candidate_tas:
            self.create_ta(ta)

        # Setup necessary links
        self._link_candidate_tas(constraints_object.rid, constraints_object.candidate_tas)
        self._link_channels(constraints_object.rid, constraints_object.channels)

        # Channels are now linked to TAs via frequency, so we need a dictionary to
        # parse out RIDs
        frequencies_to_rids = {}
        for channel in constraints_object.channels:
            frequencies_to_rids[channel.frequency.value] = channel.rid
        self._link_eligible_frequencies(constraints_object.candidate_tas, frequencies_to_rids)

        return constraints_object.rid

    def _link_candidate_tas(self, constraint_rid, tas):
        """A post processing step done to link a ConstraintsObject to it's list
           of candidate_tas in the OrientDB database via a Containment edge.

        :param str constraint_rid: The rid of the ConstraintsObject to link to tas
        :param [<TA>] tas: The list of candidate_tas to link to this ConstraintsObject
        """
        for ta in tas:
            self.set_containment_relationship(parent_rid=constraint_rid, child_rid=ta.rid)

    def _link_channels(self, constraint_rid, channels):
        """A post processing step done to link a ConstraintsObject to it's list
           of channels in the OrientDB database via a Containment edge.

        :param str constraint_rid: The rid of the ConstraintsObject to link to tas
        :param [<Channel>] channels: The list of channels to link to this ConstraintsObject
        """
        for channel in channels:
            self.set_containment_relationship(parent_rid=constraint_rid, child_rid=channel.rid)

    def _link_eligible_frequencies(self, tas, frequencies_to_rids):
        """A post processing step done to link the list of candidate_tas to their list
           list of eligible_frequencies in the OrientDB database via a Containment edge.

        :param [<TA>] tas: The list of candidate_tas to link to their eligible_frequencies
        """
        for ta in tas:
            for channel in ta.eligible_frequencies:
                self.set_containment_relationship(parent_rid=ta.rid,
                                                  child_rid=frequencies_to_rids[channel.value])
    def create_channel(self, channel):
        """Indexes a channel in the database
        Adds the property channel.rid to the channel indexed. rid is set to the OrientDB
        generated rid when storing this Channel in the database.

        :param Channel channel: The Channel to store in the database
        """
        properties = {
        'frequency': channel.frequency.value,
        'capacity': channel.capacity.value
        }
        channel.rid = self.create_node('Channel', properties)

    def create_ta(self, ta):
        """Indexes a TA in the database
        Adds the property ta.rid to the ta indexed. rid is set to the OrientDB
        rid when storing this TA in the database.

        :param TA ta: The TA to store in the database
        """
        properties = {
        'id': ta.id_,
        'minimum_voice_bandwidth': ta.minimum_voice_bandwidth.value,
        'minimum_safety_bandwidth': ta.minimum_safety_bandwidth.value,
        'latency': ta.latency.get_microseconds(),
        'scaling_factor': ta.scaling_factor,
        'c': ta.c
        }
        ta.rid = self.create_node('TA', properties)

    def update_bandwidth(self, bandwidth_rates):
        """
        Modifies the Value field of a ServiceLevelProfile's Rate vertex.

        :param bandwidth_rates: New Value to update Rate with.
        :type bandwidth_rates: list
        """
        for bandwidth_rate in bandwidth_rates:
            slp_id = bandwidth_rate[0]
            rate_value = bandwidth_rate[1]

            rate_node = self.get_rate_node(slp_id)

            value_field_name = 'Value'
            sql_update_statement = sql.condition_str(
                value_field_name, rate_value, '=')
            logger.debug('Updating bandwidth: {0}, {1}, {2}'.format(
                slp_id, rate_node._rid, sql_update_statement))
            self.update_node(rate_node._rid, sql_update_statement)

    def delete_nodes_by_class(self, clazz):
        """
        Deletes all nodes of given class type.

        :param str clazz: Class type to delete.
        """
        vertices = self.get_nodes_by_type(clazz)
        vertex_rids = [vertex._rid for vertex in vertices]
        self.delete_nodes_by_rid(vertex_rids)

    def get_scheduled_tas(self):
        """Retrieves a list of TAs that have been scheduled in an MDL file in the database.

        :returns [<TA>] scheduled_tas: The list of TAs that have been scheduled in an MDL file
        """
        scheduled_tas = set()

        orientdb_response = self.get_nodes_by_type('TxOp')
        if orientdb_response is None:
            raise NodeNotFoundException(
                'Unable to find any RadioLinks in the database.',
                'OrientDBSession.get_scheduled_tas'
            )

        for node in orientdb_response:
            radio_link = self.get_connected_nodes(targetNode_rid=node._rid, direction='out', edgetype='Containment',
                                                  maxdepth=2, filterdepth=2)
            radio_link_name = radio_link[0].Name
            ta = re.search('TA[0-9]+', radio_link_name).group(0)
            scheduled_tas.add(ta)
        return scheduled_tas

    def _get_rate_node(self, slp_id):
        """
        Retrieves Rate child of specified ServiceLevelProfile.

        :param str slp_id: Key to identify ServiceLevelProfile.
        :returns pyorient.otypes.OrientRecord rate_node: A PyOrient node
        """
        slp_node = None
        rate_node = None

        slp_nodes = self.get_nodes_by_type('ServiceLevelProfile')
        for n in slp_nodes:
            if n.ID == slp_id:
                slp_node = n

        if slp_node is None:
            raise NodeNotFoundException(
                'Unable to find slp_id: {0}'.format(slp_id),
                'OrientDBSession.get_rate_node')

        rate_class_name = 'Rate'
        rate_depth_from_slp = 4
        slp_children = self.get_connected_nodes(
            slp_node._rid,
            maxdepth=rate_depth_from_slp,
            filterdepth=rate_depth_from_slp)
        for n in slp_children:
            if n._class == rate_class_name:
                rate_node = n

        if rate_node is None:
            raise NodeNotFoundException(
                'Unable to find rate child of slp_id: {0}'.format(slp_id),
                'OrientDBSession.get_rate_node')

        return rate_node

    def retrieve_constraints(self):
        """
        Retrieves constraints from the provided database

        :returns ConstraintsObject constraints_object: A Constraints Object
        """
        orientdb_constraints_objects = self._get_system_wide_constraints()

        constraints_objects = []
        for orientdb_constraints_object in orientdb_constraints_objects:
            connected_nodes = self.get_connected_nodes(orientdb_constraints_object._rid, filterdepth=1)
            candidate_tas = []
            channels = []

            for node in connected_nodes:
                if node._class == 'TA':
                    candidate_tas.append(self.construct_ta_from_node(node))
                elif node._class == 'Channel':
                    channels.append(self.construct_channel_from_node(node))

            constraints_objects.append(ConstraintsObject(
                id_ = orientdb_constraints_object.id,
                candidate_tas=candidate_tas,
                channels=channels,
                goal_throughput_bulk=BandwidthRate(
                    BandwidthTypes.BULK,
                    Kbps(int(orientdb_constraints_object.goal_throughput_bulk))
                ),
                goal_throughput_voice=BandwidthRate(
                    BandwidthTypes.VOICE,
                    Kbps(int(orientdb_constraints_object.goal_throughput_voice))
                ),
                goal_throughput_safety=BandwidthRate(
                    BandwidthTypes.SAFETY,
                    Kbps(int(orientdb_constraints_object.goal_throughput_safety))
                ),
                guard_band=timedelta(microseconds=1000 * int(orientdb_constraints_object.guard_band)),
                epoch=timedelta(microseconds=1000 * int(orientdb_constraints_object.epoch)),
                txop_timeout=TxOpTimeout(int(orientdb_constraints_object.txop_timeout)),
                seed=orientdb_constraints_object.seed))

        return constraints_objects

    def _get_system_wide_constraints(self):
        """Gets the system wide ConstraintsObject stored in the OrientDB database

        :returns [<pyorient.otypes.OrientRecord>] constraints_objects: The list of pyorient ConstraintsObject records
        """
        orientdb_response = self.get_nodes_by_type('Constraints')

        if not orientdb_response:
            raise ConstraintsNotFoundException(
                'OrientDB database [{0}] does not contain any Constraints objects'.format(
                    self._orientdb_client._db_name), 'OrientDBSession._get_system_wide_constraints')

        constraints_objects = []
        for x in orientdb_response:
            if x.constraint_type == 'System Wide Constraint':
                constraints_objects.append(x)
        return constraints_objects

    def construct_ta_from_node(self, orientdb_node):
        """Constructs a TA object from an OrientDB node.

        :param pyorient.otypes.OrientRecord orientdb_node: A pyorient node
        :returns TA ta: A TA object constructed from the pyorient node
        """
        orient_record = self.get_connected_nodes(orientdb_node._rid, direction='in', filterdepth=1)

        eligible_frequencies=[]
        for record in orient_record:
            if record._class == 'Channel':
                eligible_frequencies.append(Frequency(int(record.frequency)))

        ta = TA(
            id_=orientdb_node.id,
            minimum_voice_bandwidth=Kbps(
                float(orientdb_node.minimum_voice_bandwidth)),
            minimum_safety_bandwidth=Kbps(
                float(orientdb_node.minimum_safety_bandwidth)),
            latency=timedelta(microseconds=1000*int(orientdb_node.latency)),
            scaling_factor=float(orientdb_node.scaling_factor),
            c=float(orientdb_node.c),
            eligible_frequencies=eligible_frequencies)

        return ta

    def construct_channel_from_node(self, orientdb_node):
        """Constructs a Channel object from a pyorient node

        :param pyorient.otypes.OrientRecord orientdb_node: A pyorient channel node
        :returns Channel channel: A Channel object constructed from the pyorient node
        """
        channel = Channel(frequency=Frequency(int(orientdb_node.frequency)),
                            capacity=Kbps(int(orientdb_node.capacity)))
        return channel

    def _get_tas(self):
        """
        Retrieves the list of TAs from the provided database

        :returns List[TA] candidate_tas: A list of TA's
        """
        candidate_tas = []

        orientdb_response = self.get_nodes_by_type('TA')

        if not orientdb_response:
            raise TAsNotFoundException(
                'OrientDB database [{0}] does not contain any TAs'.format(
                    self._orientdb_client._db_name),
                'OrientDBSession._get_tas')

        for ta_node in orientdb_response:
            candidate_tas.append(self.construct_ta_from_node(ta_node))

        return candidate_tas

    def _get_channels(self):
        """
        Retrieves nodes of class type 'Channel' from the database and constructs a :class:`cp1.src.cp1_src.cp1.data_objects.processing.Channel` for each node.

        :return [Channel] channels: A list of Channel objects
        :raises TAsNotFoundException:
        """
        channels = []

        orientdb_response = self.get_nodes_by_type('Channel')

        if not orientdb_response:
            raise ChannelsNotFoundException(
                'OrientDB database [{0}] does not contain any Channels'.format(
                    self._orientdb_client._db_name),
                'OrientDBSession._get_channels')

        for channel_node in orientdb_response:
            channels.append(self.construct_channel_from_node(channel_node))

        return channels

    def get_nodes_by_properties(self, target_name, property_conditions=[]):
        """
        Get nodes that fit the property conditions specified.

        :param target_name: The node class, i.e. 'TA' or 'Channel'
        :param list property_conditions:         list of property condition strings in the form of:
                                            name='MDL Description', description='This is a scenario 1'
                                            Use orientdb_sql.condition_str() to help create condition strings.
        :return:                            list of orient record objects
        :raises BrassException:             source of exception is set to the function name
        """
        try:
            sql_cmd = sql.select_sql(target_name, [property_conditions])
            return self._orientdb_client.run_command(
                sql_cmd
            )
        except:
            raise BrassException(sys.exc_info()[1], 'BrassOrientDBHelper.get_node_by_properties')

    def create_node(self, node_type, properties={}):
        """
        Decorator function to count the number of nodes indexed into the database
        and return the new _rid of the indexed node.

        :param str node_type: The class of the node to index
        :param dict{str: str} properties: The properties of the node to index

        :returns str _rid: The OrientDB `Record ID <http://www.orientdb.com/docs/last/Tutorial-Record-ID.html>` of the indexed node.
                           This is a unique identifier that can be used to retrieve the node or set links between this node and others.
        """
        if(self.explicit):
            if self.node_count == 0:
                logger.debug('Indexing Started...')
            elif(self.node_count % 100 == 0):
                logger.debug('Indexed {0} MDL Elements'.format(self.node_count))
            self.node_count += 1

        old_nodes = []
        try:
            old_nodes = self.get_nodes_by_type(node_type)
        except:
            pass

        # Create the node
        super(OrientDBSession, self).create_node(node_type, properties)

        # Retreive RID
        new_nodes = self.get_nodes_by_type(node_type)
        new_node = next(filter(lambda x: x._rid not in set(x._rid for x in old_nodes), new_nodes), None)

        if new_node is None:
            raise NodeNotFoundException(
                'Unable to retrieve the node that was just indexed. node_type: {0}\nproperties: {1}'.format(node_type, properties),
                'OrientDBSession.create_node'
            )

        new_rid = new_node._rid

        return new_rid

    def create_empty_node(self, node_type):
        old_nodes = []
        try:
            old_nodes = self.get_nodes_by_type(node_type)
        except:
            pass

        # Create the node
        self._orientdb_client.run_command('INSERT INTO ' + node_type + ' CONTENT {}')

        # Retrieve RID
        new_nodes = self.get_nodes_by_type(node_type)
        new_node = next(filter(lambda x: x._rid not in set(x._rid for x in old_nodes), new_nodes), None)

        return new_node._rid

    def create_node_class(self, name):
        """
        A decorator function to count the number of classes created.
        Creates an OrientDB class with the corresponding name.

        :param str name: The name of the class to create
        """
        if(self.explicit):
            if self.node_class_count == 0:
                logger.debug('Creating OrientDB classes for MDL Elements...')
            elif(self.node_class_count % 20 == 0):
                logger.debug('Created {0} Node Classes'.format(
                    self.node_class_count))
            self.node_class_count += 1
        return super(OrientDBSession, self).create_node_class(name)

    def set_containment_relationship(self, parent_rid=None, child_rid=None, parent_conditions=[], child_conditions=[]):
        """
        A decorator function to count the number of containment edges created.
        Creates a link of class type 'Containment' between two vertices in the database.

        parent_node <- child_node

        :param str parent_rid: The Record ID of the parent
        :param str child_rid: The Record ID of the child
        :param str parent_conditions: The search conditions of the parent node
        :param str child_conditions: The search conditions of the child node
        """
        if(self.explicit):
            if (self.containment_edge_count == 0):
                logger.debug('Creating Containment Edges...')
            elif(self.containment_edge_count % 100 == 0):
                logger.debug('Created {0} Containment Edges'.format(
                    self.containment_edge_count))
            self.containment_edge_count += 1
        return super(OrientDBSession, self).set_containment_relationship(parent_rid=parent_rid, child_rid=child_rid, parent_conditions=parent_conditions, child_conditions=child_conditions)

    def set_reference_relationship(self, reference_rid=None, referent_rid=None, reference_condition=[], referent_condition=[]):
        """
        A decorator function to count the number of reference edges created.
        Creates a link of class type 'Reference' between two vertices in the database.

        reference node -> referent node

        :param str reference_rid: The Record ID of the reference node
        :param str referent_rid: The Record ID of the referent node
        :param str reference_condition: The search conditions of the reference node
        :param str referent_condition: The search conditions of the referent node
        """
        if(self.explicit):
            if (self.reference_edge_count == 0):
                logger.debug('Creating Reference Edges...')
            elif(self.reference_edge_count % 10 == 0):
                logger.debug('Created {0} Reference Edges'.format(
                    self.reference_edge_count))
            self.reference_edge_count += 1
        return super(OrientDBSession, self).set_reference_relationship(reference_rid=reference_rid, referent_rid=referent_rid, reference_condition=reference_condition, referent_condition=referent_condition)

    def _update_ran(self, rl_ids):
        # First, we need the DestinationRadioGroupRef ID matching the radio
        # link we are about to move rans for.
        for k, v in rl_ids.items():
            # Radio Link we want.
            connected_nodes = self.get_connected_nodes(targetNode_rid=v[1], direction='in', edgetype='Containment',
                                                  maxdepth=1, filterdepth=1)
            found = False
            for node in connected_nodes:
                if node._class == 'DestinationRadioGroupRef':
                    found = True
                    # 'RadioLink_4097_to_61441': [4919, '#99:0', 'RadioGroup_RAN_4919_61441']
                    v.append(node.IDREF)
            if not found:
                raise DestinationRadioGroupRefNotFoundException('Unable to find DestinationRadioGroupRef for RadioLink ({0}) in OrientDB database'.format(k), 'OrientDBSession._update_ran')

        # Second, we need the RadioGroup._rid of the corresponding DestinationRadioGroupRefID
        for k, v in rl_ids.items():
            radios = self.get_nodes_by_type('RadioGroup')
            for radio in radios:
                if radio.ID == v[2]:
                    # 'RadioLink_4097_to_61441': [4919, '#99:0', 'RadioGroup_RAN_4919_61441', '#66:0']
                    v.append(radio._rid)

        for k, v in rl_ids.items():
            i = 0
            rans = self.get_nodes_by_type('RANConfiguration')

            # All radio configurations are under 4919 by default, so
            # we don't need to do anything if it is already under 4919
            for ran in rans:

                connected_nodes = self.get_connected_nodes(targetNode_rid=ran._rid, direction='in', edgetype='Containment',
                maxdepth=1, filterdepth=1)
                # Only one channel will have a radio groups element, so we must
                # create the radio groups for other elements before continuing
                radio_groups_rid = None
                found = False
                for node in connected_nodes:
                    # Initially, this is the only channel with a pre-existing RadioGroups
                    # i.e. Channel 4919
                    if node._class == 'RadioGroups':
                        found = True
                        radio_groups_rid = node._rid
                if not found:
                    radio_groups_rid = self.create_node('RadioGroups', {'uid': 'RadioGroups-{0}'.format(i + 1)})
                    self.set_containment_relationship(parent_rid=ran._rid, child_rid=radio_groups_rid)
                    i += 1

                # First we need to disconnect the existing reference
                # to 4919
                if ran.Name == 'RAN_4919':
                    self.remove_link(referent_rid=radio_groups_rid, reference_rid=v[3])

                # If this is the matching RAN Configuration, setup a link
                # between it's radio groups, and the radio group element you want
                # to move here
                freq = ran.Name[4:]
                matching_ran = freq == str(v[0])

                if matching_ran:
                    self.set_containment_relationship(parent_rid=radio_groups_rid, child_rid=v[3])

        for k, v in rl_ids.items():
            i = 0
            # 'RadioLink_4097_to_61441': [4919, '#99:0', 'RadioGroup_RAN_4919_61441', '#66:0']
            tmns_apps = self.get_nodes_by_type('TmNSApp')
            for tmns_app in tmns_apps:
                tmns_app_connected_nodes = self.get_connected_nodes(targetNode_rid=tmns_app._rid, direction='in', edgetype='Containment',
                    maxdepth=1, filterdepth=1)
                for tmns_radio in tmns_app_connected_nodes:
                    if tmns_radio._class == 'TmNSRadio':
                        tmns_radio_connected_nodes = self.get_connected_nodes(targetNode_rid=tmns_radio._rid, direction='in', edgetype='Containment',
                            maxdepth=1, filterdepth=1)
                        for node in tmns_radio_connected_nodes:
                            if node._class == 'RANConfigurationRef':
                                ran_configuration_ref_node = node
                        for node in tmns_radio_connected_nodes:
                            if node._class == 'JoinRadioGroupRefs':
                                join_radio_grp_ref_children = self.get_connected_nodes(targetNode_rid=node._rid, direction='in', edgetype='Containment',
                                    maxdepth=1, filterdepth=1)
                                for radio_group_ref in join_radio_grp_ref_children:
                                    if radio_group_ref._class == 'RadioGroupRef':
                                        if radio_group_ref.IDREF == v[2]:
                                            self.remove_link(referent_rid=tmns_radio._rid, reference_rid=ran_configuration_ref_node._rid)
                                            ran_configuration_ref_rid = self.create_node('RANConfigurationRef', {'IDREF': 'RANConfig15_RAN_{0}'.format(str(v[0])),'uid': 'RANConfigurationRef-{0}'.format(i + 1)})
                                            self.set_containment_relationship(parent_rid=tmns_radio._rid, child_rid=ran_configuration_ref_rid)
                                            i += 1
