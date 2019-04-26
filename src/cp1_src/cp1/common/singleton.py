"""singleton.py

Module that holds singleton class objects which can be extended.
Author: Tameem Samawi (tsamawi@cra.com)
"""
from abc import ABCMeta


class SingletonABCMeta(ABCMeta):
    """Singleton class extended by any abstract class that should be singletons.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                SingletonABCMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Singleton(type):
    """Singleton class extended by any class that should be singleton.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
