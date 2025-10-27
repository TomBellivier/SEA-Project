import pygame as pg
import random as rd
import otus
import plant


class Simulation():

    def __init__(self, screen, screen_size):

        self.screen = screen

        # taille de l'écran total
        self.screen_size = screen_size

        # on met un mode qui affiche les infos de l'otus séléctionné
        self.show_info = True

        # on met un mode qui permet de suivre un otus
        self.follow = False

        # on créer la police qui va être utilisée dans l'affichage des infos
        self.font = pg.font.SysFont("monospace", 20)

        # on crée l'ensemble des otus
        self.gotus = pg.sprite.Group()
        for i in range(1, 21):
            new_otus = otus.Otus(self, num=i)
            self.gotus.add(new_otus)

        # par défaut, l'otus séléctionné est le dernier crée
        self.main_otus = new_otus

        # on crée l'ensemble des plantes
        self.gplant = pg.sprite.Group()

        for i in range(40):
            new_plant = plant.Plant(self)
            self.gplant.add(new_plant)

    def update(self, timer):

        if self.show_info:

            pg.draw.circle(self.screen, (200, 180, 170), self.main_otus.rect.center, self.main_otus.sight)

            # on affiche un trait fin désigant la cible de l'otus séléctionné, déssiné en premier pour
            # ne pas dessiner sur les autres éléments
            pg.draw.line(self.screen, (255, 50, 50), self.main_otus.rect.center, self.main_otus.target[:2])

            # on affiche le réseau de neuronne de l'otus principal sur l'écran
            self.main_otus.brain.show_neat(self.screen)

        # on dessine tout les otus
        self.gotus.draw(self.screen)

        # on dessine toutes les plantes
        self.gplant.draw(self.screen)

        # on met à jour les otus
        for ot in self.gotus:
            ot.update(self.screen, timer)

        # on crée une plante avec une faible probabilité
        if rd.random() < 0.05:
            new_plant = plant.Plant(self)
            self.gplant.add(new_plant)

    # on affiche le réseau de neurone de l'otus principal
    def show_neat_graphic(self):

        self.main_otus.show_neat_graphic()
