import concurrent.futures
import copy
import socket
from datetime import datetime
import shlex
import subprocess
import time
import sys

import matplotlib as plt
from PyQt5.QtSvg import QSvgWidget

plt.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from PyQt5.QtCore import Qt, QTimer, QRect, QThread, QSortFilterProxyModel
from PyQt5.QtWidgets import (QSplitter, QSizePolicy, QApplication, QMainWindow, QPushButton, QLabel,
                             QTabWidget, QGridLayout, QWidget, QPlainTextEdit, QComboBox,
                             QGroupBox, QVBoxLayout, QHBoxLayout, QButtonGroup,
                             QCheckBox, QSpacerItem, QFrame, QLineEdit, QTableView)
from PyQt5.QtGui import QTextCursor

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

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
            font-size: 12px;            
            border: 1px solid gray;
            border-color: rgb(180, 180, 180);
            margin-top: 7px;
        }

        QGroupBox::title#ClientDetails 
        {
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 2px 50px;
            background-color: rgb(180, 180, 180);
            color: rgb(255, 255, 255);
        }

        QGroupBox#ClientGroup 
        { 
            font-weight: bold; 
            font-size: 12px;
        }

        *[styleClass~="group-box-compact"] 
        { 
            font-size: 10px;
            font-weight: font-semibold; 
            color: rgb(70, 70, 70); 
        }

        *[styleClass~="group-box-compact"] * 
        {
            font-size: 10px;
            padding: 0px;
            margin: 0px;
        }
        
        *[styleClass~="button-compact"] 
        {
            font-size: 10px; 
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

###############
### logging ###
###############

import tor.server.ServerSettings as ss
from tor.base.LogManager import setupLogging, getLogger
setupLogging(ss.DASHBOARD_LOG_CONFIG_FILEPATH)
log = getLogger()

###################
### TOR imports ###
###################

from tor.base import DBManager
from tor.base import NetworkUtils
from tor.base.GUI import TORIcons
from tor.base.GUI.SvgButton import SvgButton
from tor.server.GUI.ClientDetailViewCompact import ClientDetailViewCompact
from tor.server.GUI.ClientDetailViewFull import ClientDetailViewFull
from tor.server.GUI.DatenAndEventSelection import DatenAndEventSelection
from tor.server.GUI.plots.PickupProblems import PickupProblems
from tor.server.GUI.plots.RollWarnings import RollWarnings
from tor.server.GUI.plots.ResultPositions import ResultPositions
from tor.server.GUI.plots.ResultStatistic import ResultStatistic
from tor.server.GUI.TableModels import LogMessageTableModel, DiceResultTableModel, ResultStatisticsTableModel, LogMessageSortFilterProxyModel
from tor.server.Job import Job
from tor.server.Job import DefaultJobs
from tor.server.TORCommands import TORCommands

import tor.TORSettingsLocal as tsl
import tor.TORSettings as ts

#################
### Constants ###
#################

THREAD_POOL_SIZE = 27
DEFAULT_TIMEOUT = 3
DEFAULT_TIMEOUT_SERVER = 3
DEFAULT_TIMEOUT_SSH = 7
DEFAULT_TIMEOUT_PING: float = 2.5

NEW_PROGRAM_NAME = "<new>"

TAKE_N_RESULTS_FOR_RECENT_CONTRIBUTIONS = 200

def executeCommand(cmd, timeout=DEFAULT_TIMEOUT):
    cmdList = shlex.split(cmd)
    #print(cmd, cmdList)
    p = subprocess.Popen(cmdList)
    try:
        p.wait(timeout)
    except subprocess.TimeoutExpired:
        p.kill()
        log.info("KILLED: {}".format(cmd))
    val = p.returncode
    #print("val: {}".format(val))
    return val

class ClientDetails:
    def __init__(self, data=None):
        if data is None:
            self.Id = -1
            self.IP = None
            self.Material = None
            self.Position = -1
            self.Latin = None
            self.AllowUserMode = False
            self.IsActive = False
            self.UseSchedule = False
        else:
            self.Id = data.Id
            self.IP = data.IP
            self.Material = data.Material
            self.Position = data.Position
            self.Latin = data.Latin
            self.AllowUserMode = data.AllowUserMode
            self.IsActive = data.IsActive
            self.UseSchedule = data.UseSchedule
        self.ClientServiceStatus = "unknown"
        self.StatusManagerServiceStatus = "unknown"
        self.CurrentJobCode = None
        self.CurrentJobParameters = None
        self.ResultAverage = -1
        self.ResultStddev = -1
        self.IsOnline = False
        self.VersionOkay = False
        self.Version = "unknown"

    def sendMsgToStatusManager(self, msg, timeout=ts.STATUS_TIMEOUT):
        answer = None
        try:
            conn = NetworkUtils.createConnection(self.IP, ts.STATUS_PORT, timeout, verbose=False)
            NetworkUtils.sendData(conn, msg)
            answer = NetworkUtils.recvData(conn)
            conn.close()
        except Exception as e:
            log.error("Error connecting to StatusManager:")
            log.error("{}".format(repr(e)))
        return answer

    def IsBadStatistics(self):
        maxStddevResult = 0.17
        avgResultOptimal = 3.5
        maxStddev = 1.77
        return self.ResultAverage < (avgResultOptimal - maxStddevResult) or self.ResultAverage > (avgResultOptimal + maxStddevResult) or self.ResultStddev > maxStddev

    def getClientStatus(self):
        answer = None
        try:
            msg = {"TYPE": "STATUS"}
            answer = self.sendMsgToStatusManager(msg)
            self.IsOnline = True
            self.StatusManagerServiceStatus = "active"
        except socket.timeout as e:
            log.error(f"Timeout while connecting to {self.Latin}")
            self.checkOnlineStatusByPing()
            self.StatusManagerServiceStatus = "inactive"
        except Exception as e:
            log.error("Error connecting to StatusManager service:")
            log.error("{}".format(repr(e)))
            self.checkOnlineStatusByPing()
            self.StatusManagerServiceStatus = "unknown"

        if isinstance(answer, dict):
            self.Version = answer["TOR_VERSION"]
            self.VersionOkay = ts.VERSION_TOR == self.Version
            if not self.VersionOkay:
                log.warning(f"wrong TOR version at client <{self.Position} - {self.Latin}> (v{self.Version})")
            else:
                log.info(f"correct TOR version at {self.Latin} found")
            self.ClientServiceStatus = answer["TOR_CLIENT_SERVICE"]
        else:
            self.Version = "unknown"
            self.VersionOkay = False
            log.info(f"Could not load client status for {self.Latin}")

    def checkOnlineStatusByPing(self):
        log.info(f"checkOnlineStatusByPing for client {self.Latin}")
        cmd = TORCommands.CLIENT_PING.format(self.IP)
        val = executeCommand(cmd, timeout=DEFAULT_TIMEOUT_PING)
        #TODO: check this. val=0 als happens if ping is not successful
        if val == 0:
            self.IsOnline = True
        else:
            self.IsOnline = False

    def __executeSSH(self, cmd, timeout=DEFAULT_TIMEOUT_SSH, asRoot=False):
        cmdSSH = ""
        if asRoot:
            cmdSSH = TORCommands.CLIENT_SSH_CONNECTION_X11ROOT.format(tsl.PATH_TO_SSH_KEY, self.IP)
        else:
            cmdSSH = TORCommands.CLIENT_SSH_CONNECTION.format(tsl.PATH_TO_SSH_KEY, self.IP)
        cmdFull = cmdSSH + " \"" + cmd + "\""
        log.info("EXECUTE: {}".format(cmdFull))
        if window is not None:
            window.addStatusText("<font color=\"Blue\">{}</font>".format(cmdFull))
        val = executeCommand(cmdFull, timeout=timeout)
        #print("FINISHE: {}".format(cmdFull))
        return val

    def executeSSH(self, cmd, timeout=DEFAULT_TIMEOUT_SSH, useWaitCursor=True, asRoot=False):
        val = -1
        if useWaitCursor:
            with WaitCursor():
                val = self.__executeSSH(cmd, timeout=timeout, asRoot=asRoot)
        else:
            val = self.__executeSSH(cmd, timeout=timeout, asRoot=asRoot)
        return val

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.IsBusy = False
        self.IsUpdating = False

        self.currentSelectedTabIndex = 0
        self.setWindowTitle(f"The Transparency of Randomness v{ts.VERSION_TOR}")
        self.setWindowIcon(TORIcons.APP_ICON)

        self.cdvs = []
        self.cds = []
        clients = DBManager.getAllClients()
        layClientDetails = QHBoxLayout()
        layClientDetails.setContentsMargins(0, 0, 0, 0)

        if ss.BOX_FORMATION == "3x3x3":
            grpClientDetailsRegions = [QGroupBox() for i in range(3)]
            for g in grpClientDetailsRegions:
                g.setObjectName("ClientGroup")
            grpClientDetailsRegions[0].setTitle("Front")
            grpClientDetailsRegions[1].setTitle("Middle")
            grpClientDetailsRegions[2].setTitle("Back")
            layClientDetailsRegions = [QGridLayout() for i in range(3)]
            if ss.BOX_VIEW_COMPACT == True:
                if len(clients) != 27:
                    log.error("Positions are not set for all 27 boxes.")
                for i in range(3):
                    grpClientDetailsRegions[i].setLayout(layClientDetailsRegions[i])
                    for j in range(3):
                        for k in range(3):
                            c = clients[i*9 + j*3 + k]
                            cdv = ClientDetailViewCompact(app)
                            cd = ClientDetails(c)
                            cdv.clientDetails = cd
                            cdv.grpMainGroup.setTitle("#{}: {}...".format(cd.Position, cd.Latin[0:9]))
                            layClientDetailsRegions[i].addWidget(cdv, k, 3*i + j)
                            self.cdvs.append(cdv)
                            self.cds.append(cd)
                    layClientDetails.addWidget(grpClientDetailsRegions[i])
            else:
                for i in range(3):
                    grpClientDetailsRegions[i].setLayout(layClientDetailsRegions[i])
                    layClientDetailsRegions[i].setSpacing(2)
                    layClientDetailsRegions[i].setContentsMargins(2, 2, 2, 2)
                    for j in range(3):
                        for k in range(3):
                            cdv = ClientDetailViewFull(app, position=9*i + 3*j + k + 1, changeClientCallback=self.reloadClients, openDetailTabCallback=self.openClientDetailTab, compact=True)
                            for c in clients:
                                if c.Position == cdv.position:
                                    cd = ClientDetails(c)
                                    cdv.clientDetails = cd
                                    self.cds.append(cd)
                            cdv.updateClientArea()
                            self.cdvs.append(cdv)
                            layClientDetailsRegions[i].addWidget(cdv, k, 3*i + j)
                    layClientDetails.addWidget(grpClientDetailsRegions[i])
        elif ss.BOX_FORMATION == "3x3":
            for i in range(9):
                cdv = ClientDetailViewFull(app, position=i + 1, changeClientCallback=self.reloadClients, openDetailTabCallback=self.openClientDetailTab)
                for c in clients:
                    if c.Position == cdv.position:
                        cd = ClientDetails(c)
                        cdv.clientDetails = cd
                        self.cds.append(cd)
                cdv.updateClientArea()
                self.cdvs.append(cdv)
            layDashboardClientsGrid = QGridLayout()
            for i in range(3):
                for j in range(3):
                    layDashboardClientsGrid.addWidget(self.cdvs[i * 3 + j], i, j)
                layDashboardClientsGrid.setColumnMinimumWidth(i, 300)
            layClientDetails.addLayout(layDashboardClientsGrid)

        wdgClientDetails = QWidget()
        wdgClientDetails.setLayout(layClientDetails)

        #QuickJobs
        programNames = DBManager.getAllJobProgramNames()
        self.quickTourNames = [pn.Name for pn in programNames if pn.Name.startswith(ts.DASHBOARD_QUICK_JOB_PREFIX)]
        self.cmbQuickTour = QComboBox()
        self.cmbQuickTour.setMaximumWidth(100)
        for i in range(len(self.quickTourNames)):
            self.cmbQuickTour.insertItem(i, self.quickTourNames[i], self.quickTourNames[i])
        self.btnStartQuickTour = SvgButton(TORIcons.ICON_START)
        self.btnStartQuickTour.clicked.connect(self.btnStartQuickTour_clicked)

        layDashboardQuickTour = QHBoxLayout()
        layDashboardQuickTour.addWidget(self.cmbQuickTour)
        layDashboardQuickTour.addWidget(self.btnStartQuickTour)

        wdgDashboardQuickTour = QWidget()
        wdgDashboardQuickTour.setLayout(layDashboardQuickTour)


        self.btnStartAllTORPrograms = QPushButton()
        self.btnStartAllTORPrograms.setText("START")
        self.btnStartAllTORPrograms.clicked.connect(self.btnStartAllTORPrograms_clicked)
        self.btnStartAllTORPrograms.setStyleSheet("QPushButton { font-weight: bold }; ")

        self.btnStopAllTORPrograms = QPushButton()
        self.btnStopAllTORPrograms.setText("STOP")
        self.btnStopAllTORPrograms.clicked.connect(self.btnStopAllTORPrograms_clicked)
        self.btnStopAllTORPrograms.setStyleSheet("QPushButton { font-weight: bold }; ")

        self.btnStartAllClientService = QPushButton()
        self.btnStartAllClientService.setText("Start all active boxes")
        self.btnStartAllClientService.clicked.connect(self.btnStartAllClientService_clicked)

        self.btnStopAllClientService = QPushButton()
        self.btnStopAllClientService.setText("Stop all boxes")
        self.btnStopAllClientService.clicked.connect(self.btnStopAllClientService_clicked)

        self.btnSaveSettings = QPushButton()
        self.btnSaveSettings.setText("Save Settings")
        self.btnSaveSettings.clicked.connect(self.btnSaveSettings_clicked)

        self.btnRestoreSettings = QPushButton()
        self.btnRestoreSettings.setText("Restore Settings")
        self.btnRestoreSettings.clicked.connect(self.btnRestoreSettings_clicked)

        self.svgStatusTORServer = QSvgWidget(TORIcons.LED_RED)
        self.svgStatusTORServer.setFixedSize(8, 8)

        self.btnStartTORServer = QPushButton()
        self.btnStartTORServer.setText("Start TOR Server")
        self.btnStartTORServer.clicked.connect(self.btnStartTORServer_clicked)

        self.btnStopTORServer = QPushButton()
        self.btnStopTORServer.setText("Stop TOR Server")
        self.btnStopTORServer.clicked.connect(self.btnStopTORServer_clicked)

        self.svgStatusTORInteractive = QSvgWidget(TORIcons.LED_RED)
        self.svgStatusTORInteractive.setFixedSize(8, 8)

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
        layDashboardButtons.addWidget(QLabel("<h3>Job</h3>"))
        layDashboardButtons.addWidget(wdgDashboardQuickTour)
        layDashboardButtons.addSpacing(spacerSize)
        layDashboardButtons.addSpacing(spacerSize)
        #layDashboardButtons.addWidget(QLabel("<h3>The Transparency<br/>of Randomness</h3>"))
        #layDashboardButtons.addWidget(self.btnStartAllTORPrograms)
        #layDashboardButtons.addWidget(self.btnStopAllTORPrograms)
        #layDashboardButtons.addSpacing(spacerSize)
        layDashboardButtons.addWidget(QLabel("Clients"))
        layDashboardButtons.addWidget(self.btnStartAllClientService)
        layDashboardButtons.addWidget(self.btnStopAllClientService)
        layDashboardButtons.addSpacing(spacerSize)
        layDashboardButtons.addWidget(QLabel("LEDs"))
        layDashboardButtons.addWidget(self.btnTurnOnLEDs)
        layDashboardButtons.addWidget(self.btnTurnOffLEDs)
        layDashboardButtons.addSpacing(spacerSize)
        layTmp = QHBoxLayout()
        layTmp.addWidget(QLabel("Server"))
        layTmp.addWidget(self.svgStatusTORServer)
        layDashboardButtons.addLayout(layTmp)
        layDashboardButtons.addWidget(self.btnStartTORServer)
        layDashboardButtons.addWidget(self.btnStopTORServer)
        layDashboardButtons.addSpacing(spacerSize)
        layTmp = QHBoxLayout()
        layTmp.addWidget(QLabel("Visitor App"))
        layTmp.addWidget(self.svgStatusTORInteractive)
        layDashboardButtons.addLayout(layTmp)
        layDashboardButtons.addWidget(self.btnStartTORInteractive)
        layDashboardButtons.addWidget(self.btnStopTORInteractive)
        layDashboardButtons.addWidget(self.btnEndAllUserModes)
        layDashboardButtons.addSpacerItem(QSpacerItem(0, spacerSize, QSizePolicy.Expanding, QSizePolicy.MinimumExpanding))
        layDashboardButtons.addWidget(self.btnUpdateDashboard)
        layDashboardButtons.addWidget(self.lblLastUpdateTime)

        wdgDashboardButtons = QWidget()
        wdgDashboardButtons.setMaximumWidth(250)
        wdgDashboardButtons.setLayout(layDashboardButtons)

        layDashboard = QHBoxLayout()
        layDashboard.addWidget(wdgClientDetails)
        layDashboard.addWidget(wdgDashboardButtons)

        wdgDashboard = QWidget()
        wdgDashboard.setLayout(layDashboard)

        ###########################################################

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
        layJobOverview.addStretch()

        wdgJobOverivew = QWidget()
        wdgJobOverivew.setLayout(layJobOverview)

        # Client Details

        tblRowHeight = 12

        availableClients = DBManager.getAllAvailableClients()
        self.cmbClient = QComboBox()
        self.cmbClient.setFixedWidth(180)
        self.cmbClient.insertItem(0, "All", None)
        for i, c in enumerate(availableClients):
            self.cmbClient.insertItem(i+1, f"{f'#{c.Position}:' if c.Position is not None else '        '} {c.Latin}", c)
        self.cmbClient.currentIndexChanged.connect(self.cmbClient_currentIndexChanged)

        self.btnRefreshClientDetails = QPushButton("Refresh")
        self.btnRefreshClientDetails.clicked.connect(self.btnRefreshClientDetails_clicked)

        layClientSelection = QHBoxLayout()
        layClientSelection.addWidget(QLabel("Box: "))
        layClientSelection.addWidget(self.cmbClient)
        layClientSelection.addSpacing(100)
        layClientSelection.addWidget(self.btnRefreshClientDetails)
        layClientSelection.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))

        wdgClientSelection = QWidget()
        wdgClientSelection.setLayout(layClientSelection)

        self.tblResults = QTableView()
        self.tblResults.horizontalHeader().setStretchLastSection(True)
        self.tblResults.setWordWrap(False)
        self.tblResults.setTextElideMode(Qt.ElideRight)
        self.tblResults.verticalHeader().setDefaultSectionSize(tblRowHeight)

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

        self.cdvDetails = ClientDetailViewFull(app, 0)
        self.cdvDetails.btnErrorLogGoToDetails.setVisible(False)
        self.cdvDetails.btnX.setVisible(False)
        self.cdvDetails.btnChange.setVisible(False)

        layClientDetailsTop = QHBoxLayout()
        layClientDetailsTop.addWidget(self.tblResults)
        layClientDetailsTop.addSpacing(100)
        layClientDetailsTop.addWidget(grpClientDetailInfos)
        layClientDetailsTop.addSpacing(100)
        layClientDetailsTop.addWidget(self.cdvDetails)
        layClientDetailsTop.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))

        wdgClientDetailsTop = QWidget()
        wdgClientDetailsTop.setLayout(layClientDetailsTop)

        self.tblLogMessages = QTableView()
        self.tblLogMessages.horizontalHeader().setStretchLastSection(True)
        self.tblLogMessages.setWordWrap(False)
        self.tblLogMessages.setTextElideMode(Qt.ElideRight)
        self.tblLogMessages.verticalHeader().setDefaultSectionSize(tblRowHeight)

        self.prxLogMessages = LogMessageSortFilterProxyModel(None)
        self.chkLogMessagesError = QCheckBox()
        self.chkLogMessagesError.stateChanged.connect(self.prxLogMessages.chkErrorChanged)
        self.chkLogMessagesError.setChecked(self.prxLogMessages.chkErrorStatus)
        self.chkLogMessagesWarning = QCheckBox()
        self.chkLogMessagesWarning.stateChanged.connect(self.prxLogMessages.chkWarningChanged)
        self.chkLogMessagesWarning.setChecked(self.prxLogMessages.chkWarningStatus)
        self.chkLogMessagesInfo = QCheckBox()
        self.chkLogMessagesInfo.stateChanged.connect(self.prxLogMessages.chkInfoChanged)
        self.chkLogMessagesInfo.setChecked(self.prxLogMessages.chkInfoStatus)

        self.tblResultStatistics = QTableView()
        #self.tblResultStatistics.horizontalHeader().setStretchLastSection(True)
        self.tblResultStatistics.setWordWrap(False)
        self.tblResultStatistics.setTextElideMode(Qt.ElideRight)
        self.tblResultStatistics.setSortingEnabled(True)
        self.tblResultStatistics.verticalHeader().setDefaultSectionSize(tblRowHeight)

        layClientDetailsBottom = QHBoxLayout()
        layClientDetailsBottom.addWidget(self.chkLogMessagesError)
        layClientDetailsBottom.addWidget(self.chkLogMessagesWarning)
        layClientDetailsBottom.addWidget(self.chkLogMessagesInfo)
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
        layLogMessageChk = QHBoxLayout()
        layLogMessageChk.addWidget(QLabel("Log messages:"))
        layLogMessageChk.addSpacing(20)
        layLogMessageChk.addWidget(self.chkLogMessagesError)
        layLogMessageChk.addWidget(QLabel("Errors"))
        layLogMessageChk.addSpacing(20)
        layLogMessageChk.addWidget(self.chkLogMessagesWarning)
        layLogMessageChk.addWidget(QLabel("Warnings"))
        layLogMessageChk.addSpacing(20)
        layLogMessageChk.addWidget(self.chkLogMessagesInfo)
        layLogMessageChk.addWidget(QLabel("Info"))
        layLogMessageChk.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))
        layDetails.addLayout(layLogMessageChk)
        layDetails.addWidget(wdgClientDetailsBottom)

        wdgDetails = QWidget()
        wdgDetails.setLayout(layDetails)

        #################
        ##### Plots #####
        #################

        # Plot Result Statistic
        wdgResultStatistic = QWidget()
        layResultStatistic = QVBoxLayout()

        self.filterResultStatistic = DatenAndEventSelection(self.filterResultStatistic_update)
        self.pltResultStatistic = ResultStatistic()
        self.toolbarResultStatistic = NavigationToolbar(self.pltResultStatistic.canvas, self)

        layResultStatistic.addWidget(self.filterResultStatistic)
        layResultStatistic.addWidget(self.toolbarResultStatistic)
        layResultStatistic.addWidget(self.pltResultStatistic.canvas)
        layResultStatistic.addWidget(QWidget())
        layResultStatistic.addStretch(1)

        wdgResultStatistic.setLayout(layResultStatistic)


        # Plot Roll Warnings
        wdgRollWarnings = QWidget()
        layRollWarnings = QVBoxLayout()

        self.filterRollWarnings = DatenAndEventSelection(self.filterRollWarnings_update)
        self.filterRollWarnings.chkEvent.setVisible(False)
        self.filterRollWarnings.cmbEvent.setVisible(False)
        self.filterRollWarnings.chkTime.setChecked(True)
        self.filterRollWarnings.timStart.setEnabled(True)
        self.filterRollWarnings.timEnd.setEnabled(True)
        self.pltRollWarnings = RollWarnings()

        layRollWarnings.addWidget(self.filterRollWarnings)
        layRollWarnings.addWidget(self.pltRollWarnings.canvas)
        layRollWarnings.addWidget(QWidget())
        layRollWarnings.addStretch(1)

        wdgRollWarnings.setLayout(layRollWarnings)


        # Plot Result Positions
        wdgResultPositions = QWidget()
        layResultPositions = QVBoxLayout()

        self.chkResultPositionsGlobalColorbar = QCheckBox()

        self.filterResultPositions = DatenAndEventSelection(self.filterResultPositions_update, customElements=[QLabel("global scale"), self.chkResultPositionsGlobalColorbar])
        self.pltResultPositions = ResultPositions()

        layResultPositions.addWidget(self.filterResultPositions)
        layResultPositions.addWidget(self.pltResultPositions.canvas)
        layResultPositions.addWidget(QWidget())
        layResultPositions.addStretch(1)

        wdgResultPositions.setLayout(layResultPositions)


        # Plot Pickup Problems
        wdgPickupProblems = QWidget()
        layPickupProblems = QVBoxLayout()

        self.chkPickupProblemsGlobalColorbar = QCheckBox()

        self.filterPickupProblems = DatenAndEventSelection(self.filterPickupProblems_update, customElements=[QLabel("global scale"), self.chkPickupProblemsGlobalColorbar])
        self.filterPickupProblems.chkEvent.setVisible(False)
        self.filterPickupProblems.cmbEvent.setVisible(False)
        self.filterPickupProblems.chkTime.setChecked(True)
        self.filterPickupProblems.timStart.setEnabled(True)
        self.filterPickupProblems.timEnd.setEnabled(True)
        self.pltPickupProblems = PickupProblems()

        layPickupProblems.addWidget(self.filterPickupProblems)
        layPickupProblems.addWidget(self.pltPickupProblems.canvas)
        layPickupProblems.addWidget(QWidget())
        layPickupProblems.addStretch(1)

        wdgPickupProblems.setLayout(layPickupProblems)

        ##############

        tabStatistics = QTabWidget()
        tabStatistics.addTab(wdgResultStatistic, "Results")
        tabStatistics.addTab(wdgRollWarnings, "Roll Warnings")
        tabStatistics.addTab(wdgResultPositions, "Result Positions")
        tabStatistics.addTab(wdgPickupProblems, "Pickup Problems")

        layTORServer = QVBoxLayout()
        layTORServer.addWidget(QLabel("TOR server"))

        wdgTORServer = QWidget()
        wdgTORServer.setLayout(layTORServer)

        self.dashboardTabIndex = 0
        self.clientJobsTabIndex = 1
        self.clientDetailsTabIndex = 2
        self.statisticsTabIndex = 3

        self.tabDashboard = QTabWidget()
        self.tabDashboard.addTab(wdgDashboard, "Dashboard")
        #self.tabDashboard.addTab(wdgTORServer, "TORServer")
        self.tabDashboard.addTab(wdgJobOverivew, "Jobs")
        self.tabDashboard.addTab(wdgDetails, "Detail View")
        self.tabDashboard.addTab(tabStatistics, "Statistics")
        self.dashboardTabIndex = 0
        self.tabDashboard.currentChanged.connect(self.tabDashboard_currentChanged)

        self.txtStatus = QPlainTextEdit()
        self.txtStatus.setReadOnly(True)

        splMain = QSplitter(Qt.Vertical)
        splMain.addWidget(self.tabDashboard)
        splMain.addWidget(self.txtStatus)

        self.setCentralWidget(splMain)

        self.initDashboard()
        self.updateDashboard()
        timerFetchData = QTimer(self)
        timerFetchData.timeout.connect(self.updateDashboardFromTimer)
        timerFetchData.start(120 * 1000)

    ###############
    ### methods ###
    ###############

    def reloadAllClientStatus(self):
        threadPool = concurrent.futures.ThreadPoolExecutor(THREAD_POOL_SIZE)
        threadFutures = [threadPool.submit(cdv.clientDetails.getClientStatus) for cdv in self.cdvs if cdv.clientDetails is not None]
        concurrent.futures.wait(threadFutures)

    def reloadClients(self):
        with WaitCursor():
            clients = DBManager.getAllClients()
            self.cds.clear()
            for cdv in self.cdvs:
                cdv.clientDetails = None
                for c in clients:
                    if c.Position == cdv.position:
                        cd = ClientDetails(c)
                        cdv.clientDetails = cd
                        self.cds.append(cd)
                cdv.updateClientArea()
            self.reloadAllClientStatus()
            for cdv in self.cdvs:
                cdv.refreshClientStatus()

    def openClientDetailTab(self, clientId):
        with WaitCursor():
            self.tabDashboard.setCurrentIndex(self.clientDetailsTabIndex)
            for i in range(self.cmbClient.count()):
                c = self.cmbClient.itemData(i)
                if c is not None and c != 0 and c.Id == clientId:
                    self.cmbClient.setCurrentIndex(i)
                    break
            self.chkLogMessagesError.setChecked(True)
            self.chkLogMessagesWarning.setChecked(False)
            self.chkLogMessagesInfo.setChecked(False)

    def tabDashboard_currentChanged(self, index):
        with WaitCursor():
            if index == self.dashboardTabIndex:
                self.updateDashboard()
            elif index == self.clientJobsTabIndex:
                self.cmbTour.setCurrentText("JMAF2022")
            elif index == self.clientDetailsTabIndex:
                self.loadAllClientDetails()
            elif index == self.statisticsTabIndex:
                pass
            self.currentSelectedTabIndex = index

    def sendMsgToTORServer(self, msg, timeout=ts.STATUS_TIMEOUT_TOR_SERVER):
        answer = None
        try:
            conn = NetworkUtils.createConnection(ts.SERVER_IP, ts.SERVER_PORT, timeout, verbose=False)
            NetworkUtils.sendData(conn, msg)
            answer = NetworkUtils.recvData(conn)
            conn.close()
        except Exception as e:
            log.error("Error connecting to TORServer:")
            log.error("{}".format(repr(e)))
        return answer

    def checkStatusTORServer(self):
        msg = { "DASH": "STATUS" }
        answer = self.sendMsgToTORServer(msg)
        if isinstance(answer, dict) and "STATUS" in answer and answer["STATUS"] == "OK":
            self.svgStatusTORServer.load(TORIcons.LED_GREEN)
            self.svgStatusTORServer.setToolTip("running")
        else:
            self.svgStatusTORServer.load(TORIcons.LED_RED)
            self.svgStatusTORServer.setToolTip("not responding")

    def checkStatusTORInteractive(self):
        import requests
        isUp = False
        try:
            response = requests.head(f"http://{ts.TOR_INTERACTIVE_IP}/check", timeout=1)
            isUp = response.status_code == 200
        except requests.RequestException as e:
            log.error("Could not reach TOR-Interactive:")
            log.error("{}".format(repr(e)))
        if isUp:
            self.svgStatusTORInteractive.load(TORIcons.LED_GREEN)
            self.svgStatusTORInteractive.setToolTip("running")
        else:
            self.svgStatusTORInteractive.load(TORIcons.LED_RED)
            self.svgStatusTORInteractive.setToolTip("not responding")

    def executeCommandOnTORServer(self, cmd, timeout=DEFAULT_TIMEOUT_SERVER):
        val = -1
        with WaitCursor():
            cmdSSH = TORCommands.SERVER_SSH_CONNECTION.format(tsl.PATH_TO_SSH_KEY, tsl.SERVER_IP)
            cmdFull = cmdSSH + " \"" + cmd + "\""
            log.info("SERVEXE: {}".format(cmdFull))
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

    def sendMsgToAllClients(self, msg, timeout=ts.STATUS_TIMEOUT, onlyActive=False):
        threadPool = concurrent.futures.ThreadPoolExecutor(THREAD_POOL_SIZE)
        threadFutures = [threadPool.submit(c.sendMsgToStatusManager, msg, timeout) for c in self.cds if (c.IsOnline and (not onlyActive or c.IsActive))]
        concurrent.futures.wait(threadFutures)

    def initDashboard(self):
        for cdv in self.cdvs:
            if cdv.clientDetails is not None:
                cdv.svgIsOnline.setToolTip("Id: {}\nIP: {}\nMaterial: {}\nLatin name: {}".format(cdv.clientDetails.Id, cdv.clientDetails.IP, cdv.clientDetails.Material, cdv.clientDetails.Latin))
                cdv.lblIp.setText(cdv.clientDetails.IP)

    def updateDashboardFromTimer(self):
        if not self.IsBusy and self.tabDashboard.currentIndex() == self.dashboardTabIndex:
            self.updateDashboard()

    def updateDashboard(self):
        if self.IsUpdating:
            return
        self.IsUpdating = True
        log.info("updateDashboard")
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
                    c.UseSchedule = d.UseSchedule
                    break
        for cdv in self.cdvs:
            if cdv.clientDetails is not None:
                if isinstance(cdv, ClientDetailViewFull):
                    cdv.refreshJobDisplay()
                else:
                    jobStr = "{} {}".format(cdv.clientDetails.CurrentJobCode, cdv.clientDetails.CurrentJobParameters)
                    cdv.lblCurrentJob.setText(jobStr[0:9])
                    cdv.lblCurrentJob.setToolTip(jobStr)
                cdv.lblResultAverage.setText("{:.2f}±{:.2f}".format(cdv.clientDetails.ResultAverage, cdv.clientDetails.ResultStddev))
                cdv.lblResultStddev.setText("+-{}".format(cdv.clientDetails.ResultStddev))
                if cdv.clientDetails.IsBadStatistics():
                    cdv.svgResultAverageStatus.load(TORIcons.LED_RED)
                else:
                    cdv.svgResultAverageStatus.load(TORIcons.LED_GREEN)
                if isinstance(cdv, ClientDetailViewFull):
                    cdv.refreshErrorLog()

        self.reloadAllClientStatus()

        for cdv in self.cdvs:
            cdv.refreshClientStatus()

        self.checkStatusTORServer()
        self.checkStatusTORInteractive()

        self.lblLastUpdateTime.setText("last update: {}".format(datetime.now().strftime("%H:%M:%S")))
        log.info("updateDashboard finished")
        self.IsUpdating = False

    def addSpacerLineToStatusText(self):
        self.txtStatus.appendPlainText("----------------------")
        self.txtStatus.moveCursor(QTextCursor.End)
        app.processEvents()

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

    def btnStartQuickTour_clicked(self):
        with WaitCursor():
            jobProgramName = self.cmbQuickTour.currentData()
            if jobProgramName is not None and jobProgramName != "":
                DBManager.setJobsByJobProgram(jobProgramName)
                self.updateDashboard()

    def btnStartAllTORPrograms_clicked(self):
        with WaitCursor():
            DBManager.clearAllCurrentStates()
            self.executeCommandOnTORServer(TORCommands.SERVER_SERVICE_START)
            self.sendMsgToAllClients(TORCommands.MSG_CLIENT_SERVICE_START, timeout=ts.STATUS_TIMEOUT_SERVICE, onlyActive=True)
            self.executeCommandOnTORServer(TORCommands.INTERACTIVE_START)
            if ss.STARTUP_JOB_PROGRAM_NAME is not None and ss.STARTUP_JOB_PROGRAM_NAME != "":
                DBManager.setJobsByJobProgram(ss.STARTUP_JOB_PROGRAM_NAME, ss.STARTUP_JOB_DELAY_MINUTES)
            for c in self.cds:
                if not c.IsActive:
                    c.sendMsgToStatusManager(TORCommands.MSG_CLIENT_TURN_ON_LEDS, ts.STATUS_TIMEOUT_LED)

    def btnStopAllTORPrograms_clicked(self):
        with WaitCursor():
            jobs = []
            for c in self.cds:
                j = copy.deepcopy(DefaultJobs.WAIT)
                j.ClientId = c.Id
                jobs.append(j)
            DBManager.saveJobs(jobs)

            allWaiting = False
            countWaiting = 0
            while allWaiting == False:
                time.sleep(5)
                busyClients = DBManager.getBusyClients()
                if len(busyClients) == 0:
                    allWaiting = True
                else:
                    msg = "waiting for {} boxes to finish...".format(len(busyClients))
                    log.info(msg)
                    self.addStatusText(msg)
                countWaiting = countWaiting + 1
                if countWaiting > 15:
                    break

            msg = "all boxes ready waiting..."
            log.info(msg)
            self.addStatusText(msg)
            time.sleep(3)
            self.executeCommandOnTORServer(TORCommands.INTERACTIVE_STOP)
            self.sendMsgToAllClients(TORCommands.MSG_CLIENT_SERVICE_STOP, ts.STATUS_TIMEOUT_SERVICE)
            self.executeCommandOnTORServer(TORCommands.SERVER_SERVICE_STOP)
            DBManager.clearAllCurrentStates()
            time.sleep(3)
            self.sendMsgToAllClients(TORCommands.MSG_CLIENT_TURN_OFF_LEDS, ts.STATUS_TIMEOUT_LED)

    def btnStartAllClientService_clicked(self):
        log.info("start")
        with WaitCursor():
            self.sendMsgToAllClients(TORCommands.MSG_CLIENT_SERVICE_START, ts.STATUS_TIMEOUT_SERVICE, onlyActive=True)
        self.updateDashboard()

    def btnStopAllClientService_clicked(self):
        log.info("stop")
        with WaitCursor():
            self.sendMsgToAllClients(TORCommands.MSG_CLIENT_SERVICE_STOP, ts.STATUS_TIMEOUT_SERVICE)
        self.updateDashboard()

    def btnSaveSettings_clicked(self):
        log.info("saved")

    def btnRestoreSettings_clicked(self):
        log.info("restored")

    def btnStartTORServer_clicked(self):
        self.svgStatusTORServer.load(TORIcons.LED_GRAY)
        self.svgStatusTORServer.setToolTip("starting...")
        app.processEvents()
        self.executeCommandOnTORServer(TORCommands.SERVER_SERVICE_START)
        log.info("start TORServer")
        self.checkStatusTORServer()

    def btnStopTORServer_clicked(self):
        self.svgStatusTORServer.load(TORIcons.LED_GRAY)
        self.svgStatusTORServer.setToolTip("stopping...")
        app.processEvents()
        self.executeCommandOnTORServer(TORCommands.SERVER_SERVICE_STOP)
        log.info("stop TORServer")
        self.checkStatusTORServer()

    def btnStartTORInteractive_clicked(self):
        self.svgStatusTORInteractive.load(TORIcons.LED_GRAY)
        self.svgStatusTORInteractive.setToolTip("starting...")
        self.executeCommandOnTORServer(TORCommands.INTERACTIVE_START)
        log.info("start tor interactive")
        self.checkStatusTORInteractive()

    def btnStopTORInteractive_clicked(self):
        self.svgStatusTORInteractive.load(TORIcons.LED_GRAY)
        self.svgStatusTORInteractive.setToolTip("starting...")
        self.executeCommandOnTORServer(TORCommands.INTERACTIVE_STOP)
        log.info("stop tor interactive")
        self.checkStatusTORInteractive()

    def btnEndAllUserModes_clicked(self):
        #INFO: only sets flags realted to usermode in database, client should exit after given time interval by its own
        for c in self.cds:
            DBManager.exitUserMode(c.Id)
        log.info("ended all user modes")

    def btnTurnOnLEDs_clicked(self):
        self.sendMsgToAllClients(TORCommands.MSG_CLIENT_TURN_ON_LEDS, ts.STATUS_TIMEOUT_LED)
        log.info("turn on LEDs")

    def btnTurnOffLEDs_clicked(self):
        self.sendMsgToAllClients(TORCommands.MSG_CLIENT_TURN_OFF_LEDS, ts.STATUS_TIMEOUT_LED)
        log.info("turn off LEDs")

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
        for cd in self.cds:
            if cd.Position == position:
                return cd
        return None

    def showDataInTable(self, data, table, tableModel):
        model = tableModel(data)
        proxyModel = QSortFilterProxyModel()
        proxyModel.setSourceModel(model)
        table.setModel(proxyModel)

    def showDataInLogMessagesTable(self, data, table, tableModel, clientId):
        model = tableModel(data)
        self.prxLogMessages.clientId = clientId
        proxyModel = self.prxLogMessages
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
        self.setTableWidths(self.tblResultStatistics, [w, 100, w, w, w, w, w, w, w, w])

    def loadAllClientDetails(self):
        logMessages = DBManager.getClientLog()
        self.showDataInLogMessagesTable(logMessages, self.tblLogMessages, LogMessageTableModel, None)
        self.setTableWidths(self.tblLogMessages, [50, 150, 50, 150, 200, 200])

        diceResults = DBManager.getResults()
        self.showDataInTable(diceResults, self.tblResults, DiceResultTableModel)
        self.setTableWidths(self.tblResults, [50, 150, 50, 50, 50, 50, 200])

        self.loadResultStatistics()

        for i in range(len(self.clientDetailInfoList)):
            self.setClientDetailInfoListText(i, "---")

    def loadClientDetails(self, client):
        logMessages = DBManager.getClientLogByClientId(client.Id)
        self.showDataInLogMessagesTable(logMessages, self.tblLogMessages, LogMessageTableModel, client.Id)
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
        self.setClientDetailInfoListText(6, "YES" if client.UseSchedule else "NO")
        self.setClientDetailInfoListText(7, client.Position)

        clientContributions = DBManager.getAllClientResultContribution(TAKE_N_RESULTS_FOR_RECENT_CONTRIBUTIONS)
        for cc in clientContributions:
            if cc.Id == client.Id:
                self.setClientDetailInfoListText(11, "{:.2f}".format(cc.Contribution))
                self.setClientDetailInfoListText(12, "{:.2f}".format(cc.AverageResult))
                break

    def reloadClientDetailsBySelectedIndex(self, index):
        c = self.cmbClient.itemData(index)
        if c is None:
            self.addStatusText("show details for all clients")
            self.loadAllClientDetails()
            self.cdvDetails.clientDetails = None
        else:
            self.addStatusText(f"select client {c.Id}")
            self.loadClientDetails(c)
            self.cdvDetails.clientDetails = ClientDetails(c)
            job = DBManager.getNextJobForClientId(c.Id)
            self.cdvDetails.clientDetails.CurrentJobCode = job.JobCode
            self.cdvDetails.clientDetails.CurrentJobParameters = job.JobParameters
            self.cdvDetails.clientDetails.getClientStatus()
        self.cdvDetails.updateClientArea()
        self.cdvDetails.refreshClientStatus()
        self.cdvDetails.refreshJobDisplay()
        self.cdvDetails.refreshErrorLog()

    def cmbClient_currentIndexChanged(self, index):
        self.reloadClientDetailsBySelectedIndex(index)

    def btnRefreshClientDetails_clicked(self):
        index = self.cmbClient.currentIndex()
        self.reloadClientDetailsBySelectedIndex(index)

    #############
    ### Plots ###
    #############

    def filterResultStatistic_update(self):
        start, end, event = self.filterResultStatistic.getDateAndEvent()
        self.pltResultStatistic.updatePlot(start, end, event)
        self.pltResultStatistic.canvas.draw()

    def filterRollWarnings_update(self):
        start, end, _ = self.filterRollWarnings.getDateAndEvent()
        self.pltRollWarnings.updatePlot(start, end)
        self.pltRollWarnings.canvas.draw()

    def filterResultPositions_update(self):
        start, end, event = self.filterResultPositions.getDateAndEvent()
        globalColorBar = self.chkResultPositionsGlobalColorbar.isChecked()
        self.pltResultPositions.updatePlot(start, end, event, globalColorBar)
        self.pltResultPositions.canvas.draw()

    def filterPickupProblems_update(self):
        start, end, _ = self.filterPickupProblems.getDateAndEvent()
        globalColorBar = self.chkPickupProblemsGlobalColorbar.isChecked()
        self.pltPickupProblems.updatePlot(start, end, globalColorBar)
        self.pltPickupProblems.canvas.draw()

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

###################
### application ###
###################

log.info("Start Dashboard")

window = MainWindow()
window.show()

app.exec()
