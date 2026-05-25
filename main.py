# Fichier principal du jeu
import pygame
from screens.menu import menu_principal
from screens.jeu import boucle_jeu

if __name__ == "__main__":
    pygame.init()

    LARGEUR_ECRAN, HAUTEUR_ECRAN = 1280, 720
    ecran = pygame.display.set_mode((LARGEUR_ECRAN, HAUTEUR_ECRAN), pygame.RESIZABLE)
    pygame.display.set_caption("Projet Overdrive")
    horloge = pygame.time.Clock()
    FPS = 60

    fullscreen = False

    en_cours = True
    etat = "menu"
    while en_cours:
        for event in pygame.event.get([ pygame.KEYDOWN]):
            if event.key == pygame.K_F11:
                fullscreen = not fullscreen
                if fullscreen:
                    ecran = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                else:
                    ecran = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
            else:
                pygame.event.post(event)  # remettre l'event dans la file

        if etat == "menu":
            etat, en_cours = menu_principal(ecran, horloge, FPS)
        elif etat == "jeu":
            en_cours = boucle_jeu(ecran, horloge, FPS, True)
            etat = "menu" 
        elif etat == "jeudev":
            en_cours = boucle_jeu(ecran, horloge, FPS, False, dev_mode=True)
            etat = "menu"

    pygame.quit()
