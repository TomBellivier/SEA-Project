#v1.1
import numpy as np
import pygame as pg
import random as rd
import math as m
import otus
import plant


class Simulation():

    def __init__(self, screen, screen_size):

        self.screen = screen

        # taille de l'écran total
        self.screen_size = screen_size
        self.limit_points = [
            10, 10, screen_size[0] - 10, screen_size[1] - 10
        ]

        # on cree la matrice recuperant les valeurs d'energie present sur le terrain

        self.start_energy = 60
        self.ground = np.ones((100, 100)) * self.start_energy
        self.plant_limit = 250

        # on initialise le zoom à 1 et le point de zoom au milieu de l'écran
        self.zoom = 1
        self.zoom_rate = 1.1
        self.zoom_center = (screen_size[0]/2, screen_size[1]/2)

        # on met un mode qui affiche les infos de l'otus séléctionné
        self.show_info = True

        # on met un mode qui permet de suivre un otus
        self.follow = False

        # on créer la police qui va être utilisée dans l'affichage des infos
        self.font = pg.font.SysFont("monospace", 20)

        # on défini un groupe de particule
        self.particles = pg.sprite.Group()

        # on crée l'ensemble des otus
        self.gotus = pg.sprite.Group()
        for i in range(1, 51):
            new_otus = otus.Otus(self, num=i)
            self.gotus.add(new_otus)

        # par défaut, l'otus séléctionné est le dernier crée
        self.main_otus = new_otus

        # on crée l'ensemble des plantes
        self.gplant = pg.sprite.Group()

        for i in range(15):
            new_plant = plant.Plant(self)
            self.gplant.add(new_plant)

    def update(self, timer):
        if timer % 16 == 0:
            pass
            # afficher le nombre de plante
            print("nomre de plante dans la simulation : ", len(self.gplant))

        if self.show_info:

            pg.draw.circle(self.screen, (200, 160-self.main_otus.heating*160, 200), self.main_otus.rect.center, self.main_otus.pherange, 2)

            pg.draw.circle(self.screen, (200, 180, 170), self.main_otus.rect.center, self.main_otus.sight, 4)

            # on affiche un trait fin désigant la cible de l'otus séléctionné, déssiné en premier pour
            # ne pas dessiner sur les autres éléments
            pg.draw.line(self.screen, (255, 50, 50), self.main_otus.rect.center, self.main_otus.target[:2])

            # on affiche le réseau de neuronne de l'otus principal sur l'écran
            self.main_otus.brain.show_neat(self.screen)

        if self.follow:
            xvalue = m.sin(m.radians(self.main_otus.angle)) * self.main_otus.speed * self.zoom
            yvalue = m.cos(m.radians(self.main_otus.angle)) * self.main_otus.speed * self.zoom
        else:
            xvalue = 0
            yvalue = 0

        for i in range(2):
            self.limit_points[i * 2] += xvalue
            self.limit_points[i * 2 + 1] += yvalue

        # on affiche les limites du terrain
        pg.draw.line(self.screen, (0, 0, 0), (self.limit_points[0], self.limit_points[1]), (self.limit_points[2], self.limit_points[1]))
        pg.draw.line(self.screen, (0, 0, 0), (self.limit_points[2], self.limit_points[1]), (self.limit_points[2], self.limit_points[3]))
        pg.draw.line(self.screen, (0, 0, 0), (self.limit_points[2], self.limit_points[3]), (self.limit_points[0], self.limit_points[3]))
        pg.draw.line(self.screen, (0, 0, 0), (self.limit_points[0], self.limit_points[3]), (self.limit_points[0], self.limit_points[1]))

        # on affiche les particules
        self.particles.draw(self.screen)

        for particle in self.particles:
            particle.update()

        # on dessine tout les otus
        self.gotus.draw(self.screen)

        # on dessine toutes les plantes
        self.gplant.draw(self.screen)

        for pl in self.gplant:
            pl.update()

        # on met à jour les otus sauf le séléctionné (déjà mis à jour)
        for ot in self.gotus:
            ot.update(self.screen, timer, xvalue, yvalue)

        if self.follow:
            for pl in self.gplant:
                pl.move(xvalue, yvalue)
        if len(self.gplant) == 0:
            for i in range(15):
                new_plant = plant.Plant(self)
                self.gplant.add(new_plant)
        if rd.random() < 0.05:
            new_plant = plant.Plant(self)
            self.gplant.add(new_plant)
        if len(self.gotus) <= 1:
            for i in range(1, 51):
                new_otus = otus.Otus(self, num=i)
                self.gotus.add(new_otus)

    # fonction qui fait les changement necessaires pour centrer l'otus sélectionné et déplacer tout les autres éléments
    def switch_to_follow_mode(self):
        xvalue = self.screen_size[0] / 2 - self.main_otus.rect.centerx
        yvalue = self.screen_size[1] / 2 - self.main_otus.rect.centery

        # on décale les limites
        for i in range(2):
            self.limit_points[i * 2] += xvalue
            self.limit_points[i * 2 + 1] += yvalue

        # on décale les otus
        for ot in self.gotus:
            ot.move(xvalue, yvalue)

        # on décale les plantes
        for pl in self.gplant:
            pl.move(xvalue, yvalue)

    # on affiche le réseau de neurone de l'otus principal
    def show_neat_graphic(self):

        self.main_otus.show_neat_graphic()

    # on crée une fonction qui met à jour l'écran lors d'un zoom
    def update_zoom(self, direction, reset=False):

        # valeur qui va multiplier toutes les variables dépendant du zoom
        zoom_factor = self.zoom_rate ** direction

        # on récupère les coordonnées de la souris
        mouse_pos = pg.mouse.get_pos()

        # on modifie la valeur du zoom; si direction vaut soit -1 soit 1
        self.zoom *= zoom_factor

        if self.follow:
            # le zoom se fera sur l'otus séléctioné
            self.zoom_center = (self.main_otus.rect.centerx, self.main_otus.rect.centery)

        else:
            # le zoom se fera sur la position de la souris
            if not reset:
                self.zoom_center = mouse_pos

        # on met à jour les points limites
        self.limit_points = [
            self.zoom_center[0] - (self.zoom_center[0] - self.limit_points[0]) * zoom_factor,
            self.zoom_center[1] - (self.zoom_center[1] - self.limit_points[1]) * zoom_factor,
            self.zoom_center[0] - (self.zoom_center[0] - self.limit_points[2]) * zoom_factor,
            self.zoom_center[1] - (self.zoom_center[1] - self.limit_points[3]) * zoom_factor
        ]

        # on met à jour les otus
        for ot in self.gotus:

            # d'abord, leur taille
            ot.size = ot.init_size * self.zoom

            # ensuite leur position
            ot.position = [self.zoom_center[0] - (self.zoom_center[0] - ot.rect.centerx) * zoom_factor,
                           self.zoom_center[1] - (self.zoom_center[1] - ot.rect.centery) * zoom_factor]

            # leur image
            ot.update_image()

            # ensuite, leur champ de vision
            ot.sight = ot.init_sight * self.zoom

            # enfin, la portée de leur phéromones
            ot.pherange = ot.init_pherange * self.zoom

        # on met à jour les plantes
        for pl in self.gplant:

            # d'abord, leur taille
            pl.size = pl.init_size * self.zoom

            # ensuite leur position
            pl.position = [self.zoom_center[0] - (self.zoom_center[0] - pl.rect.centerx) * zoom_factor,
                           self.zoom_center[1] - (self.zoom_center[1] - pl.rect.centery) * zoom_factor]

            # leur image
            pl.update_image()

        # on met à jour les cibles des otus
        for ot in self.gotus:

            if ot.target[2] is not None:

                # si la cible est définie, on réajuste directement sur la cible
                ot.target = (
                    ot.target[2].rect.centerx,
                    ot.target[2].rect.centery,
                    ot.target[2]
                )

            else:

                ot.target = (
                    self.zoom_center[0] - (self.zoom_center[0] - ot.target[0]) * zoom_factor,
                    self.zoom_center[1] - (self.zoom_center[1] - ot.target[1]) * zoom_factor,
                    ot.target[2]
                )

    # fonction qui permet de choisir des coordonnées du terrain (entre les points limites)
    def choice_coordinates(self):
        return [rd.random() * (self.limit_points[2] - self.limit_points[0]) + self.limit_points[0],
                rd.random() * (self.limit_points[3] - self.limit_points[1]) + self.limit_points[1]]
