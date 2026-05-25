
import pygame
import sys
from core.Class.batiments import Batiment
from core.Class.npc import Npc

C_BG          = (20,  16,  12)
C_PANEL       = (35,  28,  20)
C_BORDER      = (90,  70,  40)
C_HEADER      = (55,  42,  25)
C_CARD        = (45,  36,  22)
C_CARD_HOV    = (65,  52,  30)
C_CARD_SEL    = (100, 75,  30)
C_CARD_ASSIGN = (30,  55,  30)
C_CARD_FULL   = (55,  30,  30)
C_TEXT        = (220, 195, 140)
C_TEXT_DIM    = (130, 110,  70)
C_TEXT_GREEN  = (100, 200, 100)
C_TEXT_RED    = (220, 100,  80)
C_TEXT_GOLD   = (220, 170,  50)
C_BTN         = (70,  55,  25)
C_BTN_HOV     = (100, 78,  35)
C_BTN_AUTO    = (40,  55,  40)
C_BTN_AUTO_H  = (55,  80,  55)
C_SCROLL_BG   = (28,  22,  14)
C_SCROLL_THB  = (80,  62,  35)

ICONE_TYPE = {
    Batiment.TYPE_MINE:        "Mine Or",
    Batiment.TYPE_FARM:        "Farm Bouffe",
    Batiment.TYPE_GENERATEUR:  "Generateur Vapeur",
    Batiment.TYPE_RESIDENTIEL: "Maison",
    Batiment.TYPE_TOURELLE:    "Tourelle",
}


def _charger_police(taille):
    try:
        return pygame.font.Font("assets/fonts/Minecraft.ttf", taille)
    except Exception:
        return pygame.font.SysFont("monospace", taille)


def _rect_arrondi(surface, couleur, rect, rayon=6, bordure=0, coul_bordure=None):
    pygame.draw.rect(surface, couleur, rect, border_radius=rayon)
    if bordure and coul_bordure:
        pygame.draw.rect(surface, coul_bordure, rect, bordure, border_radius=rayon)


def _compter_assigned(npc_list, batiment):
    return sum(1 for n in npc_list if n.lieu_travail is batiment)


