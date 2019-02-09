import os
import sys
from cp1.utils.orientdb_storage import OrientDBStorage
from cp1.utils.orientdb_retrieval import OrientDBRetrieval
from cp1.utils.orientdb_importer import OrientDBImporter
from cp1.utils.orientdb_exporter import OrientDBExporter
from cp1.processing.algorithm import Algorithm
from cp1.processing.process_bandwidth import ProcessBandwidth
from cp1.data_objects.mdl.frequency import Frequency
from cp1.data_objects.mdl.txop import TxOp
from cp1.data_objects.mdl.microseconds import Microseconds
from cp1.data_objects.mdl.milliseconds import Milliseconds
from cp1.data_objects.mdl.schedule import Schedule
from cp1.data_objects.mdl.txop_timeout import TxOpTimeout
from cp1.data_objects.constraints.constraints_object import ConstraintsObject
from cp1.data_objects.mdl.mdl_id import MdlId
from cp1.data_objects.mdl.kbps import Kbps
from cp1.data_objects.constraints.ta import TA
from cp1.data_objects.constraints.channel import Channel
from brass_api.orientdb.orientdb_helper import BrassOrientDBHelper
from brass_api.orientdb.brass_orientdb_client import BrassOrientDBClient
from cp1.common.logger import Logger


# Setup
logger = Logger().logger
scenario_database_name = 'cra_scenarios'
constraints_database_name = 'cra_constraints'
output_file = 'mdl_files/CRA_Scenarios_After_Adaptation.xml'
mdl_file = os.path.abspath('mdl_files/CRA_Scenarios_Before_Adaptation.xml')
brass_config_file = os.path.abspath('../../../conf/brass_config.json')
cra_config_file = os.path.abspath('../../../conf/cra_config.json')
bandwidth_file = os.path.abspath('../../../conf/mdl_ids.json')

scenario_orientdb = OrientDBStorage(
    database_name=scenario_database_name,
    config_file=brass_config_file)

constraints_orientdb = OrientDBRetrieval(
    database_name=constraints_database_name,
    config_file=brass_config_file
)

logger.info('***************************Challenge Problem 1 Started*********************')
logger.info('***************************Retrieving Constraints...***********************')
constraints_object = constraints_orientdb.get_constraints()
logger.debug(constraints_object)

logger.info('***************************Optimizing Schedule...**************************')
algorithm = Algorithm(constraints_object)
new_schedule = algorithm.optimize()

logger.info('***************************Processing Bandwidth...*************************')
process_bandwidth = ProcessBandwidth(constraints_object, bandwidth_file, up_ratio=0.5)
bandwidth_rates = process_bandwidth.process()
logger.info(bandwidth_rates)

logger.info('***************************Importing MDL file...***************************')
logger.info('Importing {0} into {1}'.format(mdl_file, scenario_database_name))
logger.info('Parsing MDL file into intermediary data object...')
importer = OrientDBImporter(scenario_database_name, mdl_file, brass_config_file)
importer.import_xml()
importer.orientDB_helper.close_database()

logger.info('***************************Updating MDL File Bandwidth...******************')
scenarios_orientdb_helper.open_database()
scenarios_orientdb_helper.update_bandwidth(bandwidth_rates)
logger.info('***************************Updating MDL File Schedule...*******************')
scenarios_orientdb_helper.update_schedule(new_schedule)
scenarios_orientdb_helper.close_database()

logger.info('***************************Exporting MDL File...***************************')
logger.info('Exporting {0} to {1}'.format(scenario_database_name, output_file))
exporter = OrientDBExporter(scenario_database_name, output_file, brass_config_file)
exporter.export_xml()
exporter.orientDB_helper.close_database()

logger.info('***************************Challenge Problem 1 Complete********************')
logger.info('***************************************************************************')
logger.info('***************************************************************************')
logger.info('***************************************************************************\n\n\n')
