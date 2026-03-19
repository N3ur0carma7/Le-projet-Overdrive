import pygame
from screens.menu import Bouton
import os

def confirmation_ecraser(ecran, horloge, FPS):
    LARGEUR_ECRAN, HAUTEUR_ECRAN = ecran.get_size()
    en_confirmation = True

    boutons = [
        Bouton("Confirmer", LARGEUR_ECRAN//2 - 120, 300, 240, 50),
        Bouton("Annuler", LARGEUR_ECRAN//2 - 120, 400, 240, 50),
    ]

    while en_confirmation:
        horloge.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "menu"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if boutons[0].clic():
                    if os.path.exists("save/save.json"):
                        os.remove("save/save.json")
                    return "jeu"
                if boutons[1].clic():
                    return "menu"

        overlay = pygame.Surface((LARGEUR_ECRAN, HAUTEUR_ECRAN))
        overlay.fill((50, 50, 50))
        ecran.blit(overlay, (0, 0))

        for btn in boutons:
            btn.afficher(ecran)

        font = pygame.font.SysFont("Arial", 35)
        text_surface = font.render("Êtes-vous sûr de vouloir écraser votre sauvegarde actuelle ?", True, (255, 255, 255))
        ecran.blit(text_surface, (LARGEUR_ECRAN//2 - 450, 100))

        pygame.display.flip()