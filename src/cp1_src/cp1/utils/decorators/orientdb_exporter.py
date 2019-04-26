"""orientdb_exporter.py

Decorator for :class:`brass_api.translator.orientdb_exporter`
Developed to provide a progress update while exporting MDL files.
Author: Tameem Samawi (tsamawi@cra.com)
"""
from brass_api.translator.orientdb_exporter import OrientDBXMLExporter
from cp1.common.logger import Logger

logger = Logger().logger


class OrientDBExporter(OrientDBXMLExporter):
    def __init__(self, databaseName, xmlfile, configFile='config.json'):
        self.export_count = 0
        return super(OrientDBExporter, self).__init__(databaseName=databaseName, xmlfile=xmlfile, configFile=configFile)

    def print_node(self, record, numberTabs=0):
        if(self.export_count == 0):
            logger.info('Exporting OrientDB Nodes...')
        elif(self.export_count % 100 == 0):
            logger.info('Exported {0} Nodes'.format(self.export_count))
        self.export_count += 1
        return super(OrientDBExporter, self).print_node(record=record, numberTabs=numberTabs)
