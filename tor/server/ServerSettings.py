import logging
import os
import platform
import sys

import tor.TORSettingsLocal as tsl

SERVER_LOG_LEVEL = logging.INFO

VERIFY_MAGNET_BY_CLIENTID = False
TOR_MAGNET_PICTURE_DIRECTORY = os.path.join(tsl.TOR_BASE_DIRECTORY_SERVER, "pictures")

if sys.platform == "linux" and platform.platform() == "Linux-5.4.51-v7l+-armv7l-with-debian-10.4":
    ON_RASPI = True
else:
    ON_RASPI = False