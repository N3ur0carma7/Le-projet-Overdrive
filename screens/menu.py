import pygame
import json
import os
from multiplayer.client import connection
from multiplayer.serveur import server_running
from core.Class.buttons import Bouton
import threading
import time


def menu_principal(ecran, horloge, FPS):
    LARGEUR_ECRAN, HAUTEUR_ECRAN = ecran.get_size()
    en_cours = True
    etat_suivant = "menu"

    def creer_boutons():
        W, H = ecran.get_size()
        return [
            Bouton("Commencer", W//2 - 100, 200, 200, 50),
            Bouton("Continuer", W // 2 - 100, 300, 200, 50),
            Bouton("Rejoindre", W//2 - 100, 400, 200, 50),
            Bouton("Paramètres", W//2 - 100, 500, 200, 50),
            Bouton("Quitter", W//2 - 100, 600, 200, 50),
            Bouton("DEV", W // 2 - 500, 200, 200, 50),
        ]

    # créer les boutons
    boutons = creer_boutons()

    while en_cours:
        horloge.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return etat_suivant, False
            if event.type == pygame.VIDEORESIZE:
                LARGEUR_ECRAN, HAUTEUR_ECRAN = event.w, event.h
                boutons = creer_boutons()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if boutons[0].clic():  # Jouer
                    if os.path.exists("save/save.json"): # Check si une sauvegarde existe déjà
                        from screens.menuEcraserSauvegarde import confirmation_ecraser
                        etat_confirmation = confirmation_ecraser(ecran, horloge, FPS)
                        if etat_confirmation is False:
                            return etat_suivant, False
                        elif etat_confirmation == "menu":
                            return etat_confirmation, True
                        elif etat_confirmation == "jeu":
                            threading.Thread(target=connection, args=()).start()
                            time.sleep(1)
                            threading.Thread(target=server_running, args=()).start()
                            return etat_confirmation, True
                    else:
                        threading.Thread(target=connection, args=()).start()
                        time.sleep(1)
                        threading.Thread(target=server_running, args=()).start()
                        return "jeu", True
                if boutons[1].clic():
                    if os.path.exists("save/save.json"):
                        threading.Thread(target=connection, args=()).start()
                        time.sleep(1)
                        threading.Thread(target=server_running, args=()).start()
                        return "jeu", True
                if boutons[2].clic():  # Rejoindre
                    threading.Thread(target=connection, args=()).start()
                    return "jeu", True

                if boutons[3].clic():  # Paramètres
                    print("Ouvrir menu paramètres")
                if boutons[4].clic():  # Quitter
                    return etat_suivant, False
                if boutons[5].clic():
                    return "jeudev", True

        ecran.fill((50, 50, 50))
        for btn in boutons:
            btn.afficher(ecran)

        W, H = ecran.get_size()
        font = pygame.font.SysFont("Arial", 100)
        text_surface = font.render("Overdrive", True,
                                   (255, 255, 255))
        ecran.blit(text_surface, (W // 2 - 225, 70))

        pygame.display.flip()