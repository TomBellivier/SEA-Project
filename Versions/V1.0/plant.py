import pygame as pg
import numpy as np
import matplotlib.pyplot as plt
import random as rd
import math as m


# on crée une classe qui gère une plante
class Plant(pg.sprite.Sprite):

    def __init__(self, simulation):
        super().__init__()

        self.simulation = simulation

        # on défini le nom de l'espèce végétale
        self.name = "jaizon"

        # on associe à la plante une image
        self.size = 10

        self.init_image = pg.image.load(f"{self.name}.png")
        self.image = pg.transform.scale(self.init_image, (self.size, self.size))

        # on défini aléatoirement les coordonnées de la plante
        self.position = (rd.randint(10, self.simulation.screen_size[0] - 10), rd.randint(10, self.simulation.screen_size[1] - 10))
        self.rect = self.image.get_rect()
        self.rect.x = self.position[0]
        self.rect.y = self.position[1]
        self.rect = self.image.get_rect(center=self.rect.center)

        self.energy_capacity = 20
