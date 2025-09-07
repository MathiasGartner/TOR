import os

from PyQt5.QtGui import QPixmap, QIcon

APP_ICON = QIcon(os.path.join(os.path.dirname(__file__), "..", "..", "resources", "icon.svg"))

LED_RED = os.path.join(os.path.dirname(__file__), "..", "..", "resources", "led-red.svg")
LED_GREEN = os.path.join(os.path.dirname(__file__), "..", "..", "resources", "led-green.svg")
LED_GRAY = os.path.join(os.path.dirname(__file__), "..", "..", "resources", "led-gray.svg")

ICON_ADD = os.path.join(os.path.dirname(__file__), "..", "..", "resources", "icon-add.svg")
ICON_CLOSE = os.path.join(os.path.dirname(__file__), "..", "..", "resources", "icon-close.svg")
ICON_INFO = os.path.join(os.path.dirname(__file__), "..", "..", "resources", "icon-info.svg")
ICON_OK = os.path.join(os.path.dirname(__file__), "..", "..", "resources", "icon-ok.svg")
ICON_START = os.path.join(os.path.dirname(__file__), "..", "..", "resources", "icon-start.svg")