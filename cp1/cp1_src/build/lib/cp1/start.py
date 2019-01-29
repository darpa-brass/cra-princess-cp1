import os
from cp1.data_objects.mdl.frequency import Frequency
from cp1.data_objects.mdl.txop import TxOp
from cp1.data_objects.mdl.microseconds import Microseconds
from cp1.data_objects.mdl.milliseconds import Milliseconds
from cp1.data_objects.mdl.schedule import Schedule
from cp1.data_objects.mdl.txop_timeout import TxOpTimeout
from cra.orientdb.orientdb_helper import OrientDBHelper
from cp1.utils.orientdb_updates import OrientDBUpdates
from brass_api.orientdb.orientdb_helper import BrassOrientDBHelper
from brass_api.translator.orientdb_exporter import OrientDBXMLExporter


# Setup
mdl_file = os.path.abspath('CRA_Scenario_Before_Adaptation.xml')
scenario_database_name = 'cra_sample'
constraints_database_name = 'tas_and_constraints'
config_file = os.path.abspath('../../../../cra-princess-cp1/conf/brass_config.json')
output_file = 'CRA_Scenario_After_Adaptation.xml'


scenarios_orientdb_helper = OrientDBHelper(
    database_name=scenario_database_name,
    config_file=config_file)

constraints_orientdb_helper = OrientDBHelper(
    database_name=constraints_database_name,
    config_file=config_file
)

radio_key_down = 'TA_to_GndRadio'
radio_key_up = 'GndRadio_to_TA'

# Sample new transmission times
start_usec_1 = Microseconds(0)
stop_usec_1 = Microseconds(10000)
center_frequency_hz_1 = Frequency(49196000)
txop_timeout_1 = TxOpTimeout(255)
txop_1 = TxOp(start_usec_1, stop_usec_1, center_frequency_hz_1, txop_timeout_1)

start_usec_2 = Microseconds(11000)
stop_usec_2 = Microseconds(21000)
center_frequency_hz_2 = Frequency(49196000)
txop_timeout_2 = TxOpTimeout(255)
txop_2 = TxOp(start_usec_2, stop_usec_2, center_frequency_hz_2, txop_timeout_2)

start_usec_3 = Microseconds(22000)
stop_usec_3 = Microseconds(32000)
center_frequency_hz_3 = Frequency(49196000)
txop_timeout_3 = TxOpTimeout(255)
txop_3 = TxOp(start_usec_3, stop_usec_3, center_frequency_hz_3, txop_timeout_3)

start_usec_4 = Microseconds(33000)
stop_usec_4 = Microseconds(43000)
center_frequency_hz_4 = Frequency(49196000)
txop_timeout_4 = TxOpTimeout(255)
txop_4 = TxOp(start_usec_4, stop_usec_4, center_frequency_hz_4, txop_timeout_4)

start_usec_5 = Microseconds(44000)
stop_usec_5 = Microseconds(54000)
center_frequency_hz_5 = Frequency(49196000)
txop_timeout_5 = TxOpTimeout(255)
txop_5 = TxOp(start_usec_5, stop_usec_5, center_frequency_hz_5, txop_timeout_5)

start_usec_6 = Microseconds(55000)
stop_usec_6 = Microseconds(65000)
center_frequency_hz_6 = Frequency(49196000)
txop_timeout_6 = TxOpTimeout(255)
txop_6 = TxOp(start_usec_6, stop_usec_6, center_frequency_hz_6, txop_timeout_6)

start_usec_7 = Microseconds(66000)
stop_usec_7 = Microseconds(76000)
center_frequency_hz_7 = Frequency(49196000)
txop_timeout_7 = TxOpTimeout(255)
txop_7 = TxOp(start_usec_7, stop_usec_7, center_frequency_hz_7, txop_timeout_7)

start_usec_8 = Microseconds(77000)
stop_usec_8 = Microseconds(88000)
center_frequency_hz_8 = Frequency(49196000)
txop_timeout_8 = TxOpTimeout(255)
txop_8 = TxOp(start_usec_8, stop_usec_8, center_frequency_hz_8, txop_timeout_8)

start_usec_9 = Microseconds(89000)
stop_usec_9 = Microseconds(99000)
center_frequency_hz_9 = Frequency(49196000)
txop_timeout_9 = TxOpTimeout(255)
txop_9 = TxOp(start_usec_9, stop_usec_9, center_frequency_hz_9, txop_timeout_9)


new_schedule = Schedule(Milliseconds(100), Microseconds(1000))
new_schedule.add(radio_key_down, txop_1)
new_schedule.add(radio_key_up, txop_2)
new_schedule.add(radio_key_down, txop_3)
new_schedule.add(radio_key_up, txop_4)
new_schedule.add(radio_key_down, txop_5)
new_schedule.add(radio_key_up, txop_6)
new_schedule.add(radio_key_down, txop_7)
new_schedule.add(radio_key_up, txop_8)
new_schedule.add(radio_key_down, txop_9)

# Import MDL File
scenarios_orientdb_helper.import_mdl(scenario_database_name, config_file, mdl_file)

# Overwrite schedule
brass_orientdb_helper = BrassOrientDBHelper(scenario_database_name, config_file)
orientdb_updates = OrientDBUpdates(brass_orientdb_helper)
brass_orientdb_helper.open_database()
store_result = orientdb_updates.update_schedule(new_schedule.schedule)

# Export MDL File
exporter = OrientDBXMLExporter(scenario_database_name, output_file, config_file)
exporter.export_xml()
brass_orientdb_helper.close_database()
