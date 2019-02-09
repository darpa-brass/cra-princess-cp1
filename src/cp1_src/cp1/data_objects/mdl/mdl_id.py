"""

mdl_id.py

Data object representing Id's in MDL files as well as other data objects such as Channels. Forces Ids to be unique.
Author: Tameem Samawi (tsamawi@cra.com)
"""

from cp1.common.exception_class import MdlIdInitializationException
from cp1.data_objects.mdl.id_set import IdSet

class MdlId:
    def __init__(self, value):
        if not isinstance(value, str):
            raise MdlIdInitializationException('Must be str: value {0}'.format(
                value
            ), 'MdlId.__init__')
        if not value.strip():
            raise MdlIdInitializationException('Must not be empty: value {0}'.format(
                value
            ), 'MdlId.__init__')
        if value in IdSet().ids:
            raise MdlIdInitializationException('Must be unique: value {0}'.format(
                value
            ), 'MdlId.__init__')
        else:
            IdSet().ids.add(value)
            self.value = value

    def __str__(self):
        return 'MdlId: {0}'.format(self.value)

mdl = MdlId('hi')
