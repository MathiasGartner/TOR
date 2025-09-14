from tor.base.LogManager import getLogger
log = getLogger("InaManager")

import time

from tor.base.Singleton import Singleton
import tor.client.ClientSettings as cs

if cs.ON_RASPI:
    from ina219 import INA219
    from ina219 import DeviceRangeError

class InaManager(Singleton):
    def __init__(self, brightness=None):
        if hasattr(self, "_initialized") and self._initialized:
            log.warning("wanted to initialize InaManager again")
            return
        self._initialized = True

        self.__ina = None
        if cs.USE_INA:
            try:
                self.__ina = INA219(cs.INA_SHUNT_OHMS)
                self.__ina.configure(gain=INA219.GAIN_2_80MV)
                log.info("INA initialized")
            except Exception as e:
                log.error("Error while initializing INA")
                log.error("{}".format(repr(e)))
                self.__ina = None

    def close(self):
        self.reset()

    def configure(self):
        try:
            if self.__ina is not None:
                self.__ina.configure()
        except Exception as e:
            log.error("Error while configuring INA")
            log.error("{}".format(repr(e)))

    def reset(self):
        try:
            if self.__ina is not None:
                self.__ina.reset()
        except Exception as e:
            log.error("Error while resetting INA")
            log.error("{}".format(repr(e)))

    def sleep(self):
        try:
            if self.__ina is not None:
                self.__ina.sleep()
        except Exception as e:
            log.error("Error while sleeping INA")
            log.error("{}".format(repr(e)))

    def wake(self):
        try:
            if self.__ina is not None:
                self.__ina.wake()
        except Exception as e:
            log.error("Error while waking INA")
            log.error("{}".format(repr(e)))

    def current(self):
        val = 0.0
        try:
            if self.__ina is not None:
                val = self.__ina.current()
        except DeviceRangeError as e:
            log.warning("INA current overflow")
            log.warning("{}".format(repr(e)))
            val = cs.INA_OVERFLOW_VAL
        except Exception as e:
            log.error("Error while reading INA current")
            log.error("{}".format(repr(e)))
            val = cs.INA_OVERFLOW_VAL
        return val

    def magnetHasContact(self):
        hasContact = True
        if self.__ina is None:
            return True
        log.debug(f"t_INA: {time.time()}")
        val = self.current()
        numTries = 0
        while val == 0.0 and numTries < cs.INA_NUM_RESET_TRIES:
            numTries += 1
            log.debug(f"t_INA: {time.time()}")
            log.info(f"retry INA: val: {val}, numTries: {numTries}")
            self.reset()
            self.configure()
            val = self.current()
        log.info(f"INA current: {val}")
        hasContact = val > cs.INA_CURRENT_THRESHOLD
        log.info(f"magnet has contact: {hasContact}")
        return hasContact

