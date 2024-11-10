import logging
log = logging.getLogger(__name__)

import numpy as np

import tor.TORSettings as ts
import tor.server.ServerSettings as ss

if ss.ON_RASPI:
    import tflite_runtime.interpreter as tflite
else:
    import tensorflow.lite as tflite

class PositionVerification:
    def __init__(self, clientId=None):
        self.clientId = clientId
        modelFilePath = ts.VERIFY_MAGNET_TFMODELFILE if clientId is None else ts.VERIFY_MAGNET_TFMODELFILE_ID.format(self.clientId)
        self.isInitialized = False
        try:
            self.loadModelFile(modelFilePath)
            self.isInitialized = True
            log.info("loaded PositionVerification for id: {}".format(self.clientId))
        except Exception as e:
            self.isInitialized = False
            log.warning("could not initialize PositionVerification for id: {}".format(self.clientId))
            log.warning("modelFilePath: {}".format(modelFilePath))
            log.warning("{}".format(repr(e)))

    def loadModelFile(self, modelFilePath):
        self.interpreter = tflite.Interpreter(model_path=modelFilePath)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def verifyPosition(self, image):
        input_shape = self.input_details[0]['shape']
        #print(input_shape)
        im_normalized = np.array(image).astype(np.float32) / 255.0
        input_data = [ im_normalized.tolist() ]
        input_data = np.array(input_data).astype(np.float32)
        input_data = np.reshape(input_data, input_shape)
        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
        self.interpreter.invoke()
        output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
        guessWrong = output_data[0][0]
        guessOk = output_data[0][1]
        isOk = guessWrong < guessOk
        log.info("verification weights (wrong/ok): {}/{}, isOk={}".format(guessWrong, guessOk, isOk))
        return isOk
