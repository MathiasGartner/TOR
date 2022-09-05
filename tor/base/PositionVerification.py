import logging
log = logging.getLogger(__name__)

import numpy as np
import tflite_runtime.interpreter as tflite

import tor.client.ClientSettings as cs

class PositionVerification:
    def __init__(self):
        self.interpreter = tflite.Interpreter(model_path=cs.VERIFY_MAGNET_TFMODELFILE)
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
        isOk = output_data[0][0] < output_data[0][1]
        log.info("verification weights [[wrong ok]]: {}, isOk={}".format(output_data, isOk))
        return isOk