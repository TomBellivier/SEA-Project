#v1.1

import pygame as pg
import numpy as np
import random as rd
import math as m
from PIL import Image
import brain
import metabolism
import genes
import particleLauncher

from lifeLimits import life_limits

# ce modèle sert à connaitre l'emplacement des zones transparente, claires ou c=foncées de l'image de l'otus
model = np.array([
            [-1, -1, -1, -1, -1, -1,  0, -1, -1,  0, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1,  0, -1, -1, -1, -1,  0, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1,  0,  0,  0,  0, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1,  0,  0,  1,  1,  0,  0, -1, -1, -1, -1, -1],
            [-1, -1, -1,  2,  2,  1,  1,  1,  1,  1,  1,  2,  2, -1, -1, -1],
            [-1, -1, -1,  2,  1,  1,  2,  2,  2,  2,  1,  1,  2, -1, -1, -1],
            [-1, -1,  0,  1,  1,  2,  2,  2,  2,  2,  2,  1,  1,  0, -1, -1],
            [-1,  0,  1,  1,  1,  2,  3,  3,  3,  3,  2,  1,  1,  1,  0, -1],
            [-1,  0,  1,  1,  1,  2,  3,  3,  3,  3,  2,  1,  1,  1,  0, -1],
            [-1,  0,  0,  0,  1,  2,  2,  3,  3,  2,  2,  1,  0,  0,  0, -1],
            [-1,  0, -1, -1,  0,  1,  2,  2,  2,  2,  1,  0, -1, -1,  0, -1],
            [-1, -1, -1, -1,  2,  1,  1,  1,  1,  1,  1,  2, -1, -1, -1, -1],
            [-1, -1, -1, -1,  2,  1,  1,  1,  1,  1,  1,  2, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1,  2,  1,  1,  1,  1,  2, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1,  0,  1,  1,  0, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1,  0,  0, -1, -1, -1, -1, -1, -1, -1]
        ])

limits = life_limits


