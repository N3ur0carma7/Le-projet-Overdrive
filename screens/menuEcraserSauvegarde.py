import os

import pygame
from core.Class.buttons import BoutonImage

def confirmation_ecraser(ecran, horloge, FPS):
    LARGEUR_ECRAN, HAUTEUR_ECRAN = ecran.get_size()
    en_confirmation = True

    def btn_path(name, state):
        return os.path.join("assets", "buttons", "menu", f"{name}_{state}.png")

    boutons = [
        BoutonImage(LARGEUR_ECRAN // 2 - 140, 350, 300, 70,
                    btn_path("continuer", "normal"), btn_path("continuer", "hover")),
        BoutonImage(LARGEUR_ECRAN // 2 - 140, 460, 300, 70,
                    btn_path("menu_principal", "normal"), btn_path("menu_principal", "hover")),
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

        overlay = pygame.Surface((LARGEUR_ECRAN, HAUTEUR_ECRAN), pygame.SRCALPHA)
        overlay.fill((10, 5, 0, 180))
        ecran.blit(overlay, (0, 0))

        panel = pygame.Surface((LARGEUR_ECRAN - 120, 220), pygame.SRCALPHA)
        panel.fill((20, 12, 5, 220))
        pygame.draw.rect(panel, (130, 85, 30, 220), panel.get_rect(), 3)
        ecran.blit(panel, (60, 90))

        font = pygame.font.SysFont("Arial", 32, bold=True)
        texte = "Êtes-vous sûr de vouloir écraser votre sauvegarde actuelle ?"
        text_surface = font.render(texte, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(LARGEUR_ECRAN // 2, 180))
        ecran.blit(text_surface, text_rect)

        for btn in boutons:
            btn.afficher(ecran)

        pygame.display.flip()