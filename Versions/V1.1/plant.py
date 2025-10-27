#v1.1

import pygame as pg
import numpy as np
import matplotlib.pyplot as plt
import random as rd
import math as m

SIZE = 4

imgs = {"jaizon": (pg.image.load(f"../assets/jaizon.png"), pg.image.load(f"../assets/jaizon_decaying.png"))}

# on crée une classe qui gère une plante
class Plant(pg.sprite.Sprite):

    def __init__(self, simulation, coordinates=[0, 0]):
        super().__init__()

        self.simulation = simulation

        # on défini le nom de l'espèce végétale
        self.name = "jaizon"

        # on associe à la plante une image
        self.init_size = SIZE
        self.size = self.init_size * simulation.zoom

        # on définit l'image initiale de la plante
        if coordinates == [0, 0]:
            self.position = self.simulation.choice_coordinates()
        else:
            self.position = coordinates
        self.init_image = imgs[self.name][0]
        self.image = pg.transform.scale(self.init_image, (self.size, self.size))
        #self.decaying_image = imgs[self.name][1]
        #self.update_image()

        self.rect = self.image.get_rect()

        self.rect.x = self.position[0] - self.rect.centerx
        self.rect.y = self.position[1] - self.rect.centery

        self.zone = [m.floor(self.rect.centerx / self.simulation.screen_size[0] * 100), m.floor(self.rect.centery / self.simulation.screen_size[1] * 100)]

        # on défini aléatoirement les coordonnées de la plante
        self.rect.x = self.position[0]
        self.rect.y = self.position[1]
        self.rect = self.image.get_rect(center=self.rect.center)

        self.dying = False
        self.decaying_rate = 250    # time to decaye completely

        self.energy_density = 1         # energy / pixel
        self.energy_stock = 2
        #self.energy_to_growth = 0.5     # proportion
        #self.energy_drain = 0.0001           # energy / time
        #self.energy_to_reproduce = 10
        #self.spread_effect = 100

    def update_image(self):
        points = self.simulation.limit_points

        if points[0] > self.position[0]:

            self.position[0] = points[2]

        elif points[2] < self.position[0]:

            self.position[0] = points[0]

        if points[1] > self.position[1]:

            self.position[1] = points[3]

        elif points[3] < self.position[1]:

            self.position[1] = points[1]

        self.update_size()

        # on défini la position de l'image de l'otus
        self.rect = self.image.get_rect()

        self.rect.x = self.position[0] - self.rect.centerx
        self.rect.y = self.position[1] - self.rect.centery

    def update_size(self):
        self.image = pg.transform.scale(self.init_image, (self.size, self.size))

    def move(self, xvalue, yvalue):

        self.position[0] += xvalue
        self.position[1] += yvalue

        self.rect.centerx = self.position[0]
        self.rect.centery = self.position[1]

# Correspond à la misa à joru des plantes (comment elles se reproduisent etc...)

#    def update(self):
#        if not self.dying:
#            self.grow()
#            self.heal()
#
#            if self.energy_stock < 0:
#                self.dying = True
#                print("dead")
#                self.init_image = self.decaying_image
#                self.update_size()

#        else:
#            self.die()
#            if self.init_size < SIZE:
#                self.simulation.gplant.remove(self)#

#    def die(self):
#        energy_lost = self.energy_density * self.init_size / self.decaying_rate
#        self.simulation.ground[self.zone[0], self.zone[1]] += energy_lost
#        self.init_size -= energy_lost / self.energy_density / 5
#        self.size = self.init_size * self.simulation.zoom
#        self.update_size()
#
#    def heal(self):
#        self.energy_stock -= self.energy_drain / 10
#        self.simulation.ground[self.zone[0], self.zone[1]] += self.energy_drain / 10
#
#    def grow(self):
#        energy = self.simulation.ground[self.zone[0], self.zone[1]]
#
#        energy_drained = energy * self.energy_drain
#        if self.simulation.ground[self.zone[0], self.zone[1]] - energy_drained >= 0:
#            self.init_size += energy_drained * self.energy_to_growth / self.energy_density / 5
#            self.size = self.init_size * self.simulation.zoom
#            self.update_size()
#            self.energy_stock += energy_drained * (1 - self.energy_to_growth)
#            self.simulation.ground[self.zone[0], self.zone[1]] -= energy_drained

#        if self.energy_stock > self.energy_to_reproduce:
#            if self.simulation.plant_limit > len(self.simulation.gplant):
#                self.reproduce()

#    def reproduce(self):
#        coo1 = 2 * (rd.random() - 0.5)
#        coo2 = m.sqrt(1-coo1**2) * (2 * (rd.random() < 0.5) - 1)
#        coordinates = [coo1 * self.spread_effect + self.rect.x, coo2 * self.spread_effect + self.rect.y]
#        self.energy_stock -= SIZE / self.energy_density - 2
#        new_plant = Plant(self.simulation, coordinates)
#        self.simulation.gplant.add(new_plant)


