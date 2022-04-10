import argparse
import logging
import time
import numpy as np
import os
import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QTabWidget, QGridLayout, QWidget, QPlainTextEdit, QComboBox, QSpinBox
from PyQt5.QtGui import QPixmap

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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Calibration")

        # Homing
        self.lblHoming = QLabel("Start the homing routine:")
        self.btnStartHoming = QPushButton("Start")
        self.btnStartHoming.clicked.connect(self.btnStartHoming_clicked)
        layHoming = QGridLayout()
        layHoming.addWidget(self.lblHoming, 0, 0)
        layHoming.addWidget(self.btnStartHoming, 0, 1)
        wdgHoming = QWidget()
        wdgHoming.setLayout(layHoming)

        # Bed
        self.btnCalibrateBed = QPushButton("Calibrate bed")
        self.btnCalibrateBed.clicked.connect(self.btnCalibrateBed_clicked)

        # Magnet
        label2 = QLabel("Here you can calibrate the drop off locations.")

        # Camera
        label3 = QLabel("Calibrate the camera settings")
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
        self.pixImageOriginal = QPixmap()
        self.lblImageOriginal = QLabel()
        self.lblImageOriginal.setPixmap(self.pixImageOriginal)
        self.pixImageRecognition = QPixmap()
        self.lblImageRecognition = QLabel()
        self.lblImageRecognition.setPixmap(self.pixImageRecognition)
        layCamera = QGridLayout()
        row = 0
        layCamera.addWidget(label3, row, 0)
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
        layCamera.addWidget(self.lblImageOriginal, row, 1)
        row += 1
        layCamera.addWidget(QLabel("analyzed image:"), row, 0)
        layCamera.addWidget(self.lblImageRecognition, row, 1)
        row += 1
        layCamera.addWidget(self.btnTakePicture, row, 0)
        layCamera.addWidget(self.btnCameraSave, row, 1)
        wdgCamera = QWidget()
        wdgCamera.setLayout(layCamera)

        tabFunctions = QTabWidget()
        tabFunctions.addTab(wdgHoming, "Homing")
        tabFunctions.addTab(self.btnCalibrateBed, "Bed")
        tabFunctions.addTab(label2, "Magnet")
        tabFunctions.addTab(wdgCamera, "Camera")

        self.txtStatus = QPlainTextEdit()
        self.txtStatus.setReadOnly(True)

        layMain = QGridLayout()
        layMain.addWidget(tabFunctions, 0, 0)
        layMain.addWidget(self.txtStatus, 1, 0)

        wdgMain = QWidget()
        wdgMain.setLayout(layMain)
        self.setCentralWidget(wdgMain)

        self.initSettings()

    def initSettings(self):
        cm.loadSettings()
        self.cmbISO.setCurrentText(str(cs.CAM_ISO))
        self.txtShutter.setValue(cs.CAM_SHUTTER_SPEED)
        self.txtContrast.setValue(cs.CAM_CONTRAST)

    def addSpacerLineToStatusText(self):
        self.txtStatus.appendPlainText("----------------------")

    def addStatusText(self, text, spacerLineBefore=False, spacerLineAfter=False):
        if spacerLineBefore:
            self.addSpacerLineToStatusText()
        self.txtStatus.appendPlainText(text)
        if spacerLineAfter:
            self.addSpacerLineToStatusText()
        app.processEvents()

    def btnStartHoming_clicked(self):
        self.btnStartHoming.setDisabled(True)
        self.addStatusText("started homing...", spacerLineBefore=True)
        if cs.ON_RASPI:
            mm.doHoming()
        else:
            time.sleep(3)
        self.addStatusText("homing finished", spacerLineAfter=True)
        self.btnStartHoming.setDisabled(False)

    def cmbISO_currentTextChanged(self, value):
        cs.CAM_ISO = int(value)

    def txtShutter_valueChanged(self, value):
        cs.CAM_SHUTTER_SPEED = value

    def txtContrast_valueChanged(self, value):
        cs.CAM_CONTRAST = value

    def btnTakePicture_clicked(self):
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
            self.addStatusText("http://" + cm.clientIdentity["IP"] + "/camera.html")
            lm.clear()
            mm.setTopLed(cs.LED_TOP_BRIGHTNESS_OFF)
        else:
            time.sleep(3)
        #self.pixImageOriginal.load(os.path.join(cs.WEB_DIRECTORY, "camera.jpg"))
        #self.pixImageRecognition.load(os.path.join(cs.WEB_DIRECTORY, "recognized.jpg"))
        #self.lblImageRecognition.pixmap(self.pixImageRecognition)
        #self.lblImageRecognition.show()
        self.addStatusText("image recognition fished. save settings if okay.", spacerLineAfter=True)

    def btnCameraSave_clicked(self):
        cm.saveCameraSettings()
        self.addStatusText("settings saved", spacerLineBefore=True, spacerLineAfter=True)

    def btnCalibrateBed_clicked(self):
        print("Clicked!")

app = QApplication(sys.argv)

window = MainWindow()
window.show()

window.setWindowTitle("Calibrate \"{}\"".format(cm.clientIdentity["Material"]))

app.exec()
