import logging
import time
import os
import sys

from functools import partial

from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import QSizePolicy, QApplication, QMainWindow, QPushButton, QLabel, QTabWidget, QGridLayout, QWidget, QPlainTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, QGroupBox, QVBoxLayout, QHBoxLayout, QLayout, QRadioButton, QButtonGroup, QMessageBox, QCheckBox
from PyQt5.QtGui import QPixmap, QIcon, QPainter

app = QApplication(sys.argv)
app.setStyleSheet("* { font-size: 11px } QGroupBox { font-weight: bold; }")
window = None

class WaitCursor(object):
    def __enter__(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        if window is not None:
            window.setEnabled(False)
        app.processEvents()

    def __exit__(self, exc_type, exc_val, exc_tb):
        QApplication.restoreOverrideCursor()
        if window is not None:
            window.setEnabled(True)
        app.processEvents()

###################
### TOR imports ###
###################

from tor.base import DBManager
import tor.TORSettingsLocal as tsl
import tor.TORSettings as ts

###############
### logging ###
###############

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=ts.SERVER_LOG_LEVEL)
log = logging.getLogger(__name__)

class TORCommands:
    r'ssh -i {0} pi@{1} "sudo rm -r tor; sudo rm -r scripts"'
    SERVER_SSH_CONNECTION = "ssh -i {0} pi@{1}"
    CLIENT_SSH_CONNECTION = "ssh -i {0} pi@{1}"

    SERVER_SERVICE_START = "sudo systemctl daemon-reload; sudo systemctl restart TORServer"
    SERVER_SERVICE_STOP = "sudo systemctl stop TORServer"

    INTERACTIVE_START = "sudo systemctl daemon-reload; sudo systemctl restart TORInteractive"
    INTERACTIVE_STOP = "sudo systemctl stop TORInteractive"

    CLIENT_PING = "ping -i 0.2 -c 1 {}"

    CLIENT_SERVICE_START = "sudo systemctl daemon-reload; sudo systemctl restart TORClient"
    CLIENT_SERVICE_STOP = "sudo systemctl stop TORClient"

    CLIENT_TURN_ON_LEDS = "sudo torenv/bin/python3 -m tor.client.scripts.led 40 140 120 -b 20;"
    CLIENT_TURN_OFF_LEDS = "sudo torenv/bin/python3 -m tor.client.scripts.led 0 0 0;"

class TORIcons:
    APP_ICON = QIcon(os.path.join(os.path.dirname(__file__), r'../../resources/logo.png'))

    LED_RED = QPixmap(os.path.join(os.path.dirname(__file__), r'../../resources/led-red.png')).scaled(15, 15)
    LED_GREEN = QPixmap(os.path.join(os.path.dirname(__file__), r'../../resources/led-green.png')).scaled(15, 15)
    LED_GRAY = QPixmap(os.path.join(os.path.dirname(__file__), r'../../resources/led-gray.png')).scaled(15, 15)

class ClientDetails:
    def __init__(self):
        self.Id = -1
        self.IP = None
        self.Material = None
        self.Position = -1
        self.Latin = None
        self.AllowUserMode = False
        self.ServiceStatus = None
        self.CurrentJobCode = None
        self.ResultAverage = -1
        self.ResultStddev = -1
        self.IsOnline = False

    def IsBadStatistics(self):
        maxStddevResult = 0.17
        return self.ResultAverage < (3.5-maxStddevResult) or self.ResultAverage > (3.5+maxStddevResult) or self.ResultStddev > 1.77

    def getClientServiceStatus(self):
        self.ServiceStatus = "active" if self.Id % 2 == 0 else "inactive"

    def checkOnlineStatus(self):
        cmd = TORCommands.CLIENT_PING.format(self.IP)
        val = os.system(cmd)
        if val == 0:
            self.IsOnline = True
        else:
            self.IsOnline = False

    def executeSSH(self, cmd):
        cmdSSH = TORCommands.CLIENT_SSH_CONNECTION.format(tsl.PATH_TO_SSH_KEY, self.IP)
        cmdFull = cmdSSH + " \"" + cmd + "\""
        print("EXECUTE: {}".format(cmdFull))
        window.addStatusText("<font color=\"Blue\">{}</font>".format(cmdFull))

