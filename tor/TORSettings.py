import logging

import tor.TORSettingsPrivate as tsp
import tor.TORSettingsLocal as tsl

DB_HOST = tsp.DB_HOST
DB_USER = tsp.DB_USER
DB_PASSWORD = tsp.DB_PASSWORD

SERVER_IP = tsl.SERVER_IP
SERVER_PORT = tsl.SERVER_PORT

SERVER_LOG_LEVEL = logging.INFO

CLIENT_IDS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 32]

DICE_RESULT_EVENT_SOURCE = 'CyberArts2021'