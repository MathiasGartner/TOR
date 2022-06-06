import concurrent.futures
import copy
from datetime import datetime
import logging
import shlex
import subprocess
import time
import os
import sys

from functools import partial

from PyQt5.QtCore import Qt, QTimer, QRect, QThread, QAbstractTableModel, QAbstractListModel, QVariant, \
    QSortFilterProxyModel
from PyQt5.QtWidgets import QSizePolicy, QApplication, QMainWindow, QPushButton, QLabel, QTabWidget, QGridLayout, QWidget, QPlainTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, QGroupBox, QVBoxLayout, QHBoxLayout, QLayout, QRadioButton, QButtonGroup, QMessageBox, QCheckBox, QSpacerItem, QFrame, QLineEdit, QTableView, QTableWidgetItem
from PyQt5.QtGui import QPixmap, QIcon, QPainter, QTextCursor, QColor

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
from tor.server.Job import Job
from tor.server.Job import DefaultJobs
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

NEW_PROGRAM_NAME = "<new>"

TAKE_N_RESULTS_FOR_RECENT_CONTRIBUTIONS = 200

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
        #layLEDs.addWidget(QLabel("LEDs"))
        layLEDs.addWidget(self.btnTurnOnLEDs)
        layLEDs.addWidget(self.btnTurnOffLEDs)

        grpLEDs = QGroupBox("LEDs")
        grpLEDs.setLayout(layLEDs)
        #wdgLEDs = QWidget()
        #wdgLEDs.setLayout(layLEDs)

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
        #layMain.addWidget(wdgLEDs)

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

        self.currentSelectedTabIndex = 0
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
                    layClientDetailsRegions[i].addWidget(cdv, k, 3*i + j)
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


        programNames = DBManager.getAllJobProgramNames()
        self.jobProgramNames = [pn.Name for pn in programNames]
        self.cmbTour = QComboBox()
        self.cmbTour.insertItem(-1, NEW_PROGRAM_NAME)
        for i in range(len(self.jobProgramNames)):
            self.cmbTour.insertItem(i, self.jobProgramNames[i])
        self.cmbTour.currentIndexChanged.connect(self.cmbTour_currentIndexChanged)
        self.btnStartTour = QPushButton("Start")
        self.btnStartTour.clicked.connect(self.btnStartTour_clicked)
        self.btnEditTour = QPushButton("Edit")
        self.btnEditTour.clicked.connect(self.btnEditTour_clicked)

        layTourSelection = QHBoxLayout()
        layTourSelection.addWidget(QLabel("Program: "))
        layTourSelection.addWidget(self.cmbTour)
        layTourSelection.addSpacing(100)
        layTourSelection.addWidget(self.btnStartTour)
        layTourSelection.addWidget(self.btnEditTour)
        layTourSelection.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding))

        wdgTourSelection = QWidget()
        wdgTourSelection.setLayout(layTourSelection)

        self.jobListWidgets = []
        layJobList = QGridLayout()
        jobs = DBManager.getCurrentJobs()
        layJobList.addWidget(QLabel("<h3>Box</h3>"), 0, 0)
        layJobList.addWidget(QLabel("<h3>Quit</h3>"), 0, 1)
        layJobList.addWidget(QLabel("<h3>Wait</h3>"), 0, 2)
        layJobList.addWidget(QLabel("<h3>Run</h3>"), 0, 3)
        layJobList.addWidget(QLabel("<h3>Run & Wait</h3>"), 0, 4)
        layJobList.addWidget(QLabel("<h3>Parameters</h3>"), 0, 5)
        chkQuitAll = QCheckBox()
        chkQuitAll.clicked.connect(self.chkQuitAll_clicked)
        chkWaitAll = QCheckBox()
        chkWaitAll.clicked.connect(self.chkWaitAll_clicked)
        chkRunAll = QCheckBox()
        chkRunAll.clicked.connect(self.chkRunAll_clicked)
        chkRunAndWaitAll = QCheckBox()
        chkAllGroup = QButtonGroup(self)
        chkAllGroup.addButton(chkQuitAll)
        chkAllGroup.addButton(chkWaitAll)
        chkAllGroup.addButton(chkRunAll)
        chkAllGroup.addButton(chkRunAndWaitAll)
        chkRunAndWaitAll.clicked.connect(self.chkRunAndWaitAll_clicked)
        txtParametersAll = QLineEdit()
        txtParametersAll.textChanged.connect(self.txtParametersAll_textChanged)
        layJobList.addWidget(chkQuitAll, 1, 1)
        layJobList.addWidget(chkWaitAll, 1, 2)
        layJobList.addWidget(chkRunAll, 1, 3)
        layJobList.addWidget(chkRunAndWaitAll, 1, 4)
        layJobList.addWidget(txtParametersAll, 1, 5)
        row = 2
        clientCount = 0
        for c in self.cds:
            chkQuit = QCheckBox()
            chkWait = QCheckBox()
            chkRun = QCheckBox()
            chkRunAndWait = QCheckBox()
            txtParameters = QLineEdit()
            chkGroup = QButtonGroup(self)
            chkGroup.addButton(chkQuit)
            chkGroup.addButton(chkWait)
            chkGroup.addButton(chkRun)
            chkGroup.addButton(chkRunAndWait)
            layJobList.addWidget(QLabel("Pos {}: {}".format(c.Position, c.Latin)), row, 0)
            layJobList.addWidget(chkQuit, row, 1)
            layJobList.addWidget(chkWait, row, 2)
            layJobList.addWidget(chkRun, row, 3)
            layJobList.addWidget(chkRunAndWait, row, 4)
            layJobList.addWidget(txtParameters, row, 5)
            self.jobListWidgets.append([c.Id, chkQuit, chkWait, chkRun, chkRunAndWait, txtParameters])
            row += 1
            clientCount += 1
            if clientCount % 9 == 0 and clientCount < 27:
                line = QFrame()
                line.setGeometry(QRect())
                line.setFrameShape(QFrame.HLine)
                line.setFrameShadow(QFrame.Sunken)
                layJobList.addWidget(line, row, 0, 1, 6)
                row += 1

        self.fillJobList(jobs)

        self.wdgJobList = QWidget()
        self.wdgJobList.setEnabled(False)
        self.wdgJobList.setLayout(layJobList)

        lblJobDescriptionText = QLabel(
            """
                The parameters for Job 'W' are of the form 't' where 't' is optional<br>check every t seconds if there is another job to do
                <br><br><br> 
                The parameters for Job 'RW' are of the form 'r w t'<br>run r times, then wait w times for t seconds
            """)
        lblJobDescriptionText.setAlignment(Qt.AlignTop)

        layJobListAndDescriptions = QHBoxLayout()
        layJobListAndDescriptions.addWidget(self.wdgJobList)
        layJobListAndDescriptions.addSpacing(100)
        layJobListAndDescriptions.addWidget(lblJobDescriptionText)
        layJobListAndDescriptions.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding))

        wdgJobListAndDescriptions = QWidget()
        wdgJobListAndDescriptions.setLayout(layJobListAndDescriptions)

        layJobOverview = QVBoxLayout()
        #layJobOverview.addWidget(QLabel("Job Overview"))
        layJobOverview.addWidget(wdgTourSelection)
        layJobOverview.addWidget(wdgJobListAndDescriptions)

        wdgJobOverivew = QWidget()
        wdgJobOverivew.setLayout(layJobOverview)

        # Client Details

        self.cmbClient = QComboBox()
        self.cmbClient.setFixedWidth(180)
        self.cmbClient.insertItem(-1, "All", -1)
        for c in self.cds:
            self.cmbClient.insertItem(c.Position, "#{}: {}".format(c.Position, c.Latin), c.Position)
        self.cmbClient.currentIndexChanged.connect(self.cmbClient_currentIndexChanged)

        self.btnRereshClientDetails = QPushButton("Refresh")
        self.btnRereshClientDetails.clicked.connect(self.btnRereshClientDetails_clicked)

        layClientSelection = QHBoxLayout()
        layClientSelection.addWidget(QLabel("Box: "))
        layClientSelection.addWidget(self.cmbClient)
        layClientSelection.addSpacing(100)
        layClientSelection.addWidget(self.btnRereshClientDetails)
        layClientSelection.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))

        wdgClientSelection = QWidget()
        wdgClientSelection.setLayout(layClientSelection)

        self.tblResults = QTableView()
        self.tblResults.horizontalHeader().setStretchLastSection(True)
        self.tblResults.setWordWrap(False)
        self.tblResults.setTextElideMode(Qt.ElideRight)

        self.clientDetailInfoList = [
            ["Name", QLabel("-")],
            ["Position", QLabel("-")],
            ["ID", QLabel("-")],
            ["IP", QLabel("-")],
            ["MAC", QLabel("-")],
            ["Allow User Mode", QLabel("-")],
            ["User Mode Active", QLabel("-")],
            ["Is Active", QLabel("-")],
            ["Current State", QLabel("-")],
            ["Current Job", QLabel("-")],
            ["Recent results", QLabel("-")],
            ["Average contribution", QLabel("-")],
            ["Average result (3.5)", QLabel("-")],
            ["Results last hour", QLabel("-")],
            ["Results last 2 hours", QLabel("-")],
            ["Results today", QLabel("-")],
            ["Results Total", QLabel("-")]
        ]
        layClientDetailInfos = QGridLayout()
        for num, (text, widget) in enumerate(self.clientDetailInfoList):
            layClientDetailInfos.addWidget(QLabel(text), num, 0)
            layClientDetailInfos.addWidget(widget, num, 1)

        grpClientDetailInfos = QGroupBox()
        grpClientDetailInfos.setTitle("Details")
        grpClientDetailInfos.setLayout(layClientDetailInfos)

        layClientDetailsTop = QHBoxLayout()
        layClientDetailsTop.addWidget(self.tblResults)
        layClientDetailsTop.addSpacing(100)
        layClientDetailsTop.addWidget(grpClientDetailInfos)
        layClientDetailsTop.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))

        wdgClientDetailsTop = QWidget()
        wdgClientDetailsTop.setLayout(layClientDetailsTop)


        self.tblLogMessages = QTableView()
        self.tblLogMessages.horizontalHeader().setStretchLastSection(True)
        self.tblLogMessages.setWordWrap(False)
        self.tblLogMessages.setTextElideMode(Qt.ElideRight)

        self.tblResultStatistics = QTableView()
        #self.tblResultStatistics.horizontalHeader().setStretchLastSection(True)
        self.tblResultStatistics.setWordWrap(False)
        self.tblResultStatistics.setTextElideMode(Qt.ElideRight)
        self.tblResultStatistics.setSortingEnabled(True)

        layClientDetailsBottom = QHBoxLayout()
        layClientDetailsBottom.addWidget(self.tblLogMessages)
        layClientDetailsBottom.addSpacing(20)
        layClientDetailsBottom.addWidget(self.tblResultStatistics)
        #layClientDetailsBottom.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))

        wdgClientDetailsBottom = QWidget()
        wdgClientDetailsBottom.setLayout(layClientDetailsBottom)

        layDetails = QVBoxLayout()
        layDetails.addWidget(wdgClientSelection)
        layDetails.addWidget(QLabel("Results"))
        layDetails.addWidget(wdgClientDetailsTop)
        layDetails.addWidget(QLabel("Log messages"))
        layDetails.addWidget(wdgClientDetailsBottom)


        wdgDetails = QWidget()
        wdgDetails.setLayout(layDetails)


        layTORServer = QVBoxLayout()
        layTORServer.addWidget(QLabel("TOR server"))

        wdgTORServer = QWidget()
        wdgTORServer.setLayout(layTORServer)

        self.clientDetailsTabIndex = 2

        self.tabDashboard = QTabWidget()
        self.tabDashboard.addTab(wdgDashboard, "Dashboard")
        #self.tabDashboard.addTab(wdgTORServer, "TORServer")
        self.tabDashboard.addTab(wdgJobOverivew, "Jobs")
        self.tabDashboard.addTab(wdgDetails, "Detail View")
        self.dashboardTabIndex = 0
        self.tabDashboard.currentChanged.connect(self.tabDashboard_currentChanged)

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
        timerFetchData.start(120 * 1000)

    ###############
    ### methods ###
    ###############

    def tabDashboard_currentChanged(self, index):
        if index == self.clientDetailsTabIndex:
            self.loadAllClientDetails()
        self.currentSelectedTabIndex = index

    def executeCommandOnTORServer(self, cmd, timeout=DEFAULT_TIMEOUT_SERVER):
        val = -1
        with WaitCursor():
            cmdSSH = TORCommands.SERVER_SSH_CONNECTION.format(tsl.PATH_TO_SSH_KEY, tsl.SERVER_IP)
            cmdFull = cmdSSH + " \"" + cmd + "\""
            print("SERVEXE: {}".format(cmdFull))
            if window is not None:
                window.addStatusText("<font color=\"Red\">{}</font>".format(cmdFull))
            val = executeCommand(cmdFull, timeout=timeout)
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
                    break
        results = DBManager.getAllClientStatistics()
        for r in results:
            for c in self.cds:
                if c.Id == r.Id:
                    c.ResultAverage = r.ResultAverage
                    c.ResultStddev = r.ResultStddev
                    break
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
                    break
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
        if QThread.currentThread() != self.thread():
            return
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
            self.executeCommandOnAllClients(TORCommands.CLIENT_TURN_OFF_LEDS)

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
        with WaitCursor():
            self.updateDashboard()

    ############
    ### Jobs ###
    ############

    def fillJobList(self, jobs):
        for j in jobs:
            for w in self.jobListWidgets:
                if j.Id == w[0]:
                    if j.JobCode == DefaultJobs.QUIT.JobCode:
                        w[1].setChecked(True)
                    elif j.JobCode == DefaultJobs.WAIT.JobCode:
                        w[2].setChecked(True)
                    elif j.JobCode == DefaultJobs.RUN.JobCode:
                        w[3].setChecked(True)
                    elif j.JobCode == DefaultJobs.RUN_AND_WAIT.JobCode:
                        w[4].setChecked(True)
                    if j.JobParameters != "None":
                        w[5].setText(j.JobParameters)
                    break

    def cmbTour_currentIndexChanged(self, index):
        programName = self.cmbTour.currentText()
        if programName != NEW_PROGRAM_NAME:
            programJobs = DBManager.getJobsByProgramName(programName)
            self.fillJobList(programJobs)
            self.wdgJobList.setEnabled(False)

    def btnStartTour_clicked(self):
        jobs = []
        for w in self.jobListWidgets:
            j = Job()
            if w[1].isChecked():
                j = copy.deepcopy(DefaultJobs.QUIT)
            elif w[2].isChecked():
                j = copy.deepcopy(DefaultJobs.WAIT)
            elif w[3].isChecked():
                j = copy.deepcopy(DefaultJobs.RUN)
            elif w[4].isChecked():
                j = copy.deepcopy(DefaultJobs.RUN_AND_WAIT)
            j.JobParameters = w[5].text()
            j.ClientId = w[0]
            jobs.append(j)
        DBManager.saveJobs(jobs)

    def btnEditTour_clicked(self):
        self.cmbTour.setCurrentText(NEW_PROGRAM_NAME)
        self.wdgJobList.setEnabled(True)

    def chkQuitAll_clicked(self, checked):
        for w in self.jobListWidgets:
            w[1].setChecked(checked)

    def chkWaitAll_clicked(self, checked):
        for w in self.jobListWidgets:
            w[2].setChecked(checked)

    def chkRunAll_clicked(self, checked):
        for w in self.jobListWidgets:
            w[3].setChecked(checked)

    def chkRunAndWaitAll_clicked(self, checked):
        for w in self.jobListWidgets:
            w[4].setChecked(checked)

    def txtParametersAll_textChanged(self, text):
        for w in self.jobListWidgets:
            w[5].setText(text)

    ###############
    ### Details ###
    ###############

    def getClientDetailsByPosition(self, position):
        return self.cds[position - 1]

    def showDataInTable(self, data, table, tableModel):
        model = tableModel(data)
        proxyModel = QSortFilterProxyModel()
        proxyModel.setSourceModel(model)
        table.setModel(proxyModel)

    def setTableWidths(self, table, widths):
        for i, w in enumerate(widths):
            table.setColumnWidth(i, w)

    def setClientDetailInfoListText(self, num, text):
        self.clientDetailInfoList[num][1].setText(str(text))

    def loadResultStatistics(self):
        resultStatistics = DBManager.getResultStatistics(ts.DICE_RESULT_EVENT_SOURCE)
        self.showDataInTable(resultStatistics, self.tblResultStatistics, ResultStatisticsTableModel)
        w = 50
        self.setTableWidths(self.tblResultStatistics, [100, w, w, w, w, w, w, w, w])

    def loadAllClientDetails(self):
        logMessages = DBManager.getClientLog()
        self.showDataInTable(logMessages, self.tblLogMessages, LogMessageTableModel)
        self.setTableWidths(self.tblLogMessages, [50, 150, 50, 150, 200, 200])

        diceResults = DBManager.getResults()
        self.showDataInTable(diceResults, self.tblResults, DiceResultTableModel)
        self.setTableWidths(self.tblResults, [50, 150, 50, 50, 50, 50, 200])

        self.loadResultStatistics()

        for i in range(len(self.clientDetailInfoList)):
            self.setClientDetailInfoListText(i, "---")

    def loadClientDetails(self, client):
        logMessages = DBManager.getClientLogByClientId(client.Id)
        self.showDataInTable(logMessages, self.tblLogMessages, LogMessageTableModel)
        self.setTableWidths(self.tblLogMessages, [50, 150, 200, 200])

        diceResults = DBManager.getResultsByClientId(client.Id)
        self.showDataInTable(diceResults, self.tblResults, DiceResultTableModel)
        self.setTableWidths(self.tblResults, [50, 50, 50, 50, 200])

        self.loadResultStatistics()

        self.setClientDetailInfoListText(0, client.Latin)
        self.setClientDetailInfoListText(1, client.Position)
        self.setClientDetailInfoListText(2, client.Id)
        self.setClientDetailInfoListText(3, client.IP)
        self.setClientDetailInfoListText(4, "")
        self.setClientDetailInfoListText(5, "YES" if client.AllowUserMode else "NO")
        self.setClientDetailInfoListText(6, "YES" if client.IsActive else "NO")
        self.setClientDetailInfoListText(7, client.Position)

        clientContributions = DBManager.getAllClientResultContribution(TAKE_N_RESULTS_FOR_RECENT_CONTRIBUTIONS)
        for cc in clientContributions:
            if cc.Id == client.Id:
                self.setClientDetailInfoListText(11, "{:.2f}".format(cc.Contribution))
                self.setClientDetailInfoListText(12, "{:.2f}".format(cc.AverageResult))
                break

    def reloadClientDetailsBySelectedIndex(self, index):
        position = self.cmbClient.itemData(index)
        if position == -1:
            self.addStatusText("show details for all clients")
            self.loadAllClientDetails()
        else:
            c = self.getClientDetailsByPosition(position)
            self.addStatusText("select client at position {}".format(c.Position))
            self.loadClientDetails(c)

    def cmbClient_currentIndexChanged(self, index):
        self.reloadClientDetailsBySelectedIndex(index)

    def btnRereshClientDetails_clicked(self):
        index = self.cmbClient.currentIndex()
        self.reloadClientDetailsBySelectedIndex(index)

