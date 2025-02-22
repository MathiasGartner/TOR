import os

from PyQt5.QtGui import QPixmap, QIcon

APP_ICON = QIcon(os.path.join(os.path.dirname(__file__), "..", "..", "resources", "icon.svg"))

LED_RED = QPixmap(os.path.join(os.path.dirname(__file__), "..", "..", "resources", "led-red.svg")).scaled(16, 16)
LED_GREEN = QPixmap(os.path.join(os.path.dirname(__file__), "..", "..", "resources", "led-green.svg")).scaled(16, 16)
LED_GRAY = QPixmap(os.path.join(os.path.dirname(__file__), "..", "..", "resources", "led-gray.svg")).scaled(16, 16)

ICON_INFO = QPixmap(os.path.join(os.path.dirname(__file__), "..", "..", "resources", "icon-info.svg")).scaled(16, 16)
ICON_INFO_BTN = QIcon(ICON_INFO)

ICON_ADD = QPixmap(os.path.join(os.path.dirname(__file__), "..", "..", "resources", "icon-add.svg")).scaled(16, 16)
ICON_ADD_BTN = QIcon(ICON_ADD)

ICON_CLOSE = QPixmap(os.path.join(os.path.dirname(__file__), "..", "..", "resources", "icon-close.svg")).scaled(16, 16)
ICON_CLOSE_BTN = QIcon(ICON_CLOSE)

ICON_START = QPixmap(os.path.join(os.path.dirname(__file__), "..", "..", "resources", "icon-start.svg")).scaled(16, 16)
ICON_START_BTN = QIcon(ICON_START)