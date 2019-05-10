"""orientdb_session.py

Any helper functions that store data in OrientDB.
Author: Tameem Samawi (tsamawi@cra.com)
"""
import re
import sys

from brass_api.translator.orientdb_importer import OrientDBXMLImporter as MDLImporter
from brass_api.translator.orientdb_exporter import OrientDBXMLExporter as MDLExporter
from brass_api.orientdb.orientdb_helper import BrassOrientDBHelper
from brass_api.common.exception_class import BrassException
import brass_api.orientdb.orientdb_sql as sql

from cp1.data_objects.constants.constants import *
from cp1.utils.constraint_types import ConstraintTypes
from cp1.utils.channel_generator import ChannelGenerator
from cp1.utils.ta_generator import TAGenerator
from cp1.data_objects.mdl.kbps import Kbps
from cp1.data_objects.mdl.txop import TxOpTimeout
from cp1.data_objects.mdl.frequency import Frequency
from cp1.data_objects.mdl.milliseconds import Milliseconds
from cp1.data_objects.mdl.bandwidth_rate import BandwidthRate
from cp1.data_objects.mdl.bandwidth_types import BandwidthTypes
from cp1.data_objects.processing.ta import TA
from cp1.data_objects.processing.channel import Channel
from cp1.data_objects.processing.schedule import Schedule
from cp1.data_objects.processing.constraints_object import ConstraintsObject

