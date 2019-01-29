"""

id_list.py

Singleton object to store all IDs.
Author: Tameem Samawi (tsamawi@cra.com)
"""


from cp1.common.singleton import Singleton


class IdSet(metaclass=Singleton):
    def __init__(self):
        self.ids = set()
