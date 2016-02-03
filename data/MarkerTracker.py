import cv2
import numpy as np
from data.Player import Player
from AbstractMarkerTracker import AbstractMarkerTracker


class MarkerTracker(AbstractMarkerTracker):
    def __init__(self, frame):
        self.player_id = 0
        self.frame = frame
        self.VIDEO_SIZE = (400, 300)
        self.GAME_SIZE = (800, 600)
        self.data = dict()
        self.p1 = (0, 0)
        self.p2 = (0, 0)

    def set_player_id(self, player_id_to_set):
        self.player_id = player_id_to_set
        pass

    def set_color_mask(self, player_id):
        """
        Assigns lower/upper color for player
        :param player_id:
        :return:
        """
        if player_id.playerColor == Player.PLAYER_BLUE:
            self.data[player_id]['lower'] = np.array([90, 80, 80], dtype=np.uint8)
            self.data[player_id]['upper'] = np.array([110, 255, 255], dtype=np.uint8)
        else:
            self.data[player_id]['lower'] = np.array([21, 58, 28], dtype=np.uint8)
            self.data[player_id]['upper'] = np.array([105, 224, 154], dtype=np.uint8)

    def get_markers_positions(self, frame):
        hsv = self.filter_frame(self.player_id, frame)
        mask = self.get_mask(hsv, self.player_id)
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        maximumArea = 0
        bestContour = None
        for contour in contours:
            currentArea = cv2.contourArea(contour)
            if currentArea > maximumArea:
                bestContour = contour
                maximumArea = currentArea

        if bestContour is not None:
            M = cv2.moments(bestContour)
            x, y = int(M['m10'] / M['m00']), int(M['m01'] / M['m00'])
            if self.player_id == Player.PLAYER_BLUE:
                x += self.VIDEO_SIZE[0] // 2
                (x, y) = self.p2
            if self.player_id == Player.PLAYER_RED:
                (x, y) = self.p1
        return self.p1, self.p2

    def filter_frame(self, player_id, frame):
        if player_id == Player.PLAYER_RED:
            halfFrame = frame[:, :self.VIDEO_SIZE[0] // 2]
        else:
            halfFrame = frame[:, self.VIDEO_SIZE[0] // 2:]
        halfFrame = cv2.blur(halfFrame, (3, 3))
        hsv = cv2.cvtColor(halfFrame, cv2.COLOR_BGR2HSV)
        return hsv

    def get_mask(self, hsv, player_id):
        mask = cv2.inRange(hsv, self.data[player_id]['lower'], self.data[player_id]['upper'])
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.medianBlur(mask, 5)
        return mask
























