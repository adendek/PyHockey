from __future__ import division
import cv2
import numpy as np
from AbstractMarkerTracker import AbstractMarkerTracker


class MarkerTracker(AbstractMarkerTracker):
    def __init__(self):
        self.hsv = None
        self.player_red = []
        self.player_blue = []
        self.VIDEO_SIZE = (400, 300)
        self.GAME_SIZE = (800, 600)
        self.data = {'player_red': self.player_red, 'player_blue': self.player_blue}
        self.p1 = (0, 0)
        self.p2 = (0, 0)
        self.player_blue.append(np.array([90, 80, 80], dtype=np.uint8)) #low hsv limit
        self.player_blue.append(np.array([110, 255, 255], dtype=np.uint8)) #up hsv limit
        self.player_red.append(np.array([21, 58, 28], dtype=np.uint8)) #low hsv limit
        self.player_red.append(np.array([105, 224, 154], dtype=np.uint8)) #up hsv limit

    def get_markers_positions(self, frame):
        for player, limit in self.data.iteritems():
            cv2.imshow('frame', frame)
            k = cv2.waitKey(33) & 0xFF
            if player == 'player_blue':
                halfframe = frame[:, self.VIDEO_SIZE[0] // 2:]
            else:
                halfframe = frame[:, :self.VIDEO_SIZE[0] // 2]
            halfframe = cv2.blur(halfframe, (3, 3))
            self.hsv = cv2.cvtColor(halfframe, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(self.hsv, limit[0], limit[1])
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
                    self.p2 = (int(x* self.GAME_SIZE[0] / self.VIDEO_SIZE[0] + self.GAME_SIZE[0] / 2), int(y* self.GAME_SIZE[1] / self.VIDEO_SIZE[1]))
                    x += self.VIDEO_SIZE[0] // 2
                    cv2.circle(frame, (int(x), int(y)), 10, (255, 0, 0), 2)
                else:
                    self.p1 = (int(x* self.GAME_SIZE[0] / self.VIDEO_SIZE[0]), int(y * self.GAME_SIZE[1] / self.VIDEO_SIZE[1]))
                    cv2.circle(frame, (int(x), int(y)), 10, (0, 0, 255), 2)
        return self.p1, self.p2
