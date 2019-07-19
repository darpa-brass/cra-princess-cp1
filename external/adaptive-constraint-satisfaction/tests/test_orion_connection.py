"""

test_orion_connection.py

This program tests connection to the orion server and
connection to a database on orion.


Author: Di Yao (di.yao@vanderbilt.edu)

"""


from lxml import etree
import os
import json
import sys
import pyorient

class Processor(object):
    def __init__(self, databaseName, configFile = 'config.json'):
        data_file= open(configFile, 'r')
        config_data = json.load(data_file)
        data_file.close()
        self.username = config_data['server']['username']
        self.password = config_data['server']['password']
        server = config_data['server']['address']
        port =  config_data['server']['port']
        self.client = pyorient.OrientDB(server, port)
        self.session_id = None #self.session_id = self.client.connect( self.username, self.password )

        self.db_name = databaseName
        self.db_username = None
        self.db_password = None
        if 'database' in config_data:
            if 'username' in config_data['database'] and 'password' in config_data['database']:
                self.db_username = config_data['database']['username']
                self.db_password = config_data['database']['password']

    def connectToServer(self):
        self.session_id = self.client.connect( self.username, self.password )
        print ('Client Session ID: {0}'.format(self.session_id))

    def openDatabase(self):
        """
        Opens the orientDB database.
        :argument:
        :return:
        """

        self.client.db_open(self.db_name, self.db_username, self.db_password)

    def closeDatabase(self):
        """
        Closes the orientDB database.
        :argument:
        :return:
        """

        self.client.db_close()


def main(database, configFile):
    """
    Instantiates a Processor object and passes in the orientDB database name.
    Calls runExample() on the processor object.
    Closes the orientDB database.

    :argument:
                database (str):     orientDB database name
                remotePlocal (str): remote or local database, not used currently
    :return:
    """

    import os

    if os.path.exists(configFile):
        processor=Processor(database, configFile)
        try:
            processor.connectToServer()
            print ('Successfully connected to orion server.')
        except:
            print ('Unexpected error - connecting to orion server: {0}'.format(sys.exc_info()[1]))
            exit(1)

        try:
            processor.openDatabase()
            print ('Successfully connected to database "{0}".'.format(database))
            result = processor.client.command('select * from V')
            print (result)


            processor.closeDatabase()
            processor.client.close()
        except:
            print ('Unexpected error - connecting to database:'.format(sys.exc_info()[0]))
            exit(1)
    else:
        print('{0} does not exit.'.format(configFile))


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        database = sys.argv[1]
        configFile = sys.argv[2]
    else:
        print('Not enough arguments. The script should be called as following: python test_orion_connection.py myOrientDbDatabase configFile.json')

    main(database, configFile)