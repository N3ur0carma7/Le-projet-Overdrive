import pygame
from screens.menu import Bouton

def menu_pause(ecran, horloge, FPS):
    LARGEUR_ECRAN, HAUTEUR_ECRAN = ecran.get_size()
    en_pause = True
    etat_retour = "jeu"

    # boutons
    boutons = [
        Bouton("Menu principal", LARGEUR_ECRAN//2 - 120, 300, 240, 50),
        Bouton("Quitter", LARGEUR_ECRAN//2 - 120, 400, 240, 50)
    ]

    while en_pause:
        horloge.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # ESC ferme le menu pause
                return "jeu"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if boutons[0].clic():
                    return "menu"
                if boutons[1].clic():
                    return False

        # fond semi-transparent
        overlay = pygame.Surface((LARGEUR_ECRAN, HAUTEUR_ECRAN))
        overlay.set_alpha(180)
        overlay.fill((50, 50, 50))
        ecran.blit(overlay, (0, 0))

        # afficher les boutons
        for btn in boutons:
            btn.afficher(ecran)

        pygame.display.flip()
