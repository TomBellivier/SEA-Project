#v1.1

import pygame as pg
import numpy as np
import matplotlib.pyplot as plt
import random as rd
import math as m
import copy


class Brain:

    def __init__(self, otus, I, O, parent_brain=None):

        self.otus = otus

        # fonction qui peuvent être utilisées par les noeuds cachés
        self.functions = ("X", "SIN", "SIG", "GAU", "SQRT", "SQ", "MOY", "NEG")

        # on défini les synapses et les noeuds inputs et outputs
        if parent_brain is None:
            self.set_variables(I, O)
        else:
            # si on rélaise une simple copie, les dictionnaires des enfants auront celle des parents,
            # ce qui va modifier aussi leur cerveau s'il y a mutation
            self.synapses = copy.deepcopy(parent_brain.synapses)
            self.nodes = copy.deepcopy(parent_brain.nodes)

    def set_variables(self, I, O):
        # deux dictionnaires qui vont stocker tous les synapses (liaisons entre neurones) et les noeuds (neurones)
        self.synapses = {}
        self.nodes = {}

        # on créer des variables dans le dictionnaire pour ne pas les recalculer
        self.nodes["Num H node"] = 0
        self.nodes["Num O node"] = O
        self.nodes["Num I node"] = I

        # on commence par ajouter tout les neurones d'input et d'ouput
        for i in range(I):
            for o in range(O):
                # un neurone est composé d'une fonction et d'un poids qu'il va ajouter à la valeur du synapse dans sa fonction
                self.nodes["O" + str(o)] = ["MOY", 0]

                # un synapse est composé d'un nombre qui va être multiplié par la valeur sortant du neurone le précédant
                self.synapses[("I" + str(i), "O" + str(o))] = rd.random()

            self.nodes["I" + str(i)] = ["SIG", 0]

       # self.synapses = {('I1', 'O1'): 0.8811540000451784, ('I1', 'O0'): 0.7955097767785083, ('I0', 'O0'): 0.517580016364619,
       #  ('I1', 'H19'): 0.8604177826356012, ('H19', 'O1'): 0.4152567253463756}
       # self.nodes = {'Num H node': 20, 'Num O node': 2, 'Num I node': 2, 'O0': ['MOY', 0], 'O1': ['MOY', 0], 'I0': ['SIG', 0],
       #  'I1': ['SIG', 0], 'H19': ['SIN', 0.21575343618818765]}

    # on modifie la valeur d'une synapse
    def change_synapse(self, F, S):

        # on teste si le synapse existe
        if self.synapses.get((F, S)):

            # on modifie très légèrement le poids du synapse
            self.synapses[(F, S)] += (rd.random()-0.5) / 50

    # On ajoute une synapse
    def add_synapse(self, F, S):

        if self.nodes.get(F) and self.nodes.get(S):

            # on teste si le synapse existe déjà entre deux neurones ou si le synapse réalise une boucle avec les différents synapses
            if not self.synapses.get((F, S)) and not self.synapses.get((S, F)) and not self.loop_check((F, S)):

                # on associe au synapse une valeur comprise entre 0 et 1
                self.synapses[(F, S)] = rd.random()

    # On supprime une synapse existante
    def suppr_synapse(self, F, S):

        # on teste si le synapse existe
        if self.synapses.get((F, S)):

            # on suprime le synapse du dictionnaire
            del (self.synapses[(F, S)])

            # on initialise une liste vide qui va récupérer tout les noeuds reliés au synapse, et qui vont donc être supprimés s'il se retrouvent isolés
            to_suppr = []

            for nod in self.nodes.keys():
                if (F == nod or S == nod) and nod[0] != "I" and nod[0] != "O":

                    compter = [0, 0]

                    for syn in self.synapses.keys():
                        if nod == syn[0]:
                            compter[0] += 1

                        if nod == syn[1]:
                            compter[1] += 1

                    # si un des deux nombres et nul, cela veut dire que le noeud n'est pas lié à de synapse à l'avant
                    # ou à l'arrière : il est isolé et doit donnc être supprimé
                    if 0 in compter:
                        to_suppr.append(nod)

            # on supprime tout les noeuds qui ont été récupérés
            for nod in to_suppr:
                self.suppr_node(nod)

    def change_node(self, N):

        # on vérifie si le noeud existe et qu'il est modifiable
        if self.nodes.get(N) and N[0] != 'I' and N[0] != 'O' and N[0] != 'N':

            # soit on modifie le poids du noeud (légèrement), soit on modifie sa fonction, soit on modifie les deux
            if rd.random() > 0.9:

                self.nodes[N] = [self.nodes[N][0], self.nodes[N][1] + (rd.random()-0.5) / 50]

            elif rd.random() > 0.99:

                self.nodes[N] = [rd.choice(self.functions), self.nodes[N][1]]

            else:

                self.nodes[N] = [rd.choice(self.functions), self.nodes[N][1] + (rd.random()-0.5) / 50]

    # on ajoute un noeud
    def add_node(self, F, S):

        # on vérifie que les deux noeuds existent bel et bien
        if self.nodes.get(F) and self.nodes.get(S):

            # on crée le nom du nouveau noeud
            H = "H" + str(self.nodes["Num H node"])

            # on ajoute le nouveau noeud
            self.nodes["H" + str(self.nodes["Num H node"])] = [rd.choice(self.functions), rd.random()]
            self.nodes["Num H node"] += 1

            # on ajoute deux synapses pour ne pas que le noeud soit isolé: un à l'arrière du noeud, l'autre à l'avant
            self.add_synapse(F, H)
            self.add_synapse(H, S)

    # On supprime un noeud
    def suppr_node(self, N):

        # on vérifie que le noeud choisi n'est pas un input ou un output, ceux-ci ne devant pas être supprimés
        if self.nodes.get(N) and N[0] != 'I' and N[0] != 'O' and N[0] != 'N':

            # on supprime le noeud choisi
            del (self.nodes[N])

            # on crée une liste vide qui va récupérer les synapses isolés précédement liés au noeud
            to_suppr = []

            for syn in self.synapses.keys():
                if N in syn:
                    to_suppr.append(syn)

            # on supprime tout les synapses récupérés
            for syn in to_suppr:
                if self.synapses.get(syn):
                    self.suppr_synapse(syn[0], syn[1])

    # forward propagation : on calcule les output avec les input en fonctio des différents poids des synapses et fonctions
    def forward_propagation(self, VARS):

        out_puts = []

        for ot in self.nodes.keys():
            if ot[0] == "O":
                out_puts.append(self.recursive_chain(ot, VARS))

        return out_puts

    # fonction récursive partant des nodes "outputs", avant de remonter vers les "inputs"
    def recursive_chain(self, NOD, VARS):

        # la récusrivité s'arrête lorsque l'on obtient un noeud input : on récupère alors la variable qui doit être traitée par ce noeud
        if NOD[0] == "I":

            # on corrige la valeur entrée dans le neurone pour ne pas obtenir des valeurs trop petites ou trop proche de 1 via la fonction sigmoide
            v = VARS[int(NOD[1:])]
            b = 5 / v[1]

            return 1 / (1 + m.exp(- v[0] * b))

        else:

            # on créer une liste contenant toutes les valeurs des synapses reliés au noeud, multiplié par la valeur transmise par le noeud précédent
            syn_list = [
                self.synapses[syn] * self.recursive_chain(syn[0], VARS) for syn in self.synapses.keys() if syn[1] == NOD
]

            # on calcule la valeur qui va passer dans la fonction du noeud
            value = sum(syn_list) + self.nodes[NOD][1]

            # on calcule la valeur finale que va transmettre le noeud aux synapses suivants
            if self.nodes[NOD][0] == "X":

                value = value

            elif self.nodes[NOD][0] == "SIN":

                value = m.sin(value)

            elif self.nodes[NOD][0] == "SIG":

                value = 1 / (1 + m.exp(- value)) - 1 / 2

            elif self.nodes[NOD][0] == "GAU":

                value = m.exp(- value**2)

            elif self.nodes[NOD][0] == "SQRT":

                value = m.sqrt(abs(value))

            elif self.nodes[NOD][0] == "SQ":

                value = value**2

            elif self.nodes[NOD][0] == "MOY":

                if len(syn_list) > 0:

                    value = value/len(syn_list)

                else:

                    value = value

            elif self.nodes[NOD][0] == "NEG":

                value = - value

            return value

    # vérifier recursivement si on a pas formé une boucle de synapse
    def loop_check(self, syn, path=""):

        # si on obtient un input, il n'y a pas de boucle formée avec ce synapse
        if syn[0] == "I":
            return False

        # si on tombe sur un noeud que l'on a déjà croisé, il y a une boucle
        elif syn[0] in path:
            return True

        else:
            # on enregistre le chemin pris
            n_path = path + syn[1]
            list_paths = [self.loop_check(s, n_path) for s in self.synapses.keys() if s[1] == syn[0]]

            # on retourne la somme des bouleens : si elle est supérieure à 0, il y a au moins une boucle
            return sum(list_paths) > 0

    # pour ajouter des synapses ou des noeud, les changer ou les supprimer
    def mutate(self):
        if len(self.synapses) == 0:
            self.set_variables(int(self.nodes["Num I node"]), int(self.nodes["Num O node"]))

        last_synapses = self.synapses
        last_nodes = self.nodes

        nH = self.nodes["Num H node"] - 1
        nO = self.nodes["Num O node"] - 1
        nI = self.nodes["Num I node"] - 1

        # on cherche ici à modifier les noeuds ou les synapses
        if rd.random() > 0.05:

            # on veux changer un synapse
            if rd.random() > 0.3:

                syn = rd.choice(list(self.synapses.keys()))

                self.change_synapse(syn[0], syn[1])

            # on change un noeud
            else:

                # les noeuds pouvant être changés ne sont que les noeuds cachés
                change_list = [nod for nod in self.nodes.keys() if nod[0] != "N"]

                change = rd.choice(change_list)

                self.change_node(change)

        # on ajoute ou supprime un noeud ou une synapse
        else:

            # ajouter un noeud ou un synapse (le changer s'il est déjà existant)
            if rd.random() > 0.2:

                # ajouter un noeud ou un synapse a peu de différence (on crée un chemin entre deux noeuds dans les
                # deux cas), les calculs sont donc les mêmes
                if self.nodes["Num H node"] > 0:

                    # on choisit le noeud à partir duquel on va ajouter le noeud ou la synapse
                    typ1 = rd.choice(["H", "I", "I"])
                    num1 = rd.randint(0, self.nodes[f"Num {typ1} node"] - 1)
                    nod1 = typ1 + str(num1)

                    # on choisit le deuxième noeud
                    if self.nodes["Num H node"] > 1:

                        typ2 = rd.choice(["H", "O"])

                    else:

                        typ2 = "O"

                    if typ2 == "H":

                        num2 = rd.randint(0, nH)

                        # on essaye de ne pas avoir un synapse entre le même noeud
                        while num2 == num1:

                            num2 = rd.randint(0, nH)

                    else:

                        num2 = rd.randint(0, nO)

                    nod2 = typ2 + str(num2)

                # s'il n'existe aucun noeud caché, on ajoute le synapse (ou le noeud) entre un input et un output
                else:

                    nod1 = "I" + str(rd.randint(0, nI))
                    nod2 = "O" + str(rd.randint(0, nO))

                syn = (nod1, nod2)
                nod = "H" + str(self.nodes["Num H node"])

                if rd.random() > 0.3:

                    # si le synapse existe déjà, on le modifie
                    if syn in self.synapses:

                        self.change_synapse(nod1, nod2)

                    else:

                        self.add_synapse(nod1, nod2)

                else:

                    self.add_node(nod1, nod2)

            # on supprime un synapse ou un noeud
            else:

                # on supprime un synapse
                if rd.random() > 0.3:

                    suppr = rd.choice(list(self.synapses.keys()))

                    self.suppr_synapse(suppr[0], suppr[1])

                # on supprime un noeud
                else:

                    # on crée une liste ne prenant pas en compte les valeurs spéciales que l'on à ajouté à l'initialisation
                    suppr_list = [nod for nod in self.nodes.keys() if nod[0] != "N"]

                    suppr = rd.choice(suppr_list)

                    self.suppr_node(suppr)

        if last_nodes == self.nodes and last_synapses == self.synapses and rd.random() > 0.1 and len(self.synapses) != 0:
            self.mutate()

    # on affiche le réseau de neurone
    def show_neat(self, screen, screen_size=(400, 250)):

        font = pg.font.SysFont('monospace', 20)
        font2 = pg.font.SysFont('monospace', 10)

        screen = self.otus.simulation.screen
        text1 = f"Vie : {round(self.otus.metabolism.health, 1)}/{self.otus.metabolism.max_health}"
        text2 = f"Energie : {round(self.otus.metabolism.energy, 1)}/{self.otus.metabolism.max_energy}"
        text3 = f"Lignée : {self.otus.progeny}"
        text4 = f"Code : {self.otus.genome.sequence}"
        screen.blit(self.otus.simulation.font.render(text1, 1, (0, 0, 0)), (0, 20))
        screen.blit(self.otus.simulation.font.render(text2, 1, (0, 0, 0)), (0, 40))
        screen.blit(self.otus.simulation.font.render(text3, 1, (0, 0, 0)), (0, 0))
        screen.blit(self.otus.simulation.font.render(text4, 1, (0, 0, 0)), (0, 60))

        h_nodes = sum([1 for nod in self.nodes if nod[0] == "H"])
        center = (screen_size[0]//2 + 20, screen_size[1]//2 + 20)
        diameter = min(screen_size) - 90

        coords = {}

        for nod in self.nodes.keys():

            if nod[0] == "N":
                pass

            elif nod[0] == "I":
                coords[nod] = (95, 20 + round(screen_size[1] / (int(self.nodes["Num I node"]) + 1) * (int(nod[1:]) + 1)))

            elif nod[0] == "O":
                coords[nod] = (screen_size[0] - 55, 20 + round(screen_size[1] / (int(self.nodes["Num O node"]) + 1) * (int(nod[1:]) + 1)))

            else:
                coords[nod] = (center[0] + diameter / 2 * m.cos(2 * m.pi * int(nod[1:]) / h_nodes),
                               center[1] + diameter / 2 * m.sin(2 * m.pi * int(nod[1:]) / h_nodes))

        compter = 0
        for syn in self.synapses.keys():

            compter += 1

            c = round(205 * self.synapses[syn] + 25) % 255
            pg.draw.line(screen, (c, c, c), coords[syn[0]], coords[syn[1]], width=3)

        for nod in coords.keys():

            pg.draw.circle(screen, (0, 0, 0), coords[nod], 20)
            screen.blit(font.render(nod, 1, (255, 255, 255)), (coords[nod][0] - 10, coords[nod][1] - 20))

            text = (self.nodes[nod][0], round(float(self.nodes[nod][1]), 3))
            screen.blit(font2.render(str(text[0]), 1, (255, 255, 255)), (coords[nod][0] - 15, coords[nod][1] - 4))
            screen.blit(font2.render(str(text[1]), 1, (255, 255, 255)), (coords[nod][0] - 15, coords[nod][1] + 3))

    def show_graphic(self, VARS, n_inputs, n_outputs):
        print(self.synapses, "\n", self.nodes)
        colors = ["red", "blue", "green", "orange", "black"]
        N = 13

        values = {i: [] for i in range(n_outputs)}
        inputs = [np.linspace(- VARS[i][1], VARS[i][1], N) for i in range(n_inputs)]

        axes = plt.axes(projection="3d")

        for i in range(N):
            for z in values.keys():
                values[z].append([])

            for j in range(N):
                var = [(((i+0.5)/N - 0.5) * VARS[k][1], VARS[k][1]) for k in range(n_inputs)]

                compter = 0
                for z in values.keys():
                    values[z][i].append([self.forward_propagation(var)[compter]])
                    compter += 1

            compter = 0
            for z in inputs:
                axes.scatter3D(z, values[0][i], values[1][i], color=colors[compter])
                compter += 1

        axes.set_xlabel("input")
        axes.set_ylabel("output 1")
        axes.set_zlabel("output 2")

        plt.show()

