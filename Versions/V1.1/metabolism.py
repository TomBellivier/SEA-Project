#v1.1
import math

import genes
from lifeLimits import life_limits


class Metabolism:

    def __init__(self, otus):

        self.otus = otus

        self.max_health = round(genes.decrypt(otus.genome.sequence[32:40], life_limits["health"]))
        self.health = self.max_health

        self.max_energy = round(genes.decrypt(otus.genome.sequence[40:48], life_limits["energy"]))
        self.energy = self.max_energy * 0.5

    def damage(self, amount):

        amount = abs(amount)

        self.health -= amount

        if self.health < 0:
            self.otus.dying = True
            self.energy = self.max_energy * 0.5
            print(self.otus.rect.x, self.otus.rect.y)

        elif self.health > self.max_health:
            self.health = self.max_health

    def spend_energy(self, amount):

        amount = abs(amount)

        if self.energy - amount > 0:

            self.energy -= amount

            if self.energy < self.max_energy / 2:
                self.otus.heating = False

            if self.otus.dying:
                zone = [math.floor(self.otus.rect.centerx/100), math.floor(self.otus.rect.centery /100)]
                self.otus.simulation.ground[zone[0], zone[1]] += amount

        else:

            if not self.otus.dying:
                amount -= self.energy
                self.energy = 0

                self.damage(amount)
            else:
                self.otus.dies()

    def gain_energy(self, amount):

        amount = abs(amount)

        if self.energy + amount > self.max_energy:

            self.otus.heating = True

            self.energy = self.max_energy

            # dégats négatifs : soigne l'otus
            self.damage(- (self.energy + amount - self.max_energy))

        else:
            self.energy += amount


