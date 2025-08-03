import os

import tor.TORSettingsPrivate as tsp
import tor.TORSettingsLocal as tsl

VERSION_TOR = "1.25.0"

DB_HOST = tsp.DB_HOST
DB_USER = tsp.DB_USER
DB_PASSWORD = tsp.DB_PASSWORD

SEND_MAIL = True
MAIL_USERNAME = "thetransparencyofrandomness@gmail.com"
MAIL_OAUTH_FILE = os.path.join(tsl.TOR_PROGRAM_DIRECTORY_SERVER, "resources", "gmail_oauth2.json")
#MAIL_RECIPIENTS = ["mathiasgartner@gmx.at"]
#MAIL_RECIPIENTS = [MAIL_USERNAME, "mathiasgartner@gmx.at"]
MAIL_RECIPIENTS = [MAIL_USERNAME, "mathiasgartner@gmx.at", "vera.tolazzi@gmx.at"]

VERIFY_MAGNET_TFMODELFILE = os.path.join(tsl.TOR_POSITION_VERIFICATION_MODEL_DIRECTORY_SERVER, "position_verification.tflite")
VERIFY_MAGNET_TFMODELFILE_ID = os.path.join(tsl.TOR_POSITION_VERIFICATION_MODEL_DIRECTORY_SERVER, "position_verification_{}.tflite")

SERVER_IP = tsl.SERVER_IP
SERVER_PORT = tsl.SERVER_PORT

STATUS_PORT = tsl.STATUS_PORT
STATUS_TIMEOUT = 1.0
STATUS_TIMEOUT_LED = 4.0
STATUS_TIMEOUT_SERVICE = 6.0
STATUS_TIMEOUT_TOR_SERVER = 4.0

MAX_MSG_LENGTH = 1024+424

CLIENT_IDS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 32]

#DICE_RESULT_EVENT_SOURCE = 'Test2021'
#DICE_RESULT_EVENT_SOURCE = 'Test2022'
#DICE_RESULT_EVENT_SOURCE = 'ArsElectronica2020'
#DICE_RESULT_EVENT_SOURCE = 'CyberArts2021'
#DICE_RESULT_EVENT_SOURCE = 'Kapelica2022'
#DICE_RESULT_EVENT_SOURCE = 'JMAF2022'
#DICE_RESULT_EVENT_SOURCE = 'Test2024'
DICE_RESULT_EVENT_SOURCE = 'Test2025'
#DICE_RESULT_EVENT_SOURCE = 'Zorlu2025'