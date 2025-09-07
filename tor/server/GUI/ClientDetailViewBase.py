from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import QCheckBox, QLabel, QPushButton, QWidget

from tor.base import DBManager
from tor.base.GUI import TORIcons
from tor.server.TORCommands import TORCommands

import tor.TORSettings as ts

class ClientDetailViewBase(QWidget):
    def __init__(self):
        super().__init__()

        self.clientDetails = None

        # Status
        self.svgIsOnline = QSvgWidget(TORIcons.LED_RED)
        self.lblCurrentJob = QLabel()
        self.lblResultAverage = QLabel()
        self.lblResultStddev = QLabel()

        # LEDs
        self.btnTurnOnLEDs = QPushButton()
        self.btnTurnOnLEDs.setText("ON")
        self.btnTurnOnLEDs.clicked.connect(self.btnTurnOnLEDs_clicked)
        self.btnTurnOffLEDs = QPushButton()
        self.btnTurnOffLEDs.setText("OFF")
        self.btnTurnOffLEDs.clicked.connect(self.btnTurnOffLEDs_clicked)

        # Options
        self.chkUserMode = QCheckBox()
        self.chkUserMode.clicked.connect(self.chkUserMode_clicked)
        self.chkIsActivated = QCheckBox()
        self.chkIsActivated.clicked.connect(self.chkIsActivated_clicked)
        self.chkUseSchedule = QCheckBox()
        self.chkUseSchedule.clicked.connect(self.chkUseSchedule_clicked)

        # Client Service
        self.btnStartClientService = QPushButton()
        self.btnStartClientService.setText("Start")
        self.btnStartClientService.clicked.connect(self.btnStartClientService_clicked)
        self.btnStopClientService = QPushButton()
        self.btnStopClientService.setText("Stop")
        self.btnStopClientService.clicked.connect(self.btnStopClientService_clicked)

    def btnTurnOnLEDs_clicked(self):
        self.clientDetails.sendMsgToStatusManager(TORCommands.MSG_CLIENT_TURN_ON_LEDS, timeout=ts.STATUS_TIMEOUT_LED)

    def btnTurnOffLEDs_clicked(self):
        self.clientDetails.sendMsgToStatusManager(TORCommands.MSG_CLIENT_TURN_OFF_LEDS, timeout=ts.STATUS_TIMEOUT_LED)

    def chkUserMode_clicked(self, checked):
        self.clientDetails.AllowUserMode = checked
        DBManager.setUserModeEnabled(self.clientDetails.Id, checked)

    def chkIsActivated_clicked(self, checked):
        self.clientDetails.IsActive = checked
        DBManager.setClientIsActive(self.clientDetails.Id, checked)

    def chkUseSchedule_clicked(self, checked):
        self.clientDetails.UseSchedule = checked
        DBManager.setClientUseSchedule(self.clientDetails.Id, checked)

    def refreshClientStatus(self):
        #to be implemented in subclasses
        pass

    def btnStartClientService_clicked(self):
        self.clientDetails.sendMsgToStatusManager(TORCommands.MSG_CLIENT_SERVICE_START, ts.STATUS_TIMEOUT_SERVICE)
        self.clientDetails.getClientStatus()
        self.refreshClientStatus()

    def btnStopClientService_clicked(self):
        self.clientDetails.sendMsgToStatusManager(TORCommands.MSG_CLIENT_SERVICE_STOP, ts.STATUS_TIMEOUT_SERVICE)
        self.clientDetails.getClientStatus()
        self.refreshClientStatus()
