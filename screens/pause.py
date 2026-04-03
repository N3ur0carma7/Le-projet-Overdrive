

import pygame
import time
import random
import os
from multiplayer.client import send_server, DISCONNECT_MESSAGE, CLIENT, disconnect
from core.Class.buttons import BoutonImage
from core.Class.player import Player
from core.saves import save_game

save = pygame.image.load("assets/save_done.png")


def menu_pause(ecran, horloge, FPS, buildings, online_data, player: Player, screenshot):
    LARGEUR_ECRAN, HAUTEUR_ECRAN = ecran.get_size()
    en_pause = True

    font_path = os.path.join("assets", "fonts", "Minecraft.ttf")
    try:
        font_titre = pygame.font.Font(font_path, 60)
    except:
        font_titre = pygame.font.SysFont("Arial", 60, bold=True)

    def btn_path(name, state):
        return os.path.join("assets", "buttons", "menu", f"{name}_{state}.png")

    BTN_SPACING = 100
    BTN_H = 70
    BTN_W = 300
    btn_y_start = HAUTEUR_ECRAN // 2 - 130
    panel_w = BTN_W + 60
    panel_h = 300
    panel_x = LARGEUR_ECRAN // 2 - panel_w // 2
    panel_y = HAUTEUR_ECRAN // 2 - 140

    # boutons
    boutons = [
        BoutonImage(LARGEUR_ECRAN//2 - BTN_W//2, btn_y_start + 0 * BTN_SPACING, BTN_W, BTN_H,
                    btn_path("Continuer", "normal"), btn_path("Continuer", "hover")),
        BoutonImage(LARGEUR_ECRAN//2 - BTN_W//2, btn_y_start + 1 * BTN_SPACING, BTN_W, BTN_H,
                    btn_path("Sauvegarder", "normal"), btn_path("Sauvegarder", "hover")),
        BoutonImage(LARGEUR_ECRAN//2 - BTN_W//2, btn_y_start + 2 * BTN_SPACING, BTN_W, BTN_H,
                    btn_path("Quitter", "normal"), btn_path("Quitter", "hover"))
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
                    if online_data and CLIENT is not None:
                        disconnect()
                    return "menu"
                if boutons[1].clic():
                    if not save_game(buildings, player, online_data):
                        print("ERREUR CRITIQUE: Écriture du fichier save/save.json")
                        return False
                    print("Sauvegarde réussite, retour au jeu")
                    ecran.blit(save, (0, 0))
                    pygame.display.flip()
                    time.sleep(1)
                    return "jeu"
                if boutons[2].clic():
                    if online_data and CLIENT is not None:
                        disconnect()
                    return False

        blurred = pygame.transform.smoothscale(screenshot, (LARGEUR_ECRAN//4, HAUTEUR_ECRAN//4))
        blurred = pygame.transform.smoothscale(blurred, (LARGEUR_ECRAN, HAUTEUR_ECRAN))
        ecran.blit(blurred, (0, 0))

        overlay = pygame.Surface((LARGEUR_ECRAN, HAUTEUR_ECRAN), pygame.SRCALPHA)
        overlay.fill((10, 5, 0, 150))
        ecran.blit(overlay, (0, 0))

        panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel_surf.fill((10, 5, 0, 110))
        pygame.draw.rect(panel_surf, (130, 85, 30, 200), (0, 0, panel_w, panel_h), 2)
        corner_size = 8
        for cx2, cy2 in [(0, 0), (panel_w - corner_size, 0), (0, panel_h - corner_size), (panel_w - corner_size, panel_h - corner_size)]:
            pygame.draw.rect(panel_surf, (180, 120, 40, 220), (cx2, cy2, corner_size, corner_size))
        ecran.blit(panel_surf, (panel_x, panel_y))

        titre = font_titre.render("PAUSE", True, (220, 160, 50))
        shadow = font_titre.render("PAUSE", True, (50, 25, 5))
        tx = LARGEUR_ECRAN // 2 - titre.get_width() // 2
        ty = panel_y - titre.get_height() - 28
        ecran.blit(shadow, (tx + 3, ty + 3))
        ecran.blit(titre, (tx, ty))

        line_y = ty + titre.get_height() + 6
        pygame.draw.line(ecran, (160, 100, 40), (LARGEUR_ECRAN // 2 - 200, line_y), (LARGEUR_ECRAN // 2 + 200, line_y), 2)

        # afficher les boutons
        for btn in boutons:
            btn.afficher(ecran)

        pygame.display.flip()
