import pygame as pg
import random as rd
from math import sqrt


class Particle(pg.sprite.Sprite):

    def __init__(self, group, zoom, x, y):
        super().__init__()

        self.group = group

        self.size = 2.5 * zoom**0.8

        self.init_image = pg.image.load("pheromone.png")
        self.image = pg.transform.scale(self.init_image, (self.size, self.size))

        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y

        self.age = 0

        xspeed = rd.random()
        yspeed = rd.random()

        self.speed = ((xspeed - 0.5)*zoom, (yspeed - 0.5)*zoom)

        self.duration = 20

    def move(self):

        self.rect.x += self.speed[0] * rd.random()
        self.rect.y += self.speed[1] * rd.random()

    def update(self):

        self.age += 1

        self.move()

        if self.age > self.duration:

            self.group.remove(self)