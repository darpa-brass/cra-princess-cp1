"""

store_result.py

Updates OrientDB with optimization results.
Author: Tameem Samawi (tsamawi@cra.com)

"""
from cra.utils.logger import Logger
from cp1.utils.cra_orientdb_helper import CRAOrientDBHelper
from brass_api.orientdb.orientdb_helper import BrassOrientDBHelper
from cp1.common.exception_class import StoreResultInitializationException
from cp1.data_objects.mdl.frequency import Frequency
import brass_api.orientdb.orientdb_sql as sql
import cp1.data_objects.mdl.schedule as Schedule


logger = Logger().logger


class OrientDBUpdates(CRAOrientDBHelper):
    def __init__(self, orientdb_helper):
        """
        :param orientdb_helper: BRASS SwRI provided database helper object.
        :type orientdb_helper: BrassOrientDBHelper
        """
        # If we mock this, we cannot check the instance
        # if not isinstance(orientdb_helper, BrassOrientDBHelper):
        #     raise StoreResultInitializationException('orientdb_helper must be an instance of BrassOrientDBHelper. orientdb_herlper: [{0}]'.format(orientdb_helper), '__init__')
        self.orientdb_helper = orientdb_helper

    def store_result(self, optimization_result):
        """
        Updates the database with output from the algorithm's results.

        :param optimization_result: The Optimization Algorithm result containing a new schedule, frequency and bandwidth
        rates
        :type optimization_result: OptimizationResult
        """
        if not isinstance(optimization_result, Schedule):
            raise ValueError(
                'optimization_result must be an instance of OptimizationResult.')

        self.orientdb_helper.open_database()
        if optimization_result.mdl_schedule is not None:
            self.update_schedule(optimization_result.mdl_schedule)
        if optimization_result.mdl_frequency is not None:
            self.update_frequency(optimization_result.mdl_frequency)
        if optimization_result.mdl_bandwidth_set is not None:
            self.update_bandwidth(optimization_result.mdl_bandwidth_set)
        self.orientdb_helper.close_database()

    def update_schedule(self, schedule):
        """
        Updates the CenterFrequencyHz field of all TxOp nodes in the database

        :param schedule: A dict where each key is RadioLink ID and value is a list of ordered MDLTxOp objects by start_usec.
        :type mdl_schedule: dict<str, List[MDLTxOp]>
        """
        # Delete existing TxOp nodes
        self.delete_nodes_by_class(self.orientdb_helper, 'TxOp')
        added_txops = set()

        radio_link_vertices = self.orientdb_helper.get_nodes_by_type(
            "RadioLink")
        for key in schedule:
            # Check database contains RadioLink
            new_txop_list = schedule[key]
            radio_link = None
            for vertex in radio_link_vertices:
                if vertex.ID == key:
                    radio_link = vertex
                    print('Match')
            if radio_link is None:
                logger.warn('Unable to find RadioLink with ID: [%s]', key)

            # Get TransmissionSchedule for RadioLink
            transmission_schedule = None
            radio_link_children = self.orientdb_helper.get_child_nodes(
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
                txop_properties = {
                    "StartUSec": new_txop.start_usec.value,
                    "StopUSec": new_txop.stop_usec.value,
                    "TxOpTimeout": new_txop.txop_timeout.value,
                    "CenterFrequencyHz": new_txop.center_frequency_hz.value
                }
                self.orientdb_helper.create_node("TxOp", txop_properties)
                orientdb_txop = self.orientdb_helper.get_nodes_by_type('TxOp')
                for txop in orientdb_txop:
                    if txop._rid not in txop_rids and txop._rid not in added_txops:
                        added_txops.add(txop._rid)
                        txop_rids.append(txop._rid)
                        self.orientdb_helper.set_containment_relationship(
                            parent_rid=transmission_schedule._rid, child_rid=txop._rid)

    def modify_rate_value(self, slp_id, new_rate_value):
        """
        Modifies the Value field of a ServiceLevelProfile's Rate vertex.

        :param slp_id: ServiceLevelProfile ID.
        :type slp_id: str

        :param new_rate_value: New Value to update Rate with.
        :type new_rate_value: int
        """
        logger.debug(
            "Adjusting bandwidth:\n[slp_id: %s]\n[new_rate_value: %s]",
            slp_id,
            new_rate_value)

        rate_node = get_rate_node(slp_id, new_rate_value)

        value_field_name = 'Value'
        sql_update_statement = sql.condition_str(
            value_field_name, new_rate_value, '=')

        self.update_node(rate_node._rid, sql_update_statement)

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
