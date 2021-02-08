# -*- coding: utf-8 -*-
"""
Created on Thu Jul  2 03:40:59 2020

@author: hp
"""
import time
import cv2
import numpy as np

from db.video_store import insert_image, get_image

SHOW_FACE = not True
DISPLAY_IMAGE = True


def determine_state(cap):
    model_file = "models/res10_300x300_ssd_iter_140000.caffemodel"
    config_file = "models/deploy.prototxt.txt"
    net = cv2.dnn.readNetFromCaffe(config_file, model_file)
    previous_state = None
    image_id = 0
    no_errors = True

    while no_errors:
        no_errors, img = cap.read()
        if no_errors:
            img = cv2.resize(img, None, fx=0.5, fy=0.5)
            height, width = img.shape[:2]
            img2 = img.copy()

            blob = cv2.dnn.blobFromImage(cv2.resize(img, (300, 300)),
                                         1.0, (300, 300), (104.0, 117.0, 123.0))
            net.setInput(blob)
            faces3 = net.forward()

            number_of_faces = 0
            for i in range(faces3.shape[2]):
                confidence = faces3[0, 0, i, 2]
                if confidence > 0.5:
                    number_of_faces += 1
                    if SHOW_FACE:
                        box = faces3[0, 0, i, 3:7] * np.array([width, height, width, height])
                        (x, y, x1, y1) = box.astype("int")
                        cv2.rectangle(img2, (x, y), (x1, y1), (0, 0, 255), 2)

            states = ["Absent", "Present", "Group"]
            state = states[number_of_faces if number_of_faces <= 2 else 2]

            if previous_state is None:
                previous_state = state
            elif state != previous_state:
                image_id += 1
                previous_state = state
                image_array = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                insert_image(image_array, state, image_array.shape)
                if DISPLAY_IMAGE:
                    get_image(image_id).show()

            print(f"[{state}] {time.ctime()}")

            if SHOW_FACE:
                cv2.imshow("dnn", img2)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            time.sleep(0.5)

    cap.release()
    cv2.destroyAllWindows()
