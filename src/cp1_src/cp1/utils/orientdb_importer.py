from brass_api.translator.orientdb_importer import OrientDBXMLImporter
from cp1.utils.orientdb_storage import OrientDBStorage
from cp1.common.logger import Logger

logger = Logger().logger


class OrientDBImporter(OrientDBXMLImporter):
    """
    Class responsible for importing mdl xml files into an orientdb database.
    :param      databaseName:
    :param      mdlFile:
    :param      configFile:
    """
    def __init__(self, databaseName, mdlFile, configFile = 'config.json'):
        self.loadrObject = []
        self.uniqueIdentifiers = {}

        self.orientDB_helper = OrientDBStorage(database_name=databaseName, config_file=configFile)
        self.mdlFile = mdlFile
        self.orientDB_helper.open_database(over_write=True)
        self._schema = None

    def import_xml(self):
        return super(OrientDBImporter, self).import_xml()