def afficher_menu_travail(ecran, batiments, npcs, player):

    horloge   = pygame.time.Clock()
    f_titre   = _charger_police(22)
    f_sous    = _charger_police(14)
    f_petit   = _charger_police(11)
    f_icone   = _charger_police(12)

    W, H = ecran.get_size()

    PW = min(900, W - 80)
    PH = min(620, H - 80)
    PX = (W - PW) // 2
    PY = (H - PH) // 2

    COL_W    = (PW - 60) // 2
    COL_L_X  = PX + 20
    COL_R_X  = PX + 40 + COL_W
    COL_Y    = PY + 90
    COL_H    = PH - 130

    CARD_H   = 68
    CARD_GAP = 8

    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))

    npc_selectionne = None
    scroll_g = 0
    scroll_d = 0

    en_cours = True
    while en_cours:
        horloge.tick(60)
        mx, my = pygame.mouse.get_pos()

        batiments_prod = [
            b for b in batiments
            if b.type not in (
                Batiment.TYPE_RESIDENTIEL,
                Batiment.TYPE_TOURELLE,
                Batiment.TYPE_TILE
            )
        ]

        hov_npc = None
        hov_bat = None

        ecran.blit(overlay, (0, 0))

        _rect_arrondi(
            ecran,
            C_PANEL,
            pygame.Rect(PX, PY, PW, PH),
            rayon=10,
            bordure=2,
            coul_bordure=C_BORDER
        )

        titre_surf = f_titre.render(
            "Assignation des Villageois",
            True,
            C_TEXT_GOLD
        )

        ecran.blit(
            titre_surf,
            (PX + (PW - titre_surf.get_width()) // 2, PY + 14)
        )

        sous_surf = f_petit.render(
            "Cliquer un villageois puis un batiment | TAB ou echap pour fermer",
            True,
            C_TEXT_DIM
        )

        ecran.blit(
            sous_surf,
            (PX + (PW - sous_surf.get_width()) // 2, PY + 42)
        )

        pygame.draw.line(
            ecran,
            C_BORDER,
            (PX + 16, PY + 64),
            (PX + PW - 16, PY + 64),
            1
        )

        pop_totale = len(npcs)
        nb_assignes = sum(
            1 for n in npcs
            if n.lieu_travail is not None
        )

        hdr_g = f_sous.render(
            f"Villageois ({nb_assignes}/{pop_totale} actifs)",
            True,
            C_TEXT
        )

        hdr_d = f_sous.render(
            f"Batiments de production ({len(batiments_prod)})",
            True,
            C_TEXT
        )

        _rect_arrondi(
            ecran,
            C_HEADER,
            pygame.Rect(COL_L_X, COL_Y - 28, COL_W, 24),
            rayon=4
        )

        _rect_arrondi(
            ecran,
            C_HEADER,
            pygame.Rect(COL_R_X, COL_Y - 28, COL_W, 24),
            rayon=4
        )

        ecran.blit(hdr_g, (COL_L_X + 8, COL_Y - 26))
        ecran.blit(hdr_d, (COL_R_X + 8, COL_Y - 26))

        clip_g = pygame.Rect(COL_L_X, COL_Y, COL_W, COL_H)
        clip_d = pygame.Rect(COL_R_X, COL_Y, COL_W, COL_H)

        ecran.set_clip(clip_g)

        for i, npc in enumerate(npcs):

            cy = COL_Y + i * (CARD_H + CARD_GAP) - scroll_g

            card_rect = pygame.Rect(
                COL_L_X,
                cy,
                COL_W,
                CARD_H
            )

            if cy + CARD_H < COL_Y or cy > COL_Y + COL_H:
                continue

            if card_rect.collidepoint(mx, my):
                hov_npc = i

            est_sel = (npc_selectionne is npc)
            est_hov = (hov_npc == i)

            coul = (
                C_CARD_SEL if est_sel
                else (C_CARD_HOV if est_hov else C_CARD)
            )

            _rect_arrondi(
                ecran,
                coul,
                card_rect,
                rayon=5,
                bordure=1 if est_sel else 0,
                coul_bordure=C_TEXT_GOLD
            )

            nom = f"Villageois #{i+1}"

            etat_txt, etat_col = {
                Npc.ETAT_ERRANCE:      ("errance", C_TEXT_DIM),
                Npc.ETAT_VERS_TRAVAIL: ("en route", C_TEXT),
                Npc.ETAT_AU_TRAVAIL:   ("au travail", C_TEXT_GREEN),
                Npc.ETAT_VERS_MAISON:  ("rentre", C_TEXT_DIM),
            }.get(npc.etat, ("?", C_TEXT_DIM))

            s_nom = f_sous.render(nom, True, C_TEXT)
            s_etat = f_petit.render(etat_txt, True, etat_col)

            ecran.blit(s_nom,  (COL_L_X + 12, cy + 10))
            ecran.blit(s_etat, (COL_L_X + 12, cy + 30))

            if npc.lieu_travail is not None:
                prod_nom = ICONE_TYPE.get(
                    npc.lieu_travail.type,
                    npc.lieu_travail.type
                )

                s_prod = f_petit.render(
                    f"Travail : {prod_nom}",
                    True,
                    C_TEXT_GOLD
                )

            else:
                s_prod = f_petit.render(
                    "Sans travail",
                    True,
                    C_TEXT_DIM
                )

            ecran.blit(s_prod, (COL_L_X + 12, cy + 48))

            if est_sel:
                pygame.draw.circle(
                    ecran,
                    C_TEXT_GOLD,
                    (COL_L_X + COL_W - 14, cy + CARD_H // 2),
                    5
                )

        ecran.set_clip(None)

        ecran.set_clip(clip_d)

        for j, bat in enumerate(batiments_prod):

            cy = COL_Y + j * (CARD_H + CARD_GAP) - scroll_d

            card_rect = pygame.Rect(
                COL_R_X,
                cy,
                COL_W,
                CARD_H
            )

            if cy + CARD_H < COL_Y or cy > COL_Y + COL_H:
                continue

            if card_rect.collidepoint(mx, my):
                hov_bat = j

            nb_ici = _compter_assigned(npcs, bat)
            est_hov = (hov_bat == j)

            if nb_ici == 0:
                coul = C_CARD_HOV if est_hov else C_CARD
            else:
                coul = C_CARD_ASSIGN

            _rect_arrondi(
                ecran,
                coul,
                card_rect,
                rayon=5,
                bordure=1 if est_hov and npc_selectionne else 0,
                coul_bordure=C_TEXT_GREEN
            )

            type_nom = ICONE_TYPE.get(bat.type, bat.type)
            prod_val = bat.get_production()

            s_nom = f_sous.render(
                f"{type_nom} niv.{bat.niveau}",
                True,
                C_TEXT
            )

            s_prod = f_petit.render(
                f"Production : {prod_val}/min",
                True,
                C_TEXT_GOLD
            )

            s_assign = f_petit.render(
                f"{nb_ici} villageois assignes",
                True,
                C_TEXT_GREEN if nb_ici > 0 else C_TEXT_DIM
            )

            ecran.blit(s_nom,    (COL_R_X + 12, cy + 8))
            ecran.blit(s_prod,   (COL_R_X + 12, cy + 28))
            ecran.blit(s_assign, (COL_R_X + 12, cy + 46))

            bar_x = COL_R_X + COL_W - 60
            bar_w = 44
            bar_h = 8
            bar_y = cy + CARD_H // 2 - bar_h // 2

            pygame.draw.rect(
                ecran,
                C_SCROLL_BG,
                (bar_x, bar_y, bar_w, bar_h),
                border_radius=4
            )

            max_workers = max(1, len(npcs))
            fill = int(bar_w * nb_ici / max_workers)

            if fill > 0:
                pygame.draw.rect(
                    ecran,
                    C_TEXT_GREEN,
                    (bar_x, bar_y, fill, bar_h),
                    border_radius=4
                )

        ecran.set_clip(None)

        BTN_W, BTN_H = 130, 36
        BTN_Y = PY + PH - 52

        btn_auto_rect = pygame.Rect(
            PX + 20,
            BTN_Y,
            BTN_W,
            BTN_H
        )

        hov_auto = btn_auto_rect.collidepoint(mx, my)

        _rect_arrondi(
            ecran,
            C_BTN_AUTO_H if hov_auto else C_BTN_AUTO,
            btn_auto_rect,
            rayon=5,
            bordure=1,
            coul_bordure=C_BORDER
        )

        s_auto = f_sous.render(
            "Auto assigner",
            True,
            C_TEXT
        )

        ecran.blit(
            s_auto,
            (
                btn_auto_rect.centerx - s_auto.get_width() // 2,
                btn_auto_rect.centery - s_auto.get_height() // 2
            )
        )

        btn_clear_rect = pygame.Rect(
            PX + 165,
            BTN_Y,
            BTN_W + 10,
            BTN_H
        )

        hov_clear = btn_clear_rect.collidepoint(mx, my)

        _rect_arrondi(
            ecran,
            C_CARD_FULL if hov_clear else (40, 30, 20),
            btn_clear_rect,
            rayon=5,
            bordure=1,
            coul_bordure=C_BORDER
        )

        s_clear = f_sous.render(
            "Vider tout",
            True,
            C_TEXT
        )

        ecran.blit(
            s_clear,
            (
                btn_clear_rect.centerx - s_clear.get_width() // 2,
                btn_clear_rect.centery - s_clear.get_height() // 2
            )
        )

        btn_fermer_rect = pygame.Rect(
            PX + PW - BTN_W - 20,
            BTN_Y,
            BTN_W,
            BTN_H
        )

        hov_fermer = btn_fermer_rect.collidepoint(mx, my)

        _rect_arrondi(
            ecran,
            C_BTN_HOV if hov_fermer else C_BTN,
            btn_fermer_rect,
            rayon=5,
            bordure=1,
            coul_bordure=C_BORDER
        )

        s_fermer = f_sous.render(
            "Fermer [TAB]",
            True,
            C_TEXT
        )

        ecran.blit(
            s_fermer,
            (
                btn_fermer_rect.centerx - s_fermer.get_width() // 2,
                btn_fermer_rect.centery - s_fermer.get_height() // 2
            )
        )

        if npc_selectionne is not None:

            idx = npcs.index(npc_selectionne)

            leg = f_sous.render(
                f"Villageois #{idx+1} selectionne",
                True,
                C_TEXT_GOLD
            )

            ecran.blit(
                leg,
                (PX + (PW - leg.get_width()) // 2, BTN_Y - 22)
            )

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                if event.key in (
                    pygame.K_ESCAPE,
                    pygame.K_TAB
                ):
                    en_cours = False
                if event.key == pygame.K_F11:
                    from screens import game_logic
                    game_logic.toggle_fullscreen()
            if event.type == pygame.MOUSEWHEEL:
                if clip_g.collidepoint(mx, my):
                    total_g = len(npcs) * (CARD_H + CARD_GAP)
                    scroll_g = max(
                        0,
                        min(
                            scroll_g - event.y * 20,
                            max(0, total_g - COL_H)
                        )
                    )
                elif clip_d.collidepoint(mx, my):

                    total_d = len(batiments_prod) * (CARD_H + CARD_GAP)

                    scroll_d = max(
                        0,
                        min(
                            scroll_d - event.y * 20,
                            max(0, total_d - COL_H)
                        )
                    )
            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):
                if btn_fermer_rect.collidepoint(mx, my):
                    en_cours = False
                elif btn_auto_rect.collidepoint(mx, my):
                    from screens.game_logic import effacer_toutes_assignations
                    effacer_toutes_assignations()
                    _auto_assigner(batiments, npcs)
                    npc_selectionne = None
                elif btn_clear_rect.collidepoint(mx, my):
                    from screens.game_logic import effacer_toutes_assignations
                    effacer_toutes_assignations()
                    for n in npcs:
                        n.assigner_travail(None)
                    npc_selectionne = None
                elif clip_g.collidepoint(mx, my):
                    for i, npc in enumerate(npcs):
                        cy = COL_Y + i * (CARD_H + CARD_GAP) - scroll_g

                        card_rect = pygame.Rect(
                            COL_L_X,
                            cy,
                            COL_W,
                            CARD_H
                        )
                        if card_rect.collidepoint(mx, my):
                            npc_selectionne = (
                                None if npc_selectionne is npc else npc
                            )
                            break
                elif (
                    clip_d.collidepoint(mx, my)
                    and npc_selectionne is not None
                ):
                    for j, bat in enumerate(batiments_prod):
                        cy = COL_Y + j * (CARD_H + CARD_GAP) - scroll_d
                        card_rect = pygame.Rect(
                            COL_R_X,
                            cy,
                            COL_W,
                            CARD_H
                        )
                        if card_rect.collidepoint(mx, my):
                            from screens.game_logic import marquer_assignation_manuelle
                            npc_selectionne.assigner_travail(bat)
                            marquer_assignation_manuelle(npc_selectionne, bat)
                            npc_selectionne = None
                            break
    return "fermer"

def _auto_assigner(batiments, npcs):
    lieux = [
        b for b in batiments
        if b.type not in (
            Batiment.TYPE_RESIDENTIEL,
            Batiment.TYPE_TOURELLE,
            Batiment.TYPE_TILE
        )
    ]

    for i, npc in enumerate(npcs):

        if lieux:
            npc.assigner_travail(lieux[i % len(lieux)])
        else:
            npc.assigner_travail(None)
