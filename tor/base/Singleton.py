import logging
log = logging.getLogger(__name__)
logSerial = logging.getLogger("serial")

import abc
import threading

class Singleton(abc.ABC):
    _instances = {}
    _locks = {}

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            # ensure a lock exists per subclass
            if cls not in cls._locks:
                cls._locks[cls] = threading.Lock()

            with cls._locks[cls]:
                if cls not in cls._instances:
                    cls._instances[cls] = super().__new__(cls)
        else:
            log.warning(f"wanted to create {cls} again")
        return cls._instances[cls]

    @classmethod
    def resetInstance(cls):
        """Destroy the singleton instance for this class"""
        if cls in cls._locks:
            with cls._locks[cls]:
                instance = cls._instances.get(cls)
                if instance:
                    instance.close()
                    cls._instances.pop(cls, None)

    @abc.abstractmethod
    def close(self):
        pass