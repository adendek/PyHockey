import pygame

from data.DrawableInterface import Drawable
from data.Kinematics import *


class Disc(PhysicsObject, Drawable):

    PICTURE_PATH = "resources/graphics/disc.png"

    def __init__(self, init_x, init_y, mass, radius, borders):
        PhysicsObject.__init__(self, init_x, init_y, mass, radius, borders)
        image = pygame.transform.scale(pygame.image.load(self.PICTURE_PATH), (2*radius, 2*radius))
        Drawable.__init__(self, image, None, Vector(init_x, init_y))
    # TODO: Use some drawing to display the picture on a pitch
    # Use position, radius, picture_path


    @property
    def pos(self):
        return self._pos

    @property
    def vel(self):
        return self._vel

    @property
    def radius(self):
        return self._radius

    @property
    def picture_path(self):
        return self._picture_path

    def moveTo(self, x, y):
        self._pos.state = (x, y)

    def move(self, x_move, y_move):
        self._pos.change_state((x_move, y_move))

    def accelerate(self, v_x_diff, v_y_diff):
        self._vel.change_state((v_x_diff, v_y_diff))

    @vel.setter
    def vel(self, vel):
        self._vel.state = vel

    def printStatus(self):
        print("Position: " + self._pos.x + ", " + self._pos.y)
        print("Velocity: " + self._vel.x + ", " + self._vel.y)
        print("Velocity value: " + self._vel.length)