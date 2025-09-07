from PyQt5.QtWidgets import QPushButton
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtGui import QPainter, QCursor
from PyQt5.QtCore import QRectF, Qt

class SvgButton(QPushButton):
    def __init__(self, svg_path, text="", parent=None):
        super().__init__(text, parent)
        self._renderer = QSvgRenderer(svg_path)
        if not self.text():
            self.setFixedSize(16, 16)
        self.setCursor(Qt.PointingHandCursor)

    def setSvg(self, svg_path):
        self._renderer.load(svg_path)
        self.update()  # repaint

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform |
                               QPainter.HighQualityAntialiasing)

        if self.text():  # If button has text, paint normally + SVG
            super().paintEvent(event)

            # Draw icon to the left
            icon_size = min(self.height(), 24)
            target = QRectF(5, (self.height() - icon_size)/2, icon_size, icon_size)
            self._renderer.render(painter, target)
        else:  # Only icon, no text
            # Draw the SVG centered and filling the button
            target = QRectF(0, 0, self.width(), self.height())
            self._renderer.render(painter, target)

        painter.end()