import logging
log = logging.getLogger(__name__)

import time

import tor.client.ClientSettings as cs
from tor.base.utils import Utils

if cs.ON_RASPI:
    from ina219 import INA219

class InaManager:
    def __init__(self, brightness=None):
        self.ina = INA219(cs.INA_SHUNT_OHMS)
        self.ina.configure()

    def sleep(self):
        self.ina.sleep()

    def wake(self):
        self.ina.wake()

    def magnetHasContact(self):
        log.info(f"t_INA: {time.time()}")
        val = self.ina.current()
        numTries = 0
        while val == 0.0 and numTries < cs.INA_NUM_RESET_TRIES:
            log.info(f"t_INA: {time.time()}")
            self.ina.reset()
            self.ina.configure()
            val = self.ina.current()
            numTries += 1
        log.info(f"INA current: {val}")
        hasContact = val > cs.INA_CURRENT_THRESHOLD
        log.info(f"status: {hasContact}")
        return hasContact

