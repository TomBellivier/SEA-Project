import pygame as pg
import numpy as np
import matplotlib.pyplot as plt
import random as rd
import math as m


class Metabolism():

    def __init__(self, otus):

        self.otus = otus

        self.max_health = 100
        self.health = self.max_health

        self.max_energy = 100
        self.energy = self.max_energy * 0.5

    def damage(self, amount):

        amount = abs(amount)

        self.health -= amount

        if self.health < 0:
            self.otus.dies()

    def spend_energy(self, amount):

        amount = abs(amount)

        if self.energy - amount > 0:

            self.energy -= amount

        else:

            amount -= self.energy
            self.energy = 0

            self.damage(amount)

    def gain_energy(self, amount):

        amount = abs(amount)

        if self.energy + amount > self.max_energy:

            self.otus.reproduce()

            self.energy -= self.max_energy * 0.5 + amount

        else:
            self.energy += amount


