import brass_api.orientdb.orientdb_sql as sql
from brass_api.translator.orientdb_importer import OrientDBXMLImporter as MDLImporter
from brass_api.translator.orientdb_exporter import OrientDBXMLExporter as MDLExporter
from cra.common.exception_class import NodeNotFoundException
from cra.utils.logger import Logger
from brass_api.orientdb.orientdb_helper import BrassOrientDBHelper
from cra.mdl_data.mdl_frequency import MDLFrequency


logger = Logger().logger


class OrientDBHelper(BrassOrientDBHelper):
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
        logger.debug('Importing mdl file %s into database %s', mdl_file, database_name)
        importer = MDLImporter(databaseName=database_name, configFile=config_file, mdlFile=mdl_file)
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
        logger.debug('Exporting database %s into output file %s', database, output_file)
        exporter = MDLExporter(databaseName=database, configFile=config_file, xmlfile=output_file)
        exporter.export_xml()
        exporter.orientDB_helper.close_database()

    def modify_rate_value(self, orientdb_helper, slp_id, new_rate_value):
        """
        Modifies the Value field of a ServiceLevelProfile's Rate vertex.

        :param orientdb_helper: BRASS SwRI provided database helper object.
        :type orientdb_helper: BrassOrientDBHelper

        :param slp_id: ServiceLevelProfile ID.
        :type slp_id: str

        :param new_rate_value: New Value to update Rate with.
        :type new_rate_value: int
        """
        logger.debug("Adjusting bandwidth:\n[slp_id: %s]\n[new_rate_value: %s]", slp_id, new_rate_value)

        rate_node = get_rate_node(orientdb_helper, slp_id, new_rate_value)

        value_field_name = 'Value'
        sql_update_statement = sql.condition_str(value_field_name, new_rate_value, '=')

        orientdb_helper.update_node(rate_node._rid, sql_update_statement)

    def get_rate_node(self, orientdb_helper, slp_id):
        """
        Retrieves Rate child of specified ServiceLevelProfile.

        :param orientdb_helper: BRASS SwRI provided database helper object.
        :type orientdb_helper: BrassOrientDBHelper

        :param slp_id: Key to identify ServiceLevelProfile.
        :type slp_id: str

        :returns rate_node: A PyOrient node
        """
        slp_node = None
        rate_node = None

        slp_nodes = orientdb_helper.get_nodes_by_type('ServiceLevelProfile')
        for n in slp_nodes:
            if n.ID == slp_id:
                slp_node = n

        if slp_node is None:
            raise NodeNotFoundException("Unable to find slp_id: {0}".format(slp_id), 'get_rate_node')

        rate_class_name = 'Rate'
        rate_depth_from_slp = 4
        slp_children = orientdb_helper.get_connected_nodes(slp_node._rid, maxdepth=rate_depth_from_slp, filterdepth=rate_depth_from_slp)
        for n in slp_children:
            if n._class == rate_class_name:
                rate_node = n

        if rate_node is None:
            raise NodeNotFoundException("Unable to find rate child of slp_id: {0}".format(slp_id), 'get_rate_node')

        return rate_node

    def get_constraints(self, orientdb_helper):
        """
        Retrieves constraints from the provided database

        :param orientdb_helper: BRASS SwRI provided database helper object.
        :type orientdb_helper: BrassOrientDBHelper

        :returns constraints_object: A Constraints Object
        """
        return orientdb_helper.get_nodes_by_type('Constraint')

    def get_tas(self, orientdb_helper):
        """
        Retrieves constraints from the provided database

        :param orientdb_helper: BRASS SwRI provided database helper object.
        :type orientdb_helper: BrassOrientDBHelper

        :returns constraints_object: A Constraints Object
        """
        return orientdb_helper.get_nodes_by_type('TA')

    def get_channels(self, orientdb_helper):
        """
        Retrieves constraints from the provided database

        :param orientdb_helper: BRASS SwRI provided database helper object.
        :type orientdb_helper: BrassOrientDBHelper

        :returns constraints_object: A Constraints Object
        """
        return orientdb_helper.get_nodes_by_type('Channel')