# on crée une classe pour gérer un otus
class Otus(pg.sprite.Sprite):

    def __init__(self, simulation, parents=None, num=0):

        super().__init__()

        self.simulation = simulation

        self.num_descendants = 0

        if parents is None:
            self.progeny = str(num)
        else:
            self.progeny = parents[0].progeny + "." + str(num) + "+" + parents[1].progeny + "." + str(num)

        # l'otus n'est en premier lieu pas en rut
        self.heating = False

        # on crée le génome de l'otus
        self.genome = genes.Genome(self, parents=parents)

        # on crée le métabolisme de l'otus
        self.metabolism = metabolism.Metabolism(self)

        # on définit une taille
        self.init_size = 6
        self.size = self.init_size * simulation.zoom

        self.dying = False

        # on défini une vitesse
        self.max_speed = genes.decrypt(self.genome.sequence[:8], limits["speed"])
        self.speed = self.max_speed * simulation.zoom

        # on défini une vitesse angulaire et un angle de départ aléatoire
        self.angle = rd.randint(0, 360)
        self.max_angle_speed = genes.decrypt(self.genome.sequence[8:16], limits["angle speed"])
        self.angle_speed = self.max_angle_speed * simulation.zoom

        # on défini un champ de vision
        self.init_sight = genes.decrypt(self.genome.sequence[16:24], limits["sight"])
        self.sight = self.init_sight * simulation.zoom

        # on définit une portée de phéromone
        self.init_pherange = genes.decrypt(self.genome.sequence[72:80], limits["pheromones range"])
        self.pherange = self.init_pherange * simulation.zoom

        # on défini une masse
        self.weight = genes.decrypt(self.genome.sequence[24:32], limits["weight"])

        # on défini une cible vers laquelle l'otus devrait se diriger
        self.target = (rd.randint(10, self.simulation.screen_size[0] - 10), rd.randint(10, self.simulation.screen_size[1] - 10), None)

        # on défini le nombre d'entrée et de sortie que va recevoir le cerveau de l'otus
        self.inputs, self.outputs = 2, 2

        # on crée une liste qui va recevoir les paramètre que l'on va donner au cerveau de l'otus
        self.brain_vars = []

        # on crée le cerveau de l'otus, sil a des parents, il herite de leur cerveau avec quelques mutations
        if parents is None:
            self.brain = brain.Brain(self, self.inputs, self.outputs)
        else:
            self.brain = brain.Brain(self, self.inputs, self.outputs, parents[0].brain)

            for i in range(2):
                self.brain.mutate()

        # on défini l'image de l'otus selon le code génétique ( 3 gènes ; un pour chaque composante de couleur rgb)
        light = (round(genes.decrypt(self.genome.sequence[48:50], limits["color"])),
                 round(genes.decrypt(self.genome.sequence[56:58], limits["color"])),
                 round(genes.decrypt(self.genome.sequence[64:66], limits["color"])))
        medium = (round(genes.decrypt(self.genome.sequence[50:52], limits["color"])),
                 round(genes.decrypt(self.genome.sequence[58:60], limits["color"])),
                 round(genes.decrypt(self.genome.sequence[66:68], limits["color"])))
        dark = (round(genes.decrypt(self.genome.sequence[52:54], limits["color"])),
                 round(genes.decrypt(self.genome.sequence[60:62], limits["color"])),
                 round(genes.decrypt(self.genome.sequence[68:70], limits["color"])))
        supdark = (round(genes.decrypt(self.genome.sequence[54:56], limits["color"])),
                 round(genes.decrypt(self.genome.sequence[62:64], limits["color"])),
                 round(genes.decrypt(self.genome.sequence[70:72], limits["color"])))

        self.colors = (supdark, dark, medium, light)
        self.init_image = self.bride_colors(supdark, dark, medium, light)

        self.position = [0, 0]

        # on actualise la taille de l'image
        self.update_image()

        # si l'otus est un nouveau né, il apparait près de ses parents
        if parents is None:
            coordinates = self.simulation.choice_coordinates()
            self.rect.x = coordinates[0]
            self.rect.y = coordinates[1]
        else:
            self.rect.x = parents[0].rect.x
            self.rect.y = parents[0].rect.y

        self.rect = self.image.get_rect(center=self.rect.center)

        # on défini la position réelle de l'otus
        self.position = [self.rect.x + self.size / 2, self.rect.y + self.size / 2]

    # fonction pour actualiser l'image
    def update_image(self):

        self.reset_image = pg.transform.scale(self.init_image, (self.size, self.size))

        self.image = pg.transform.rotozoom(self.reset_image, self.angle, 1)

        # on défini la position de l'image de l'otus
        self.rect = self.image.get_rect()

        self.update_position()

    # on met à jour les paramètres généraux de l'otus : position, vitesse...
    def update(self, screen, timer, xvalue, yvalue):

        if not self.dying:

            # on calcul ici la distance séparant l'otus de sa cible
            d = m.sqrt(((self.target[0] - self.rect.center[0]) ** 2 + (self.target[1] - self.rect.center[1]) ** 2))
            d += 0.001 * (d == 0)

            # on calcule ensuite l'angle entre la direction de l'otus et sa cible
            angle = (self.angle + m.degrees(m.asin((self.target[0] - self.rect.center[0]) / d)) % 360) % 360

            # on défini les variables d'input du cerveau
            self.brain_vars = [(d, self.sight), (angle, 360)]

            # on récupère les résultats que nous a renvoyé le cerveau
            results = self.brain.forward_propagation(self.brain_vars)

            # on met à jour les variables concernées par ces résultats
            self.update_vars(results)

            # on fait bouger l'otus : avancer, tourner...
            self.turn()
            self.forward()

            self.metabolism.spend_energy(0.01)

            # on fait bouger l'otus par rapport à l'otus sélectionné
            if self.simulation.follow:
                self.move(xvalue, yvalue)

            # on met à jour une nouvelle cible
            self.update_target(timer)

            # si l'otus est en rut, on libère des particules
            if timer % 5 == 0 and self.heating:
                self.simulation.particles.add(particleLauncher.Particle(self.simulation.particles, self.simulation.zoom, self.rect.centerx, self.rect.centery))

        else:

            self.metabolism.spend_energy(0.01)

    # on affiche le réseau de neurone de l'otus
    def show_neat_graphic(self):

        self.brain.show_graphic(self.brain_vars, self.inputs, self.outputs)

    # on fait tourner l'otus
    def turn(self):

        self.angle += self.angle_speed

        self.angle = self.angle % 360

        self.metabolism.spend_energy(self.angle_speed * 0.005)

        # on doit faire tourner l'image de l'otus, et réajuster le centre de l'image
        self.image = pg.transform.rotozoom(self.reset_image, self.angle, 1)
        self.rect = self.image.get_rect(center=self.rect.center)

    def move(self, xvalue, yvalue):
        self.position[0] += xvalue
        self.position[1] += yvalue

        self.target = (
            self.target[0] + xvalue,
            self.target[1] + yvalue,
            self.target[2]
        )

    # on fait avancer l'otus
    def forward(self):

        # on fait avancer l'otus
        self.position[0] -= m.sin(m.radians(self.angle)) * self.speed * self.simulation.zoom
        self.position[1] -= m.cos(m.radians(self.angle)) * self.speed * self.simulation.zoom

        center = self.simulation.zoom_center

        points = self.simulation.limit_points

        out = False

        # on replace l'otus à l'opposé de la carte lorsqu'il dépasse les limites de l'écran
        if points[0] > self.position[0]:

            self.position[0] = points[2]
            out = True

        elif points[2] < self.position[0]:

            self.position[0] = points[0]
            out = True

        if points[1] > self.position[1]:

            self.position[1] = points[3]
            out = True

        elif points[3] < self.position[1]:

            self.position[1] = points[1]
            out = True

        self.metabolism.spend_energy(self.speed * 0.01)

        # on met à jour la position de l'image de l'otus
        self.update_position()

        if out and self == self.simulation.main_otus and self.simulation.follow:
            self.simulation.switch_to_follow_mode()

    # on met à jour la position de l'image de l'otus
    def update_position(self):

        self.rect.x += self.position[0] - self.rect.centerx
        self.rect.y += self.position[1] - self.rect.centery

    # on met à jour les vaiables concernées par les résultats retournés par le cerveau
    def update_vars(self, results):
        self.speed = results[0] * self.max_speed
        self.angle_speed = (results[1]-0.5) * self.max_angle_speed

    def search_plant(self, d_target):
        closest = None

        for plant in self.simulation.gplant:

            d = m.sqrt(((plant.rect.center[0] - self.rect.center[0]) ** 2 + (plant.rect.center[1] - self.rect.center[1]) ** 2))

            if d < d_target:
                d_target = d
                closest = plant

        # si la plante la plus proche est dans le champs de vision de l'otus, elle devient sa nouvelle cible
        if d_target < self.sight*1.2 and closest is not None:
            self.target = (closest.rect.center[0], closest.rect.center[1], closest)

        else:
            coordinates = (rd.randint(10, self.simulation.screen_size[0] - 10), rd.randint(10, self.simulation.screen_size[1] - 10))
            self.target = (coordinates[0], coordinates[1], None)

    # on met à jour une cible
    def update_target(self, timer):

        if self.target[2] in self.simulation.gotus:
            self.target = (self.target[2].rect.centerx, self.target[2].rect.centery, self.target[2])

        # on calcule la distance avec la cible actuelle
        d_target = m.sqrt(((self.target[0] - self.rect.centerx) ** 2 + (self.target[1] - self.rect.centery) ** 2))

        # l'otus mange la cible si c'est une plante et si il est assez proche
        if d_target < self.size and self.target[2] in self.simulation.gplant:
            self.eat(self.target[2])
        elif d_target < self.size and self.target[2] in self.simulation.gotus and self.heating:
            self.reproduce(self.target[2])
            self.target[2].reproduce(self)

        # on met à jour la cible des otus régulièrement
        if timer % 20 == 0:
            # si l'otus n'est pas en rut, il va vouloir se nourrir et va chercher une plante
            if not self.heating:

                if self.target[2] not in self.simulation.gplant or d_target > 0.8 * self.sight:

                    self.search_plant(d_target)

                elif (self.target[2] not in self.simulation.gplant) and (self.target[2] is not None):

                    coordinates = (rd.randint(10, self.simulation.screen_size[0] - 10), rd.randint(10, self.simulation.screen_size[1] - 10))
                    self.target = (coordinates[0], coordinates[1], None)

            if self.heating:

                if (self.target[2] not in self.simulation.gotus) or (d_target > self.target[2].pherange * 1.2) or (self.target[2] in self.simulation.gotus and not self.target[2].heating):

                    mindist = -1
                    closest = None

                    for ot in self.simulation.gotus:

                        if ot != self and ot.heating:

                            d_target = m.sqrt(((ot.rect.centerx - self.rect.centerx) ** 2 + (ot.rect.centery - self.rect.centery) ** 2))

                            if d_target < mindist or mindist == -1:

                                mindist = d_target

                                closest = ot

                    if closest is not None and mindist < closest.pherange:
                        self.target = (closest.rect.center[0], closest.rect.center[1], closest)

                    elif closest is None or d_target > closest.pherange * 1.2:

                        coordinates = (rd.randint(10, self.simulation.screen_size[0] - 10), rd.randint(10, self.simulation.screen_size[1] - 10))
                        self.target = (coordinates[0], coordinates[1], None)

    # lorsqu'un otus mange une plante, sa cible change si la plante mangée était sa cible,
    # et on supprime la plante en question
    def eat(self, plant):

        self.metabolism.gain_energy(plant.energy_stock + plant.init_size / plant.energy_density)

        self.simulation.gplant.remove(plant)

        coordinates = (rd.randint(10, self.simulation.screen_size[0] - 10), rd.randint(10, self.simulation.screen_size[1] - 10))
        self.target = (coordinates[0], coordinates[1], None)

    # fonction qui gère la mort d'un otus, en l'enlevant du groupe
    def dies(self):

        self.simulation.gotus.remove(self)

        if self == self.simulation.main_otus:

            for otus in self.simulation.gotus:
                self.simulation.main_otus = otus
                break

    # fonction qui gère la reproduction de l'otus, en ajoutant un certain nombre de nouveaux otus
    def reproduce(self, otherparent):

        self.heating = False

        babynum = rd.randint(0, round(genes.decrypt(self.genome.sequence[80:88], limits["number of babies"])))

        self.metabolism.spend_energy(self.metabolism.energy/2)

        for i in range(babynum):

            self.num_descendants += 1

            baby = Otus(self.simulation, parents=(self, otherparent), num=self.num_descendants)
            self.simulation.gotus.add(baby)

    # fonction qui permet de varier les couleurs des otus
    def bride_colors(self, supdark, dark, medium, light):

        # ces trois types de couleurs demandés correspondent aux différentes parties coloriables de l'otus
        colors = [supdark, dark, medium, light]

        # on crée un boucle multiple qui crée une liste contenant les couleurs de l'image de l'otus
        im = []
        for i in range(16):

            im.append([])

            for j in range(16):

                # si la valeur vaut -1, la case sera blanche, pour être transformer après en transparant
                if model[i, j] != -1:

                    im[i].append([])

                    for k in range(3):
                        c = round(colors[model[i, j]][k] * 34 + (model[i, j]) * 26)
                        im[i][j].append(c)

                else:

                    im[i].append([255, 255, 255])

        # on convertit la liste en tableau numpy, puis en image PIL
        im = np.array(im, dtype=np.uint8)
        pillow_im = Image.fromarray(im)

        # passer en PIL permet de convertir un tableau numpy en image pygame
        mode = pillow_im.mode
        size = pillow_im.size
        data = pillow_im.tobytes()
        image = pg.image.fromstring(data, size, mode)

        # enfin, on transforme la couleur blanche en transparant
        image.set_colorkey((255, 255, 255))

        return image