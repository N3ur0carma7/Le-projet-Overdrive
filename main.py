#this is main file



import pygame
from screens.menu import menu_principal
from screens.jeu import boucle_jeu

if __name__ == "__main__":
    pygame.init()
    LARGEUR_ECRAN, HAUTEUR_ECRAN = 1280, 720
    ecran = pygame.display.set_mode((LARGEUR_ECRAN, HAUTEUR_ECRAN))
    pygame.display.set_caption("Mon Jeu")
    horloge = pygame.time.Clock()
    FPS = 60

    # état initial = menu
    en_cours = True
    etat = "menu"

    while en_cours:
        if etat == "menu":
            # retourne le prochain état selon le bouton cliqué
            etat, en_cours = menu_principal(ecran, horloge, FPS)
        elif etat == "jeu":
            en_cours = boucle_jeu(ecran, horloge, FPS)
            etat = "menu"  # revenir au menu après jeu

    pygame.quit()
