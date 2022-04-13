import logging
import time
import os
import sys

from functools import partial

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QTabWidget, QGridLayout, QWidget, QPlainTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, QGroupBox, QVBoxLayout, QLayout, QRadioButton, QButtonGroup, QMessageBox
from PyQt5.QtGui import QPixmap, QIcon

app = QApplication(sys.argv)
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

#####################################
### check if TORClient is running ###
#####################################

def getTORClientServiceStatus():
    val = os.system('systemctl is-active --quiet TORClient.service')
    return val

torClientServiceStatus = getTORClientServiceStatus()
#torClientSerivceStatus = 0
while torClientServiceStatus == 0:
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText("Detected running service \"TORClient\".")
    msg.setInformativeText("In order to run the calibration program the TORClient service has to be stopped.")
    msg.setWindowTitle("TOR Calibration")
    closeBtn = msg.addButton("Stop TORClient", QMessageBox.YesRole)
    cancelBtn = msg.addButton("Exit calibration program", QMessageBox.NoRole)
    msg.exec_()
    if msg.clickedButton() == closeBtn:
        print("closing TORClient service")
        with WaitCursor():
            msgInfo = QMessageBox()
            msgInfo.setIcon(QMessageBox.Information)
            msgInfo.setText("Closing service \"TORClient\"...")
            msgInfo.setInformativeText("This window will be closed automatically as soon as the service is finished.")
            msgInfo.setWindowTitle("TOR Calibration")
            msgInfo.setWindowFlags(Qt.CustomizeWindowHint or Qt.WindowTitleHint)
            dummyBtn = msgInfo.addButton("Dummy", QMessageBox.NoRole)
            msgInfo.removeButton(dummyBtn)
            msgInfo.show()
            time.sleep(0.1)
            app.processEvents()
            #TODO: stop TORCLient in a more controlled way, eg. create performance to move to parking pos ("Q") and make sure that the service is not restarted automatically
            if cs.ON_RASPI:
                os.system('sudo systemctl stop TORClient')
            attemptsToWaitForTORClientQuit = 0
            while torClientServiceStatus == 0 and attemptsToWaitForTORClientQuit < 5:
                app.processEvents()
                time.sleep(2)
                torClientServiceStatus = getTORClientServiceStatus()
                attemptsToWaitForTORClientQuit += 1
                print("{}/5".format(attemptsToWaitForTORClientQuit))
            msgInfo.hide()
    else:
        exit()

###################
### TOR imports ###
###################

from tor.client import ClientSettings as cs
from tor.client.MovementManager import MovementManager
if cs.ON_RASPI:
    from tor.client.MovementRoutines import MovementRoutines
from tor.client.Position import Position
if cs.ON_RASPI:
    from tor.base.DieRecognizer import DieRecognizer
if cs.ON_RASPI:
    from tor.client.Camera import Camera
from tor.client.ClientManager import ClientManager
from tor.client.LedManager import LedManager

###############
### logging ###
###############

logging.basicConfig(format='%(levelname)s: %(message)s', level=cs.LOG_LEVEL)
log = logging.getLogger(__name__)

###########################
### get client identity ###
###########################

cm = ClientManager()
welcomeMessage = "I am client with ID {} and IP {}. My ramp is made out of {}, mounted on position {}"
print("#######################")
print(welcomeMessage.format(cm.clientId, cm.clientIdentity["IP"], cm.clientIdentity["Material"], cm.clientIdentity["Position"]))
print("#######################")

### load custom settings from file and server
ccsModuleName = "tor.client.CustomClientSettings." + cm.clientIdentity["Material"]
try:
    import importlib
    customClientSettings = importlib.import_module(ccsModuleName)
    print("Custom config file loaded.")
except:
    print("No CustomClientSettings found.")

if cs.ON_RASPI:
    cm.loadSettings()
    cm.loadMeshpoints()

######################
### Initialization ###
######################
if cs.ON_RASPI:
    lm = LedManager()
    mm = MovementManager()
    mr = MovementRoutines()

########################
### imports on raspi ###
########################
if cs.ON_RASPI:
    import cv2