from cp1.common.exception_class import NodeNotFoundException
from cp1.common.exception_class import TAsNotFoundException
from cp1.common.exception_class import SystemWideConstraintsNotFoundException
from cp1.common.exception_class import ConstraintsNotFoundException
from cp1.common.exception_class import ChannelNotFoundException
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

    def update_schedule(self, schedule):
        """
        Deletes existing TxOp nodes in database.
        Stores the list of TxOp nodes found in schedule.

        :param dict<str, List[TxOp]> schedule:
        """
        self.delete_nodes_by_class('TxOp')
        added_txops = set()

        radio_link_vertices = self.get_nodes_by_type(
            'RadioLink')
        for key in schedule:
            # Check database contains RadioLink
            new_txop_list = schedule[key]
            radio_link = None
            for vertex in radio_link_vertices:
                if vertex.ID == key:
                    radio_link = vertex
            if radio_link is None:
                logger.warn('Unable to find RadioLink with ID: [%s]', key)

            # Get TransmissionSchedule for RadioLink
            transmission_schedule = None
            radio_link_children = self.get_child_nodes(
                radio_link._rid)
            for child in radio_link_children:
                if child._class == 'TransmissionSchedule':
                    transmission_schedule = child
            if transmission_schedule is None:
                logger.warn(
                    'Unable to find Transmission schedule for RadioLink: [%s]',
                    radio_link)

            # Insert new TxOp under TransmissionSchedule
            txop_rids = []
            for new_txop in new_txop_list:
                logger.info('Adding TxOp to TransmissionSchedule: {0}, {1}, {2}'.format(
                    key, new_txop.start_usec.value, new_txop.stop_usec.value))
                txop_properties = {
                    'StartUSec': int(new_txop.start_usec.value),
                    'StopUSec': int(new_txop.stop_usec.value),
                    'TxOpTimeout': new_txop.txop_timeout.value,
                    'CenterFrequencyHz': new_txop.center_frequency_hz.value
                }
                self.create_node("TxOp", txop_properties)
                orientdb_txop = self.get_nodes_by_type('TxOp')
                for txop in orientdb_txop:
                    if txop._rid not in txop_rids and txop._rid not in added_txops:
                        added_txops.add(txop._rid)
                        txop_rids.append(txop._rid)
                        self.set_containment_relationship(
                            parent_rid=transmission_schedule._rid, child_rid=txop._rid)

    def create_constraints_object(self, constraints_object):
        constraints_object_properties = {
            'id': constraints_object.id_,
            'constraints_type': 'System Wide Constraint',
            'goal_throughput_bulk': constraints_object.goal_throughput_bulk.rate.value,
            'goal_throughput_voice': constraints_object.goal_throughput_voice.rate.value,
            'goal_throughput_safety': constraints_object.goal_throughput_safety.rate.value,
            'guard_band': constraints_object.guard_band.value,
            'epoch': constraints_object.epoch.value,
            'txop_timeout': constraints_object.txop_timeout.value,
            'channel_seed': constraints_object.channel_seed,
            'ta_seed': constraints_object.ta_seed,
            'constraint_type': 'System Wide Constraint'
        }
        rid = self.create_node('Constraints', constraints_object_properties, identifying_field='id', identifying_value=constraints_object.id_)
        constraints_object.rid = rid

        # Create Channels and TAs
        for channel in constraints_object.channels:
            self.create_channel(channel)
        for ta in constraints_object.candidate_tas:
            self.create_ta(ta)

        # Setup necessary links
        self.link_constraint_to_tas(rid, constraints_object.candidate_tas)
        self.link_constraint_to_channels(rid, constraints_object.channels)
        self.link_eligible_channels(constraints_object.candidate_tas)

        return rid

    def link_constraint_to_tas(self, constraint_rid, tas):
        for ta in tas:
            self.set_containment_relationship(parent_rid=constraint_rid, child_rid=ta.rid)
    def link_constraint_to_channels(self, constraint_rid, channels):
        for channel in channels:
            self.set_containment_relationship(parent_rid=constraint_rid, child_rid=channel.rid)
    def link_eligible_channels(self, tas):
        for ta in tas:
            for channel in ta.eligible_channels:
                self.set_containment_relationship(parent_rid=ta.rid, child_rid=channel.rid)

    def create_channel(self, channel):
        properties = {
        'frequency': channel.frequency.value,
        'capacity': channel.capacity.value
        }
        rid = self.create_node('Channel', properties, identifying_field='frequency', identifying_value=channel.frequency.value)
        channel.rid = rid

        return rid

    def create_ta(self, ta):
        properties = {
        'id': ta.id_,
        'minimum_voice_bandwidth': ta.minimum_voice_bandwidth.value,
        'minimum_safety_bandwidth': ta.minimum_safety_bandwidth.value,
        'latency': ta.latency.value,
        'scaling_factor': ta.scaling_factor,
        'c': ta.c
        }
        rid = self.create_node('TA', properties, identifying_field='id', identifying_value=ta.id_)
        ta.rid = rid

        return rid

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
            logger.info('Updating bandwidth: {0}, {1}, {2}'.format(
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
        """
        scheduled_tas = set()

        orientdb_response = self.get_nodes_by_type('TxOp')
        if orientdb_response is None:
            raise NodeNotFoundException(
                'Unable to find any RadioLinks in the database.',
                'OrientDBRetrieval.get_scheduled_tas'
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

    def get_constraints(self):
        """
        Retrieves constraints from the provided database

        :returns ConstraintsObject constraints_object: A Constraints Object
        """
        orientdb_constraints_object = self._get_first_system_wide_constraints()

        connected_nodes = self.get_connected_nodes(orientdb_constraints_object._rid, filterdepth=1)
        candidate_tas = []
        channels = []

        for node in connected_nodes:
            if node._class == 'TA':
                candidate_tas.append(self.construct_ta_from_node(node))
            elif node._class == 'Channel':
                channels.append(self.construct_channel_from_node(node))

        constraints_object=ConstraintsObject(
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
            guard_band=Milliseconds(int(orientdb_constraints_object.guard_band)),
            epoch=Milliseconds(int(orientdb_constraints_object.epoch)),
            txop_timeout=TxOpTimeout(int(orientdb_constraints_object.txop_timeout)),
            ta_seed=orientdb_constraints_object.ta_seed,
            channel_seed=orientdb_constraints_object.channel_seed)

        return constraints_object

    def _get_first_system_wide_constraints(self):
        orientdb_response = self.get_nodes_by_type('Constraints')

        if not orientdb_response:
            raise ConstraintsNotFoundException(
                'Constraints database {0} does not contain any Constraints objects'.format(
                    self._orientdb_client._db_name), 'OrientDBSession._get_system_wide_constraints')

        # try:
        #     system_wide_constraints_objects = list(filter(lambda x: x.constraints_type != ORIENTDB_CONSTRAINTS_TYPE))
        # except:
        #     raise ConstraintsNotFoundException('Constraints Database {0} is missing the required constraints_type field'.format(self._orientdb_client._db_name))

        # if len(orientdb_response) == 0:
        #     raise SystemWideConstraintsNotFoundException(
        #         'Constraints database {0} does not contain a System Wide Constraint'.format(
        #             self._orientdb_client._db_name), 'OrientDBSession._get_system_wide_constraints')
        for x in orientdb_response:
            if x.constraint_type == 'System Wide Constraint':
                return x
        raise ConstraintsNotFoundException('Constraints Database {0} is missing a System Wide Constraints object.', 'OrientDBSession._get_system_wide_constraints')


    def construct_ta_from_node(self, orientdb_node):
        channel_nodes = self.get_connected_nodes(orientdb_node._rid, direction='out', filterdepth=1)

        eligible_channels=[]
        for channel_node in channel_nodes:
            if channel_node._class == 'Channel':
                channel = Channel(
                    frequency=Frequency(channel.frequency),
                    capacity=Kbps(channel.capacity)
                )
                eligible_channels.append(channel)

        ta_obj = TA(
            id_=orientdb_node.id,
            minimum_voice_bandwidth=Kbps(
                int(orientdb_node.minimum_voice_bandwidth)),
            minimum_safety_bandwidth=Kbps(
                int(orientdb_node.minimum_safety_bandwidth)),
            latency=Milliseconds(int(orientdb_node.latency)),
            scaling_factor=float(orientdb_node.scaling_factor),
            c=float(orientdb_node.c),
            eligible_channels=eligible_channels)

        return ta_obj

    def construct_channel_from_node(self, orientdb_node):
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
                'Constraints database {0} does not contain any TAs'.format(
                    self._orientdb_client._db_name),
                'OrientDBSession._get_tas')

        for ta_node in orientdb_response:
            candidate_tas.append(self.construct_ta_from_node(ta_node))
        return candidate_tas

    def _get_channels(self):
        channels = []
        orientdb_response = self.get_nodes_by_type('Channel')

        if not orientdb_response:
            raise TAsNotFoundException(
                'Constraints database {0} does not contain any Channels'.format(
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

    def create_node(self, node_type, properties={}, identifying_field=None, identifying_value=None):
        if(self.explicit):
            if self.node_count == 0:
                logger.info('Indexing Started...')
            elif(self.node_count % 100 == 0):
                logger.info('Indexed {0} MDL Elements'.format(self.node_count))
            self.node_count += 1
        super(OrientDBSession, self).create_node(node_type, properties)

        new_rid = None
        if identifying_field is not None:
            new_rid = self.get_nodes_by_properties(target_name=node_type, property_conditions=sql.condition_str(identifying_field, identifying_value))[0]._rid
        return new_rid

    def create_node_class(self, name):
        if(self.explicit):
            if self.node_class_count == 0:
                logger.info('Creating OrientDB classes for MDL Elements...')
            elif(self.node_class_count % 20 == 0):
                logger.info('Created {0} Node Classes'.format(
                    self.node_class_count))
            self.node_class_count += 1
        return super(OrientDBSession, self).create_node_class(name)

    def set_containment_relationship(self, parent_rid=None, child_rid=None, parent_conditions=[], child_conditions=[]):
        if(self.explicit):
            if (self.containment_edge_count == 0):
                logger.info('Creating Containment Edges...')
            elif(self.containment_edge_count % 100 == 0):
                logger.info('Created {0} Containment Edges'.format(
                    self.containment_edge_count))
            self.containment_edge_count += 1
        return super(OrientDBSession, self).set_containment_relationship(parent_rid=parent_rid, child_rid=child_rid, parent_conditions=parent_conditions, child_conditions=child_conditions)

    def set_reference_relationship(self, reference_rid=None, referent_rid=None, reference_condition=[], referent_condition=[]):
        if(self.explicit):
            if (self.reference_edge_count == 0):
                logger.info('Creating Reference Edges...')
            elif(self.reference_edge_count % 10 == 0):
                logger.info('Created {0} Reference Edges'.format(
                    self.reference_edge_count))
            self.reference_edge_count += 1
        return super(OrientDBSession, self).set_reference_relationship(reference_rid=reference_rid, referent_rid=referent_rid, reference_condition=reference_condition, referent_condition=referent_condition)
