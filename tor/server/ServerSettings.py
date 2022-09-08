import logging
import os

import tor.TORSettingsLocal as tsl

SERVER_LOG_LEVEL = logging.INFO

VERIFY_MAGNET_BY_CLIENTID = False
TOR_MAGNET_PICTURE_DIRECTORY = os.path.join(tsl.TOR_BASE_DIRECTORY_SERVER, "pictures")