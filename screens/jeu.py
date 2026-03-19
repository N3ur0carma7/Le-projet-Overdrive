import pygame
import math
import os

from core.Class.player import Player
from core.Class.batiments import Batiment
from core.Class.npc import Npc
from core.saves import load_save
from screens.GUI.menu_amelioration import afficher_menu_amelioration
import core.sounds as sound


def boucle_jeu(ecran, horloge, FPS):
    HAUTEUR_BARRE = 100
    LARGEUR_ECRAN, HAUTEUR_ECRAN = ecran.get_size()
    dims = [LARGEUR_ECRAN, HAUTEUR_ECRAN]  # mutable pour mise a jour au resize



    herbe = pygame.image.load("assets/grass.png").convert()
    TAILLE_CASE = herbe.get_width()

    images_batiments = {
        Batiment.TYPE_RESIDENTIEL: {
            1: pygame.image.load("assets/buildings/house_lvl1.png").convert_alpha(),
            2: pygame.image.load("assets/buildings/house_lvl2.png").convert_alpha(),
            3: pygame.image.load("assets/buildings/house_lvl3.png").convert_alpha()
        },
        Batiment.TYPE_MINE: {
            1: pygame.image.load("assets/buildings/mine_lvl1.png").convert_alpha(),
            2: pygame.image.load("assets/buildings/mine_lvl2.png").convert_alpha(),
            3: pygame.image.load("assets/buildings/mine_lvl3.png").convert_alpha()
        }
    }

    TYPES_BATIMENTS = [
        Batiment.TYPE_RESIDENTIEL,
        Batiment.TYPE_MINE
    ]

    TAILLE_ICONE = 64

    player = Player()
    batiments = []
    npcs = []

    image_pnj = pygame.image.load("assets/pnj.png").convert_alpha()
    image_argent_raw = pygame.image.load("assets/argent.png").convert_alpha()
    HAUTEUR_ARGENT = 32
    _aw, _ah = image_argent_raw.get_size()
    image_argent = pygame.transform.smoothscale(image_argent_raw, (int(_aw * HAUTEUR_ARGENT / _ah), HAUTEUR_ARGENT))
    font_argent = pygame.font.Font("assets/fonts/Minecraft.ttf", 20)

    def synchroniser_npcs():
        """Synchronise les PNJ selon la population sans reinitialiser les PNJ existants."""
        population_attendue = {}
        for b in batiments:
            if b.type == Batiment.TYPE_RESIDENTIEL:
                population_attendue[id(b)] = b.get_population()

        npcs_par_maison = {}
        for npc in list(npcs):
            cle = id(npc.maison)
            if cle not in npcs_par_maison:
                npcs_par_maison[cle] = []
            npcs_par_maison[cle].append(npc)

        maisons_valides = {id(b) for b in batiments if b.type == Batiment.TYPE_RESIDENTIEL}
        for npc in list(npcs):
            if id(npc.maison) not in maisons_valides:
                npcs.remove(npc)

        for b in batiments:
            if b.type != Batiment.TYPE_RESIDENTIEL:
                continue
            cle = id(b)
            actuels = npcs_par_maison.get(cle, [])
            attendus = population_attendue.get(cle, 0)

            while len(actuels) < attendus:
                npc = Npc(b)
                npc.TAILLE_CASE = TAILLE_CASE
                npcs.append(npc)
                actuels.append(npc)

            while len(actuels) > attendus:
                npc = actuels.pop()
                if npc in npcs:
                    npcs.remove(npc)

        lieux_travail = [b for b in batiments if b.type != Batiment.TYPE_RESIDENTIEL]
        for i, npc in enumerate(npcs):
            if lieux_travail:
                npc.assigner_travail(lieux_travail[i % len(lieux_travail)])
            else:
                npc.assigner_travail(None)

    if os.path.exists("save/save.json"):
        if not load_save(batiments, player):
            print("ERREUR CRITIQUE: Lecture du fichier save/save.json")
            return False

    synchroniser_npcs()

    batiment_selectionne = None

    def collision(batiments, nouveau):
        for b in batiments:
            if b.collision(nouveau):
                return True
        return False

    camera_x, camera_y = 0.0, 0.0
    zoom = 1.0

    ZOOM_MIN = 0.5
    ZOOM_MAX = 3.0
    VITESSE_ZOOM = 0.1

    deplacement_camera = False
    derniere_souris = (0, 0)

    def calculer_rects_icones():
        rects = []
        marge = 20
        for i in range(len(images_batiments)):
            rect = pygame.Rect(
                marge + i * (TAILLE_ICONE + marge),
                dims[1] - HAUTEUR_BARRE + (HAUTEUR_BARRE - TAILLE_ICONE) // 2,
                TAILLE_ICONE,
                TAILLE_ICONE
            )
            rects.append(rect)
        return rects

    rects_icones = calculer_rects_icones()

    def dessiner_grille(surface):
        lw, lh = dims[0], dims[1]
        largeur_vue = lw / zoom
        hauteur_vue = (lh - HAUTEUR_BARRE) / zoom

        debut_x = int(camera_x // TAILLE_CASE) * TAILLE_CASE
        debut_y = int(camera_y // TAILLE_CASE) * TAILLE_CASE

        couleur_grille = (20, 80, 20)
        epaisseur = 2


        for y in range(debut_y, debut_y + int(hauteur_vue) + TAILLE_CASE, TAILLE_CASE):
            for x in range(debut_x, debut_x + int(largeur_vue) + TAILLE_CASE, TAILLE_CASE):
                # 1. On dessine l'image de l'herbe
                surface.blit(herbe, (x - camera_x, y - camera_y))
                rect_case = (x - camera_x, y - camera_y, TAILLE_CASE, TAILLE_CASE)
                pygame.draw.rect(surface, couleur_grille, rect_case, epaisseur)

                # 2. On dessine le contour de la case par-dessus
                rect_case = (x - camera_x, y - camera_y, TAILLE_CASE, TAILLE_CASE)
                pygame.draw.rect(surface, couleur_grille, rect_case, epaisseur)

    en_cours = True
    production_acc = 0.0  # accumulateur production en coins

    while en_cours:
        dt = horloge.tick(FPS) / 1000.0  # secondes ecoulees

        # Production des batiments
        for b in batiments:
            production_acc += b.get_production() * dt / 60.0
        gains = int(production_acc)
        if gains > 0:
            player.money += gains
            production_acc -= gains

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.VIDEORESIZE:
                dims[0], dims[1] = event.w, event.h
                rects_icones[:] = calculer_rects_icones()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "menu"

            if event.type == pygame.MOUSEWHEEL:
                ancien_zoom = zoom
                zoom += event.y * VITESSE_ZOOM
                zoom = max(ZOOM_MIN, min(ZOOM_MAX, zoom))

                centre_x = camera_x + dims[0] / (2 * ancien_zoom)
                centre_y = camera_y + dims[1] / (2 * ancien_zoom)

                camera_x = centre_x - dims[0] / (2 * zoom)
                camera_y = centre_y - dims[1] / (2 * zoom)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
                deplacement_camera = True
                derniere_souris = pygame.mouse.get_pos()

            if event.type == pygame.MOUSEBUTTONUP and event.button == 2:
                deplacement_camera = False

            if event.type == pygame.MOUSEMOTION and deplacement_camera:
                sx, sy = pygame.mouse.get_pos()
                dx = sx - derniere_souris[0]
                dy = sy - derniere_souris[1]
                camera_x -= dx / zoom
                camera_y -= dy / zoom
                derniere_souris = (sx, sy)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                batiment_selectionne = None

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                sx, sy = pygame.mouse.get_pos()

                clic_barre = False
                for i, rect in enumerate(rects_icones):
                    if rect.collidepoint(sx, sy):
                        batiment_selectionne = None if batiment_selectionne == i else i
                        clic_barre = True
                        break

                if not clic_barre and sy < dims[1] - HAUTEUR_BARRE:

                    mx = camera_x + sx / zoom
                    my = camera_y + sy / zoom

                    if batiment_selectionne is not None:
                        type_batiment = TYPES_BATIMENTS[batiment_selectionne]
                        image_ref = images_batiments[type_batiment][1]


                        grid_x = int(mx // TAILLE_CASE) * TAILLE_CASE
                        grid_y = int(my // TAILLE_CASE) * TAILLE_CASE

                        nouveau = Batiment(type_batiment, grid_x, grid_y)

                        cout = Batiment.DATA[type_batiment][1]["cout"]
                        if not collision(batiments, nouveau) and player.money >= cout:
                            player.money -= cout
                            batiments.append(nouveau)
                            sound.son_placement.play()
                            synchroniser_npcs()


                    elif batiment_selectionne is None:
                        for b in batiments:
                            if b.get_rect().collidepoint(mx, my):
                                afficher_menu_amelioration(ecran, b, sx, player)
                                synchroniser_npcs()
                                break


        ecran.fill((0, 0, 0))

        largeur_vue = dims[0] / zoom
        hauteur_vue = (dims[1] - HAUTEUR_BARRE) / zoom

        surface_monde = pygame.Surface(
            (math.ceil(largeur_vue), math.ceil(hauteur_vue))
        ).convert()

        dessiner_grille(surface_monde)


        for b in batiments:
            image_a_dessiner = images_batiments[b.type][b.niveau]

            offset_x = (TAILLE_CASE - image_a_dessiner.get_width()) // 2
            offset_y = (TAILLE_CASE - image_a_dessiner.get_height()) // 2

            x = b.x - camera_x + offset_x
            y = b.y - camera_y + offset_y

            surface_monde.blit(image_a_dessiner, (x, y))


        if batiment_selectionne is not None:
            sx, sy = pygame.mouse.get_pos()

            mx = camera_x + sx / zoom
            my = camera_y + sy / zoom

            type_batiment = TYPES_BATIMENTS[batiment_selectionne]
            image = images_batiments[type_batiment][1]

            grid_x = int(mx // TAILLE_CASE) * TAILLE_CASE
            grid_y = int(my // TAILLE_CASE) * TAILLE_CASE


            test_batiment = Batiment(type_batiment, grid_x, grid_y)

            image_fantome = image.copy()
            image_fantome.set_alpha(128)

            if collision(batiments, test_batiment):
                image_fantome.fill((255, 0, 0, 120), special_flags=pygame.BLEND_RGBA_MULT)

            offset_x = (TAILLE_CASE - image_fantome.get_width()) // 2
            offset_y = (TAILLE_CASE - image_fantome.get_height()) // 2


            surface_monde.blit(
                image_fantome,
                (grid_x - camera_x + offset_x, grid_y - camera_y + offset_y)
            )

        surface_affichee = pygame.transform.smoothscale(
            surface_monde,
            (dims[0], dims[1] - HAUTEUR_BARRE)
        )

        ecran.blit(surface_affichee, (0, 0))

        # PNJ : mise a jour + dessin directement sur l'ecran (taille fixe, pas zoomee)
        for npc in npcs:
            npc.update()
            ex, ey = npc.ecran_pos(camera_x, camera_y, zoom)
            if -40 < ex < dims[0] + 40 and -40 < ey < dims[1] - HAUTEUR_BARRE + 40:
                npc.dessiner(ecran, image_pnj, camera_x, camera_y, zoom)

        pygame.draw.rect(
            ecran,
            (40, 40, 40),
            (0, dims[1] - HAUTEUR_BARRE, dims[0], HAUTEUR_BARRE)
        )

        for i, rect in enumerate(rects_icones):
            couleur = (200, 200, 80) if i == batiment_selectionne else (100, 100, 100)
            pygame.draw.rect(ecran, couleur, rect.inflate(8, 8))

            type_actuel = TYPES_BATIMENTS[i]
            icone = pygame.transform.smoothscale(
                images_batiments[type_actuel][1], (TAILLE_ICONE, TAILLE_ICONE)
            )
            ecran.blit(icone, rect)

        # Affichage argent en haut a droite
        marge_hud = 10
        texte_argent = font_argent.render(str(player.money), True, (255, 235, 80))
        hud_x = dims[0] - image_argent.get_width() - marge_hud
        hud_y = marge_hud
        ecran.blit(image_argent, (hud_x, hud_y))
        # Centrer le texte sur la zone noire (apres l'icone carre a gauche)
        icone_offset = image_argent.get_height()  # la piece est un carre = hauteur
        zone_noire_x = hud_x + icone_offset
        zone_noire_w = image_argent.get_width() - icone_offset
        tx = (zone_noire_x + (zone_noire_w - texte_argent.get_width()) // 2) -40
        ty = (hud_y + (image_argent.get_height() - texte_argent.get_height()) // 2) + 4
        ecran.blit(texte_argent, (tx, ty))

        pygame.display.flip()

    return True