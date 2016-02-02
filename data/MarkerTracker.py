import cv2
import numpy as np
from data.Player import Player
import threading
from AbstractMarkerTracker import AbstractMarkerTracker


class MarkerTracker(AbstractMarkerTracker):
    def __init__(self, player, player2):
        self.frame = None
        self.VIDEO_SIZE = (400, 300)
        self.GAME_SIZE = (800, 600)
        self.data = dict()
        self.player = player
        self.player2 = player2
        self.data[player.player_id] = {
            'cam_pos': self.player.mallet.pos.state,
            'pos': self.player.mallet.pos.state,
            'last_pos': self.player.mallet.pos.state,
            'vel': [(0, 0)]
        }
        self.data[player2.player_id] = {
            'cam_pos': self.player2.mallet.pos.state,
            'pos': self.player2.mallet.pos.state,
            'last_pos': self.player2.mallet.pos.state,
            'vel': [(0, 0)]
        }
        self._stop_image_processing = threading.Event()
        self.p1 = (200, 200)
        self.p2 = (600, 400)
    
    def get_players_positions(self, frame):
        return self.p1, self.p2

    def get_players_data(self, player_id):
        """
        Loop which save position of colored objects.
        :param player_id:
        :return:
        """
        while not self._stop_image_processing.is_set():
            if self.frame is None:
                continue
            hsv = self.filter_frame(player_id)
            self.refresh_player_position(player_id)
            mask = self.get_mask(hsv, player_id)
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
                game_x, game_y = self.convert_position(player_id, (x, y))
                if player_id == Player.PLAYER_BLUE:
                    x += self.VIDEO_SIZE[0] // 2
                    (game_x, game_y) = self.p2
                if player_id == Player.PLAYER_RED:
                    (game_x, game_y) = self.p1
                self.data[player_id]['cam_pos'] = (x, y)
                self.data[player_id]['pos'] = game_x, game_y
                self.data[player_id]['vel'].append(((game_x - self.data[player_id]['last_pos'][0]),
                                                    (game_y - self.data[player_id]['last_pos'][1])))
                # self.data[player_id]['vel'] = (game_x - self.data[player_id]['last_pos'][0]), (game_y - self.data[player_id]['last_pos'][1])
            else:
                self.data[player_id]['vel'].append((0, 0))
                # self.data[player_id]['vel'] = (0, 0)

    def filter_frame(self, player_id):
        if player_id == Player.PLAYER_RED:
            frame = self.frame[:, :self.VIDEO_SIZE[0] // 2]
        else:
            frame = self.frame[:, self.VIDEO_SIZE[0] // 2:]
        frame = cv2.blur(frame, (3, 3))
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        return hsv

    def refresh_player_position(self, player_id):
        self.data[player_id]['last_pos'] = self.data[player_id]['pos']
        if len(self.data[player_id]['vel']) > 4:
            self.data[player_id]['vel'].pop(0)

    def get_mask(self, hsv, player_id):
        mask = cv2.inRange(hsv, self.data[player_id]['lower'], self.data[player_id]['upper'])
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.medianBlur(mask, 5)
        return mask

    def convert_position(self, player_id, tup):
        """
        Convert coordinates to pygame proper one
        :param player_id:
        :param tup: (x, y)
        :return:
        """
        # left side
        if player_id == Player.PLAYER_RED:
            x = tup[0] * self.GAME_SIZE[0] / self.VIDEO_SIZE[0]
            y = tup[1] * self.GAME_SIZE[1] / self.VIDEO_SIZE[1]
        # right side
        else:
            x = tup[0] * self.GAME_SIZE[0] / self.VIDEO_SIZE[0] + self.GAME_SIZE[0] / 2
            y = tup[1] * self.GAME_SIZE[1] / self.VIDEO_SIZE[1]

        return int(x), int(y)

    def stop_image_processing(self):
        """
        stopping threads - get_players_data
        :return:
        """
        self._stop_image_processing.set()
