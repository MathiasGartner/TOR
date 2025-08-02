import logging
log = logging.getLogger(__name__)

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QStyle, QComboBox, QGridLayout, QLineEdit, QGroupBox, QHBoxLayout, QInputDialog, QLabel, QPushButton, QVBoxLayout, QWidget

from tor.base import DBManager
from tor.base.GUI import TORIcons
from tor.server.GUI.ClientDetailViewBase import ClientDetailViewBase
from tor.server.Job import Job, DefaultJobs

class ClientDetailViewFull(ClientDetailViewBase):
    def __init__(self, app, position: int, changeClientCallback=None, openDetailTabCallback=None, compact=False):
        super().__init__()

        self.app = app

        self.position = position
        self.changeClientCallback = changeClientCallback
        self.openDetailTabCallback = openDetailTabCallback
        self.inInstallation = self.position > 0

        self.lblTORVersion = QLabel()
        self.lblTORVersionText = QLabel()
        self.lblStatusServiceRunning = QLabel()
        self.lblClientServiceRunning = QLabel()
        self.lblResultAverageStatus = QLabel()

        self.btnX = QPushButton()
        self.btnX.setIcon(QApplication.style().standardIcon(QStyle.SP_DialogCancelButton))
        #self.btnX.setIcon(TORIcons.ICON_CLOSE_BTN)
        self.btnX.setFixedSize(16, 16)
        self.btnX.clicked.connect(self.btnX_clicked)
        self.btnChange = QPushButton()
        self.btnChange.setIcon(TORIcons.ICON_ADD_BTN)
        self.btnChange.setFixedSize(50, 50)
        self.btnChange.clicked.connect(self.btnChange_clicked)

        self.wdgEmpty = QWidget()
        layEmpty = QVBoxLayout(self.wdgEmpty)
        layEmpty.addWidget(self.btnChange, alignment=Qt.AlignCenter)

        self.wdgMain = QWidget()
        layMain = QVBoxLayout(self.wdgMain)
        #layMain.addWidget(self.btnX, alignment=Qt.AlignRight)

        layClientStatus = QGridLayout()
        row = 0
        layClientStatus.addWidget(QLabel("online:"), row, 0)
        layClientStatus.addWidget(self.lblIsOnline, row, 1)
        layClientStatus.addWidget(self.btnX, row, 1, alignment=Qt.AlignRight)
        row += 1
        layClientStatus.addWidget(QLabel("Version:"), row, 0)
        layClientStatus.addWidget(self.lblTORVersion, row, 1)
        layClientStatus.addWidget(self.lblTORVersionText, row, 2)
        row += 1
        layClientStatus.addWidget(QLabel("responding:"), row, 0)
        layClientStatus.addWidget(self.lblStatusServiceRunning, row, 1)
        row += 1
        layClientStatus.addWidget(QLabel("running:"), row, 0)
        layClientStatus.addWidget(self.lblClientServiceRunning, row, 1)
        #row += 1
        #layClientStatus.addWidget(QLabel("current job:"), row, 0)
        #layClientStatus.addWidget(self.lblCurrentJob, row, 1)
        row += 1
        layClientStatus.addWidget(QLabel("avg result:"), row, 0)
        layClientStatus.addWidget(self.lblResultAverageStatus, row, 1)
        layClientStatus.addWidget(self.lblResultAverage, row, 2)
        #layClientStatus.addWidget(QLabel("stddev:"), 3, 0)
        #layClientStatus.addWidget(self.lblResultStddev, 3, 1)

        grpClientStatus = QGroupBox("Status")
        grpClientStatus.setProperty("styleClass", "group-box-compact")
        grpClientStatus.setLayout(layClientStatus)

        #Client Service
        w = 40
        h = 16
        layClientService = QHBoxLayout()
        self.btnStartClientService.setFixedSize(w, h)
        self.btnStartClientService.setProperty("styleClass", "button-compact")
        self.btnStopClientService.setFixedSize(w, h)
        self.btnStopClientService.setProperty("styleClass", "button-compact")
        layClientService.addWidget(self.btnStartClientService)
        layClientService.addWidget(self.btnStopClientService)
        grpClientService = QGroupBox("Program")
        grpClientService.setProperty("styleClass", "group-box-compact")
        grpClientService.setLayout(layClientService)

        #LEDs
        w = 40
        h = 16
        layLEDs = QHBoxLayout()
        self.btnTurnOnLEDs.setFixedSize(w, h)
        self.btnTurnOnLEDs.setProperty("styleClass", "button-compact")
        self.btnTurnOffLEDs.setFixedSize(w, h)
        self.btnTurnOffLEDs.setProperty("styleClass", "button-compact")
        layLEDs.addWidget(self.btnTurnOnLEDs)
        layLEDs.addWidget(self.btnTurnOffLEDs)
        grpLEDs = QGroupBox("LEDs")
        grpLEDs.setProperty("styleClass", "group-box-compact")
        grpLEDs.setLayout(layLEDs)

        #Job
        layJob = QGridLayout()
        w = 90
        h = 20
        row = 0
        layJob.addWidget(QLabel("Name:"), row, 0)
        self.cmbCurrentJob = QComboBox()
        for i, j in enumerate(DefaultJobs.JOBLIST_USER_SELECTABLE):
            self.cmbCurrentJob.insertItem(i, f"{j.JobCode} - {j.Description}", j)
        self.cmbCurrentJob.currentIndexChanged.connect(self.cmbCurrentJob_currentIndexChanged)
        self.cmbCurrentJob.setFixedSize(w, h)
        layJob.addWidget(self.cmbCurrentJob, row, 1)
        row += 1
        layJob.addWidget(QLabel("Parameters:"), row, 0)
        self.txtJobParams = QLineEdit()
        self.txtJobParams.setFixedSize(w, h)
        layJob.addWidget(self.txtJobParams, row, 1)
        lblJobParamsInfo = QLabel()
        lblJobParamsInfo.setPixmap(TORIcons.ICON_INFO)
        lblJobParamsInfo.setToolTip("<b>R:</b> no Job Parameters<br/><br/><b>W:</b> no Job Parameters<br/><br/><b>RW:</b> JobParameters: r w t<br/>run 'r' times, then wait 'w' times for 't' seconds")
        layJob.addWidget(lblJobParamsInfo, row, 2)
        row += 1
        self.btnSaveJob = QPushButton("SAVE")
        self.btnSaveJob.setFixedSize(w, h)
        self.btnSaveJob.clicked.connect(self.btnSaveJob_clicked)
        layJob.addWidget(self.btnSaveJob, row, 1)
        grpJob = QGroupBox("Job")
        grpJob.setProperty("styleClass", "group-box-compact")
        grpJob.setLayout(layJob)

        #Options
        layClientOptions = QGridLayout()
        layClientOptions.addWidget(QLabel("User mode enabled"), 0, 0)
        layClientOptions.addWidget(self.chkUserMode, 0, 1)
        layClientOptions.addWidget(QLabel("Client activated"), 1, 0)
        layClientOptions.addWidget(self.chkIsActivated, 1, 1)
        grpClientOptions = QGroupBox("Options")
        grpClientOptions.setProperty("styleClass", "group-box-compact")
        grpClientOptions.setLayout(layClientOptions)

        #Error Log
        layErrorLog = QGridLayout()
        self.lblErrorLogIcon = QLabel()
        layErrorLog.addWidget(self.lblErrorLogIcon, 0, 0)
        self.lblErrorLogMessage = QLabel()
        self.lblErrorLogMessage.setWordWrap(True);
        layErrorLog.addWidget(self.lblErrorLogMessage, 0, 1)
        self.btnErrorLogAcknowledge = QPushButton()
        self.btnErrorLogAcknowledge.setIcon(QApplication.style().standardIcon(QStyle.SP_DialogApplyButton))
        self.btnErrorLogAcknowledge.clicked.connect(self.btnErrorLogAcknowledge_clicked)
        layErrorLog.addWidget(self.btnErrorLogAcknowledge, 0, 2)
        self.btnErrorLogGoToDetails = QPushButton()
        self.btnErrorLogGoToDetails.setIcon(QApplication.style().standardIcon(QStyle.SP_CommandLink))
        self.btnErrorLogGoToDetails.clicked.connect(self.btnErrorLogGoToDetails_clicked)
        layErrorLog.addWidget(self.btnErrorLogGoToDetails, 0, 3)
        grpErrorLog = QGroupBox("Error Log")
        grpErrorLog.setProperty("styleClass", "group-box-compact")
        grpErrorLog.setLayout(layErrorLog)

        layMain.addWidget(grpClientStatus)
        if compact:
            layClientServiceAndLEDs = QHBoxLayout()
            layClientServiceAndLEDs.addWidget(grpClientService)
            layClientServiceAndLEDs.addWidget(grpLEDs)
            layMain.addLayout(layClientServiceAndLEDs)
        else:
            layMain.addWidget(grpClientService)
            layMain.addWidget(grpLEDs)
        layMain.addWidget(grpJob)
        layMain.addWidget(grpClientOptions)
        layMain.addWidget(grpErrorLog)

        self.layStack = QVBoxLayout()
        self.layStack.addWidget(self.wdgEmpty)
        self.layStack.addWidget(self.wdgMain)

        self.grpMainGroup = QGroupBox()
        self.grpMainGroup.setObjectName("ClientDetails")
        self.grpMainGroup.setTitle("Client #")
        self.grpMainGroup.setLayout(self.layStack)

        layMainGroup = QVBoxLayout()
        layMainGroup.addWidget(self.grpMainGroup)
        self.setLayout(layMainGroup)

        if compact:
            layClientStatus.setContentsMargins(0, 0, 0, 0)
            layClientService.setContentsMargins(0, 0, 0, 0)
            layLEDs.setContentsMargins(0, 0, 0, 0)
            layClientOptions.setContentsMargins(0, 0, 0, 0)
            layClientOptions.setContentsMargins(0, 0, 0, 0)
            self.layStack.setContentsMargins(0, 0, 0, 0)
            layMainGroup.setContentsMargins(0, 0, 0, 0)


    def updateClientArea(self):
        if self.clientDetails is None:
            self.grpMainGroup.setTitle("No Box selected")
            self.wdgEmpty.setVisible(True)
            self.wdgMain.setVisible(False)
        else:
            self.grpMainGroup.setTitle("#{}: {}".format(self.clientDetails.Position, self.clientDetails.Latin))
            self.wdgEmpty.setVisible(False)
            self.wdgMain.setVisible(True)
        self.app.processEvents()

    def btnX_clicked(self):
        DBManager.setClientPosition(self.clientDetails.Id, None)
        self.clientDetails = None
        self.changeClientCallback()

    def btnChange_clicked(self):
        clients = DBManager.getAllAvailableClients()
        options = []
        for c in clients:
            options.append(f"\"{c.Latin}\" {f'(currently at pos. {c.Position})' if c.Position is not None else ''}")
        selection, okPressed = QInputDialog.getItem(self, f"Choose Box for Position {self.position}:", "Box:", options, 0, False)
        if okPressed and selection:
            selectedIndex = 0
            for c in options:
                if selection == c:
                    break
                selectedIndex += 1
            client = clients[selectedIndex]
            DBManager.setClientPosition(client.Id, self.position)
            self.changeClientCallback()

    def cmbCurrentJob_currentIndexChanged(self, index):
        self.txtJobParams.clear()

    def btnSaveJob_clicked(self):
        if self.clientDetails is not None:
            selectedJob: Job = self.cmbCurrentJob.currentData()
            selectedJob.ClientId = self.clientDetails.Id
            selectedJob.JobParameters = self.txtJobParams.text()
            DBManager.saveJobs(selectedJob)

    def btnErrorLogAcknowledge_clicked(self):
        if self.ErrorMessage is not None:
            DBManager.acknowledgeErrorLog(self.ErrorMessage.Id)
            self.refreshErrorLog()

    def btnErrorLogGoToDetails_clicked(self):
        self.openDetailTabCallback(self.clientDetails.Id)

    def refreshErrorLog(self):
        self.ErrorMessage = None
        if self.clientDetails is not None:
            self.ErrorMessage = DBManager.getRecentClientLogError(self.clientDetails.Id)
            if self.ErrorMessage is not None:
                self.lblErrorLogIcon.setPixmap(TORIcons.LED_RED)
                self.lblErrorLogMessage.setText(f"{self.ErrorMessage.Message}\nTime: {self.ErrorMessage.Time}\nCode: {self.ErrorMessage.MessageCode}")
                self.btnErrorLogAcknowledge.setVisible(True)
                if self.inInstallation:
                    self.btnErrorLogGoToDetails.setVisible(True)
                self.grpMainGroup.setStyleSheet("QGroupBox#ClientDetails {border-color: #FF0000} QGroupBox:title#ClientDetails { background-color: #FF0000 }")
        if self.ErrorMessage is None:
            self.lblErrorLogIcon.setPixmap(TORIcons.LED_GREEN)
            self.lblErrorLogMessage.setText("---")
            self.btnErrorLogAcknowledge.setVisible(False)
            self.btnErrorLogGoToDetails.setVisible(False)
            self.grpMainGroup.setStyleSheet("")
        self.app.processEvents()

    def refreshJobDisplay(self):
        if self.clientDetails is not None:
            index = self.cmbCurrentJob.findText(f"{self.clientDetails.CurrentJobCode} - ", Qt.MatchStartsWith)
            if index != -1:
                self.cmbCurrentJob.setCurrentIndex(index)
            self.txtJobParams.setText(self.clientDetails.CurrentJobParameters)
            self.btnSaveJob.setEnabled(True)
        else:
            self.cmbCurrentJob.setCurrentIndex(0)
            self.txtJobParams.setText("")
            self.btnSaveJob.setEnabled(False)

    def refreshClientStatus(self):
        if self.clientDetails is not None:
            self.lblIsOnline.setPixmap(TORIcons.LED_GREEN if self.clientDetails.IsOnline else TORIcons.LED_RED)
            self.lblTORVersion.setPixmap(TORIcons.LED_GREEN if self.clientDetails.VersionOkay else TORIcons.LED_RED)
            self.lblTORVersionText.setText(self.clientDetails.Version)

            self.lblStatusServiceRunning.setToolTip(self.clientDetails.StatusManagerServiceStatus)

            if self.clientDetails.StatusManagerServiceStatus == "active":
                self.lblStatusServiceRunning.setPixmap(TORIcons.LED_GREEN)
            elif self.clientDetails.StatusManagerServiceStatus == "inactive":
                self.lblStatusServiceRunning.setPixmap(TORIcons.LED_RED)
            else:
                self.lblStatusServiceRunning.setPixmap(TORIcons.LED_GRAY)

            self.lblClientServiceRunning.setToolTip(self.clientDetails.ClientServiceStatus)
            if self.clientDetails.ClientServiceStatus == "active":
                self.lblClientServiceRunning.setPixmap(TORIcons.LED_GREEN)
            elif self.clientDetails.ClientServiceStatus == "inactive":
                self.lblClientServiceRunning.setPixmap(TORIcons.LED_RED)
            else:
                self.lblClientServiceRunning.setPixmap(TORIcons.LED_GRAY)

            self.chkUserMode.setChecked(self.clientDetails.AllowUserMode)
            self.chkIsActivated.setChecked(self.clientDetails.IsActive)

        self.app.processEvents()

