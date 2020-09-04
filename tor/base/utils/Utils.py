import logging
log = logging.getLogger(__name__)

import time

def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))

def clamp255(n):
    return clamp(n, 0, 255)

def sleepUntilTimestamp(step, timestamps):
    sleepFor = timestamps[step] - time.time()
    log.info("sleep:", sleepFor)
    if sleepFor > 0:
        time.sleep(sleepFor)

def sleepUntilTimestamp(timestamp):
    sleepUntilTimestamp(0, [timestamp])