class ClientDetailView(QWidget):
    def __init__(self):
        super().__init__()

        self.clientDetails = None

        # Status
        self.lblIsOnline = QLabel()
        self.lblCurrentJob = QLabel()
        self.lblResultAverage = QLabel()
        self.lblResultStddev = QLabel()

        layClientStatus = QGridLayout()
        layClientStatus.setContentsMargins(0, 0, 0, 0)
        layClientStatus.addWidget(QLabel("online:"), 0, 0)
        layClientStatus.addWidget(self.lblIsOnline, 0, 1)
        layClientStatus.addWidget(QLabel("current job:"), 1, 0)
        layClientStatus.addWidget(self.lblCurrentJob, 1, 1)
        layClientStatus.addWidget(QLabel("avg result:"), 2, 0)
        layClientStatus.addWidget(self.lblResultAverage, 2, 1)
        layClientStatus.addWidget(QLabel("stddev:"), 3, 0)
        layClientStatus.addWidget(self.lblResultStddev, 3, 1)

        grpClientStatus = QGroupBox("Status")
        grpClientStatus.setLayout(layClientStatus)

        # LEDs
        self.btnTurnOnLEDs = QPushButton()
        self.btnTurnOnLEDs.setText("ON")
        self.btnTurnOnLEDs.setFixedSize(22, 22)
        self.btnTurnOnLEDs.clicked.connect(self.btnTurnOnLEDs_clicked)
        self.btnTurnOffLEDs = QPushButton()
        self.btnTurnOffLEDs.setText("OFF")
        self.btnTurnOffLEDs.setFixedSize(22, 22)
        self.btnTurnOffLEDs.clicked.connect(self.btnTurnOffLEDs_clicked)

        layLEDs = QHBoxLayout()
        layLEDs.setContentsMargins(0, 0, 0, 0)
        layLEDs.addWidget(self.btnTurnOnLEDs)
        layLEDs.addWidget(self.btnTurnOffLEDs)

        grpLEDs = QGroupBox("LEDs")
        grpLEDs.setLayout(layLEDs)

        # Options
        self.chkUserMode = QCheckBox()
        self.chkIsActivated = QCheckBox()

        layClientOptions = QGridLayout()
        layClientOptions.setContentsMargins(0, 0, 0, 0)
        layClientOptions.addWidget(QLabel("User mode enabled"), 0, 0)
        layClientOptions.addWidget(self.chkUserMode, 0, 1)
        layClientOptions.addWidget(QLabel("Client activated"), 1, 0)
        layClientOptions.addWidget(self.chkIsActivated, 1, 1)

        grpClientOptions = QGroupBox("Options")
        grpClientOptions.setLayout(layClientOptions)

        # TORCLient Service
        self.lblStatusClientService = QLabel()
        self.lblStatusClientService.setPixmap(TORIcons.LED_RED)
        self.btnStartClientService = QPushButton()
        self.btnStartClientService.setText("Start")
        #self.btnStartClientService.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.btnStartClientService.setFixedSize(45, 22)
        self.btnStartClientService.clicked.connect(self.btnStartClientService_clicked)
        self.btnStopClientService = QPushButton()
        self.btnStopClientService.setText("Stop")
        self.btnStopClientService.setFixedSize(45, 22)
        self.btnStopClientService.clicked.connect(self.btnStopClientService_clicked)

        layClientService = QHBoxLayout()
        layClientService.setContentsMargins(0, 0, 0, 0)
        layClientService.addWidget(self.lblStatusClientService)
        layClientService.addWidget(self.btnStartClientService)
        layClientService.addWidget(self.btnStopClientService)

        grpClientService = QGroupBox("TORClient service")
        grpClientService.setLayout(layClientService)

        # Main Layout
        layMain = QVBoxLayout()
        layMain.setContentsMargins(0, 0, 0, 0)
        layMain.addWidget(grpClientStatus)
        layMain.addWidget(grpLEDs)
        layMain.addWidget(grpClientOptions)
        layMain.addWidget(grpClientService)

        self.grpMainGroup = QGroupBox()
        self.grpMainGroup.setObjectName("ClientDetails")
        self.grpMainGroup.setStyleSheet(" QGroupBox#ClientDetails { font-size: 13px; } ")
        self.grpMainGroup.setTitle("Client #")
        self.grpMainGroup.setLayout(layMain)
        layMainGroup = QVBoxLayout()
        layMainGroup.setContentsMargins(0, 0, 0, 0)
        layMainGroup.addWidget(self.grpMainGroup)
        self.setLayout(layMainGroup)

    def btnTurnOnLEDs_clicked(self):
        self.clientDetails.executeSSH(TORCommands.CLIENT_TURN_ON_LEDS)

    def btnTurnOffLEDs_clicked(self):
        self.clientDetails.executeSSH(TORCommands.CLIENT_TURN_OFF_LEDS)

    def refreshClientServiceStatus(self):
        self.clientDetails.getClientServiceStatus()
        self.lblStatusClientService.setToolTip(self.clientDetails.ServiceStatus)
        if self.clientDetails.ServiceStatus == "active":
            self.lblStatusClientService.setPixmap(TORIcons.LED_GREEN)
        else:
            self.lblStatusClientService.setPixmap(TORIcons.LED_GRAY)
        app.processEvents()

    def btnStartClientService_clicked(self):
        self.clientDetails.executeSSH(TORCommands.CLIENT_SERVICE_START)
        self.refreshClientServiceStatus()

    def btnStopClientService_clicked(self):
        self.clientDetails.executeSSH(TORCommands.CLIENT_SERVICE_STOP)
        self.refreshClientServiceStatus()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowIcon(TORIcons.APP_ICON)
        self.setWindowTitle("TOR")

        self.cdvs = []
        self.cds = []
        clients = DBManager.getAllClients()
        layClientDetails = QHBoxLayout()
        layClientDetails.setContentsMargins(0, 0, 0, 0)
        grpClientDetailsRegions = [QGroupBox() for i in range(3)]
        for g in grpClientDetailsRegions:
            g.setObjectName("ClientGroup")
            g.setStyleSheet(" QGroupBox#ClientGroup { font-weight: bold; font-size: 16px; } ")
        grpClientDetailsRegions[0].setTitle("Front")
        grpClientDetailsRegions[1].setTitle("Middle")
        grpClientDetailsRegions[2].setTitle("Back")
        layClientDetailsRegions = [QGridLayout() for i in range(3)]
        for i in range(3):
            #layClientDetailsRegions[i].setContentsMargins(0, 0, 0, 0)
            #layClientDetailsRegions[i].setSpacing(0)
            grpClientDetailsRegions[i].setLayout(layClientDetailsRegions[i])
            #grpClientDetailsRegions[i].setContentsMargins(0, 0, 0, 0)
            for j in range(3):
                for k in range(3):
                    c = clients[i*9 + j*3 + k]
                    cdv = ClientDetailView()
                    cd = ClientDetails()
                    cd.Id = c.Id
                    cd.IP = c.IP
                    cd.Material = c.Material
                    cd.Position = c.Position
                    cd.Latin = c.Latin
                    cd.AllowUserMode = c.AllowUserMode
                    cdv.clientDetails = cd
                    cdv.grpMainGroup.setTitle("#{}: {}...".format(cd.Position, cd.Latin[0:8]))
                    layClientDetailsRegions[i].addWidget(cdv, 3*i + j, k)
                    self.cdvs.append(cdv)
                    self.cds.append(cd)
            layClientDetails.addWidget(grpClientDetailsRegions[i])
        wdgClientDetails = QWidget()
        wdgClientDetails.setLayout(layClientDetails)


        self.btnStartAllClientService = QPushButton()
        self.btnStartAllClientService.setText("Start all TORClients")
        self.btnStartAllClientService.clicked.connect(self.btnStartAllClientService_clicked)

        self.btnStopAllClientService = QPushButton()
        self.btnStopAllClientService.setText("Stop all TORClients")
        self.btnStopAllClientService.clicked.connect(self.btnStopAllClientService_clicked)

        self.btnSaveSettings = QPushButton()
        self.btnSaveSettings.setText("Save Settings")
        self.btnSaveSettings.clicked.connect(self.btnSaveSettings_clicked)

        self.btnRestoreSettings = QPushButton()
        self.btnRestoreSettings.setText("Restore Settings")
        self.btnRestoreSettings.clicked.connect(self.btnRestoreSettings_clicked)

        self.btnStartTORServer = QPushButton()
        self.btnStartTORServer.setText("Start TOR Server")
        self.btnStartTORServer.clicked.connect(self.btnStartTORServer_clicked)

        self.btnStopTORServer = QPushButton()
        self.btnStopTORServer.setText("Stop TOR Server")
        self.btnStopTORServer.clicked.connect(self.btnStopTORServer_clicked)

        self.btnStartTORInteractive = QPushButton()
        self.btnStartTORInteractive.setText("Start Visitor App")
        self.btnStartTORInteractive.clicked.connect(self.btnStartTORInteractive_clicked)

        self.btnStopTORInteractive = QPushButton()
        self.btnStopTORInteractive.setText("Stop Visitor App")
        self.btnStopTORInteractive.clicked.connect(self.btnStopTORInteractive_clicked)

        self.btnEndAllUserModes = QPushButton()
        self.btnEndAllUserModes.setText("End all visitor control")
        self.btnEndAllUserModes.clicked.connect(self.btnEndAllUserModes_clicked)

        self.btnTurnOnLEDs = QPushButton()
        self.btnTurnOnLEDs.setText("Turn on LEDs")
        self.btnTurnOnLEDs.clicked.connect(self.btnTurnOnLEDs_clicked)

        self.btnTurnOffLEDs = QPushButton()
        self.btnTurnOffLEDs.setText("Turn off LEDs")
        self.btnTurnOffLEDs.clicked.connect(self.btnTurnOffLEDs_clicked)

        layDashboardButtonsTop = QHBoxLayout()
        layDashboardButtonsTop.addWidget(self.btnStartAllClientService)
        layDashboardButtonsTop.addWidget(self.btnStopAllClientService)
        layDashboardButtonsTop.addWidget(self.btnSaveSettings)
        layDashboardButtonsTop.addWidget(self.btnRestoreSettings)
        wdgDashboardButtonsTop = QWidget()
        wdgDashboardButtonsTop.setLayout(layDashboardButtonsTop)

        layDashboardButtons2 = QHBoxLayout()
        layDashboardButtons2.addWidget(self.btnTurnOnLEDs)
        layDashboardButtons2.addWidget(self.btnTurnOffLEDs)
        wdgDashboardButtons2 = QWidget()
        wdgDashboardButtons2.setLayout(layDashboardButtons2)

        layDashboardButtonsBottom = QHBoxLayout()
        layDashboardButtonsBottom.addWidget(self.btnStartTORServer)
        layDashboardButtonsBottom.addWidget(self.btnStopTORServer)
        layDashboardButtonsBottom.addWidget(self.btnStartTORInteractive)
        layDashboardButtonsBottom.addWidget(self.btnStopTORInteractive)
        layDashboardButtonsBottom.addWidget(self.btnEndAllUserModes)
        wdgDashboardButtonsBottom = QWidget()
        wdgDashboardButtonsBottom.setLayout(layDashboardButtonsBottom)

        layDashboard = QVBoxLayout()
        layDashboard.addWidget(wdgDashboardButtonsTop)
        layDashboard.addWidget(wdgDashboardButtons2)
        layDashboard.addWidget(wdgClientDetails)
        layDashboard.addWidget(wdgDashboardButtonsBottom)

        wdgDashboard = QWidget()
        wdgDashboard.setLayout(layDashboard)

        layTORServer = QVBoxLayout()
        layTORServer.addWidget(QLabel("TOR server"))

        wdgTORServer = QWidget()
        wdgTORServer.setLayout(layTORServer)

        self.tabDashboard = QTabWidget()
        self.tabDashboard.addTab(wdgDashboard, "Dashboard")
        self.tabDashboard.addTab(wdgTORServer, "TORServer")

        self.txtStatus = QPlainTextEdit()
        self.txtStatus.setReadOnly(True)

        layMain = QVBoxLayout()
        layMain.addWidget(self.tabDashboard)
        layMain.addWidget(self.txtStatus)

        wdgMain = QWidget()
        wdgMain.setLayout(layMain)
        self.setCentralWidget(wdgMain)

        self.initSettings()

    ###############
    ### methods ###
    ###############

    def executeCommandOnTORServer(self, cmd):
        cmdSSH = TORCommands.SERVER_SSH_CONNECTION.format(tsl.PATH_TO_SSH_KEY, tsl.SERVER_IP)
        cmdFull = cmdSSH + " \"" + cmd + "\""
        print("EXECUTE: {}".format(cmdFull))
        window.addStatusText("<font color=\"Red\">{}</font>".format(cmdFull))

    def executeCommandOnAllClients(self, cmd):
        for c in self.cds:
            c.executeSSH(cmd)

    def initSettings(self):
        jobs = DBManager.getCurrentJobs()
        for j in jobs:
            for c in self.cds:
                if c.Id == j.Id:
                    c.CurrentJobCode = j.JobCode
        results = DBManager.getAllClientStatistics()
        for r in results:
            for c in self.cds:
                if c.Id == r.Id:
                    c.ResultAverage = r.ResultAverage
                    c.ResultStddev = r.ResultStddev
        for cdv in self.cdvs:
            cdv.lblCurrentJob.setText(cdv.clientDetails.CurrentJobCode)
            cdv.lblResultAverage.setText("{}".format(cdv.clientDetails.ResultAverage))
            cdv.lblResultStddev.setText("+-{}".format(cdv.clientDetails.ResultStddev))
            if cdv.clientDetails.IsBadStatistics():
                cdv.lblResultAverage.setStyleSheet("QLabel { color: \"red\"; }")
                cdv.lblResultStddev.setStyleSheet("QLabel { color: \"red\"; }")
        for cdv in self.cdvs:
            cdv.chkUserMode.setChecked(cdv.clientDetails.AllowUserMode)
            cdv.clientDetails.checkOnlineStatus()
            if cdv.clientDetails.IsOnline:
                cdv.lblIsOnline.setPixmap(TORIcons.LED_GREEN)
                cdv.refreshClientServiceStatus()
            else:
                cdv.lblIsOnline.setPixmap(TORIcons.LED_RED)

    def addSpacerLineToStatusText(self):
        self.txtStatus.appendPlainText("----------------------")

    def addStatusText(self, text, spacerLineBefore=False, spacerLineAfter=False):
        if spacerLineBefore:
            self.addSpacerLineToStatusText()
        self.txtStatus.appendHtml(text)
        if spacerLineAfter:
            self.addSpacerLineToStatusText()
        app.processEvents()

    def btnStartAllClientService_clicked(self):
        for cd in self.cds:
            cd.executeSSH(TORCommands.CLIENT_SERVICE_START)
            cd.Id *= 2
        self.initSettings()

    def btnStopAllClientService_clicked(self):
        for cd in self.cds:
            cd.executeSSH(TORCommands.CLIENT_SERVICE_STOP)
            cd.Id /= 2
        self.initSettings()

    def btnSaveSettings_clicked(self):
        print("saved")

    def btnRestoreSettings_clicked(self):
        print("restored")

    def btnStartTORServer_clicked(self):
        self.executeCommandOnTORServer(TORCommands.SERVER_SERVICE_START)
        print("start TORServer")

    def btnStopTORServer_clicked(self):
        self.executeCommandOnTORServer(TORCommands.SERVER_SERVICE_STOP)
        print("stop TORServer")

    def btnStartTORInteractive_clicked(self):
        self.executeCommandOnTORServer(TORCommands.INTERACTIVE_START)
        print("start tor interactive")

    def btnStopTORInteractive_clicked(self):
        self.executeCommandOnTORServer(TORCommands.INTERACTIVE_STOP)
        print("stop tor interactive")

    def btnEndAllUserModes_clicked(self):
        print("ended all user modes")

    def btnTurnOnLEDs_clicked(self):
        self.executeCommandOnAllClients(TORCommands.CLIENT_TURN_ON_LEDS)
        print("turn on LEDs")

    def btnTurnOffLEDs_clicked(self):
        self.executeCommandOnAllClients(TORCommands.CLIENT_TURN_OFF_LEDS)
        print("turn off LEDs")


###################
### application ###
###################

window = MainWindow()
window.show()

app.exec()
