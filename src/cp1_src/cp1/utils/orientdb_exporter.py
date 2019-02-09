from brass_api.translator.orientdb_exporter import OrientDBXMLExporter
from cp1.common.logger import Logger

logger = Logger().logger


class OrientDBExporter(OrientDBXMLExporter):
    def __init__(self, databaseName, xmlfile, configFile = 'config.json'):
        return super(OrientDBExporter, self).__init__(databaseName=databaseName, xmlfile=xmlfile, configFile=configFile)

    def print_node(self, record, numberTabs=0):
        logger.info('Exporting {0}'.format(record.uid))
        return super(OrientDBExporter, self).print_node(record=record, numberTabs=numberTabs)
