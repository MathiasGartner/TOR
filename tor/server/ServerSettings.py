import os
import platform
import sys

import tor.TORSettingsLocal as tsl

LOG_CONFIG_DIRECTORY = os.path.join(tsl.TOR_PROGRAM_DIRECTORY_SERVER, "config")
SERVER_LOG_CONFIG_FILEPATH = os.path.join(LOG_CONFIG_DIRECTORY, "logging.TORServer.yaml")
DASHBOARD_LOG_CONFIG_FILEPATH = os.path.join(LOG_CONFIG_DIRECTORY, "logging.Dashboard.yaml")

VERIFY_MAGNET_BY_CLIENTID = True
TOR_MAGNET_PICTURE_DIRECTORY = os.path.join(tsl.TOR_BASE_DIRECTORY_SERVER, "pictures")

#BOX_FORMATION = "3x3"
BOX_FORMATION = "3x3x3"
BOX_VIEW_COMPACT = False

STARTUP_JOB_DELAY_MINUTES = 2
STARTUP_JOB_PROGRAM_NAME = "Zorlu - default"

if sys.platform == "linux" and platform.platform() == "Linux-5.4.51-v7l+-armv7l-with-debian-10.4":
    ON_RASPI = True
else:
    ON_RASPI = False