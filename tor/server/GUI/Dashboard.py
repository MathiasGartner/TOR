import concurrent.futures
from datetime import datetime
import logging
import shlex
import subprocess
import time
import os
import sys

from functools import partial

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QSizePolicy, QApplication, QMainWindow, QPushButton, QLabel, QTabWidget, QGridLayout, QWidget, QPlainTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, QGroupBox, QVBoxLayout, QHBoxLayout, QLayout, QRadioButton, QButtonGroup, QMessageBox, QCheckBox, QSpacerItem
from PyQt5.QtGui import QPixmap, QIcon, QPainter, QTextCursor

app = QApplication(sys.argv)
app.setStyleSheet("""
        * 
        { 
            font-size: 11px 
        } 

        QGroupBox 
        { 
            font-weight: bold; 
        }

        QGroupBox#ClientDetails 
        { 
            font-size: 13px;            
            border: 1px solid gray;
            border-color: #FF17365D;
            margin-top: 20px;
        }

        QGroupBox::title#ClientDetails 
        {
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 2px 50px;
            background-color: #FF17365D;
            color: rgb(255, 255, 255);
        }

        QGroupBox#ClientGroup 
        { 
            font-weight: bold; font-size: 16px; 
        }

    """)
window = None

class WaitCursor(object):
    isActive = False

    def __init__(self):
        self.DoNothingBecauseAlreadyActive = False

    def __enter__(self):
        if WaitCursor.isActive:
            #print("waitCursor is active - do nothing")
            self.DoNothingBecauseAlreadyActive = True
            return
        WaitCursor.isActive = True
        QApplication.setOverrideCursor(Qt.WaitCursor)
        if window is not None:
            window.setEnabled(False)
            window.IsBusy = True
        app.processEvents()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.DoNothingBecauseAlreadyActive:
            return
        QApplication.restoreOverrideCursor()
        if window is not None:
            window.setEnabled(True)
            window.IsBusy = False
        app.processEvents()
        WaitCursor.isActive = False

###################
### TOR imports ###
###################

from tor.base import DBManager
import tor.TORSettingsLocal as tsl
import tor.TORSettings as ts

#################
### Constants ###
#################

THREAD_POOL_SIZE = 27
DEFAULT_TIMEOUT = 3
DEFAULT_TIMEOUT_SERVER = 3
DEFAULT_TIMEOUT_SSH = 7
DEFAULT_TIMEOUT_PING = 1

###############
### logging ###
###############

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=ts.SERVER_LOG_LEVEL)
log = logging.getLogger(__name__)

def executeCommand(cmd, timeout=DEFAULT_TIMEOUT):
    cmdList = shlex.split(cmd)
    #print(cmd, cmdList)
    p = subprocess.Popen(cmdList)
    try:
        p.wait(timeout)
    except subprocess.TimeoutExpired:
        p.kill()
        print("KILLED: {}".format(cmd))
    val = p.returncode
    #print("val: {}".format(val))
    return val

