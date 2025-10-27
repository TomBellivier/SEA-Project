import pygame as pg
import numpy as np
import random as rd
import math as m
from PIL import Image
import brain
import metabolism

# ce modèle sert à connaitre l'emplacement des zones transparente, claires ou c=foncées de l'image de l'otus
model = np.array([
            [-1, -1, -1, -1, -1, -1,  0, -1, -1,  0, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1,  0, -1, -1, -1, -1,  0, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1,  0,  0,  0,  0, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1,  0,  0,  1,  1,  0,  0, -1, -1, -1, -1, -1],
            [-1, -1, -1,  2,  2,  1,  1,  1,  1,  1,  1,  2,  2, -1, -1, -1],
            [-1, -1, -1,  2,  1,  1,  2,  2,  2,  2,  1,  1,  2, -1, -1, -1],
            [-1, -1,  0,  1,  1,  2,  2,  2,  2,  2,  2,  1,  1,  0, -1, -1],
            [-1,  0,  1,  1,  1,  2,  0,  0,  0,  0,  2,  1,  1,  1,  0, -1],
            [-1,  0,  1,  1,  1,  2,  0,  0,  0,  0,  2,  1,  1,  1,  0, -1],
            [-1,  0,  0,  0,  1,  2,  2,  0,  0,  2,  2,  1,  0,  0,  0, -1],
            [-1,  0, -1, -1,  0,  1,  2,  2,  2,  2,  1,  0, -1, -1,  0, -1],
            [-1, -1, -1, -1,  2,  1,  1,  1,  1,  1,  1,  2, -1, -1, -1, -1],
            [-1, -1, -1, -1,  2,  1,  1,  1,  1,  1,  1,  2, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1,  2,  1,  1,  1,  1,  2, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1,  0,  1,  1,  0, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1,  0,  0, -1, -1, -1, -1, -1, -1, -1]
        ])


