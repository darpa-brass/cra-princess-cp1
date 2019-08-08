"""orientdb_exporter.py

Decorator for :class:`brass_api.translator.orientdb_importer`
Developed to provide a progress update while exporting MDL files.
Author: Tameem Samawi (tsamawi@cra.com)
"""
from brass_api.translator.orientdb_importer import OrientDBXMLImporter
from cp1.utils.orientdb.orientdb_session import OrientDBSession


class OrientDBImporter(OrientDBXMLImporter):
    def __init__(self, databaseName, mdlFile, configFile='config.json'):
        """
        Identical to :func:`OrientDBXMLImporter.__init__ <brass_api.translator.orientdb_importer.__init__>`
        but instantiates an instance of `cp1.utils.orientdb_session` as the underlying database connection
        instead of `brass_api.orientdb.orientdb_helper`.
        """
        self.loadrObject = []
        self.uniqueIdentifiers = {}

        self.orientDB_helper = OrientDBSession(
            database_name=databaseName, config_file=configFile, explicit=True)
        self.mdlFile = mdlFile
        self.orientDB_helper.open_database(over_write=True)
        self._schema = None

    def import_xml(self):
        return super(OrientDBImporter, self).import_xml()
