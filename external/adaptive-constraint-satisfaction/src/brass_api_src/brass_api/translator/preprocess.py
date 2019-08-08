import shutil
import os

from brass_api.common.exception_class import BrassException

def create_preprocessor(xml_file):
    '''
    Returns a MDLPreprocessor or a VICTORYPreprocessor.

    :param xml_file:
    :return:
    '''

    if os.path.exists(xml_file):
        infile = open(xml_file, 'r')
        first_line = infile.readline().rstrip()
        second_line = infile.readlines()[0].rstrip()
        if 'MDL' in first_line:
            return MDLPreprocessor(xml_file)
        elif 'VCL' in second_line:
            return VICTORYPreprocessor(xml_file)
    else:
        return None


class Preprocessor(object):
    def __init__(self, xml_file):
        self.original_xml_file = xml_file
        self.orientdb_xml_file = self.original_xml_file + '.orientdb'
        self._schema = None

    def create_orientdb_xml(self):
        if os.path.exists(self.original_xml_file):
            shutil.copy2(self.original_xml_file, self.orientdb_xml_file)

    def remove_orientdb_xml(self):
        if os.path.exists(self.orientdb_xml_file):
            os.remove(self.orientdb_xml_file)

    def preprocess_xml(self):
        self.create_orientdb_xml()


class MDLPreprocessor(Preprocessor):
    def __init__(self, xml_file):
        super().__init__(xml_file)

    def preprocess_xml(self):
        super().preprocess_xml()

        self.remove_mdl_root_tag_attr()

        self.validate_mdl(self.orientdb_xml_file, self._schema)

    def add_mdl_root_tag_attr(self, mdl_schema):
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

    def remove_mdl_root_tag_attr(self):
        """
        Removes the xml attributes of the <MDLRoot> in the xmlfile
        as all the inclusions of tmats xsd files causes parsing to fail.
        The modified xml is saved inline.

        :param str xmlfile:     name and path of xml file
        :return:                the string "<MDLRoot>"
        """
        import fileinput, re

        mdl_schema = None
        mdl_root_str = None

        for lines in fileinput.FileInput(self.orientdb_xml_file, inplace=1):
            if lines.startswith('<MDLRoot'):
                print('<MDLRoot>')
                mdl_root_str = lines
            else:
                print (lines, end='')

        matchObj = re.search('MDL_(.*)xsd', mdl_root_str)
        if matchObj is not None:
            mdl_schema = matchObj.group(0)

        self._schema = mdl_schema

    def validate_mdl(self, xmlfile_path, mdl_schema):
        """
        Validates a xml file given by xmlfile_path against the mdl_schema.

        Todo: Still to need to make this work for the MDL exporter.

        :param str xmlfile_path:        name and path of xml file to validate
        :param str mdl_schema:          name of mdl_schema
        :return Boolean status:         result of validation (True or False)
        :raises BrassException:         throws any exception encountered
        """
        from lxml import etree

        BASE_DIR = os.path.dirname(os.path.realpath(__file__))
        mdl_schema = "{0}/../include/mdl_xsd/{1}".format(BASE_DIR, mdl_schema)

        status = None
        try:
            schema_doc = etree.parse(mdl_schema)
            schema = etree.XMLSchema(schema_doc)

            with open(xmlfile_path) as f:
                doc = etree.parse(f)

            status = schema.validate(doc)

        except etree.XMLSchemaParseError as e:
            status = False
            raise BrassException('Invalid MDL Schema File: ' + e.message, 'xml_util.validate_mdl')
        except etree.DocumentInvalid as e:
            status = False
            raise BrassException('Invalide MDL XML File: ' + e.message, 'xml_util.validate_mdl')
        finally:
            return status

class VICTORYPreprocessor(Preprocessor):
    def __init__(self, xml_file):
        super().__init__(xml_file)

    def preprocess_xml(self):
        super().preprocess_xml()

        self.remove_vcl_root_tag_attr()

        self.remove_vcl_namespace()

    def remove_vcl_namespace(self):
        """
        Removes vcl namespace from the root, configGroup, and ConfigItem keys in xml
        """
        import fileinput

        for lines in fileinput.FileInput(self.orientdb_xml_file, inplace=1):
            stripped_line = lines.strip()
            if stripped_line.startswith('<vcl:'):

                lines = lines.replace('<vcl:', '<', 1)
                print(lines)
            elif stripped_line.startswith('</vcl:'):
                lines = lines.replace('</vcl:', '</')
                print(lines)
            else:
                print(lines, end='')


    def remove_vcl_root_tag_attr(self):
        """
        Removes the xml attributes of the <MDLRoot> in the xmlfile
        as all the inclusions of tmats xsd files causes parsing to fail.
        The modified xml is saved inline.

        :param str xmlfile:     name and path of xml file
        :return:                the string "<MDLRoot>"
        """
        import fileinput, re

        mdl_schema = None
        mdl_root_str = None

        for lines in fileinput.FileInput(self.orientdb_xml_file, inplace=1):
            if lines.startswith('<vcl:VCL'):
                print('<VCL>')
                mdl_root_str = lines
            else:
                print(lines, end='')

        matchObj = re.search('VICTORYConfigurationLanguage(.*)xsd', mdl_root_str)
        if matchObj is not None:
            mdl_schema = matchObj.group(0)

        self._schema = mdl_schema

    def add_vcl_root_tag_attr(self, vcl_schema):
        """
        Creates a string for <MDLRoot> that includes tmats xsd files mdl schema xsd files.
        These attributes are removed during importing because they caused xml parsing to fail.

        :param str vcl_schema:      name of the mdl schema file
        :return:                    a <MDLRoot> string containing all the includes and correct MDL schema version
        """
        vcl_root_str = '<VCL xmlns:vcl="http://www.victory-standards.org/Schemas/VICTORYConfigurationLanguage.xsd"\
                        xmlns:vmt="http://www.victory-standards.org/Schemas/VICTORYManagementTypes.xsd"\
                        xmlns:vst="http://www.victory-standards.org/Schemas/VICTORYSharedTypes.xsd"\
                        xmlns:tns="http://www.w3.org/2003/05/soap-envelope"\
                        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\
                        xsi:schemaLocation="http://www.victory-standards.org/Schemas/VICTORYConfigurationLanguage.xsd file:/Volumes/Projects/10-23360_USAF_ROME/Shared/Scenarios/VICTORY%20Challenge%20Problem/Scenario%201/Scenario%201%20-%2020180328/VICTORYConfigurationLanguage.xsd">'
        return vcl_root_str
