import cv2
import numpy as np
from AbstractMarkerTracker import AbstractMarkerTracker


class MarkerTracker(AbstractMarkerTracker):
    def __init__(self, frame):
        self.hsv = None
        self.player_id = ['player_red', 'player_blue']
        self.VIDEO_SIZE = (400, 300)
        self.GAME_SIZE = (800, 600)
        self.data = dict()
        self.p1 = (0, 0)
        self.p2 = (0, 0)
        for player in self.player_id:
            if player == 'player_blue':
                halfframe = frame[:, self.VIDEO_SIZE[0] // 2:]
                self.data['player_blue']['lower'] = np.array([90, 80, 80], dtype=np.uint8)
                self.data['player_blue']['upper'] = np.array([110, 255, 255], dtype=np.uint8)
                halfframe = cv2.blur(halfframe, (3, 3))
                self.hsv[player] = cv2.cvtColor(halfframe, cv2.COLOR_BGR2HSV)
            else:
                halfframe = frame[:, :self.VIDEO_SIZE[0] // 2]
                self.data['player_red']['lower'] = np.array([21, 58, 28], dtype=np.uint8)
                self.data['player_red']['upper'] = np.array([105, 224, 154], dtype=np.uint8)
                halfframe = cv2.blur(halfframe, (3, 3))
                self.hsv[player] = cv2.cvtColor(halfframe, cv2.COLOR_BGR2HSV)

    def get_markers_positions(self, frame):
        for player in self.player_id:
            mask = cv2.inRange(self.hsv[player], self.data[player]['lower'], self.data[player]['upper'])
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
            mask = cv2.medianBlur(mask, 5)
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
                if player == 'player_blue':
                    x += self.VIDEO_SIZE[0] // 2
                    (x, y) = self.p2
                if player == 'player_red':
                    (x, y) = self.p1
        return self.p1, self.p2






