class CalibrationPoint(QWidget):
    def __init__(self):
        super().__init__()

        self.Id = -1

        self.txtCoordX = QDoubleSpinBox()
        self.txtCoordX.setRange(-50, 300)

        self.txtCoordY = QDoubleSpinBox()
        self.txtCoordX.setRange(-50, 300)

        self.txtCoordZ = QDoubleSpinBox()
        self.txtCoordX.setRange(-50, 300)

        self.btnTestPoint = QPushButton()
        self.btnTestPoint.setText("move to point")

        self.btnMoveToCenter = QPushButton()
        self.btnMoveToCenter.setText("move to center")

        layMain = QGridLayout()
        layMain.addWidget(QLabel("X"), 0, 0)
        layMain.addWidget(self.txtCoordX, 0, 1)
        layMain.addWidget(QLabel("Y"), 1, 0)
        layMain.addWidget(self.txtCoordY, 1, 1)
        layMain.addWidget(QLabel("Z"), 2, 0)
        layMain.addWidget(self.txtCoordZ, 2, 1)
        layMain.addWidget(self.btnTestPoint, 3, 0)
        layMain.addWidget(self.btnMoveToCenter, 3, 1)

        self.grpMainGroup = QGroupBox()
        self.grpMainGroup.setTitle("Point #")
        self.grpMainGroup.setLayout(layMain)
        self.layMainGroup = QVBoxLayout()
        self.layMainGroup.addWidget(self.grpMainGroup)
        self.setLayout(self.layMainGroup)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowIcon(QIcon("../../resources/logo.png"))
        self.setWindowTitle("Calibration")

        # Homing
        self.lblHoming = QLabel("Start the homing routine:")
        self.btnStartHoming = QPushButton("Start")
        self.btnStartHoming.clicked.connect(self.btnStartHoming_clicked)

        layHoming = QGridLayout()
        layHoming.addWidget(self.lblHoming, 0, 0)
        layHoming.addWidget(self.btnStartHoming, 0, 1)

        wdgHoming = QWidget()
        layHoming.setSizeConstraint(QLayout.SetFixedSize)
        wdgHoming.setLayout(layHoming)

        # Bed
        self.bcps = []
        layBedPoints = QGridLayout()
        for r in range(2):
            for c in range(3):
                bcp = CalibrationPoint()
                bcp.Id = 3 * r + c + 1
                bcp.isCloseToRamp = r == 1
                bcp.grpMainGroup.setTitle("Point {}".format(bcp.Id))
                bcp.btnTestPoint.clicked.connect(partial(self.moveToBedPoint_clicked, bcp))
                bcp.btnMoveToCenter.clicked.connect(partial(self.moveToCenterFromBed_clicked, bcp))
                layBedPoints.addWidget(bcp, r, c)
                self.bcps.append(bcp)
        wdgBedPoints = QWidget()
        wdgBedPoints.setLayout(layBedPoints)

        self.btnBedCalibrationDoHoming = QPushButton("Do homing")
        self.btnBedCalibrationDoHoming.clicked.connect(self.btnBedCalibrationDoHoming_clicked)
        self.btnRestoreBedCalibration = QPushButton("Restore settings")
        self.btnRestoreBedCalibration.clicked.connect(self.btnRestoreBedCalibration_clicked)
        self.btnSaveBedCalibration = QPushButton("Save settings")
        self.btnSaveBedCalibration.clicked.connect(self.btnSaveBedCalibration_clicked)

        layBed = QGridLayout()
        layBed.addWidget(QLabel("<h3>Calibrate the pickup points.</h3>\n<h3>Make sure that the pickup works when the point is approached from the center.</h3>"), 0, 0, 1, 3)
        layBed.addWidget(wdgBedPoints, 1, 0, 1, 3)
        layBed.addWidget(self.btnBedCalibrationDoHoming, 2, 0)
        layBed.addWidget(self.btnRestoreBedCalibration, 2, 1)
        layBed.addWidget(self.btnSaveBedCalibration, 2, 2)

        wdgBed = QWidget()
        layBed.setSizeConstraint(QLayout.SetFixedSize)
        wdgBed.setLayout(layBed)

        # Magnet
        self.mcps = []
        layMagnetPoints = QGridLayout()
        for c in range(4):
            mcp = CalibrationPoint()
            mcp.Id = c + 1
            mcp.grpMainGroup.setTitle("Point {}".format(mcp.Id))
            mcp.btnTestPoint.clicked.connect(partial(self.moveToMagnetPoint_clicked, mcp))
            mcp.btnMoveToCenter.clicked.connect(partial(self.moveToCenterFromMagnet_clicked, mcp))
            layMagnetPoints.addWidget(mcp, 0, c)
            self.mcps.append(mcp)
        wdgMagnetPoints = QWidget()
        wdgMagnetPoints.setLayout(layMagnetPoints)

        self.brpOnlyUseSpecificMagnetPoints = QButtonGroup()
        self.radOnlyUseSpecificMagnetPoints = []
        for option in ["all", "left", "right", "1", "2", "3", "4"]:
            self.radOnlyUseSpecificMagnetPoints.append(QRadioButton(option))

        self.btnMagnetCalibrationDoHoming = QPushButton("Do homing")
        self.btnMagnetCalibrationDoHoming.clicked.connect(self.btnMagnetCalibrationDoHoming_clicked)
        self.btnPickupDie = QPushButton("Pick up")
        self.btnPickupDie.clicked.connect(self.btnPickupDie_clicked)
        self.btnRestoreMagnetCalibration = QPushButton("Restore settings")
        self.btnRestoreMagnetCalibration.clicked.connect(self.btnRestoreMagnetCalibration_clicked)
        self.btnSaveMagnetCalibration = QPushButton("Save settings")
        self.btnSaveMagnetCalibration.clicked.connect(self.btnSaveMagnetCalibration_clicked)

        layMagnet = QGridLayout()
        row = 0
        layMagnet.addWidget(QLabel("<h3>Calibrate the dropoff points.</h3>\n<h3>Make sure that the dropoff works when the point is approached from the center and freshly homed.</h3>"), row, 0, 1, 4)
        row += 1
        layMagnet.addWidget(QLabel("points to use for dropoff:"), row, 0)
        layMagnetPointsSelection = QGridLayout()
        for i in range(3):
            layMagnetPointsSelection.addWidget(self.radOnlyUseSpecificMagnetPoints[i], 1+i, 0)
        for i in range(4):
            layMagnetPointsSelection.addWidget(self.radOnlyUseSpecificMagnetPoints[i+3], 1+i, 1)
        wdgMagnetPointsSelection = QWidget()
        wdgMagnetPointsSelection.setLayout(layMagnetPointsSelection)
        layMagnet.addWidget(wdgMagnetPointsSelection, row, 1)
        row += 1
        layMagnet.addWidget(wdgMagnetPoints, row, 0, 1, 4)
        row += 1
        layMagnet.addWidget(self.btnMagnetCalibrationDoHoming, row, 0)
        layMagnet.addWidget(self.btnPickupDie, row, 1)
        layMagnet.addWidget(self.btnRestoreMagnetCalibration, row, 2)
        layMagnet.addWidget(self.btnSaveMagnetCalibration, row, 3)

        wdgMagnet = QWidget()
        layMagnet.setSizeConstraint(QLayout.SetFixedSize)
        wdgMagnet.setLayout(layMagnet)

        # Camera
        self.cmbISO = QComboBox()
        self.cmbISO.addItems(["100", "200", "400", "800"])
        self.cmbISO.currentTextChanged.connect(self.cmbISO_currentTextChanged)
        self.txtShutter = QSpinBox()
        self.txtShutter.setRange(1, 10000000)
        self.txtShutter.valueChanged.connect(self.txtShutter_valueChanged)
        self.txtContrast = QSpinBox()
        self.txtContrast.setRange(-100, 100)
        self.txtContrast.valueChanged.connect(self.txtContrast_valueChanged)
        self.btnTakePicture = QPushButton("Take picture")
        self.btnTakePicture.clicked.connect(self.btnTakePicture_clicked)
        self.btnCameraSave = QPushButton("Save settings")
        self.btnCameraSave.clicked.connect(self.btnCameraSave_clicked)
        self.lblCameraOriginal = QLabel()
        self.lblCameraProcessed = QLabel()
        layCamera = QGridLayout()
        row = 0
        layCamera.addWidget(QLabel("<h3>Configuration for the camera settings</h3>"), row, 0, 1, 2)
        row += 1
        layCamera.addWidget(QLabel("ISO:"), row, 0)
        layCamera.addWidget(self.cmbISO, row, 1)
        row += 1
        layCamera.addWidget(QLabel("Shutter [µs]:"), row, 0)
        layCamera.addWidget(self.txtShutter, row, 1)
        row += 1
        layCamera.addWidget(QLabel("Contrast [-100,100]:"), row, 0)
        layCamera.addWidget(self.txtContrast, row, 1)
        row += 1
        layCamera.addWidget(QLabel("original image:"), row, 0)
        layCamera.addWidget(self.lblCameraOriginal, row, 1)
        row += 1
        layCamera.addWidget(QLabel("processed image:"), row, 0)
        layCamera.addWidget(self.lblCameraProcessed, row, 1)
        row += 1
        layCamera.addWidget(self.btnTakePicture, row, 0)
        layCamera.addWidget(self.btnCameraSave, row, 1)

        wdgCamera = QWidget()
        layCamera.setSizeConstraint(QLayout.SetFixedSize)
        wdgCamera.setLayout(layCamera)

        # Image
        self.spnImageTLX = QSpinBox()
        self.spnImageTLX.setRange(1, cs.IMG_PX_X)
        self.spnImageTLY = QSpinBox()
        self.spnImageTLY.setRange(1, cs.IMG_PX_Y)
        self.spnImageBRX = QSpinBox()
        self.spnImageBRX.setRange(1, cs.IMG_PX_X)
        self.spnImageBRY = QSpinBox()
        self.spnImageBRY.setRange(1, cs.IMG_PX_Y)
        self.lblImageOriginal = QLabel()
        self.lblImageProcessed = QLabel()
        self.btnTakeImage = QPushButton("Take image")
        self.btnTakeImage.clicked.connect(self.btnTakeImage_clicked)
        self.btnImageSave = QPushButton("Save settings")
        self.btnImageSave.clicked.connect(self.btnImageSave_clicked)

        layImage = QGridLayout()
        layImage.addWidget(QLabel("<h3>Configuration for image cropping/scaling/...</h3>\n<h3>not implemented yet...</h3>"), 0, 0, 1, 3)
        layImage.addWidget(QLabel("top left X:"), 1, 0)
        layImage.addWidget(self.spnImageTLX, 1, 1)
        layImage.addWidget(QLabel("top left Y:"), 2, 0)
        layImage.addWidget(self.spnImageTLY, 2, 1)
        layImage.addWidget(QLabel("bottom right X:"), 3, 0)
        layImage.addWidget(self.spnImageBRX, 3, 1)
        layImage.addWidget(QLabel("bottom right Y:"), 4, 0)
        layImage.addWidget(self.spnImageBRY, 4, 1)
        layImage.addWidget(QLabel("original image:"), 5, 0)
        layImage.addWidget(self.lblImageOriginal, 5, 1)
        layImage.addWidget(QLabel("processed image:"), 6, 0)
        layImage.addWidget(self.lblImageProcessed, 6, 1)
        layImage.addWidget(self.btnTakeImage, 7, 0)
        layImage.addWidget(self.btnImageSave, 7, 1)

        wdgImage = QWidget()
        layImage.setSizeConstraint(QLayout.SetFixedSize)
        wdgImage.setLayout(layImage)

        # Move
        layMove = QGridLayout()
        layMove.addWidget(QLabel("<h3>Manual movement</h3>\n<h3>Be careful! Movement ist not restricted!</h3>"), 0, 0, 1, 8)
        movementButtonSettings = [
            ("↞", 3, 1, "X", 10),
            ("←", 3, 2, "X", 1),
            ("↟", 1, 3, "Y", -10),
            ("↑", 2, 3, "Y", -1),
            ("→", 3, 4, "X", -1),
            ("↠", 3, 5, "X", -10),
            ("↓", 4, 3, "Y", 1),
            ("↡", 5, 3, "Y", 10),
            ("↟", 1, 7, "Z", -10),
            ("↑", 2, 7, "Z", -1),
            ("↓", 4, 7, "Z", 1),
            ("↡", 5, 7, "Z", 10)
        ]
        for (symbol, row, col, direction, speed) in movementButtonSettings:
            btn = QPushButton(symbol)
            btn.setMaximumWidth(30)
            btn.setMaximumHeight(30)
            btn.clicked.connect(partial(self.movementButton_clicked, direction, speed))
            layMove.addWidget(btn, row+1, col)
        layMove.setColumnMinimumWidth(6, 30)
        layMove.setRowMinimumHeight(1, 30)

        layMove.addWidget(QLabel("use W,A,S,D and Q,E on the keyboard for movement."), 7, 0, 1, 8)
        layMove.addWidget(QLabel("Keyboard step size:"), 8, 0)
        self.spnKeyboardStepsize = QSpinBox()
        self.spnKeyboardStepsize.setRange(1, 10)
        layMove.addWidget(self.spnKeyboardStepsize, 8, 1)

        wdgMove = QWidget()
        layMove.setSizeConstraint(QLayout.SetFixedSize)
        wdgMove.setLayout(layMove)

        self.tabFunctions = QTabWidget()
        self.tabFunctions.addTab(wdgHoming, "Homing")
        self.tabFunctions.addTab(wdgBed, "Bed")
        self.tabFunctions.addTab(wdgMagnet, "Magnet")
        self.tabFunctions.addTab(wdgCamera, "Camera")
        self.tabFunctions.addTab(wdgImage, "Image")
        self.tabFunctions.addTab(wdgMove, "Manual Movement")
        self.movementTabIndex = 5

        self.txtStatus = QPlainTextEdit()
        self.txtStatus.setReadOnly(True)

        layMain = QGridLayout()
        layMain.addWidget(self.tabFunctions, 0, 0)
        layMain.addWidget(self.txtStatus, 1, 0)

        wdgMain = QWidget()
        wdgMain.setLayout(layMain)
        self.setCentralWidget(wdgMain)

        self.initSettings()

    ###############
    ### methods ###
    ###############

    def initSettings(self):
        if cs.ON_RASPI:
            cm.loadSettings()
            cm.loadMeshpoints()

        self.cmbISO.setCurrentText(str(cs.CAM_ISO))
        self.txtShutter.setValue(cs.CAM_SHUTTER_SPEED)
        self.txtContrast.setValue(cs.CAM_CONTRAST)

        self.spnImageTLX.setValue(cs.IMG_TL[0])
        self.spnImageTLY.setValue(cs.IMG_TL[1])
        self.spnImageBRX.setValue(cs.IMG_BR[0])
        self.spnImageBRY.setValue(cs.IMG_BR[1])

        for i in range(len(cs.MESH_BED)):
            self.bcps[i].txtCoordX.setValue(cs.MESH_BED[i, 0])
            self.bcps[i].txtCoordY.setValue(cs.MESH_BED[i, 1])
            self.bcps[i].txtCoordZ.setValue(cs.MESH_BED[i, 2])

        self.radOnlyUseSpecificMagnetPoints[0].setChecked(True)
        if not cs.USE_MAGNET_BETWEEN_P0P1:
            self.radOnlyUseSpecificMagnetPoints[2].setChecked(True)
        if not cs.USE_MAGNET_BETWEEN_P2P3:
            self.radOnlyUseSpecificMagnetPoints[1].setChecked(True)
        if cs.ALWAYS_USE_PX >= 0:
            self.radOnlyUseSpecificMagnetPoints[int(cs.ALWAYS_USE_PX) + 3].setChecked(True)

        for i in range(len(cs.MESH_MAGNET)):
            self.mcps[i].txtCoordX.setValue(cs.MESH_MAGNET[i, 0])
            self.mcps[i].txtCoordY.setValue(cs.MESH_MAGNET[i, 1])
            self.mcps[i].txtCoordZ.setValue(cs.MESH_MAGNET[i, 2])

    def addSpacerLineToStatusText(self):
        self.txtStatus.appendPlainText("----------------------")

    def addStatusText(self, text, spacerLineBefore=False, spacerLineAfter=False):
        if spacerLineBefore:
            self.addSpacerLineToStatusText()
        self.txtStatus.appendPlainText(text)
        if spacerLineAfter:
            self.addSpacerLineToStatusText()
        app.processEvents()

    ##############
    ### homing ###
    ##############

    def doHoming(self, moveToCenterAfterHoming=False):
        self.addStatusText("started homing...", spacerLineBefore=True)
        if cs.ON_RASPI:
            mm.doHoming()
            if moveToCenterAfterHoming:
                mm.setFeedratePercentage(cs.FR_SLOW_MOVE)
                mm.moveToPos(cs.CENTER_TOP)
                mm.waitForMovementFinished()
                mm.setFeedratePercentage(cs.FR_DEFAULT)
        else:
            time.sleep(3)
        self.addStatusText("homing finished", spacerLineAfter=True)

    def btnStartHoming_clicked(self):
        with WaitCursor():
            self.doHoming()

    ###########
    ### bed ###
    ###########

    def moveToBedPoint(self, id, x, y, z, isCloseToRamp):
        self.addStatusText("Test point {}, move to position ({},{},{})".format(id, x, y, z), spacerLineBefore=True)
        if cs.ON_RASPI:
            pos = Position(x, y, z)
            if isCloseToRamp:
                mm.moveToPos(cs.BEFORE_PICKUP_POSITION, True)
                mm.waitForMovementFinished()
                mm.moveCloseToRamp(pos, True)
                mm.waitForMovementFinished()
            else:
                mm.moveToPos(pos, True)
                mm.waitForMovementFinished()
        else:
            time.sleep(2)
        self.addStatusText("reached position ({},{},{})".format(x, y, z), spacerLineAfter=True)

    def moveToBedPoint_clicked(self, bcp):
        with WaitCursor():
            self.moveToBedPoint(bcp.Id, bcp.txtCoordX.value(), bcp.txtCoordY.value(), bcp.txtCoordZ.value(), bcp.isCloseToRamp)

    def moveToCenterFromBed_clicked(self, bcp):
        with WaitCursor():
            self.addStatusText("move to center position", spacerLineBefore=True)
            if cs.ON_RASPI:
                if bcp.isCloseToRamp:
                    mm.moveCloseToRamp(cs.BEFORE_PICKUP_POSITION, segmented=True, moveto=False)
                    mm.waitForMovementFinished()
                else:
                    mm.moveToPos(cs.BEFORE_PICKUP_POSITION, True)
                    mm.waitForMovementFinished()
            else:
                time.sleep(2)
            self.addStatusText("reached center position", spacerLineAfter=True)

    def btnBedCalibrationDoHoming_clicked(self):
        with WaitCursor():
            self.doHoming(moveToCenterAfterHoming=True)

    def btnRestoreBedCalibration_clicked(self):
        with WaitCursor():
            self.initSettings()
            self.addStatusText("settings restored", spacerLineBefore=True, spacerLineAfter=True)

    def btnSaveBedCalibration_clicked(self):
        with WaitCursor():
            for i in range(len(cs.MESH_BED)):
                cs.MESH_BED[i, 0] = self.bcps[i].txtCoordX.value()
                cs.MESH_BED[i, 1] = self.bcps[i].txtCoordY.value()
                cs.MESH_BED[i, 2] = self.bcps[i].txtCoordZ.value()
            cm.saveMeshpoints("B", cs.MESH_BED)
            self.addStatusText("settings saved", spacerLineBefore=True, spacerLineAfter=True)

    ##############
    ### magnet ###
    ##############

    def moveToMagnetPoint(self, id, x, y, z):
        self.addStatusText("Test point {}, move to position ({},{},{})".format(id, x, y, z), spacerLineBefore=True)
        if cs.ON_RASPI:
            pos = Position(x, y, z)
            mr.moveToDropoffPosition(pos)
            mm.waitForMovementFinished()
            time.sleep(2)
            mm.rollDie()
            time.sleep(0.1)
        else:
            time.sleep(2)
        self.addStatusText("reached position ({},{},{})".format(x, y, z), spacerLineAfter=True)

    def moveToMagnetPoint_clicked(self, mcp):
        with WaitCursor():
            self.moveToMagnetPoint(mcp.Id, mcp.txtCoordX.value(), mcp.txtCoordY.value(), mcp.txtCoordZ.value())

    def moveToCenterFromMagnet_clicked(self, mcp):
        with WaitCursor():
            self.addStatusText("move to center position", spacerLineBefore=True)
            if cs.ON_RASPI:
                mm.moveToPos(cs.BEFORE_PICKUP_POSITION, True)
                mm.waitForMovementFinished()
            else:
                time.sleep(2)
            self.addStatusText("reached center position", spacerLineAfter=True)

    def btnMagnetCalibrationDoHoming_clicked(self):
        with WaitCursor():
            self.doHoming(moveToCenterAfterHoming=True)

    def btnPickupDie_clicked(self):
        with WaitCursor():
            mr.pickupDie()

    def btnRestoreMagnetCalibration_clicked(self):
        with WaitCursor():
            self.initSettings()
            self.addStatusText("settings restored", spacerLineBefore=True, spacerLineAfter=True)

    def btnSaveMagnetCalibration_clicked(self):
        with WaitCursor():
            cs.ALWAYS_USE_PX = -1
            cs.USE_MAGNET_BETWEEN_P0P1 = True
            cs.USE_MAGNET_BETWEEN_P2P3 = True
            if self.radOnlyUseSpecificMagnetPoints[3].isChecked():
                cs.ALWAYS_USE_PX = 0
            elif self.radOnlyUseSpecificMagnetPoints[4].isChecked():
                cs.ALWAYS_USE_PX = 1
            elif self.radOnlyUseSpecificMagnetPoints[5].isChecked():
                cs.ALWAYS_USE_PX = 2
            elif self.radOnlyUseSpecificMagnetPoints[6].isChecked():
                cs.ALWAYS_USE_PX = 3
            elif self.radOnlyUseSpecificMagnetPoints[1].isChecked():
                cs.USE_MAGNET_BETWEEN_P2P3 = False
            elif self.radOnlyUseSpecificMagnetPoints[2].isChecked():
                cs.USE_MAGNET_BETWEEN_P0P1 = False

            for i in range(len(cs.MESH_MAGNET)):
                cs.MESH_MAGNET[i, 0] = self.mcps[i].txtCoordX.value()
                cs.MESH_MAGNET[i, 1] = self.mcps[i].txtCoordY.value()
                cs.MESH_MAGNET[i, 2] = self.mcps[i].txtCoordZ.value()

            cm.saveMeshpoints("M", cs.MESH_MAGNET)
            self.addStatusText("settings saved", spacerLineBefore=True, spacerLineAfter=True)

    ##############
    ### camera ###
    ##############

    def cmbISO_currentTextChanged(self, value):
        cs.CAM_ISO = int(value)

    def txtShutter_valueChanged(self, value):
        cs.CAM_SHUTTER_SPEED = value

    def txtContrast_valueChanged(self, value):
        cs.CAM_CONTRAST = value

    def btnTakePicture_clicked(self):
        with WaitCursor():
            self.addStatusText("take picture with settings: {}, {}, {}".format(cs.CAM_ISO, cs.CAM_SHUTTER_SPEED, cs.CAM_CONTRAST), spacerLineBefore=True)
            self.addStatusText("waiting...")
            if cs.ON_RASPI:
                dr = DieRecognizer()
                lm.setAllLeds()
                mm.setTopLed(cs.LED_TOP_BRIGHTNESS)
                cam = Camera()
                image = cam.takePicture()
                cam.close()
                dieRollResult, processedImages = dr.getDieRollResult(image, returnOriginalImg=True, markDie=True)
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                dr.writeImage(image, "camera.jpg", directory=cs.WEB_DIRECTORY)
                dr.writeImage(processedImages[1], "recognized.jpg", directory=cs.WEB_DIRECTORY)
                self.addStatusText("see full images at http://" + cm.clientIdentity["IP"] + "/camera.html")
                lm.clear()
                mm.setTopLed(cs.LED_TOP_BRIGHTNESS_OFF)
                pixCameraOriginal = QPixmap(os.path.join(cs.WEB_DIRECTORY, "camera.jpg"))
                pixCameraProcessed = QPixmap(os.path.join(cs.WEB_DIRECTORY, "recognized.jpg"))
                self.lblCameraOriginal.setPixmap(pixCameraOriginal.scaled(500, 500, Qt.KeepAspectRatio))
                self.lblCameraProcessed.setPixmap(pixCameraProcessed.scaled(400, 400, Qt.KeepAspectRatio))
                app.processEvents()
            else:
                time.sleep(3)
            self.addStatusText("image recognition finished. save settings?", spacerLineAfter=True)

    def btnCameraSave_clicked(self):
        cm.saveCameraSettings()
        self.addStatusText("settings saved", spacerLineBefore=True, spacerLineAfter=True)

    ##############
    ### image ###
    ##############

    def btnTakeImage_clicked(self):
        with WaitCursor():
            self.addStatusText("taking image...", spacerLineBefore=True)
            if cs.ON_RASPI:
                if not cs.IMG_USE_WARPING:
                    cs.IMG_TL = [self.spnImageTLX.value(), self.spnImageTLY.value()]
                    cs.IMG_BR = [self.spnImageBRX.value(), self.spnImageBRY.value()]
                    dr = DieRecognizer()
                    cam = Camera()
                    lm.setAllLeds()
                    mm.setTopLed(cs.LED_TOP_BRIGHTNESS)
                    image = cam.takePicture()
                    cam.close()
                    lm.clear()
                    mm.setTopLed(cs.LED_TOP_BRIGHTNESS_OFF)
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    transformedImage = dr.cropImage(image, cs.IMG_TL, cs.IMG_BR)
                    markedImage = dr.markCropLines(image, cs.IMG_TL, cs.IMG_BR, isGray=True)
                    dr.writeImage(markedImage, "marked.jpg", directory=cs.WEB_DIRECTORY)
                    dr.writeImage(transformedImage, "transformed.jpg", directory=cs.WEB_DIRECTORY)
                    self.addStatusText("see full image at http://" + cm.clientIdentity["IP"] + "/image.html")
                    pixImageOriginal = QPixmap(os.path.join(cs.WEB_DIRECTORY, "marked.jpg"))
                    pixImageProcessed = QPixmap(os.path.join(cs.WEB_DIRECTORY, "transformed.jpg"))
                    self.lblImageOriginal.setPixmap(pixImageOriginal.scaled(200, 200, Qt.KeepAspectRatio))
                    self.lblImageProcessed.setPixmap(pixImageProcessed.scaled(350, 250, Qt.KeepAspectRatio))
                else:
                    self.addStatusText("Warping is specified for this camera. Changing settings is not possible.", spacerLineBefore=True, spacerLineAfter=True)
            else:
                time.sleep(3)
            self.addStatusText("image cropping finished. save settings?", spacerLineAfter=True)

    def btnImageSave_clicked(self):
        if not cs.IMG_USE_WARPING:
            cm.saveImageSettingsCropping(cs.IMG_TL, cs.IMG_BR)
            self.addStatusText("settings saved", spacerLineBefore=True, spacerLineAfter=True)
        else:
            self.addStatusText("Warping is specified for this camera. Changing settings is not possible.", spacerLineBefore=True, spacerLineAfter=True)

    ############
    ### move ###
    ############

    def move(self, direction, steps):
        posFrom = mm.currentPosition
        posTo = None
        deltaPos = None
        if direction == "X":
            deltaPos = Position(steps, 0, 0)
        elif direction == "Y":
            deltaPos = Position(0, steps, 0)
        elif direction == "Z":
            deltaPos = Position(0, 0, steps)
        posTo = posFrom + deltaPos
        if posTo is not None:
            mm.moveToPos(posTo, True)
            mm.waitForMovementFinished()

    def movementButton_clicked(self, direction, steps):
        with WaitCursor():
            self.addStatusText("move {} steps in {}-direction".format(steps, direction))
            if cs.ON_RASPI:
                self.move(direction, steps)
            else:
                time.sleep(abs(steps) * 0.2)

    ############
    ### main ###
    ############

    def keyPressEvent(self, event):
        if self.tabFunctions.currentIndex() == self.movementTabIndex:
            stepsize = self.spnKeyboardStepsize.value()
            if event.key() == Qt.Key_A:
                self.move("X", stepsize)
            elif event.key() == Qt.Key_D:
                self.move("X", -stepsize)
            elif event.key() == Qt.Key_S:
                self.move("Y", stepsize)
            elif event.key() == Qt.Key_W:
                self.move("Y", -stepsize)
            elif event.key() == Qt.Key_Q:
                self.move("Z", stepsize)
            elif event.key() == Qt.Key_E:
                self.move("Z", -stepsize)

###################
### application ###
###################

window = MainWindow()
window.show()

window.setWindowTitle("Calibrate \"{}\"".format(cm.clientIdentity["Material"]))

if cs.ON_RASPI:
    msgHoming = QMessageBox()
    msgHoming.setIcon(QMessageBox.Information)
    msgHoming.setText("Do you want to perform homing before you proceed?")
    msgHoming.setInformativeText("Homing is required in order to localize the magnet.")
    msgHoming.setWindowTitle("TOR Calibration")
    yesBtn = msgHoming.addButton("Yes", QMessageBox.YesRole)
    moBtn = msgHoming.addButton("No", QMessageBox.NoRole)
    msgHoming.exec_()
    if msgHoming.clickedButton() == yesBtn:
        with WaitCursor():
            window.doHoming(moveToCenterAfterHoming=True)

app.exec()