class TORCommands:
    # r'ssh -i {0} pi@{1} "sudo rm -r tor; sudo rm -r scripts"'
    SERVER_SSH_CONNECTION = "ssh -i {0} pi@{1}"
    CLIENT_SSH_CONNECTION = "ssh -i {0} pi@{1}"

    SERVER_SERVICE_START = "sudo systemctl daemon-reload; sudo systemctl restart TORServer"
    SERVER_SERVICE_STOP = "sudo systemctl stop TORServer"

    INTERACTIVE_START = "sudo systemctl daemon-reload; sudo systemctl restart TORInteractive"
    INTERACTIVE_STOP = "sudo systemctl stop TORInteractive"

    #CLIENT_PING = "ping -i 0.2 -c 1 {}"
    CLIENT_PING = "ping -c 1 {}"

    CLIENT_SERVICE_START = "sudo systemctl daemon-reload; sudo systemctl restart TORClient"
    CLIENT_SERVICE_STOP = "sudo systemctl stop TORClient"
    CLIENT_SERVICE_STATUS = "systemctl is-active --quiet TORClient"

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
        self.IsActive = False
        self.ServiceStatus = "unknown"
        self.CurrentJobCode = None
        self.CurrentJobParameters = None
        self.ResultAverage = -1
        self.ResultStddev = -1
        self.IsOnline = False

    def IsBadStatistics(self):
        maxStddevResult = 0.17
        return self.ResultAverage < (3.5-maxStddevResult) or self.ResultAverage > (3.5+maxStddevResult) or self.ResultStddev > 1.77

    def getClientServiceStatus(self):
        self.ServiceStatus = "unknown"
        if self.IsOnline:
            val = self.executeSSH(TORCommands.CLIENT_SERVICE_STATUS, useWaitCursor=False)
            if val == 0:
                self.ServiceStatus = "active"
            else:
                self.ServiceStatus = "inactive"

    def checkOnlineStatus(self):
        #self.IsOnline = True
        #return
        #if self.Id != 13 and self.Id != 27 and self.Id != 25: # and self.Id != 10:
        #    #self.IsOnline = True
        #    self.IsOnline = False
        #    return
        #else:
        #    self.IsOnline = True
        #    return
        cmd = TORCommands.CLIENT_PING.format(self.IP)
        val = executeCommand(cmd, timeout=DEFAULT_TIMEOUT_PING)
        if val == 0:
            self.IsOnline = True
        else:
            self.IsOnline = False

    def __executeSSH(self, cmd, timeout=DEFAULT_TIMEOUT_SSH):
        cmdSSH = TORCommands.CLIENT_SSH_CONNECTION.format(tsl.PATH_TO_SSH_KEY, self.IP)
        cmdFull = cmdSSH + " \"" + cmd + "\""
        print("EXECUTE: {}".format(cmdFull))
        if window is not None:
            window.addStatusText("<font color=\"Blue\">{}</font>".format(cmdFull))
        val = executeCommand(cmdFull, timeout=timeout)
        #print("FINISHE: {}".format(cmdFull))
        return val

    def executeSSH(self, cmd, timeout=DEFAULT_TIMEOUT_SSH, useWaitCursor=True):
        val = -1
        if useWaitCursor:
            with WaitCursor():
                val = self.__executeSSH(cmd, timeout=timeout)
        else:
            val = self.__executeSSH(cmd, timeout=timeout)
        return val

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
        #layClientStatus.addWidget(QLabel("stddev:"), 3, 0)
        #layClientStatus.addWidget(self.lblResultStddev, 3, 1)

        grpClientStatus = QGroupBox("Status")
        grpClientStatus.setLayout(layClientStatus)

        # LEDs
        self.btnTurnOnLEDs = QPushButton()
        self.btnTurnOnLEDs.setText("ON")
        self.btnTurnOnLEDs.setFixedSize(30, 18)
        self.btnTurnOnLEDs.clicked.connect(self.btnTurnOnLEDs_clicked)
        self.btnTurnOffLEDs = QPushButton()
        self.btnTurnOffLEDs.setText("OFF")
        self.btnTurnOffLEDs.setFixedSize(30, 18)
        self.btnTurnOffLEDs.clicked.connect(self.btnTurnOffLEDs_clicked)

        layLEDs = QHBoxLayout()
        layLEDs.setContentsMargins(0, 0, 0, 0)
        layLEDs.addWidget(self.btnTurnOnLEDs)
        layLEDs.addWidget(self.btnTurnOffLEDs)

        grpLEDs = QGroupBox("LEDs")
        grpLEDs.setLayout(layLEDs)

        # Options
        self.chkUserMode = QCheckBox()
        self.chkUserMode.clicked.connect(self.chkUserMode_clicked)
        self.chkIsActivated = QCheckBox()
        self.chkIsActivated.clicked.connect(self.chkIsActivated_clicked)

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
        self.lblStatusClientService.setToolTip("unknown")
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
        layMain.addWidget(grpClientService)
        layMain.addWidget(grpClientOptions)
        layMain.addWidget(grpLEDs)

        self.grpMainGroup = QGroupBox()
        self.grpMainGroup.setObjectName("ClientDetails")
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

    def chkUserMode_clicked(self, checked):
        self.clientDetails.AllowUserMode = checked
        DBManager.setUserModeEnabled(self.clientDetails.Id, checked)

    def chkIsActivated_clicked(self, checked):
        self.clientDetails.IsActive = checked
        DBManager.setClientIsActive(self.clientDetails.Id, checked)

    def refreshClientServiceStatus(self):
        self.lblStatusClientService.setToolTip(self.clientDetails.ServiceStatus)
        if self.clientDetails.ServiceStatus == "active":
            self.lblStatusClientService.setPixmap(TORIcons.LED_GREEN)
        else:
            self.lblStatusClientService.setPixmap(TORIcons.LED_GRAY)
        app.processEvents()

    def btnStartClientService_clicked(self):
        self.clientDetails.executeSSH(TORCommands.CLIENT_SERVICE_START)
        self.clientDetails.getClientServiceStatus()
        self.refreshClientServiceStatus()

    def btnStopClientService_clicked(self):
        self.clientDetails.executeSSH(TORCommands.CLIENT_SERVICE_STOP)
        self.clientDetails.getClientServiceStatus()
        self.refreshClientServiceStatus()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.IsBusy = False
        self.IsUpdating = False

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
                    cd.IsActive = c.IsActive
                    cdv.clientDetails = cd
                    cdv.grpMainGroup.setTitle("#{}: {}...".format(cd.Position, cd.Latin[0:9]))
                    layClientDetailsRegions[i].addWidget(cdv, 3*i + j, k)
                    self.cdvs.append(cdv)
                    self.cds.append(cd)
            layClientDetails.addWidget(grpClientDetailsRegions[i])
        wdgClientDetails = QWidget()
        wdgClientDetails.setLayout(layClientDetails)


        self.btnStartAllTORPrograms = QPushButton()
        self.btnStartAllTORPrograms.setText("START installation")
        self.btnStartAllTORPrograms.clicked.connect(self.btnStartAllTORPrograms_clicked)
        self.btnStartAllTORPrograms.setStyleSheet("QPushButton { font-weight: bold }; ")

        self.btnStopAllTORPrograms = QPushButton()
        self.btnStopAllTORPrograms.setText("STOP installation")
        self.btnStopAllTORPrograms.clicked.connect(self.btnStopAllTORPrograms_clicked)
        self.btnStopAllTORPrograms.setStyleSheet("QPushButton { font-weight: bold }; ")

        self.btnStartAllClientService = QPushButton()
        self.btnStartAllClientService.setText("Start all active TORClients")
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
        self.btnTurnOnLEDs.setText("Turn ON all LEDs")
        self.btnTurnOnLEDs.clicked.connect(self.btnTurnOnLEDs_clicked)

        self.btnTurnOffLEDs = QPushButton()
        self.btnTurnOffLEDs.setText("Turn OFF all LEDs")
        self.btnTurnOffLEDs.clicked.connect(self.btnTurnOffLEDs_clicked)

        self.btnUpdateDashboard = QPushButton()
        self.btnUpdateDashboard.setText("Update dashboard")
        self.btnUpdateDashboard.clicked.connect(self.btnUpdateDashboard_clicked)

        self.lblLastUpdateTime = QLabel()

        spacerSize = 30
        layDashboardButtons = QVBoxLayout()
        layDashboardButtons.addSpacing(spacerSize)
        layDashboardButtons.addWidget(QLabel("<h3>Installation</h3>"))
        layDashboardButtons.addWidget(self.btnStartAllTORPrograms)
        layDashboardButtons.addWidget(self.btnStopAllTORPrograms)
        layDashboardButtons.addSpacing(spacerSize)
        layDashboardButtons.addWidget(QLabel("Clients"))
        layDashboardButtons.addWidget(self.btnStartAllClientService)
        layDashboardButtons.addWidget(self.btnStopAllClientService)
        layDashboardButtons.addSpacing(spacerSize)
        layDashboardButtons.addWidget(QLabel("LEDs"))
        layDashboardButtons.addWidget(self.btnTurnOnLEDs)
        layDashboardButtons.addWidget(self.btnTurnOffLEDs)
        layDashboardButtons.addSpacing(spacerSize)
        layDashboardButtons.addWidget(QLabel("Server"))
        layDashboardButtons.addWidget(self.btnStartTORServer)
        layDashboardButtons.addWidget(self.btnStopTORServer)
        layDashboardButtons.addSpacing(spacerSize)
        layDashboardButtons.addWidget(QLabel("Visitor App"))
        layDashboardButtons.addWidget(self.btnStartTORInteractive)
        layDashboardButtons.addWidget(self.btnStopTORInteractive)
        layDashboardButtons.addWidget(self.btnEndAllUserModes)
        layDashboardButtons.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding))
        layDashboardButtons.addWidget(self.btnUpdateDashboard)
        layDashboardButtons.addWidget(self.lblLastUpdateTime)


        wdgDashboardButtons = QWidget()
        wdgDashboardButtons.setLayout(layDashboardButtons)

        """
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
        """

        layDashboard = QHBoxLayout()
        #layDashboard.addWidget(wdgDashboardButtonsTop)
        #layDashboard.addWidget(wdgDashboardButtons2)
        layDashboard.addWidget(wdgClientDetails)
        #layDashboard.addWidget(wdgDashboardButtonsBottom)
        layDashboard.addWidget(wdgDashboardButtons)

        wdgDashboard = QWidget()
        wdgDashboard.setLayout(layDashboard)

        layTORServer = QVBoxLayout()
        layTORServer.addWidget(QLabel("TOR server"))

        wdgTORServer = QWidget()
        wdgTORServer.setLayout(layTORServer)

        self.tabDashboard = QTabWidget()
        self.tabDashboard.addTab(wdgDashboard, "Dashboard")
        self.tabDashboard.addTab(wdgTORServer, "TORServer")
        self.dashboardTabIndex = 0

        self.txtStatus = QPlainTextEdit()
        self.txtStatus.setReadOnly(True)

        layMain = QVBoxLayout()
        layMain.addWidget(self.tabDashboard)
        layMain.addWidget(self.txtStatus)

        wdgMain = QWidget()
        wdgMain.setLayout(layMain)
        self.setCentralWidget(wdgMain)

        self.initDashboard()
        self.updateDashboard()
        timerFetchData = QTimer(self)
        timerFetchData.timeout.connect(self.updateDashboardFromTimer)
        timerFetchData.start(30 * 1000)

    ###############
    ### methods ###
    ###############

    def executeCommandOnTORServer(self, cmd, timeout=DEFAULT_TIMEOUT_SERVER):
        with WaitCursor():
            cmdSSH = TORCommands.SERVER_SSH_CONNECTION.format(tsl.PATH_TO_SSH_KEY, tsl.SERVER_IP)
            cmdFull = cmdSSH + " \"" + cmd + "\""
            print("SERVEXE: {}".format(cmdFull))
            if window is not None:
                window.addStatusText("<font color=\"Red\">{}</font>".format(cmdFull))
            val = self.__executeSSH(cmd, timeout=timeout)
        return val

    def __executeCommandOnClient(self, client, cmd, timeout=DEFAULT_TIMEOUT_SSH, onlyActive=False):
        if client.IsOnline:
            if not onlyActive or client.IsActive:
                client.executeSSH(cmd, timeout=timeout)

    def executeCommandOnAllClients(self, cmd, timeout=DEFAULT_TIMEOUT_SSH, onlyActive=False):
        threadPool = concurrent.futures.ThreadPoolExecutor(THREAD_POOL_SIZE)
        threadFutures = [threadPool.submit(self.__executeCommandOnClient, c, cmd, timeout, onlyActive) for c in self.cds]
        concurrent.futures.wait(threadFutures)

    def checkOnlineAndServiceStatusForClient(self, client):
        client.checkOnlineStatus()
        client.getClientServiceStatus()

    def initDashboard(self):
        for cdv in self.cdvs:
            cdv.lblIsOnline.setToolTip("Id: {}\nIP: {}\nMaterial: {}\nLatin name: {}".format(cdv.clientDetails.Id, cdv.clientDetails.IP, cdv.clientDetails.Material, cdv.clientDetails.Latin))

    def updateDashboardFromTimer(self):
        if not self.IsBusy and self.tabDashboard.currentIndex() == self.dashboardTabIndex:
            self.updateDashboard()

    def updateDashboard(self):
        if self.IsUpdating:
            return
        self.IsUpdating = True
        print("updateDashboard")
        jobs = DBManager.getCurrentJobs()
        for j in jobs:
            for c in self.cds:
                if c.Id == j.Id:
                    c.CurrentJobCode = j.JobCode
                    c.CurrentJobParameters = j.JobParameters
        results = DBManager.getAllClientStatistics()
        for r in results:
            for c in self.cds:
                if c.Id == r.Id:
                    c.ResultAverage = r.ResultAverage
                    c.ResultStddev = r.ResultStddev
        data = DBManager.getAllClients()
        for d in data:
            for c in self.cds:
                if c.Id == d.Id:
                    c.IP = d.IP
                    c.Material = d.Material
                    c.Position = d.Position
                    c.Latin = d.Latin
                    c.AllowUserMode = d.AllowUserMode
                    c.IsActive = d.IsActive
        for cdv in self.cdvs:
            cdv.lblCurrentJob.setText("{} {}".format(cdv.clientDetails.CurrentJobCode, cdv.clientDetails.CurrentJobParameters))
            cdv.lblResultAverage.setText("{:.2f}±{:.2f}".format(cdv.clientDetails.ResultAverage, cdv.clientDetails.ResultStddev))
            cdv.lblResultStddev.setText("+-{}".format(cdv.clientDetails.ResultStddev))
            if cdv.clientDetails.IsBadStatistics():
                cdv.lblResultAverage.setStyleSheet("QLabel { color: \"red\"; }")
                cdv.lblResultStddev.setStyleSheet("QLabel { color: \"red\"; }")
            else:
                cdv.lblResultAverage.setStyleSheet("")
                cdv.lblResultStddev.setStyleSheet("")

        threadPool = concurrent.futures.ThreadPoolExecutor(THREAD_POOL_SIZE)
        threadFutures = [threadPool.submit(self.checkOnlineAndServiceStatusForClient, cdv.clientDetails) for cdv in self.cdvs]
        concurrent.futures.wait(threadFutures)

        for cdv in self.cdvs:
            cdv.chkUserMode.setChecked(cdv.clientDetails.AllowUserMode)
            cdv.chkIsActivated.setChecked(cdv.clientDetails.IsActive)
            cdv.refreshClientServiceStatus()
            if cdv.clientDetails.IsOnline:
                cdv.lblIsOnline.setPixmap(TORIcons.LED_GREEN)
            else:
                cdv.lblIsOnline.setPixmap(TORIcons.LED_RED)
        self.lblLastUpdateTime.setText("last update: {}".format(datetime.now().strftime("%H:%M:%S")))
        print("updateDashboard finished")
        self.IsUpdating = False

    def addSpacerLineToStatusText(self):
        self.txtStatus.appendPlainText("----------------------")

    def addStatusText(self, text, spacerLineBefore=False, spacerLineAfter=False):
        if spacerLineBefore:
            self.addSpacerLineToStatusText()
        self.txtStatus.appendHtml(text)
        if spacerLineAfter:
            self.addSpacerLineToStatusText()
        self.txtStatus.moveCursor(QTextCursor.End)
        app.processEvents()

    def btnStartAllTORPrograms_clicked(self):
        with WaitCursor():
            self.executeCommandOnTORServer(TORCommands.SERVER_SERVICE_START)
            self.executeCommandOnAllClients(TORCommands.CLIENT_SERVICE_START, onlyActive=True)
            self.executeCommandOnTORServer(TORCommands.INTERACTIVE_START)

    def btnStopAllTORPrograms_clicked(self):
        with WaitCursor():
            self.executeCommandOnTORServer(TORCommands.INTERACTIVE_STOP)
            self.executeCommandOnAllClients(TORCommands.CLIENT_SERVICE_STOP)
            self.executeCommandOnTORServer(TORCommands.SERVER_SERVICE_STOP)

    def btnStartAllClientService_clicked(self):
        print("start")
        with WaitCursor():
            self.executeCommandOnAllClients(TORCommands.CLIENT_SERVICE_START, onlyActive=True)
        self.updateDashboard()

    def btnStopAllClientService_clicked(self):
        print("stop")
        with WaitCursor():
            self.executeCommandOnAllClients(TORCommands.CLIENT_SERVICE_STOP)
        self.updateDashboard()

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

    def btnUpdateDashboard_clicked(self):
        self.updateDashboard()


###################
### application ###
###################

window = MainWindow()
window.show()

app.exec()
