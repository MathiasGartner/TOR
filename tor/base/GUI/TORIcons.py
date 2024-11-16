import os

from PyQt5.QtGui import QPixmap, QIcon

APP_ICON = QIcon(os.path.join(os.path.dirname(__file__), "..", "..", "resources", "icon.svg"))

LED_RED = QPixmap(os.path.join(os.path.dirname(__file__), "..", "..", "resources", "led-red.svg")).scaled(16, 16)
LED_GREEN = QPixmap(os.path.join(os.path.dirname(__file__), "..", "..", "resources", "led-green.svg")).scaled(16, 16)
LED_GRAY = QPixmap(os.path.join(os.path.dirname(__file__), "..", "..", "resources", "led-gray.svg")).scaled(16, 16)