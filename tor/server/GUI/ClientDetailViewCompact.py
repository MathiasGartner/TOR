from tor.base.LogManager import getLogger
log = getLogger("ClientDetailViewCompact")

from PyQt5.QtSvg import QSvgWidget

from PyQt5.QtWidgets import QGridLayout, QGroupBox, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from tor.base.GUI import TORIcons
from tor.server.GUI.ClientDetailViewBase import ClientDetailViewBase
from tor.server.TORCommands import TORCommands

class ClientDetailViewCompact(ClientDetailViewBase):
    def __init__(self, app):
        super().__init__()

        self.app = app

        layClientStatus = QGridLayout()
        layClientStatus.setContentsMargins(0, 0, 0, 0)
        layClientStatus.addWidget(QLabel("online:"), 0, 0)
        layClientStatus.addWidget(self.svgIsOnline, 0, 1)
        layClientStatus.addWidget(QLabel("current job:"), 1, 0)
        layClientStatus.addWidget(self.lblCurrentJob, 1, 1)
        layClientStatus.addWidget(QLabel("avg result:"), 2, 0)
        layClientStatus.addWidget(self.lblResultAverage, 2, 1)
        #layClientStatus.addWidget(QLabel("stddev:"), 3, 0)
        #layClientStatus.addWidget(self.lblResultStddev, 3, 1)

        grpClientStatus = QGroupBox("Status")
        grpClientStatus.setLayout(layClientStatus)

        layLEDs = QHBoxLayout()
        layLEDs.setContentsMargins(0, 0, 0, 0)
        self.btnTurnOnLEDs.setFixedSize(30, 18)
        self.btnTurnOffLEDs.setFixedSize(30, 18)
        layLEDs.addWidget(self.btnTurnOnLEDs)
        layLEDs.addWidget(self.btnTurnOffLEDs)

        grpLEDs = QGroupBox("LEDs")
        grpLEDs.setLayout(layLEDs)

        # Calibration
        self.btnStartCalibration = QPushButton()
        self.btnStartCalibration.setText("Start")
        self.btnStartCalibration.setFixedSize(50, 18)
        self.btnStartCalibration.clicked.connect(self.btnStartCalibration_clicked)

        layCalibration = QHBoxLayout()
        layCalibration.setContentsMargins(0, 0, 0, 0)
        layCalibration.addWidget(self.btnStartCalibration)

        grpCalibration = QGroupBox("Calibration")
        grpCalibration.setLayout(layCalibration)

        layClientOptions = QGridLayout()
        layClientOptions.setContentsMargins(0, 0, 0, 0)
        layClientOptions.addWidget(QLabel("Visitor control allowed"), 0, 0)
        layClientOptions.addWidget(self.chkUserMode, 0, 1)
        layClientOptions.addWidget(QLabel("Client activated"), 1, 0)
        layClientOptions.addWidget(self.chkIsActivated, 1, 1)

        grpClientOptions = QGroupBox("Options")
        grpClientOptions.setLayout(layClientOptions)

        # TORCLient Service
        self.svgStatusClientService = QSvgWidget(TORIcons.LED_RED)
        self.svgStatusClientService.setToolTip("unknown")
        #self.btnStartClientService.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.btnStartClientService.setFixedSize(45, 22)
        self.btnStopClientService.setFixedSize(45, 22)

        layClientService = QHBoxLayout()
        layClientService.setContentsMargins(0, 0, 0, 0)
        layClientService.addWidget(self.svgStatusClientService)
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
        layMain.addWidget(grpCalibration)
        #layMain.addWidget(wdgLEDs)

        self.grpMainGroup = QGroupBox()
        self.grpMainGroup.setObjectName("ClientDetails")
        self.grpMainGroup.setTitle("Client #")
        self.grpMainGroup.setLayout(layMain)
        layMainGroup = QVBoxLayout()
        layMainGroup.setContentsMargins(0, 0, 0, 0)
        layMainGroup.addWidget(self.grpMainGroup)
        self.setLayout(layMainGroup)

    def btnStartCalibration_clicked(self):
        log.info(f"start calibration for client {self.clientDetails.Latin}.")
        #TODO: set timeout to a proper value
        self.clientDetails.executeSSH(TORCommands.CLIENT_START_CALIBRATION, timeout=7000, asRoot=True)

    def refreshClientStatus(self):
        if self.clientDetails is not None:
            self.svgStatusClientService.setToolTip(self.clientDetails.ClientServiceStatus)
            if self.clientDetails.ClientServiceStatus == "active":
                self.svgStatusClientService.load(TORIcons.LED_GREEN)
            else:
                self.svgStatusClientService.load(TORIcons.LED_GRAY)
            if self.clientDetails.IsOnline:
                self.svgIsOnline.load(TORIcons.LED_GREEN)
            else:
                self.svgIsOnline.load(TORIcons.LED_RED)
            if self.clientDetails.VersionOkay:
                pass
            else:
                pass
            self.chkUserMode.setChecked(self.clientDetails.AllowUserMode)
            self.chkIsActivated.setChecked(self.clientDetails.IsActive)
        self.app.processEvents()
