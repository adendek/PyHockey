import pygame as pg

from data.controls.AbstractGameControls import AbstractGameControls


class KeyboardGameControls(AbstractGameControls):
    def __init__(self):
        self.p1 = (200, 200)
        self.p2 = (600, 400)

    def get_players_positions(self):
        d = 10

        # red player controls
        if pg.key.get_pressed()[pg.K_w]:
            (x, y) = self.p1
            self.p1 = (x, y - d)
        if pg.key.get_pressed()[pg.K_s]:
            (x, y) = self.p1
            self.p1 = (x, y + d)
        if pg.key.get_pressed()[pg.K_a]:
            (x, y) = self.p1
            self.p1 = (x - d, y)
        if pg.key.get_pressed()[pg.K_d]:
            (x, y) = self.p1
            self.p1 = (x + d, y)

        # blue player controls
        if pg.key.get_pressed()[pg.K_UP]:
            (x, y) = self.p2
            self.p2 = (x, y - d)
        if pg.key.get_pressed()[pg.K_DOWN]:
            (x, y) = self.p2
            self.p2 = (x, y + d)
        if pg.key.get_pressed()[pg.K_LEFT]:
            (x, y) = self.p2
            self.p2 = (x - d, y)
        if pg.key.get_pressed()[pg.K_RIGHT]:
            (x, y) = self.p2
            self.p2 = (x + d, y)

        return self.p1, self.p2
