# v1.1
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

            elif event.type == pg.KEYDOWN:

                # losque l'on appuie sur la touche entrée, on affiche un graphique montrant l'influence des différents inputs
                if event.key == pg.K_RETURN:

                    simu.show_neat_graphic()

                # lorsque l'on appuie sur espace, on fait muter artificielemnt le nouvel otus
                elif event.key == pg.K_SPACE:

                    simu.main_otus.brain.mutate()

                # on active/desactive le mode information
                elif event.key == pg.K_TAB:

                    simu.show_info = not simu.show_info

                # on active/desactive le mode follow
                elif event.key == pg.K_f:

                    simu.follow = not simu.follow

                    simu.switch_to_follow_mode()

                # on réinitialise le zoom (/!\ il y a un léger décallage à chaque remise à 0 : ne pas trop en abuser
                elif event.key == pg.K_ESCAPE:

                    simu.follow = False

                    # si le zoom vaut 1, on zoom un peu pour pouvoir dézoomer au point cherché
                    if abs(simu.zoom - 1) < 0.01:

                        simu.update_zoom(1)

                    # on initialise le point de zoom aux coordonnées qui resterons les mêmes lors du dézoom :
                    simu.zoom_center = (
                        simu.limit_points[0] / (1 - simu.zoom),
                        simu.limit_points[1] / (1 - simu.zoom)
                    )

                    # on fait une boucle qui zoom ou dézoom jusqu'a ce que le zoom vaut 1
                    while abs(simu.zoom - 1) >= (simu.zoom_rate - 1) / 10:

                        if simu.zoom >= 1:

                            simu.update_zoom(-1, reset=True)

                        else:

                            simu.update_zoom(1, reset=True)

                    # enfin, on dézoom sur le centre de l'écran pour pouvoir voir le traain entier
                    simu.zoom_center = (screen_size[0] / 2, screen_size[1] / 2)
                    simu.update_zoom(-1, reset=True)

            # si on clique, on séléctionne l'otus qui est en contact avec la souris
            elif event.type == pg.MOUSEBUTTONDOWN:

                if event.button < 4:

                    for otus in simu.gotus:

                        if otus.rect.collidepoint(pg.mouse.get_pos()):

                            simu.main_otus = otus

                            if simu.follow:
                                simu.switch_to_follow_mode()

            # si on bouge la molette de la souris, on zoom/dezoom
            elif event.type == pg.MOUSEWHEEL:

                if 0.95 <= simu.zoom * 1.05 ** event.y <= 25:
                    simu.update_zoom(event.y)

        # on régule le nombre de tour de boucle par seconde
        clock.tick(FPS)

    # Pour afficher les graphique du nombre d'otus et de plante en fonction du temps
    #num_otus = np.array(num_otus)
    #num_plant = np.array(num_plant)
    #plt.plot(num_otus, c="red")
    #plt.plot(num_plant, c="green")
    #plt.show()