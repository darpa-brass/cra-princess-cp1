"""

example_traverse_print.py

This program contains code to grab the root MDL vertex (MDLRoot) in an orientDB database
then perform a depth-first traversal using "Containment" type of edges from the root vertex.
Each vertex's name and its properties are printed out during the traversal.

Author: Joseph Hite (joseph.e.hite@vanderbilt.edu)

"""

import sys
import os
api_path = os.path.join(os.getcwd(), 'src', 'brass_api_src')
sys.path.append(api_path)
from brass_api.translator.orientdb_exporter import OrientDBXMLExporter as MDLExporter
from brass_api.translator.orientdb_importer import OrientDBXMLImporter as MDLImporter

def main(database=None, config_file=None, mdl_file=None):
    """
    Connects to OrientDB database, discovers the 'TxOp' Children of 'RadioLinks', and modifies the start and end times
    :param (str) database: the name of the OrientDB database
    :param (str) config_file: path to the config file for OrientDB
    :return:
    """
    print('****************       Importing {0}          ****************'.format(mdl_file))
    importer = MDLImporter(databaseName=database, configFile=config_file, mdlFile=mdl_file)
    importer.import_xml()
    importer.orientDB_helper.close_database()

    exporter = MDLExporter(databaseName=database, xmlfile="import_export_example.xml", configFile=config_file)
    exporter.export_xml()
    exporter.orientDB_helper.close_database()


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        database = sys.argv[1]
        config_file = sys.argv[2]
        mdl_file = sys.argv[3]
    else:
        sys.exit(
            'Not enough arguments. The script should be called as following: python example_simple.py myOrientDbDatabase remote')
    main(database, config_file, mdl_file)
