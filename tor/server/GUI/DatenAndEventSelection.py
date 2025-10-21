from PyQt5.QtCore import Qt, QDateTime, QDate, QTime
from PyQt5.QtWidgets import QCheckBox, QLabel, QPushButton, QWidget, QGroupBox, QHBoxLayout, QDateTimeEdit, QComboBox

from tor.base import DBManager

class DatenAndEventSelection(QWidget):
    def __init__(self, onUpdate, customElements=None):
        super().__init__()

        grpFilter = QGroupBox("Select Data to Display")
        layFilter = QHBoxLayout()

        self.chkTime = QCheckBox()
        self.chkTime.clicked.connect(self.chkTime_clicked)
        self.timStart = QDateTimeEdit(self)
        self.timStart.setCalendarPopup(True)
        self.timStart.setDateTime(QDateTime(QDate(2025, 10, 21), QTime(5, 0)))
        self.timEnd = QDateTimeEdit(self)
        self.timEnd.setCalendarPopup(True)
        self.timEnd.setDateTime(QDateTime.currentDateTime().addSecs(3600*3))

        self.chkEvent = QCheckBox()
        self.chkEvent.clicked.connect(self.chkEvent_clicked)
        self.cmbEvent = QComboBox()
        eventSources = DBManager.getEventSources()
        for e in eventSources:
            self.cmbEvent.addItem(e.Source, e.Source)
        self.btnUpdate = QPushButton("Update Plot")
        self.btnUpdate.clicked.connect(onUpdate)

        self.chkTime.setChecked(False)
        self.timStart.setEnabled(False)
        self.timEnd.setEnabled(False)
        self.chkEvent.setChecked(True)
        self.cmbEvent.setEnabled(True)

        if customElements is not None:
            for e in customElements:
                layFilter.addWidget(e)
            layFilter.addSpacing(50)
        layFilter.addWidget(self.chkTime)
        layFilter.addWidget(QLabel("Start:"))
        layFilter.addWidget(self.timStart)
        layFilter.addWidget(QLabel("End:"))
        layFilter.addWidget(self.timEnd)
        layFilter.addSpacing(50)
        layFilter.addWidget(self.chkEvent)
        layFilter.addWidget(QLabel("Event:"))
        layFilter.addWidget(self.cmbEvent)
        layFilter.addSpacing(50)
        layFilter.addWidget(self.btnUpdate)
        layFilter.addStretch(1)
        grpFilter.setLayout(layFilter)

        layMain = QHBoxLayout()
        layMain.addWidget(grpFilter)
        self.setLayout(layMain)

    def chkTime_clicked(self, checked):
        self.timStart.setEnabled(checked)
        self.timEnd.setEnabled(checked)

    def chkEvent_clicked(self, checked):
        self.cmbEvent.setEnabled(checked)

    def getDateAndEvent(self):
        start = self.timStart.dateTime().toString(Qt.ISODate) if self.chkTime.isChecked() else None
        end = self.timEnd.dateTime().toString(Qt.ISODate) if self.chkTime.isChecked() else None
        event = self.cmbEvent.currentText() if self.chkEvent.isChecked() else None
        return start, end, event