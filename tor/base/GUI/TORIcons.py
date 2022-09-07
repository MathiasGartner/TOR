import os

from PyQt5.QtGui import QPixmap, QIcon

APP_ICON = QIcon(os.path.join(os.path.dirname(__file__), "..", "..", "resources", "icon.svg"))

LED_RED = QPixmap(os.path.join(os.path.dirname(__file__), "..", "..", "resources", "led-red.png")).scaled(15, 15)
LED_GREEN = QPixmap(os.path.join(os.path.dirname(__file__), "..", "..", "resources", "led-green.png")).scaled(15, 15)
LED_GRAY = QPixmap(os.path.join(os.path.dirname(__file__), "..", "..", "resources", "led-gray.png")).scaled(15, 15)