class DbTableModel(QAbstractTableModel):
    def __init__(self, data, parent=None):
        super(DbTableModel, self).__init__(parent)
        self.data = data
        if len(data) > 0:
            self.headers = data[0]._fields
        else:
            self.headers = []

    def rowCount(self, index):
        return len(self.data)

    def columnCount(self, index):
        return len(self.data[0])

    def data(self, QModelIndex, role=None):
        row = QModelIndex.row()
        column = QModelIndex.column()
        if role == Qt.DisplayRole:
            text = str(self.data[row][column])
            return text

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self.headers[section])
            if orientation == Qt.Vertical:
                return str(section+1)

class LogMessageTableModel(DbTableModel):
    def __init__(self, data, parent=None):
        super(LogMessageTableModel, self).__init__(data, parent)

    def data(self, QModelIndex, role=None):
        row = QModelIndex.row()
        column = QModelIndex.column()
        if role == Qt.DisplayRole:
            text = str(self.data[row][column])
            return text
        if role == Qt.BackgroundColorRole:
            if self.data[row].Type == "ERROR":
                return QVariant(QColor(255, 210, 210))

class DiceResultTableModel(DbTableModel):
    def __init__(self, data, parent=None):
        super(DiceResultTableModel, self).__init__(data, parent)

    def data(self, QModelIndex, role=None):
        row = QModelIndex.row()
        column = QModelIndex.column()
        if role == Qt.DisplayRole:
            text = str(self.data[row][column])
            return text
        if role == Qt.BackgroundColorRole:
            if self.data[row].UserGenerated == 1:
                return QVariant(QColor(210, 255, 210))

class ResultStatisticsTableModel(DbTableModel):
    def __init__(self, data, parent=None):
        super(ResultStatisticsTableModel, self).__init__(data, parent)
        self.headers = ["ID", "# 2 h", "avg 2 h", "# 4 h", "avg 4 h", "# today", "avg today", "#", "avg"]

    def data(self, QModelIndex, role=None):
        row = QModelIndex.row()
        column = QModelIndex.column()
        if role == Qt.DisplayRole:
            text = str(self.data[row][column])
            return text

###################
### application ###
###################

window = MainWindow()
window.show()

app.exec()
