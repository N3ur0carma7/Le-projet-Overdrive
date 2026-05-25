import threading

import pygame
import time
import random
import os
import multiplayer.client as client_module
from multiplayer.client import send_server, DISCONNECT_MESSAGE, CLIENT, disconnect
from core.Class.buttons import BoutonImage
from core.Class.player import Player
from core.saves import save_game
import screens.game_logic as gl

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

    import core.sounds as sounds

    music_on = sounds.is_music_enabled()

    BTN_SPACING = 100
    BTN_H = 70
    BTN_W = 300
    btn_y_start = HAUTEUR_ECRAN // 2 - 180
    panel_w = BTN_W + 60
    panel_h = 550
    panel_x = LARGEUR_ECRAN // 2 - panel_w // 2
    panel_y = HAUTEUR_ECRAN // 2 - 240

    def get_music_btn_images():
        return (btn_path("Musique_on", "normal"), btn_path("Musique_on", "hover")) if music_on else (btn_path("Musique_off", "normal"), btn_path("Musique_off", "hover"))

    musique_btn = BoutonImage(LARGEUR_ECRAN//2 - BTN_W//2, btn_y_start + 2 * BTN_SPACING, BTN_W, BTN_H,
                get_music_btn_images()[0], get_music_btn_images()[1])

    # boutons
    boutons = [
        BoutonImage(LARGEUR_ECRAN//2 - BTN_W//2, btn_y_start + 0 * BTN_SPACING, BTN_W, BTN_H,
                    btn_path("Menu_principal", "normal"), btn_path("Menu_principal", "hover")),
        BoutonImage(LARGEUR_ECRAN//2 - BTN_W//2, btn_y_start + 1 * BTN_SPACING, BTN_W, BTN_H,
                    btn_path("Sauvegarder", "normal"), btn_path("Sauvegarder", "hover")),
        BoutonImage(LARGEUR_ECRAN//2 - BTN_W//2, btn_y_start + 3 * BTN_SPACING, BTN_W, BTN_H,
                    btn_path("Quitter", "normal"), btn_path("Quitter", "hover"))
    ]
    music_btn_changed = False
    while en_pause:
        horloge.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # ESC ferme le menu pause
                return "jeu"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                from screens import game_logic
                game_logic.toggle_fullscreen()
                continue
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if boutons[0].clic():
                    if online_data and CLIENT is not None:

                        try:
                            if client_module.CLIENT is not None:
                                client_module.send_liste_joueurs_client(gl.players, client_module.CLIENT)
                        except Exception as e:
                            pass
                        disconnect()
                        gl.players = []
                        gl.batiments = []
                        gl.indice = 0
                    return "menu"
                if boutons[1].clic():
                    if not save_game(buildings, player, online_data):
                        print("ERREUR CRITIQUE: Ecriture du fichier save/save.json")
                        return False
                    print("Sauvegarde reussie, retour au jeu")
                    return "jeu_save_done"
                if musique_btn.clic():
                    if music_on:
                        sounds.set_music_enabled(False)
                    else:
                        sounds.set_music_enabled(True)
                        sounds.play_ambient(0)
                    music_on = not music_on
                    music_btn_changed = True
                if boutons[2].clic():
                    if online_data and CLIENT is not None:

                        try:
                            if client_module.CLIENT is not None:
                                client_module.send_liste_joueurs_client(gl.players, client_module.CLIENT)
                        except Exception as e:
                            pass
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
        musique_btn.afficher(ecran)

        if music_btn_changed:
            musique_btn = BoutonImage(LARGEUR_ECRAN//2 - BTN_W//2, btn_y_start + 2 * BTN_SPACING, BTN_W, BTN_H,
                        get_music_btn_images()[0], get_music_btn_images()[1])
            music_btn_changed = False

        pygame.display.flip()
