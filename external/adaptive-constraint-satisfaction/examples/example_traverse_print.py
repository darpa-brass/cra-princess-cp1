"""

example_traverse_print.py

This program contains code to grab the root MDL vertex (MDLRoot) in an orientDB database
then perform a depth-first traversal using "Containment" type of edges from the root vertex.
Each vertex's name and its properties are printed out during the traversal.

TODO: Add traversal of "Reference" type of edges.

Author: Di Yao (di.yao@vanderbilt.edu), Joseph Hite (joseph.e.hite@vanderbilt.edu)

"""

import sys
import os
api_path = os.path.join(os.getcwd(), 'src', 'brass_api_src')
sys.path.append(api_path)
from brass_api.orientdb.orientdb_helper import BrassOrientDBHelper
import brass_api.orientdb.orientdb_sql as sql


def createTabString(number_tabs):
    s = ''
    i = 1
    while i <= number_tabs:
        s += ' '
        i += 1
    return s


'''
orientDB record print function
'''


def printOrientRecord(record):
    """
    Prints a OrientRecord returned by orientDB query.

    :argument:
                record (OrientRecord):  an orientDB record containg vertex information
    :return:
    """

    record_str = []
    for key in record.oRecordData.keys():
        if 'Containment' not in key and 'Reference' not in key:
            record_str.append('{0}:{1} '.format(key, record.oRecordData[key]))

    print("{0}{1}{2}".format(record._class, createTabString(30 - len(record._class)), str(record_str)))
    # self.textFile.write("{0}{1}{2}\n".format(record._class, createTabString(30 - len(record._class)), str(recordStr)))


def main(database=None, config_file=None):
    """
    Connects to OrientDB database, discovers the 'TxOp' Children of 'RadioLinks', and modifies the start and end times
    :param (str) database: the name of the OrientDB database
    :param (str) config_file: path to the config file for OrientDB
    :return:
    """
    print('****************       Update RadioLink Schedule         ****************')

    processor = BrassOrientDBHelper(database, config_file)
    processor.open_database(over_write=False)

    select_radio = sql.select_sql('RadioLink')
    RadioLink_nodes = processor.run_query(select_radio)
    for node in RadioLink_nodes:
        print('>>>>>>> {0} : {1}'.format(node._rid, node.Name))
        printOrientRecord(node)
    select_radio = '(' + select_radio + ')'
    traverse_radio = sql.traverse_sql(select_radio, direction='in', edgetype='Containment')
    TxOp_conditional = sql.condition_str(lh='class', rh='TxOp', op='=')
    TxOp_select = sql.select_sql(traverse_radio, [TxOp_conditional])
    TxOp_nodes = processor.run_query(TxOp_select)

    # TxOp_nodes = processor.get_nodes_by_type('TxOp')

    for node in TxOp_nodes:
        print(node)
        new_startusec = sql.condition_str('StartUSec', str(int(node.StartUSec) + 105), '=')
        new_stopusec = sql.condition_str('StopUSec', str(int(node.StopUSec) + 105), '=')
        processor.update_node(node._rid, new_startusec, new_stopusec)
    print('Post Modification')
    TxOp_nodes = processor.get_nodes_by_type('TxOp')

    for node in TxOp_nodes:
        print(node)
    processor.close_database()


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        database = sys.argv[1]
        config_file = sys.argv[2]
    else:
        sys.exit(
            'Not enough arguments. The script should be called as following: '
            'python example_simple.py myOrientDbDatabase remote')
    main(database, config_file)