# on crée une classe pour gérer un otus
class Otus(pg.sprite.Sprite):

    def __init__(self, simulation, parent=None, num=0):

        super().__init__()

        self.simulation = simulation

        self.num_descendants = 0

        if parent is None:
            self.progeny = str(num)
        else:
            self.progeny = parent.progeny + "." + str(num)

        self.metabolism = metabolism.Metabolism(self)

        # on définit une taille
        self.size = 16

        # on défini une vitesse
        self.max_speed = 1
        self.speed = 1

        # on défini une vitesse angulaire et un angle de départ aléatoire
        self.angle = rd.randint(0, 360)
        self.max_angle_speed = 10
        self.angle_speed = 10

        # on défini un champ de vision
        self.sight = 200

        # on défini une masse
        self.weight = 10    # kg

        # on défini une cible vers laquelle l'otus devrait se diriger
        self.target = (rd.randint(10, self.simulation.screen_size[0] - 10), rd.randint(10, self.simulation.screen_size[1] - 10), None)

        # on défini le nombre d'entrée et de sortie que va recevoir le cerveau de l'otus
        self.inputs, self.outputs = 2, 2

        # on crée une liste qui va recevoir les paramètre que l'on va donner au cerveau de l'otus
        self.brain_vars = []

        # on crée le cerveau de l'otus, sil a des parents, il herite de leur cerveau avec quelques mutations
        if parent is None:
            self.brain = brain.Brain(self, self.inputs, self.outputs)
        else:
            self.brain = brain.Brain(self, self.inputs, self.outputs, parent.brain)

            for i in range(2):
                self.brain.mutate()

        # on défini l'image de l'otus. Si c'est un nouveau né, il hérite d'un mélange des couleurs des parents
        if parent is None:

            colors = (rd.randint(0, 5), rd.randint(0, 5), rd.randint(0, 5))
            self.colors = (colors, colors, colors)
            self.init_image = self.bride_colors(colors, colors, colors)

        else:

            medium = parent.colors[0]
            dark = (rd.randint(0, 5), rd.randint(0, 5), rd.randint(0, 5))
            light = tuple([rd.choice([medium[x], dark[x]]) for x in range(3)])

            self.colors = (dark, medium, light)
            self.init_image = self.bride_colors(dark, medium, light)

        self.reset_image = pg.transform.scale(self.init_image, (self.size, self.size))
        self.image = self.reset_image

        # on défini la position de l'image de l'otus
        self.rect = self.image.get_rect()

        # si l'otus est un nouveau né, il apparait près de ses parents
        if parent is None:
            self.rect.x = rd.randint(20, 1380)
            self.rect.y = rd.randint(20, 680)
        else:
            self.rect.x = parent.rect.x
            self.rect.y = parent.rect.y

        self.rect = self.image.get_rect(center=self.rect.center)

        # on défini la position réelle de l'otus
        self.position = [self.rect.x + self.size / 2, self.rect.y + self.size / 2]

    # on met à jour les paramètres généraux de l'otus : position, vitesse...
    def update(self, screen, timer):

        # on calcul ici la distance séparant l'otus de sa cible
        d = m.sqrt(((self.target[0] - self.rect.center[0]) ** 2 + (self.target[1] - self.rect.center[1]) ** 2))
        d += 0.001 * (d == 0)

        # on calcule ensuite l'angle entre la direction de l'otus et sa cible
        angle = (self.angle + m.degrees(m.asin((self.target[0] - self.rect.center[0]) / d)) % 360) % 360

        # on défini les variables d'input du cerveau
        self.brain_vars = [(d, m.sqrt(1400**2 + 700**2)), (angle, 360)]

        # on récupère les résultats que nous a renvoyé le cerveau
        results = self.brain.forward_propagation(self.brain_vars)

        # on met à jour les variables concernées par ces résultats
        self.update_vars(results)

        # on fait bouger l'otus : avancer, tourner...
        self.turn()
        self.forward()

        self.metabolism.spend_energy(0.01)

        # on met à jour une nouvelle cible
        self.update_target(timer)

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

    # on fait avancer l'otus
    def forward(self):

        # on fait avancer l'otus
        self.position[0] -= m.sin(m.radians(self.angle)) * self.speed
        self.position[1] -= m.cos(m.radians(self.angle)) * self.speed

        # on replace l'otus à l'opposé de la carte lorsqu'il dépasse les limites de l'écran
        if 10 > self.position[0]:

            self.position[0] = self.simulation.screen_size[0] - 10

        elif self.simulation.screen_size[0] - 10 < self.position[0]:

            self.position[0] = 10

        if 10 > self.position[1]:

            self.position[1] = self.simulation.screen_size[1] - 10

        elif self.simulation.screen_size[1] - 10 < self.position[1]:

            self.position[1] = 10

        self.metabolism.spend_energy(self.speed * 0.01)

        # on met à jour la position de l'image de l'otus
        self.update_position()

    # on met à jour la position de l'image de l'otus
    def update_position(self):

        self.rect.x += self.position[0] - self.rect.center[0]
        self.rect.y += self.position[1] - self.rect.center[1]

    # on met à jour les vaiables concernées par les résultats retournés par le cerveau
    def update_vars(self, results):
        self.speed = results[0] * self.max_speed
        self.angle_speed = (results[1]-0.5) * self.max_angle_speed

    # on met à jour une cible
    def update_target(self, timer):

        # on calcule la distance avec la cible actuelle
        d_target = m.sqrt(((self.target[0] - self.rect.center[0]) ** 2 + (self.target[1] - self.rect.center[1]) ** 2))

        # l'otus mange la cible si c'est une plante et si il est assez proche
        if d_target < self.size and self.target[2] in self.simulation.gplant:
            self.eat(self.target[2])

        # on met à jour la cible des otus régulièrement : la nouvelle cible sera la plante la plus proche
        if timer % 20 == 0 and (self.target[2] is None or d_target > 0.8 * self.sight):

            closest = None

            for plant in self.simulation.gplant:

                d = m.sqrt(((plant.rect.center[0] - self.rect.center[0]) ** 2 + (plant.rect.center[1] - self.rect.center[1]) ** 2))

                if d < d_target:

                    d_target = d
                    closest = plant

            # si la plante la plus proche est dans le champs de vision de l'otus, elle devient sa nouvelle cible
            if d_target < self.sight and closest is not None:

                self.target = (closest.rect.center[0], closest.rect.center[1], closest)

        # si la plante cible à disparu, l'otus cherche une nouvelle cible
        elif (self.target[2] not in self.simulation.gplant) and (self.target[2] is not None):

            coordinates = (rd.randint(10, self.simulation.screen_size[0] - 10), rd.randint(10, self.simulation.screen_size[1] - 10))
            self.target = (coordinates[0], coordinates[1], None)

    # lorsqu'un otus mange une plante, sa cible change si la plante mangée était sa cible,
    # et on supprime la plante en question
    def eat(self, plant):

        self.metabolism.gain_energy(plant.energy_capacity)

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
    def reproduce(self):

        for i in range(2):

            self.num_descendants += 1

            baby = Otus(self.simulation, parent=self, num=self.num_descendants)
            self.simulation.gotus.add(baby)

    # fonction qui permet de varier les couleurs des otus
    def bride_colors(self, dark, medium, light):

        # ces trois types de couleurs demandés correspondent aux différentes parties coloriables de l'otus
        colors = [dark, medium, light]

        # on crée un boucle multiple qui crée une liste contenant les couleurs de l'image de l'otus
        im = []
        for i in range(16):

            im.append([])

            for j in range(16):

                # si la valeur vaut 0, la case sera blanche, pour être transformer après en transparant
                if model[i, j] != -1:

                    im[i].append([])

                    for k in range(3):

                        c = round(colors[model[i, j]][k] * 34 + (model[i, j]) * 40)
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