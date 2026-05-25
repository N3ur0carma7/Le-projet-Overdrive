import pygame
import math
import sys
from core.Class.batiments import Batiment
import core.sounds as sound


CUIVRE          = (184, 115,  51)
CUIVRE_CLAIR    = (220, 155,  80)
CUIVRE_SOMBRE   = (120,  70,  20)
LAITON          = (205, 170,  65)
LAITON_CLAIR    = (240, 210, 100)
CHARBON         = ( 28,  22,  16)
CHARBON_CLAIR   = ( 50,  38,  26)
FUMEE           = ( 90,  80,  70)
FUMEE_CLAIR     = (130, 115, 100)
ROUGE_DANGER    = (180,  40,  30)
ROUGE_HOVER     = (220,  70,  50)
VERT_OK         = ( 60, 160,  80)
VERT_HOVER      = ( 90, 200, 110)
BLANC           = (255, 255, 255)
OR              = (255, 200,  50)

TYPE_LABELS = {
    Batiment.TYPE_RESIDENTIEL: "LOGEMENT",
    Batiment.TYPE_GENERATEUR:  "GENERATEUR",
    Batiment.TYPE_MINE:        "MINE",
    Batiment.TYPE_FARM:        "FERME",
    Batiment.TYPE_TOURELLE:    "TOURELLE",
    Batiment.TYPE_CENTRALE_VAPEUR: "FOURNAISE",
    Batiment.TYPE_CENTRALE_ARGENT: "COMPTOIR",
    Batiment.TYPE_CENTRALE_NOURRITURE: "CUISINE",
    Batiment.TYPE_STOCKAGE_NOURRITURE: "STOCKAGE NOURRITURE",
    Batiment.TYPE_STOCKAGE_ARGENT: "STOCKAGE ARGENT",
    Batiment.TYPE_STOCKAGE_VAPEUR: "STOCKAGE VAPEUR"
}

RESOURCE_LABELS = {
    Batiment.TYPE_RESIDENTIEL: ("Population", ""),
    Batiment.TYPE_GENERATEUR:  ("Vapeur",     "/min"),
    Batiment.TYPE_MINE:        ("Argent",     "/min"),
    Batiment.TYPE_FARM:        ("Nourriture", "/min"),
    Batiment.TYPE_TOURELLE:    ("Degats",     ""),
    Batiment.TYPE_CENTRALE_VAPEUR: ("Boost", "%"),
    Batiment.TYPE_CENTRALE_ARGENT: ("Boost", "%"),
    Batiment.TYPE_CENTRALE_NOURRITURE: ("Boost", "%"),
    Batiment.TYPE_STOCKAGE_ARGENT: ("Stockage", " argent"),
    Batiment.TYPE_STOCKAGE_NOURRITURE: ("Stockage", " nourriture"),
    Batiment.TYPE_STOCKAGE_VAPEUR: ("Stockage", " vapeur"),
}


def draw_rounded_rect(surface, color, rect, radius=8, width=0):
    pygame.draw.rect(surface, color, rect, width, border_radius=radius)


def draw_panel_border(surface, rect, color_outer, color_inner, radius=8):
    outer = rect
    inner = pygame.Rect(rect.x + 3, rect.y + 3, rect.w - 6, rect.h - 6)
    draw_rounded_rect(surface, color_outer, outer, radius, 2)
    draw_rounded_rect(surface, color_inner, inner, max(1, radius - 2), 1)


def draw_rivet(surface, cx, cy, r=5):
    pygame.draw.circle(surface, CUIVRE_SOMBRE, (cx, cy), r)
    pygame.draw.circle(surface, CUIVRE_CLAIR,  (cx - 1, cy - 1), r - 2)
    pygame.draw.circle(surface, CUIVRE_SOMBRE, (cx, cy), r, 1)


