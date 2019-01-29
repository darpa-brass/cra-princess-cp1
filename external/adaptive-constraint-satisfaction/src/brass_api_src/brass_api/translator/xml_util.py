"""

Module contains xml serialization functions and xml validation function.

Author: Di Yao (di.yao@vanderbilt.edu)
"""

import pyorient
import os
from brass_api.common.exception_class import *

SKIP_PROPERTY_TAGS = ['uid', 'ID', 'IDREF', 'in_Containment', 'out_Containment', 'in_Reference', 'out_Reference', 'schema']


def create_tab_string(numberTabs):
    '''
    Print formatting function that creates a string consisting of
    tabs set by "numberTabs".

    :param int numberTabs:  Number of tabs
    :return:                A string containing tabs
    '''
    s = ''
    i = 1
    while i <= numberTabs:
        s += '\t'
        i += 1
    return s


def orient_record_to_xml(record, numberTabs):
    """
    Serializes OrientRecord to xml from a vertex and writes to the xml file.
    Serialization involves traversing through a vertex's properties.
    Opening xml tag is written in this function because "ID" and "IDREF"
    properties need to be written out as xml attributes and not as xml tag text.


    :param      OrientRecord record:  an orientDB record containing data about a vertex
    :param      int numberTabs:       number of tabs to indent before xml text
    :return:    A xml string of the record

    """
    xml_str_list = []

    if record._class == 'MDLRoot':
        if 'schema' in record.oRecordData:
            xml_str_list.append( add_mdl_root_tag_attr(record.oRecordData['schema']) )
        else:
            xml_str_list.append('<MDLRoot>')
        xml_str_list.append('\n')
    else:
        xml_str_list.append( "{0}<{1}".format(create_tab_string(numberTabs), record._class) )

        if 'ID' in record.oRecordData.keys():
            xml_str_list.append(' {0}="{1}"'.format('ID', record.oRecordData['ID']) )
        elif 'IDREF' in record.oRecordData.keys():
            xml_str_list.append(' {0}="{1}"'.format('IDREF', record.oRecordData['IDREF']) )

        xml_str_list.append( ">\n" )


    for key in record.oRecordData.keys():
        if key not in SKIP_PROPERTY_TAGS:
            xml_str_list.append( '{0}<{1}>{2}</{1}>\n'.format(create_tab_string(numberTabs+1), key, record.oRecordData[key] ) )

    return ''.join(xml_str_list)


'''
The root tag in a MDL XML file has some attributes that causes exceptions for lxml parser.
Therefore these attributes need to be removed by importer and added back in by the exporter. 
'''


def add_mdl_root_tag_attr(mdl_schema):
    """
    Creates a string for <MDLRoot> that includes tmats xsd files mdl schema xsd files.
    These attributes are removed during importing because they caused xml parsing to fail.

    :param str mdl_schema:      name of the mdl schema file
    :return:                    a <MDLRoot> string containing all the includes and correct MDL schema version
    """
    mdl_root_str = '<MDLRoot xmlns="http://www.wsmr.army.mil/RCC/schemas/MDL"\
    xmlns:tmatsCommon="http://www.wsmr.army.mil/RCC/schemas/TMATS/TmatsCommonTypes"\
    xmlns:tmatsP="http://www.wsmr.army.mil/RCC/schemas/TMATS/TmatsPGroup"\
    xmlns:tmatsD="http://www.wsmr.army.mil/RCC/schemas/TMATS/TmatsDGroup"\
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\
    xsi:schemaLocation="http://www.wsmr.army.mil/RCC/schemas/MDL {0}">'.format(mdl_schema)
    return mdl_root_str

