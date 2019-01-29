"""

mdl_id.py

Data object representing Id's in MDL files as well as other data objects such as Channels.
Author: Tameem Samawi (tsamawi@cra.com)
"""

from cp1.common.exception_class import MdlIdInitializationError
from cp1.data_objects.mdl.id_set import IdSet


class MdlId:
    def __init__(self, value):
        if not isinstance(value, str):
            raise MdlIdInitializationError('Value must be a str: {0}'.format(
                value
            ), 'MdlId.__init__')
        if not value.strip():
            raise MdlIdInitializationError('Value must not be empty: {0}'.format(
                value
            ), 'MdlId.__init__')
        if value in IdSet().ids:
            raise MdlIdInitializationError('Value must be unique: {0}'.format(
                value
            ), 'MdlId.__init__')
        else:
            IdSet().ids.add(value)
            self.value = value
