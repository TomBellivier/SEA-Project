# simulation des Otus v1.0

import pygame as pg
import simulation
import os

def begin_project():

    pg.init()

    os.chdir("../assets")

    # définir une horloge
    clock = pg.time.Clock()
    FPS = 24

    # générer la fenetre
    screen_size = (1400, 700)
    pg.display.set_caption("Otus")
    screen = pg.display.set_mode(screen_size)

    font = pg.font.SysFont('monospace', 10)

    simu = simulation.Simulation(screen, screen_size)

    running = True
    timer = 0

    num_otus = []
    num_plant = []

    while running:

        # on indente un timer, qui sert d'horloge pour toute la simulation
        timer += 1

        if len(simu.gotus) == 0:

            simu = simulation.Simulation(screen, screen_size)
            print(f"simulation suivante ({timer})")

        elif timer % 640 == 0:

            num_otus.append(len(simu.gotus))
            num_plant.append(len(simu.gplant))

        # on remplit l'écran de gris clair
        screen.fill([200, 200, 190])

        simu.update(timer)

        pg.display.flip()

        for event in pg.event.get():

            # si le joueur veut quitter, on ferme la fenêtre
            if event.type == pg.QUIT:

                running = False
                pg.quit()

            if event.type == pg.KEYDOWN:

                # losque l'on appuie sur la touche entrée, on affiche un graphique montrant l'influence des différents inputs
                if event.key == pg.K_RETURN:

                    simu.show_neat_graphic()

                # lorsque l'on appuie sur espace, on fait muter artificielemnt le nouvel otus
                if event.key == pg.K_SPACE:

                    simu.main_otus.brain.mutate()

                if event.key == pg.K_TAB:

                    simu.show_info = not simu.show_info

                if event.key == pg.K_f:

                    simu.follow = not simu.follow

            if event.type == pg.MOUSEBUTTONDOWN:

                for otus in simu.gotus:

                    if otus.rect.collidepoint(pg.mouse.get_pos()):

                        simu.main_otus = otus


        # on régule le nombre de tour de boucle par seconde
        clock.tick(FPS)

    #num_otus = np.array(num_otus)
    #num_plant = np.array(num_plant)
    #plt.plot(num_otus, c="red")
    #plt.plot(num_plant, c="green")
    #plt.show()