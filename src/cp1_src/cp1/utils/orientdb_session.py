"""orientdb_session.py

Any helper functions that store data in OrientDB.
Author: Tameem Samawi (tsamawi@cra.com)
"""
import re
from brass_api.translator.orientdb_importer import OrientDBXMLImporter as MDLImporter
from brass_api.translator.orientdb_exporter import OrientDBXMLExporter as MDLExporter
from brass_api.orientdb.orientdb_helper import BrassOrientDBHelper
import brass_api.orientdb.orientdb_sql as sql

from cp1.data_objects.processing.ta import TA
from cp1.data_objects.mdl.kbps import Kbps
from cp1.data_objects.mdl.txop import TxOpTimeout
from cp1.data_objects.mdl.frequency import Frequency
from cp1.data_objects.mdl.milliseconds import Milliseconds
from cp1.data_objects.mdl.bandwidth_rate import BandwidthRate
from cp1.data_objects.mdl.bandwidth_types import BandwidthTypes
from cp1.data_objects.processing.channel import Channel
from cp1.data_objects.processing.schedule import Schedule
from cp1.data_objects.processing.constraints_object import ConstraintsObject
from cra.common.exception_class import NodeNotFoundException
from cp1.common.exception_class import TAsNotFoundException
from cp1.common.exception_class import SystemWideConstraintsNotFoundException
from cp1.common.exception_class import ConstraintsNotFoundException
from cp1.common.logger import Logger
from cp1.common.exception_class import StoreResultInitializationException
from cp1.utils.constraint_types import ConstraintTypes


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
        self._orientdb_client.open_database()
        constraints = self._get_system_wide_constraints()
        candidate_tas = self._get_tas()
        channels = self._create_channels(constraints)
        self._orientdb_client.close_database()

        return ConstraintsObject(
            goal_throughput_bulk=BandwidthRate(
                BandwidthTypes.bulk,
                Kbps(constraints.goal_throughput_bulk)
            ),
            goal_throughput_voice=BandwidthRate(
                BandwidthTypes.voice,
                Kbps(constraints.goal_throughput_voice)
            ),
            goal_throughput_safety=BandwidthRate(
                BandwidthTypes.safety,
                Kbps(constraints.goal_throughput_safety)
            ),
            latency=Milliseconds(
                constraints.latency / 1000),
            guard_band=Milliseconds(
                constraints.guard_band / 1000),
            epoch=Milliseconds(
                constraints.epoch / 1000),
            candidate_tas=candidate_tas,
            txop_timeout=TxOpTimeout(constraints.txop_timeout),
            channels=channels)

    def _get_system_wide_constraints(self):
        orientdb_response = self.get_nodes_by_type('Constraints')

        if not orientdb_response:
            raise ConstraintsNotFoundException(
                'Constraints database {0} does not contain any Constraints objects'.format(
                    self._orientdb_client._db_name), 'OrientDBSession._get_system_wide_constraints')

        if orientdb_response[0].constraint_type != ConstraintTypes.SYSTEM_WIDE.value:
            raise SystemWideConstraintsNotFoundException(
                'Constraints database {0} does not contain a System Wide Constraint'.format(
                    self._orientdb_client._db_name), 'OrientDBSession._get_system_wide_constraints')

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
                'OrientDBSession.get_tas')

        for ta in orientdb_response:
            ta_obj = TA(
                id_=(ta.id),
                minimum_voice_bandwidth=Kbps(
                    ta.minimum_voice_bandwidth),
                minimum_safety_bandwidth=Kbps(
                    ta.minimum_safety_bandwidth),
                scaling_factor=ta.scaling_factor,
                c=ta.c)
            candidate_tas.append(ta_obj)

        return candidate_tas

    def create_node(self, node_type, properties={}):
        if(self.explicit):
            if self.node_count == 0:
                logger.info('Indexing Started...')
            elif(self.node_count % 100 == 0):
                logger.info('Indexed {0} MDL Elements'.format(self.node_count))
            self.node_count += 1
        return super(OrientDBSession, self).create_node(node_type, properties)

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
