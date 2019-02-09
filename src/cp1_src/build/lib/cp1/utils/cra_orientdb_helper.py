"""

cra_orientdb_helper.py

Extention of BrassOrientDBHelper with additional queries.
Author: Tameem Samawi (tsamawi@cra.com)
"""

from cra.utils.logger import Logger
import brass_api.orientdb.orientdb_sql as sql
from brass_api.translator.orientdb_importer import OrientDBXMLImporter as MDLImporter
from brass_api.translator.orientdb_exporter import OrientDBXMLExporter as MDLExporter
from brass_api.orientdb.orientdb_helper import BrassOrientDBHelper
from cp1.data_objects.constraints.ta import TA
from cp1.data_objects.mdl.mdl_id import MdlId
from cp1.data_objects.mdl.kbps import Kbps
from cp1.data_objects.mdl.txop import TxOpTimeout
from cp1.data_objects.mdl.frequency import Frequency
from cp1.data_objects.mdl.milliseconds import Milliseconds
from cp1.data_objects.mdl.bandwidth_rate import BandwidthRate
from cp1.data_objects.mdl.bandwidth_types import BandwidthTypes
from cp1.data_objects.constraints.channel import Channel
from cp1.data_objects.constraints.constraints_object import ConstraintsObject
from cra.common.exception_class import NodeNotFoundException
from cp1.common.exception_class import TAsNotFoundException
from cp1.common.exception_class import SystemWideConstraintsNotFoundException

logger = Logger().logger


class CRAOrientDBHelper(BrassOrientDBHelper):
    def import_mdl(self, database_name, config_file, mdl_file):
        """
        Imports mdl_file into database. Contains it's own instance of BrassOrientDBHelper which is closed upon completion.

        :param database_name: OrientDB database name.
        :type database_name: str

        :param config_file: Path to database config file.
        :type config_file: str

        :param mdl_file: Path to mdl file.
        :type mdl_file: str
        """
        logger.debug(
            'Importing mdl file %s into database %s',
            mdl_file,
            database_name)
        importer = MDLImporter(
            databaseName=database_name,
            configFile=config_file,
            mdlFile=mdl_file)
        importer.import_xml()
        importer.orientDB_helper.close_database()

    def export_mdl(self, database, config_file, output_file):
        """
        Exports database to output_file. Contains it's own instance of BrassOrientDBHelper which is closed upon completion.

        :param database: Database name.
        :type database: str

        :param config_file: Path to database config file.
        :type config_file: str

        :param output_file: File to output database contents to.
        :type output_file: str
        """
        logger.debug(
            'Exporting database %s into output file %s',
            database,
            output_file)
        exporter = MDLExporter(
            databaseName=database,
            configFile=config_file,
            xmlfile=output_file)
        exporter.export_xml()
        exporter.orientDB_helper.close_database()

    def get_rate_node(self, slp_id):
        """
        Retrieves Rate child of specified ServiceLevelProfile.

        :param slp_id: Key to identify ServiceLevelProfile.
        :type slp_id: str

        :returns rate_node: A PyOrient node
        """
        slp_node = None
        rate_node = None

        slp_nodes = self.get_nodes_by_type('ServiceLevelProfile')
        for n in slp_nodes:
            if n.ID == slp_id:
                slp_node = n

        if slp_node is None:
            raise NodeNotFoundException(
                "Unable to find slp_id: {0}".format(slp_id),
                'CRAOrientDBHelper.get_rate_node')

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
                "Unable to find rate child of slp_id: {0}".format(slp_id),
                'CRAOrientDBHelper.get_rate_node')

        return rate_node

    def delete_nodes_by_class(self, clazz):
        """
        Deletes all nodes of given class type.

        :param clazz: Class type to delete.
        :type clazz: str
        """
        vertices = self.get_nodes_by_type(clazz)
        vertex_rids = [vertex._rid for vertex in vertices]
        self.delete_nodes_by_rid(vertex_rids)

    def get_constraints(self):
        """
        Retrieves constraints from the provided database

        :returns constraints_object: A Constraints Object
        """
        self._orientdb_client.open_database()
        ta_response = self.get_nodes_by_type('TA')
        constraints_response = self.get_nodes_by_type('Constraints')
        self._orientdb_client.close_database()

        candidate_tas = self.parse_ta_response(ta_response)
        constraints = self.parse_constraints_response(constraints_response)

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
            channel=Channel(
                name=MdlId('Channel_1'),
                capacity=Kbps(
                    constraints.channel_capacity),
                timeout=TxOpTimeout(
                    constraints.txop_timeout),
                frequency=Frequency(
                    constraints.channel_frequency)))

    def parse_constraints_response(self, orientdb_response):
        if not orientdb_response:
            raise SystemWideConstraintsNotFoundException(
                'Constraints database {0} does not contain any Constraints objects'.format(
                    self._orientdb_client._db_name), 'CRAOrientDBHelper.get_constraints')

        for constraint in orientdb_response:
            if constraint.constraint_type == 'System Wide Constraint':
                return constraint
        raise SystemWideConstraintsNotFoundException(
            'Constraints database {0} does not contain a System Wide Constraint'.format(
                self._orientdb_client._db_name), 'CRAOrientDBHelper.get_constraints')

    def parse_ta_response(self, orientdb_response):
        """
        Retrieves the list of TAs from the provided database

        :returns candidate_tas: A list of TA's
        """
        candidate_tas = []

        if not orientdb_response:
            raise TAsNotFoundException(
                'Constraints database {0} does not contain any TAs'.format(
                    self._orientdb_client._db_name),
                'CRAOrientDBHelper.get_tas')

        for ta in orientdb_response:
            ta_obj = TA(
                id_=MdlId(
                    ta.id),
                minimum_voice_bandwidth=Kbps(
                    ta.minimum_voice_bandwidth),
                minimum_safety_bandwidth=Kbps(
                    ta.minimum_safety_bandwidth),
                scaling_factor=ta.scaling_factor,
                c=ta.c,
                utility_threshold=ta.utility_threshold)
            candidate_tas.append(ta_obj)

        return candidate_tas
