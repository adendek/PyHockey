from __future__ import division

import os

import pygame as pg
from pygame.locals import *

from Logger import Logger
from data.Disc import Disc
from data.Pitch import Pitch
from data.Player import Player
from data.Player import TooManyPointsException
from data.ScoreBoard import GameTime
from data.ScoreBoard import OutOfGameTimeException
from data.ScoreBoard import ScoreBoard
from data.VideoCapture import VideoCapture
from data.controls.KeyboardGameControls import KeyboardGameControls


class Game(object):
    DISC_RADIUS = 16.5
    INIT_DISC1_X = 402
    INIT_DISC1_Y = 310
    INIT_DISC2_X = 402
    INIT_DISC2_Y = 400

    def __init__(self, size):
        Logger.info("GAME INIT: Initializing PyGame...")
        pg.init()

        Logger.info("GAME INIT: Initializing Display (%s)", str(size))
        pg.display.set_caption("PyHockey")
        self.screensize = (int(size[0]), int(size[1]))

        os.environ["SDL_VIDEO_CENTERED"] = "True"
        self.screen = pg.display.set_mode(self.screensize)

        self.screen_rect = self.screen.get_rect()
        Logger.info("GAME INIT: Initializing clock and fps rate...")

        self.clock = pg.time.Clock()
        self.fps = 60
        self.keys = pg.key.get_pressed()
        self.done = False
        self.playing = True

        Logger.info("GAME INIT: Initializing Model...")
        # model part
        self.pitch = Pitch()
        self.players = [Player(Player.PLAYER_RED, self.pitch), Player(Player.PLAYER_BLUE, self.pitch)]
        self.mallets = [self.players[0].mallet, self.players[1].mallet]
        pitch_borders = [(self.pitch.i_min, self.pitch.i_max), (self.pitch.j_min, self.pitch.j_max)]
        self.discs = [Disc(Game.INIT_DISC1_X, Game.INIT_DISC1_Y, 1, Game.DISC_RADIUS, pitch_borders),
                      Disc(Game.INIT_DISC2_X, Game.INIT_DISC2_Y, 1, Game.DISC_RADIUS, pitch_borders)]
        self.objects = self.discs + self.mallets
        self.scoreboard = ScoreBoard(self.players[0], self.players[1])

        Logger.info("GAME INIT: Initializing Drawables...")
        # everything that will be drawn
        self.drawables = [self.pitch]
        self.drawables.extend(self.mallets)
        self.drawables.extend(self.discs)
        self.drawables.append(self.scoreboard)

        Logger.info("GAME INIT: Initializing Video Capture...")
        self.video = VideoCapture(self.players[0], self.players[1])
        # self.video = VideoCapture2(size)
        # self.video.start_capture()
        # self.video.start_image_processing(self.players[0])
        # self.video.start_image_processing(self.players[1])
        # self.video.get_players_positions()
        # self.video.restart_capture()

        Logger.info("GAME INIT: Initializing Game Controls...")
        self.controls = KeyboardGameControls(self.players[0],self.players[1])

        Logger.info("GAME INIT: Starting game loop...")
        self.loop()
        Logger.info("GAME INIT: Game loop ended, stopping video capture...")
        # self.video.stop_image_processing()
        # self.video.stop_capture()
        Logger.info("GAME INIT: Exiting")

    def loop(self):
        background = (255, 255, 255)
        Logger.info("GAME LOOP: In Game Loop")
        while not self.done:
            self.clock.tick(self.fps)
            for event in pg.event.get():
                if event.type == QUIT:
                    Logger.info("Quit event registered")
                    self.done = True

            if not self.playing:
                continue

            try:
                GameTime.getCurrentGameTime()
            except OutOfGameTimeException:
                # self.done = True
                self.playing = False

            pos = self.controls.get_players_positions()

            # calculate velocities, it should not be here
            self.players[0].mallet.vel.state, self.players[1].mallet.vel.state = (pos[0][0] - self.players[
                0].mallet.pos.x, pos[0][1] - self.players[0].mallet.pos.y), (pos[1][0] - self.players[1].mallet.pos.x,
                                                                             pos[1][1] - self.players[1].mallet.pos.y)

            self.players[0].mallet.move_to(pos[0][0], pos[0][1])
            self.players[1].mallet.move_to(pos[1][0], pos[1][1])

            # reset screen
            self.screen.fill(background)

            # check if the goal was scored
            for pl in self.players:
                for d in self.discs:
                    if pl.goal_to_score.in_goal(d.pos.x, d.pos.y, Game.DISC_RADIUS):
                        try:
                            pl.addPoint()
                            d.move_to(d.init_x, d.init_y)
                            d.vel.x = d.vel.y = 0.
                        except TooManyPointsException:
                            self.playing = False

            for o in self.objects:
                o.friction()
                axis = self.pitch.is_border_collision(o)
                if axis:
                    o.border_collision(axis)

            # Detect and react on collisions between discs
            for i in range(len(self.objects) - 1):
                for j in range(i, len(self.objects)):
                    self.objects[i].circle_collision(self.objects[j])

            for disc in self.discs:
                disc.move(disc.vel.x, disc.vel.y)

            # draw everything
            for drawable in self.drawables:
                drawable.draw(self.screen)

            # update display
            pg.display.flip()