def draw_gear(surface, cx, cy, r_outer, r_inner, n_teeth, color, angle_offset=0):
    pts_outer = []
    pts_inner = []
    for i in range(n_teeth * 2):
        angle = math.radians(angle_offset + i * 180 / n_teeth)
        r = r_outer if i % 2 == 0 else r_inner
        pts_outer.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    if len(pts_outer) >= 3:
        pygame.draw.polygon(surface, color, pts_outer)
    pygame.draw.circle(surface, CHARBON_CLAIR, (cx, cy), r_inner // 2)
    pygame.draw.circle(surface, color, (cx, cy), r_inner // 2, 1)


def draw_pipe_horizontal(surface, x, y, w, h, color_body, color_highlight):
    body = pygame.Rect(x, y, w, h)
    draw_rounded_rect(surface, color_body, body, h // 2)
    highlight = pygame.Rect(x + 4, y + 2, w - 8, max(2, h // 4))
    draw_rounded_rect(surface, color_highlight, highlight, h // 4)


def draw_level_pips(surface, x, y, current_level, max_level=3, pip_w=22, pip_h=12, gap=5):
    for i in range(max_level):
        px = x + i * (pip_w + gap)
        rect = pygame.Rect(px, y, pip_w, pip_h)
        if i < current_level:
            draw_rounded_rect(surface, LAITON, rect, 3)
            draw_rounded_rect(surface, LAITON_CLAIR, pygame.Rect(px + 2, y + 2, pip_w - 4, 3), 2)
        else:
            draw_rounded_rect(surface, FUMEE, rect, 3)
        draw_rounded_rect(surface, CUIVRE_SOMBRE, rect, 3, 1)


def draw_stat_block(surface, font_title, font_val, label, value, unite, x, y, w, h, accent):
    rect = pygame.Rect(x, y, w, h)
    draw_rounded_rect(surface, CHARBON_CLAIR, rect, 6)
    draw_panel_border(surface, rect, CUIVRE_SOMBRE, FUMEE, 6)

    title_surf = font_title.render(label, True, FUMEE_CLAIR)
    surface.blit(title_surf, (x + w // 2 - title_surf.get_width() // 2, y + 6))

    val_text = f"{value}{unite}"
    val_surf = font_val.render(val_text, True, accent)
    surface.blit(val_surf, (x + w // 2 - val_surf.get_width() // 2, y + 26))


def draw_arrow(surface, x, cy, color):
    pts = [
        (x,      cy - 8),
        (x + 14, cy),
        (x,      cy + 8),
        (x + 4,  cy),
        (x - 10, cy),
        (x - 6,  cy),
    ]
    pygame.draw.polygon(surface, color, [(p[0], p[1]) for p in pts])


class BoutonBlit:
    def __init__(self, x, y, w, h, label, color_base, color_hover, color_text=CHARBON, enabled=True):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.color_base = color_base
        self.color_hover = color_hover
        self.color_text = color_text
        self.enabled = enabled

    def afficher(self, surface, font):
        souris = pygame.mouse.get_pos()
        hovered = self.rect.collidepoint(souris) and self.enabled

        color = self.color_hover if hovered else self.color_base
        if not self.enabled:
            color = FUMEE

        draw_rounded_rect(surface, color, self.rect, 6)

        # relief sur le bord
        top_rect = pygame.Rect(self.rect.x + 2, self.rect.y + 2,
                               self.rect.w - 4, 3)
        draw_rounded_rect(surface, (*BLANC, 60) if hovered else (*BLANC, 30),
                          top_rect, 3)
        draw_rounded_rect(surface, self.color_base if hovered else CHARBON,
                          self.rect, 6, 2)

        txt = font.render(self.label, True,
                          self.color_text if self.enabled else FUMEE_CLAIR)
        surface.blit(txt, (self.rect.centerx - txt.get_width() // 2,
                           self.rect.centery - txt.get_height() // 2))

    def clic(self):
        return self.enabled and self.rect.collidepoint(pygame.mouse.get_pos())


class MenuAmelioration:
    PANEL_W = 440
    PANEL_H = 280

    def __init__(self, ecran, batiment, clic_x, player):
        self.ecran = ecran
        self.batiment = batiment
        self.player = player
        self.clic_x = clic_x
        self._t = 0

        # Polices
        self.font_title  = pygame.font.Font("assets/fonts/Minecraft.ttf", 18)
        self.font_label  = pygame.font.Font("assets/fonts/Minecraft.ttf", 12)
        self.font_val    = pygame.font.Font("assets/fonts/Minecraft.ttf", 20)
        self.font_cost   = pygame.font.Font("assets/fonts/Minecraft.ttf", 14)
        self.font_btn    = pygame.font.Font("assets/fonts/Minecraft.ttf", 13)

        # Position du panneau (centre ecran)
        sw, sh = ecran.get_size()
        self.px = sw // 2 - self.PANEL_W // 2
        self.py = sh // 2 - self.PANEL_H // 2

        self._build_buttons()

    def _get_stat_info(self):
        bt = self.batiment
        label, unite = RESOURCE_LABELS.get(bt.type, ("Production", ""))

        has_next_data = (bt.niveau + 1) in Batiment.DATA[bt.type]

        if bt.type == Batiment.TYPE_RESIDENTIEL:
            val_actuelle = bt.get_population()
            val_suivante = (str(Batiment.DATA[bt.type][bt.niveau + 1]["population"])
                            if has_next_data else "MAX")
        elif bt.type == Batiment.TYPE_TOURELLE:
            val_actuelle = bt.get_stats().get("degat", 30)
            val_suivante = (str(Batiment.DATA[bt.type][bt.niveau + 1]["degat"])
                            if has_next_data else "MAX")
        elif bt.type == Batiment.TYPE_STOCKAGE_ARGENT:
            val_actuelle = bt.get_stockage()
            val_suivante = (str(Batiment.DATA[bt.type][bt.niveau + 1]["stockage"])
                            if has_next_data else "MAX")
        elif bt.type == Batiment.TYPE_STOCKAGE_VAPEUR:
            val_actuelle = bt.get_stockage()
            val_suivante = (str(Batiment.DATA[bt.type][bt.niveau + 1]["stockage"])
                            if has_next_data else "MAX")
        elif bt.type == Batiment.TYPE_STOCKAGE_NOURRITURE:
            val_actuelle = bt.get_stockage()
            val_suivante = (str(Batiment.DATA[bt.type][bt.niveau + 1]["stockage"])
                            if has_next_data else "MAX")
        elif bt.type == Batiment.TYPE_CENTRALE_VAPEUR:
            val_actuelle = int(bt.get_production() * 100)
            val_suivante = (str(int(Batiment.DATA[bt.type][bt.niveau + 1]["boost"] * 100))
                            if has_next_data else "MAX")
        elif bt.type == Batiment.TYPE_CENTRALE_ARGENT:
            val_actuelle = int(bt.get_production() * 100)
            val_suivante = (str(int(Batiment.DATA[bt.type][bt.niveau + 1]["boost"] * 100))
                            if has_next_data else "MAX")
        elif bt.type == Batiment.TYPE_CENTRALE_NOURRITURE:
            val_actuelle = int(bt.get_production() * 100)
            val_suivante = (str(int(Batiment.DATA[bt.type][bt.niveau + 1]["boost"] * 100))
                            if has_next_data else "MAX")
        else:
            val_actuelle = bt.get_production()
            prod_key = {"Generateur": "vapeur", "Mine": "argent", "Ferme": "nourriture"}.get(bt.type, "production")
            val_suivante = (str(Batiment.DATA[bt.type][bt.niveau + 1].get(prod_key, "?"))
                            if has_next_data else "MAX")

        return label, str(val_actuelle), val_suivante, unite

    def _can_upgrade(self):
        bt = self.batiment
        cost = bt.get_upgrade_cost()
        max_debloque = Batiment.DATA[bt.type].get("max_level", 1)
        return (
            bt.construction_finie()
            and not bt.est_max_level()
            and bt.niveau < max_debloque
            and cost is not None
            and self.player.money >= cost
        )

    def _build_buttons(self):
        px, py = self.px, self.py
        W, H = self.PANEL_W, self.PANEL_H

        if self.batiment.type == Batiment.TYPE_TILE:
            self.btn_ameliorer = None
        else:
            can = self._can_upgrade()
            self.btn_ameliorer = BoutonBlit(
                px + 30, py + H - 54, 200, 44,
                "AMELIORER",
                VERT_OK if can else FUMEE,
                VERT_HOVER if can else FUMEE,
                CHARBON,
                enabled=can
            )
        if self.batiment.type == Batiment.TYPE_TILE:
            self.btn_sell = BoutonBlit(
                px + W // 2 - 60, py + H - 54, 120, 44,
                "VENDRE",
                ROUGE_DANGER, ROUGE_HOVER, CHARBON
            )
        else:
            self.btn_sell = BoutonBlit(
                px + W - 150, py + H - 54, 120, 44,
                "VENDRE",
                ROUGE_DANGER, ROUGE_HOVER, CHARBON
            )

        self.btn_fermer = BoutonBlit(
            px + W - 38, py + 10, 28, 28,
            "X",
            CUIVRE_SOMBRE, ROUGE_DANGER, CHARBON
        )

    def draw(self, ecran):
        self._build_buttons()

        px, py = self.px, self.py
        W, H = self.PANEL_W, self.PANEL_H

        panel = pygame.Rect(px, py, W, H)

        draw_rounded_rect(ecran, (24,22,18), panel, 18)
        draw_rounded_rect(ecran, CUIVRE, panel, 18, 3)

        inner = pygame.Rect(px+8, py+8, W-16, H-16)
        draw_rounded_rect(ecran, CHARBON_CLAIR, inner, 14)

        type_label = TYPE_LABELS.get(
            self.batiment.type,
            self.batiment.type.upper()
        )

        titre = self.font_title.render(type_label, True, LAITON_CLAIR)

        ecran.blit(
            titre,
            (
                px + W//2 - titre.get_width()//2,
                py + 20
            )
        )

        level_y = py + 58
        spacing = 34

        for i in range(3):

            cx = px + W//2 - spacing + i*spacing

            color = LAITON if i < self.batiment.niveau else FUMEE

            pygame.draw.circle(
                ecran,
                color,
                (cx, level_y),
                10
            )

            pygame.draw.circle(
                ecran,
                CUIVRE_SOMBRE,
                (cx, level_y),
                10,
                2
            )

        label,val_act,val_suiv,unite = self._get_stat_info()

        card = pygame.Rect(
            px+28,
            py+90,
            W-56,
            95
        )

        draw_rounded_rect(
            ecran,
            (40,32,24),
            card,
            12
        )

        pygame.draw.line(
            ecran,
            CUIVRE,
            (card.centerx, card.y+15),
            (card.centerx, card.bottom-15),
            2
        )

        actuel = self.font_label.render(
            "ACTUEL",
            True,
            FUMEE_CLAIR
        )

        ecran.blit(
            actuel,
            (
                card.x+70,
                card.y+10
            )
        )

        valeur = self.font_val.render(
            f"{val_act}{unite}",
            True,
            CUIVRE_CLAIR
        )

        ecran.blit(
            valeur,
            (
                card.x+40,
                card.y+42
            )
        )

        suivant = self.font_label.render(
            "SUIVANT",
            True,
            FUMEE_CLAIR
        )

        ecran.blit(
            suivant,
            (
                card.centerx+55,
                card.y+10
            )
        )

        next_color = VERT_OK if val_suiv != "MAX" else FUMEE_CLAIR

        valeur2 = self.font_val.render(
            f"{val_suiv}{unite if val_suiv!='MAX' else ''}",
            True,
            next_color
        )

        ecran.blit(
            valeur2,
            (
                card.centerx+25,
                card.y+42
            )
        )

        txt = self.font_label.render(
            label.upper(),
            True,
            LAITON
        )

        ecran.blit(
            txt,
            (
                px+W//2-txt.get_width()//2,
                card.bottom+10
            )
        )

        cost = self.batiment.get_upgrade_cost()

        max_debloque = Batiment.DATA[
            self.batiment.type
        ].get("max_level",1)

        if not self.batiment.construction_finie():
            cout = "EN CONSTRUCTION"
            color = FUMEE_CLAIR

        elif self.batiment.niveau >= max_debloque:
            cout = "Upgrade non debloque"
            color = ROUGE_DANGER

        elif self.batiment.niveau >= 3:
            cout = "NIVEAU MAXIMUM"
            color = FUMEE_CLAIR

        else:

            cout = f"{cost} OR"

            color = (
                OR
                if self.player.money >= cost
                else ROUGE_DANGER
            )

        surf = self.font_cost.render(
            cout,
            True,
            color
        )

        ecran.blit(
            surf,
            (
                px+W//2-surf.get_width()//2,
                py+205
            )
        )

        if self.btn_ameliorer:
            self.btn_ameliorer.afficher(
                ecran,
                self.font_btn
            )

        self.btn_sell.afficher(
            ecran,
            self.font_btn
        )

        self.btn_fermer.afficher(
            ecran,
            self.font_btn
        )

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                from screens import game_logic
                game_logic.toggle_fullscreen()
                return None
            if event.key == pygame.K_ESCAPE:
                return "close"

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._build_buttons()

            if self.btn_fermer.clic():
                return "close"

            if self.btn_ameliorer is not None and self.btn_ameliorer.clic():
                cost = self.batiment.get_upgrade_cost()
                max_debloque = Batiment.DATA[self.batiment.type].get("max_level", 1)
                if (self.batiment.construction_finie()
                        and not self.batiment.est_max_level()
                        and self.batiment.niveau < max_debloque
                        and cost is not None
                        and self.player.money >= cost):
                    sound.son_upgrade.play()
                    self.player.money -= cost
                    self.batiment.upgrade()
                    return "upgrade"
                return "close"

            if self.btn_sell.clic():
                return "supprimer"

        return None