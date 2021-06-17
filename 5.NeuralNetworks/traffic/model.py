import cv2
import numpy as np
import os
import sys
import tensorflow as tf

from traffic import load_data

from sklearn.model_selection import train_test_split

EPOCHS = 10
IMG_WIDTH = 30
IMG_HEIGHT = 30
NUM_CATEGORIES = 43
TEST_SIZE = 0.4


def main():

    # Get image arrays and labels for all image files
    images, labels = load_data(sys.argv[1])
    labels = tf.keras.utils.to_categorical(labels)

    x = np.array(images)
    y = np.array(labels)

    # Get a compiled neural network
    model = tf.keras.models.load_model('./models/model-10.h5')

    # Evaluate neural network performance
    model.evaluate(x, y, verbose=2)

if __name__ == "__main__":
    main()