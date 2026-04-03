import pygame
import json
import os
from multiplayer.client import connection, CLIENT
from multiplayer.serveur import server_running, disconnect
from core.Class.buttons import BoutonImage
import threading
import time
import random

class Bouton:
    def __init__(self, texte, x, y, w, h):
        self.texte = texte
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.font = pygame.font.SysFont("Arial", 24)
        self.hover = False

    def clic(self):
        mx, my = pygame.mouse.get_pos()
        return self.x <= mx <= self.x + self.w and self.y <= my <= self.y + self.h

    def afficher(self, ecran):
        self.hover = self.clic()
        couleur = (180, 120, 40) if self.hover else (10, 5, 0)
        pygame.draw.rect(ecran, (130, 85, 30), (self.x, self.y, self.w, self.h), 2)
        pygame.draw.rect(ecran, couleur, (self.x, self.y, self.w, self.h))
        texte_surf = self.font.render(self.texte, True, (255, 255, 255))
        ecran.blit(texte_surf, (self.x + (self.w - texte_surf.get_width())//2, self.y + (self.h - texte_surf.get_height())//2))

def lancer_partie():
    serv = threading.Thread(target=server_running, daemon=True)
    serv.start()
    time.sleep(1)
    client = threading.Thread(target=connection, daemon=True)
    client.start()

def menu_principal(ecran, horloge, FPS):
    LARGEUR_ECRAN, HAUTEUR_ECRAN = ecran.get_size()
    en_cours = True
    etat_suivant = "menu"

    bg_path = os.path.join("assets", "background.png")
    if os.path.exists(bg_path):
        background_brut = pygame.image.load(bg_path).convert()
    else:
        background_brut = None

    font_path = os.path.join("assets", "fonts", "Minecraft.ttf")
    try:
        font_titre = pygame.font.Font(font_path, 90)
        font_sous_titre = pygame.font.Font(font_path, 22)
    except:
        font_titre = pygame.font.SysFont("Arial", 90, bold=True)
        font_sous_titre = pygame.font.SysFont("Arial", 22)

    BTN_W, BTN_H = 300, 70
    BTN_SPACING = 85

    def btn_path(name, state):
        return os.path.join("assets", "buttons", "menu", f"{name}_{state}.png")

    def creer_boutons():
        W, H = ecran.get_size()
        cx = W // 2 - BTN_W // 2
        start_y = H // 2 - 130
        return [
            BoutonImage(cx, start_y + 0 * BTN_SPACING, BTN_W, BTN_H,
                        btn_path("Commencer", "normal"), btn_path("Commencer", "hover")),
            BoutonImage(cx, start_y + 1 * BTN_SPACING, BTN_W, BTN_H,
                        btn_path("Continuer", "normal"), btn_path("Continuer", "hover")),
            BoutonImage(cx, start_y + 2 * BTN_SPACING, BTN_W, BTN_H,
                        btn_path("Rejoindre", "normal"), btn_path("Rejoindre", "hover")),

            BoutonImage(cx, start_y + 4 * BTN_SPACING, BTN_W, BTN_H,
                        btn_path("Quitter", "normal"), btn_path("Quitter", "hover")),
            # Bouton DEV discret en bas à gauche
            BoutonImage(10, ecran.get_height() - BTN_H // 2 - 10, BTN_W // 2, BTN_H // 2,
                        btn_path("DEV", "normal"), btn_path("DEV", "hover")),
        ]

    boutons = creer_boutons()

    particules = [
        {"x": random.randint(0, 1280), "y": random.randint(0, 720),
         "vy": -random.uniform(0.3, 1.0), "alpha": random.randint(30, 100),
         "r": random.randint(3, 12)}
        for _ in range(40)
    ]

    bg_cache_size = None
    bg_scaled = None
    overlay = None

    while en_cours:
        horloge.tick(FPS)
        W, H = ecran.get_size()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return etat_suivant, False
            if event.type == pygame.VIDEORESIZE:
                LARGEUR_ECRAN, HAUTEUR_ECRAN = event.w, event.h
                boutons = creer_boutons()
                overlay = None
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if boutons[0].clic():
                    if os.path.exists("save/save.json"):
                        from screens.menuEcraserSauvegarde import confirmation_ecraser
                        etat_confirmation = confirmation_ecraser(ecran, horloge, FPS)
                        if etat_confirmation is False:
                            return etat_suivant, False
                        elif etat_confirmation == "menu":
                            return etat_confirmation, True
                        elif etat_confirmation == "jeu":
                            lancer_partie()
                            return etat_confirmation, True
                    else:
                        lancer_partie()
                        return "jeu", True
                if boutons[1].clic():
                    if os.path.exists("save/save.json"):
                        lancer_partie()
                        return "jeu", True
                if boutons[2].clic():
                    threading.Thread(target=connection, daemon=True).start()
                    return "jeu", True

                if boutons[3].clic():
                    return etat_suivant, False
                if boutons[4].clic():
                    return "jeudev", True

        if background_brut is not None:
            if bg_cache_size != (W, H):
                bg_scaled = pygame.transform.smoothscale(background_brut, (W, H))
                bg_cache_size = (W, H)
            ecran.blit(bg_scaled, (0, 0))
        else:
            ecran.fill((20, 12, 5))

        if overlay is None or overlay.get_size() != (W, H):
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((10, 5, 0, 150))
        ecran.blit(overlay, (0, 0))

        for p in particules:
            p["y"] += p["vy"]
            p["alpha"] = max(0, p["alpha"] - 0.15)
            if p["y"] < -20 or p["alpha"] <= 0:
                p["x"] = random.randint(0, W)
                p["y"] = H + 10
                p["alpha"] = random.randint(30, 100)
                p["vy"] = -random.uniform(0.3, 1.0)
                p["r"] = random.randint(3, 12)
            surf_p = pygame.Surface((p["r"] * 2, p["r"] * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf_p, (180, 140, 80, int(p["alpha"])),
                               (p["r"], p["r"]), p["r"])
            ecran.blit(surf_p, (int(p["x"]) - p["r"], int(p["y"]) - p["r"]))
        # bulles
        BTN_TOTAL_H = BTN_H + BTN_SPACING * 4
        panel_w = BTN_W + 60
        panel_h = BTN_TOTAL_H + 60
        panel_x = W // 2 - panel_w // 2
        panel_y = H // 2 - 140
        panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel_surf.fill((10, 5, 0, 110))
        pygame.draw.rect(panel_surf, (130, 85, 30, 200), (0, 0, panel_w, panel_h), 2)
        corner_size = 8
        for cx2, cy2 in [(0, 0), (panel_w - corner_size, 0),
                         (0, panel_h - corner_size), (panel_w - corner_size, panel_h - corner_size)]:
            pygame.draw.rect(panel_surf, (180, 120, 40, 220),
                             (cx2, cy2, corner_size, corner_size))
        ecran.blit(panel_surf, (panel_x, panel_y))
        titre = font_titre.render("OVERDRIVE", True, (220, 160, 50))
        shadow = font_titre.render("OVERDRIVE", True, (50, 25, 5))
        tx = W // 2 - titre.get_width() // 2
        ty = panel_y - titre.get_height() - 28
        ecran.blit(shadow, (tx + 3, ty + 3))
        ecran.blit(titre, (tx, ty))

        line_y = ty + titre.get_height() + 6
        pygame.draw.line(ecran, (160, 100, 40),
                         (W // 2 - 200, line_y), (W // 2 + 200, line_y), 2)


        for btn in boutons:
            btn.afficher(ecran)

        ver_font = pygame.font.SysFont("Arial", 14)
        ver = ver_font.render("v1.0 - Overdrive", True, (80, 60, 30))
        ecran.blit(ver, (W - ver.get_width() - 10, H - 22))

        pygame.display.flip()
