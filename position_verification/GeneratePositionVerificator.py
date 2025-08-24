# INFO: Generates models for position verification
#       To take images of correct and wrong positions set the Job "TAKE_IMAGE" on the clients.
#       Use "MAGNET_POS_TRUE" or "MAGNET_POS_FALSE" to create the respective training data.
#       SQL queries for jobs:
#           insert into jobqueue (ClientId, JobCode, JobParameters) select id, "TAKE_IMAGE", "MAGNET_POS_TRUE" from client;
#           insert into jobqueue (ClientId, JobCode, JobParameters) select id, "TAKE_IMAGE", "MAGNET_POS_FALSE" from client;
#       1) run the copy_images.py script to create copy scripts
#       2) run copy_images_magnet to copy the images to a local machine (e.g. Yoga12)
#       3) run this script to train and generate the models
#       4) copy the *.tflite files to the machine hosting the TORServer

import cv2
import glob
import matplotlib.pyplot as plt
import numpy as np
import os
import tensorflow as tf
from sklearn.model_selection import train_test_split

from tor.base.utils import Utils
import tor.TORSettings as ts

# INFO: set local directories
#data_dir = "/home/gartner/TOR2022/20220812_CoffeaArabica_Magnet/cropped/"
#model_dir = "./model/"
#data_dir = os.path.join("D:" + os.sep, "TOR2022", "Pictures", Utils.getFilenameTimestampDay())
#data_dir = os.path.join("D:" + os.sep, "TOR2022", "Pictures", "20220905")
#model_dir = os.path.join("D:" + os.sep, "Sources", "TOR", "position_verification", "model")
#data_dir = os.path.join("/home/tor", "TORPictures", "magnet_20220913")
data_dir = os.path.join("/home/tor", "TORPictures", "magnet_initial")
model_dir = os.path.join("/home/tor", "Sources", "TOR", "position_verification", "model")

saved_model_dirname = os.path.join(model_dir, "PositionVerificationTFModel")
saved_model_dirname_id = os.path.join(model_dir, "PositionVerificationTFModel_{}")
light_model_filename = os.path.join(model_dir, "position_verification.tflite")
light_model_filename_id = os.path.join(model_dir, "position_verification_{}.tflite")

class_names = ["wrong", "ok"]
num_classes = len(class_names)

img_height = 30
img_width = 30

def importImages(directory, pattern=None):
    image_list = []
    if pattern is None:
        pattern = "*.png"
    for filename in glob.glob(os.path.join(directory, pattern)):
        im = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
        #im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        image_list.append(im)
    return image_list

