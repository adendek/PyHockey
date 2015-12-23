from __future__ import division

import threading

import cv2
import numpy as np

from data.Player import Player


class VideoCapture:
    def __init__(self, player, player2=None):
        self.player = player
        self.player2 = None
        self.data = dict()
        self.frame = None
        self.VIDEO_SIZE = (400, 300)

        self.data[player.player_id] = {
            'cam_pos': self.player.mallet.pos.state,
            'pos': self.player.mallet.pos.state,
            'last_pos': self.player.mallet.pos.state,
            'vel': [(0, 0)]
            # 'vel': (0, 0)
        }
        self.set_color_mask(self.player)
        if player2:
            self.player2 = player2
            self.data[player2.player_id] = {
                'cam_pos': self.player2.mallet.pos.state,
                'pos': self.player2.mallet.pos.state,
                'last_pos': self.player2.mallet.pos.state,
                # 'vel': (0, 0)
                'vel': [(0, 0)]
            }
            self.set_color_mask(self.player2)

        self._stop_capture = threading.Event()
        self._stop_image_processing = threading.Event()

    def set_color_mask(self, player):
        """
        Assigns lower/upper and circle color for player
        :param player:
        :return:
        """
        if player.playerColor == Player.PLAYER_BLUE:
            self.data[player.playerColor]['lower'] = np.array([90, 80, 80], dtype=np.uint8)
            self.data[player.playerColor]['upper'] = np.array([110, 255, 255], dtype=np.uint8)
            self.data[player.playerColor]['circle_color'] = (255, 0, 0)
        else:
            self.data[player.playerColor]['lower'] = np.array([21, 58, 28], dtype=np.uint8)
            self.data[player.playerColor]['upper'] = np.array([105, 224, 154], dtype=np.uint8)
            self.data[player.playerColor]['circle_color'] = (0, 0, 255)

    def convert_position(self, player_id, tup):
        """
        Convert coordinates to pygame proper one
        :param player_id:
        :param tup: (x, y)
        :return:
        """
        GAME_SIZE = (800, 600)
        # left side
        if player_id == Player.PLAYER_RED:
            x = tup[0] * GAME_SIZE[0] / self.VIDEO_SIZE[0]
            y = tup[1] * GAME_SIZE[1] / self.VIDEO_SIZE[1]
        # right side
        else:
            x = tup[0] * GAME_SIZE[0] / self.VIDEO_SIZE[0] + GAME_SIZE[0] / 2
            y = tup[1] * GAME_SIZE[1] / self.VIDEO_SIZE[1]

        return int(x), int(y)

    def get_image(self):
        """
        Loop which retrieve frames from Camera
        :return:
        """
        cap = cv2.VideoCapture(0)
        while not self._stop_capture.is_set():
            _, frame = cap.read()
            self.frame = cv2.resize(cv2.flip(frame, 1), self.VIDEO_SIZE)
            for player_id in self.data.keys():
                cv2.circle(self.frame, self.data[player_id]['cam_pos'], 10, self.data[player_id]['circle_color'], 2)
            cv2.imshow('frame', self.frame)
            k = cv2.waitKey(33) & 0xFF
        cv2.destroyAllWindows()

    def get_players_data(self, player_id):
        """
        Loop which save position of colored objects.
        :param player_id:
        :return:
        """
        while not self._stop_image_processing.is_set():

            if self.frame is None:
                continue
            if player_id == Player.PLAYER_RED:
                frame = self.frame[:, :self.VIDEO_SIZE[0] // 2]
            else:
                frame = self.frame[:, self.VIDEO_SIZE[0] // 2:]
            frame = cv2.blur(frame, (3, 3))
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            self.data[player_id]['last_pos'] = self.data[player_id]['pos']
            if len(self.data[player_id]['vel']) > 4:
                self.data[player_id]['vel'].pop(0)
            mask = cv2.inRange(hsv, self.data[player_id]['lower'], self.data[player_id]['upper'])
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
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
                game_x, game_y = self.convert_position(player_id, (x, y))
                if player_id == Player.PLAYER_BLUE:
                    x += self.VIDEO_SIZE[0] // 2
                self.data[player_id]['cam_pos'] = (x, y)
                self.data[player_id]['pos'] = game_x, game_y
                self.data[player_id]['vel'].append(((game_x - self.data[player_id]['last_pos'][0]),
                                                    (game_y - self.data[player_id]['last_pos'][1])))
                # self.data[player_id]['vel'] = (game_x - self.data[player_id]['last_pos'][0]), (game_y - self.data[player_id]['last_pos'][1])
            else:
                self.data[player_id]['vel'].append((0, 0))
                # self.data[player_id]['vel'] = (0, 0)

    def start_capture(self):
        """
        starting new thread - get_image
        :return:
        """
        threading.Thread(target=self.get_image).start()

    def start_image_processing(self, player):
        """
        starting new thread - get_players_data
        :return:
        """
        threading.Thread(target=self.get_players_data, args=(player.player_id,)).start()

    def stop_capture(self):
        """
        stopping threads - get_image
        :return:
        """
        self._stop_capture.set()

    def stop_image_processing(self):
        """
        stopping threads - get_players_data
        :return:
        """
        self._stop_image_processing.set()

    @property
    def pos(self):
        """
        Gives position of object(s)
        :return: (x, y) or (x1, y1), (x2, y2)
        """
        if self.player2:
            return self.data[self.player.player_id]['pos'], self.data[self.player2.player_id]['pos']
        return self.data[self.player.player_id]['pos']

    @property
    def vel(self):
        """
        Gives velocity of object(s)
        :return: (vx, vy) or (vx1, vy1), (vx2, vy2)
        """
        p1_vel = (
        sum([x[0] for x in self.data[self.player.player_id]['vel']]) / len(self.data[self.player.player_id]['vel']),
        sum([x[1] for x in self.data[self.player.player_id]['vel']]) / len(self.data[self.player.player_id]['vel']))
        # print self.data[self.player.player_id]['vel'], self.data[self.player2.player_id]['vel']
        if self.player2:
            p2_vel = (sum([x[0] for x in self.data[self.player2.player_id]['vel']]) / len(
                    self.data[self.player2.player_id]['vel']),
                      sum([x[1] for x in self.data[self.player2.player_id]['vel']]) / len(
                              self.data[self.player2.player_id]['vel']))
            # print p1_vel, p2_vel
            # return self.data[self.player.player_id]['vel'], self.data[self.player2.player_id]['vel']
            return p1_vel, p2_vel
        return p1_vel
        # return self.data[self.player.player_id]['vel']
