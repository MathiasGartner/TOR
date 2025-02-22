import logging
log = logging.getLogger(__name__)

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QComboBox, QGridLayout, QLineEdit, QGroupBox, QHBoxLayout, QInputDialog, QLabel, QPushButton, QVBoxLayout, QWidget

from tor.base import DBManager
from tor.base.GUI import TORIcons
from tor.server.GUI.ClientDetailViewBase import ClientDetailViewBase
from tor.server.Job import Job, DefaultJobs

class ClientDetailViewFull(ClientDetailViewBase):
    def __init__(self, app, position: int, changeClientCallback=None):
        super().__init__()

        self.app = app

        self.position = position
        self.changeClientCallback = changeClientCallback

        self.lblTORVersion = QLabel()
        self.lblTORVersionText = QLabel()
        self.lblStatusServiceRunning = QLabel()
        self.lblClientServiceRunning = QLabel()

        self.btnX = QPushButton()
        self.btnX.setIcon(TORIcons.ICON_CLOSE_BTN)
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
        layMain.addWidget(self.btnX, alignment=Qt.AlignRight)

        layClientStatus = QGridLayout()
        #layClientStatus.setContentsMargins(0, 0, 0, 0)
        row = 0
        layClientStatus.addWidget(QLabel("online:"), row, 0)
        layClientStatus.addWidget(self.lblIsOnline, row, 1)
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
        layClientStatus.addWidget(self.lblResultAverage, row, 1)
        #layClientStatus.addWidget(QLabel("stddev:"), 3, 0)
        #layClientStatus.addWidget(self.lblResultStddev, 3, 1)

        grpClientStatus = QGroupBox("Status")
        grpClientStatus.setLayout(layClientStatus)

        #LEDs
        layLEDs = QHBoxLayout()
        #layLEDs.setContentsMargins(0, 0, 0, 0)
        self.btnTurnOnLEDs.setFixedSize(30, 18)
        self.btnTurnOffLEDs.setFixedSize(30, 18)
        layLEDs.addWidget(self.btnTurnOnLEDs)
        layLEDs.addWidget(self.btnTurnOffLEDs)
        grpLEDs = QGroupBox("LEDs")
        grpLEDs.setLayout(layLEDs)

        #Job
        layJob = QGridLayout()
        row = 0
        layJob.addWidget(QLabel("Current Job:"), row, 0)
        self.cmbCurrentJob = QComboBox()
        for i, j in enumerate(DefaultJobs.JOBLIST_USER_SELECTABLE):
            self.cmbCurrentJob.insertItem(i, f"{j.JobCode} - {j.Description}", j)
        self.cmbCurrentJob.currentIndexChanged.connect(self.cmbCurrentJob_currentIndexChanged)
        layJob.addWidget(self.cmbCurrentJob, row, 1)
        row += 1
        layJob.addWidget(QLabel("Job Parameters:"), row, 0)
        self.txtJobParams = QLineEdit()
        self.txtJobParams.setFixedWidth(130)
        layJob.addWidget(self.txtJobParams, row, 1)
        lblJobParamsInfo = QLabel()
        lblJobParamsInfo.setPixmap(TORIcons.ICON_INFO)
        lblJobParamsInfo.setToolTip("<b>R:</b> no Job Parameters<br/><br/><b>W:</b> no Job Parameters<br/><br/><b>RW:</b> JobParameters: r w t<br/>run 'r' times, then wait 'w' times for 't' seconds")
        layJob.addWidget(lblJobParamsInfo, row, 2)
        row += 1
        btnSaveJob = QPushButton("SAVE")
        btnSaveJob.clicked.connect(self.btnSaveJob_clicked)
        layJob.addWidget(btnSaveJob, row, 1)
        grpJob = QGroupBox("Job")
        grpJob.setLayout(layJob)

        #Options
        layClientOptions = QGridLayout()
        #layClientOptions.setContentsMargins(0, 0, 0, 0)
        layClientOptions.addWidget(QLabel("User mode enabled"), 0, 0)
        layClientOptions.addWidget(self.chkUserMode, 0, 1)
        layClientOptions.addWidget(QLabel("Client activated"), 1, 0)
        layClientOptions.addWidget(self.chkIsActivated, 1, 1)
        grpClientOptions = QGroupBox("Options")
        grpClientOptions.setLayout(layClientOptions)

        layMain.addWidget(grpClientStatus)
        layMain.addWidget(grpLEDs)
        layMain.addWidget(grpJob)
        layMain.addWidget(grpClientOptions)

        self.layStack = QVBoxLayout()
        self.layStack.addWidget(self.wdgEmpty)
        self.layStack.addWidget(self.wdgMain)

        self.grpMainGroup = QGroupBox()
        self.grpMainGroup.setObjectName("ClientDetails")
        self.grpMainGroup.setTitle("Client #")
        self.grpMainGroup.setLayout(self.layStack)

        layMainGroup = QVBoxLayout()
        #layMainGroup.setContentsMargins(0, 0, 0, 0)
        layMainGroup.addWidget(self.grpMainGroup)
        self.setLayout(layMainGroup)


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

