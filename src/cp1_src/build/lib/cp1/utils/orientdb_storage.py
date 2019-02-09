"""

orientdb_storage.py

Any helper functions that store data in OrientDB.
Author: Tameem Samawi (tsamawi@cra.com)
"""
from cp1.common.logger import Logger
from cp1.utils.orientdb_retrieval import OrientDBRetrieval
from brass_api.orientdb.orientdb_helper import BrassOrientDBHelper
from cp1.common.exception_class import StoreResultInitializationException
from cp1.data_objects.mdl.frequency import Frequency
import brass_api.orientdb.orientdb_sql as sql
import cp1.data_objects.mdl.schedule as Schedule

logger = Logger().logger


class OrientDBStorage(OrientDBRetrieval):
    def __init__(self,  database_name=None, config_file=None, orientdb_client=None):
        self.node_count = 0
        return super(OrientDBStorage, self).__init__(database_name, config_file, orientdb_client)

    def create_node(self, node_type, properties={}):
        if(self.node_count % 100 == 0 and self.node_count != 0):
            logger.info('Indexed {0} MDL Elements'.format(self.node_count))
        self.node_count += 1
        return super(OrientDBStorage, self).create_node(node_type, properties)

    def create_node_class(self, name):
        logger.info('Created {0} Class'.format(name))
        return super(OrientDBStorage, self).create_node_class(name)

    def create_edge_class(self, name):
        logger.info('Created {0} Relationship Class'.format(name))
        return super(OrientDBStorage, self).create_edge_class(name)

    def set_containment_relationship(self, parent_conditions, child_conditions):
        parent_id = parent_conditions[0].lstrip("\"uid=\'").rstrip("\'\"")
        child_id = child_conditions[0].lstrip("\"uid=\'").rstrip("\'\"")
        logger.info('Creating parent/child relationship from {0} to {1}'.format(parent_id, child_id))
        return super(OrientDBStorage, self).set_containment_relationship(parent_conditions=parent_conditions, child_conditions=child_conditions)

    def update_schedule(self, schedule):
        """
        Deletes existing TxOp nodes in database.
        Stores the list of TxOp nodes found in schedule.

        :param schedule: An instance of Schedule
        :type schedule: dict<str, List[MDLTxOp]>
        """
        self.delete_nodes_by_class('TxOp')
        added_txops = set()

        radio_link_vertices = self.get_nodes_by_type(
            "RadioLink")
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
                logger.info('Adding TxOp to TransmissionSchedule: {0}, {1}, {2}'.format(key, new_txop.start_usec.value, new_txop.stop_usec.value))
                txop_properties = {
                    "StartUSec": int(new_txop.start_usec.value),
                    "StopUSec": int(new_txop.stop_usec.value),
                    "TxOpTimeout": new_txop.txop_timeout.value,
                    "CenterFrequencyHz": new_txop.center_frequency_hz.value
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
            logger.info('Updating bandwidth: {0}, {1}, {2}'.format(slp_id, rate_node._rid, sql_update_statement))
            self.update_node(rate_node._rid, sql_update_statement)

    def delete_nodes_by_class(self, clazz):
        """
        Deletes all nodes of given class type.

        :param clazz: Class type to delete.
        :type clazz: str
        """
        vertices = self.get_nodes_by_type(clazz)
        vertex_rids = [vertex._rid for vertex in vertices]
        self.delete_nodes_by_rid(vertex_rids)
    # def update_frequency(self, mdl_frequency):
    #     """
    #     Updates the CenterFrequencyHz field of all TxOp nodes in the database
    #
    #     :param mdl_frequency: Object containing 'value' field with new frequency. Object performs type checking.
    #     :type mdl_frequency: MDLFrequency
    #     """
    #     if not isinstance(mdl_frequency, MDLFrequency):
    #         raise ValueException('mdl_frequency must be an instance of MDLFrequency. mdl_frequency: [{0}]'.format(mdl_frequency), 'store_result.__update_frequency')
    #     TxOp_nodes = self.orientdb_helper.get_nodes_by_type('TxOp')
    #     new_fqhz = sql.condition_str(
    #         'CenterFrequencyHz', mdl_frequency.value, '=')
    #     for node in TxOp_nodes:
    #         self.orientdb_helper.update_node(node._rid, new_fqhz)
    #         logger.debug(
    #             "Updated node %s with frequency %s",
    #             node._rid,
    #             mdl_frequency.value)
    #
    # def __update_bandwidth(self, mdl_bandwidth_set):
    #     """
    #     Calls update_rate_nodes to update Voice, Safety, Bulk and RFNM bandwidth values.
    #
    #     :param mdl_bandwidth_set: Bandwidth update keys and values.
    #     :type mdl_bandwidth_set: MDLBandwidthSet
    #     """
    #     modify_rate_value(self.orientdb_helper, mdl_bandwidth_set.voice)
    #     modify_rate_value(self.orientdb_helper, mdl_bandwidth_set.safety)
    #     modify_rate_value(self.orientdb_helper, mdl_bandwidth_set.bulk)
    #     modify_rate_value(self.orientdb_helper, mdl_bandwidth_set.rfnm)
