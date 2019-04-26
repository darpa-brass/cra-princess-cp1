"""mdl_id.py

Data object representing IDs in MDL files. Forces IDs to be unique by using IdSet.
Author: Tameem Samawi (tsamawi@cra.com)
"""
from cp1.data_objects.mdl.id_set import IdSet


class MdlId:
    def __init__(self, value):
        IdSet().ids.add(value)
        self.value = value

    def __str__(self):
        return 'MdlId: {0}'.format(self.value)

    @classmethod
    def clear(cls):
        IdSet().ids.clear()
