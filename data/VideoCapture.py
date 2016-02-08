from __future__ import division

import cv2

from AbstractVideoCapture import AbstractVideoCapture


class VideoCapture(AbstractVideoCapture):
    def __init__(self):
        self.VIDEO_SIZE = (400, 300)
        self.cap = cv2.VideoCapture(0)  # 0 for camera

    def get_frame(self):
        ret, frame = self.cap.read()
        frame = cv2.resize(cv2.flip(frame, 1), self.VIDEO_SIZE)  # vertical flip+ resize
        return frame