def createVerificationModel(id=None, show=False):
    pattern = None
    if id is not None:
        pattern = "*_id={}_*.png".format(id)
    noImages = importImages(os.path.join(data_dir, "wrong"), pattern)
    yesImages = importImages(os.path.join(data_dir, "ok"), pattern)

    dataset_im = []
    dataset_lbl = []
    for im in noImages:
        im_normalized = im.astype(np.float64) / 255.0
        dataset_im.append(im_normalized.tolist())
        dataset_lbl.append(0)
    for im in yesImages:
        im_normalized = im.astype(np.float64) / 255.0
        dataset_im.append(im_normalized.tolist())
        dataset_lbl.append(1)

    if len(dataset_im) < 10:
        print("not enough images for id: {}".format(id))
        return

    train_images, test_images, train_labels, test_labels = train_test_split(dataset_im, dataset_lbl, test_size=0.3, random_state=123)

    if show:
        plt.figure(figsize=(10,10))
        for i in range(25):
            plt.subplot(5,5,i+1)
            plt.xticks([])
            plt.yticks([])
            plt.grid(False)
            plt.imshow(train_images[i], cmap=plt.cm.binary)
            plt.xlabel(class_names[train_labels[i]])
        plt.show()

    model1 = tf.keras.Sequential([
        tf.keras.layers.Flatten(input_shape=(img_height, img_width)),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(num_classes)
    ])

    model2 = tf.keras.Sequential([
        tf.keras.layers.Flatten(input_shape=(img_height, img_width)),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(num_classes)
    ])

    filterSize = 5
    model3 = tf.keras.Sequential([
        tf.keras.layers.Conv2D(filterSize, 3, activation='relu', input_shape=(img_height, img_width, 1)),
        tf.keras.layers.MaxPooling2D(),
        tf.keras.layers.Conv2D(filterSize, 3, activation='relu'),
        tf.keras.layers.MaxPooling2D(),
        tf.keras.layers.Conv2D(filterSize, 3, activation='relu'),
        tf.keras.layers.MaxPooling2D(),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(num_classes)
    ])

    model4 = tf.keras.Sequential([
        tf.keras.layers.Conv2D(16, 3, padding='same', activation='relu', input_shape=(img_height, img_width, 1)),
        tf.keras.layers.MaxPooling2D(),
        tf.keras.layers.Conv2D(32, 3, padding='same', activation='relu'),
        tf.keras.layers.MaxPooling2D(),
        tf.keras.layers.Conv2D(64, 3, padding='same', activation='relu'),
        tf.keras.layers.MaxPooling2D(),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(num_classes)
    ])

    model = model4
    if show:
        model.summary()

    model.compile(
        optimizer='adam',
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=['accuracy']
    )

    model.fit(train_images, train_labels, epochs=10)

    test_loss, test_acc = model.evaluate(test_images, test_labels, verbose=2)

    print('\nTest accuracy:', test_acc)

    probability_model = tf.keras.Sequential([model, tf.keras.layers.Softmax()])

    modelFilePath = saved_model_dirname if id is None else saved_model_dirname_id.format(id)
    modelTFLightFilePath = light_model_filename if id is None else light_model_filename_id.format(id)

    probability_model.save(modelFilePath)

    converter = tf.lite.TFLiteConverter.from_saved_model(modelFilePath)
    tflite_model = converter.convert()

    with open(modelTFLightFilePath, "wb") as f:
        f.write(tflite_model)

    predictions = probability_model.predict(test_images)
    print(predictions)

    if show:
        num_rows = 6
        num_cols = 3
        num_images = num_rows * num_cols
        plt.figure(figsize=(2 * 2 * num_cols, 2 * num_rows))
        for i in range(num_images):
            plt.subplot(num_rows, 2 * num_cols, 2 * i + 1)
            plot_image(i, predictions[i], test_labels, test_images)
            plt.subplot(num_rows, 2 * num_cols, 2 * i + 2)
            plot_value_array(i, predictions[i], test_labels)
        plt.tight_layout()
        plt.show()

def plot_image(i, predictions_array, true_label, img):
    true_label, img = true_label[i], img[i]
    plt.grid(False)
    plt.xticks([])
    plt.yticks([])

    plt.imshow(img, cmap=plt.cm.binary)

    predicted_label = np.argmax(predictions_array)
    if predicted_label == true_label:
        color = 'blue'
    else:
        color = 'red'

    plt.xlabel("{} {:2.0f}% ({})".format(class_names[predicted_label],
                                100*np.max(predictions_array),
                                class_names[true_label]),
                                color=color)

def plot_value_array(i, predictions_array, true_label):
    true_label = true_label[i]
    plt.grid(False)
    plt.xticks(range(10))
    plt.yticks([])
    thisplot = plt.bar(range(2), predictions_array, color="#777777")
    plt.ylim([0, 1])
    predicted_label = np.argmax(predictions_array)

    thisplot[predicted_label].set_color('red')
    thisplot[true_label].set_color('blue')


#################
# create models #
#################

createVerificationModel(show=True)

#ids = [14, 19]
#ids = [1, 30, 12]
ids = ts.CLIENT_IDS
for id in ids:
    createVerificationModel(id, show=True)