
import pygame
import math
import os

from core.Class.player import Player
from core.Class.batiments import Batiment
from core.saves import load_save
from screens.GUI.menu_amelioration import afficher_menu_amelioration


def boucle_jeu(ecran, horloge, FPS):
    LARGEUR_ECRAN, HAUTEUR_ECRAN = ecran.get_size()
    HAUTEUR_BARRE = 100

    herbe = pygame.image.load("assets/grass.png").convert()
    TAILLE_CASE = herbe.get_width()

    images_batiments = {
        Batiment.TYPE_RESIDENTIEL: {
            1: pygame.image.load("assets/buildings/house_lvl1.png").convert_alpha(),
            2: pygame.image.load("assets/buildings/house_lvl2.png").convert_alpha(),  # Image niveau 2
            3: pygame.image.load("assets/buildings/house_lvl3.png").convert_alpha()  # Image niveau 3
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

    if os.path.exists("save/save.json"):
        if not load_save(batiments, player):
            print("ERREUR CRITIQUE: Lecture du fichier save/save.json")
            return False

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

    rects_icones = []
    marge = 20

    for i in range(len(images_batiments)):
        rect = pygame.Rect(
            marge + i * (TAILLE_ICONE + marge),
            HAUTEUR_ECRAN - HAUTEUR_BARRE + (HAUTEUR_BARRE - TAILLE_ICONE) // 2,
            TAILLE_ICONE,
            TAILLE_ICONE
        )
        rects_icones.append(rect)

    def dessiner_grille(surface):
        largeur_vue = LARGEUR_ECRAN / zoom
        hauteur_vue = (HAUTEUR_ECRAN - HAUTEUR_BARRE) / zoom

        debut_x = int(camera_x // TAILLE_CASE) * TAILLE_CASE
        debut_y = int(camera_y // TAILLE_CASE) * TAILLE_CASE

        for y in range(debut_y, debut_y + int(hauteur_vue) + TAILLE_CASE, TAILLE_CASE):
            for x in range(debut_x, debut_x + int(largeur_vue) + TAILLE_CASE, TAILLE_CASE):
                surface.blit(herbe, (x - camera_x, y - camera_y))

    en_cours = True

    while en_cours:
        horloge.tick(FPS)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "menu"

            if event.type == pygame.MOUSEWHEEL:
                ancien_zoom = zoom
                zoom += event.y * VITESSE_ZOOM
                zoom = max(ZOOM_MIN, min(ZOOM_MAX, zoom))

                centre_x = camera_x + LARGEUR_ECRAN / (2 * ancien_zoom)
                centre_y = camera_y + HAUTEUR_ECRAN / (2 * ancien_zoom)

                camera_x = centre_x - LARGEUR_ECRAN / (2 * zoom)
                camera_y = centre_y - HAUTEUR_ECRAN / (2 * zoom)

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

                # 1. Vérification du clic sur la barre du bas
                clic_barre = False
                for i, rect in enumerate(rects_icones):
                    if rect.collidepoint(sx, sy):
                        batiment_selectionne = None if batiment_selectionne == i else i
                        clic_barre = True
                        break

                # 2. Si on a cliqué dans la zone de jeu (pas sur la barre)
                if not clic_barre and sy < HAUTEUR_ECRAN - HAUTEUR_BARRE:

                    # Traduction des coordonnées de l'écran vers le monde avec zoom et caméra
                    mx = camera_x + sx / zoom
                    my = camera_y + sy / zoom

                    # CAS A : On a un bâtiment en main -> On tente de le CONSTRUIRE
                    if batiment_selectionne is not None:
                        # On aligne sur la grille
                        grid_x = int(mx // TAILLE_CASE) * TAILLE_CASE
                        grid_y = int(my // TAILLE_CASE) * TAILLE_CASE

                        type_batiment = TYPES_BATIMENTS[batiment_selectionne]
                        nouveau = Batiment(type_batiment, grid_x, grid_y)

                        if not collision(batiments, nouveau):
                            batiments.append(nouveau)
                            # Optionnel: on peut forcer batiment_selectionne = None ici pour devoir recliquer sur l'icône à chaque fois

                    # CAS B : On n'a RIEN en main -> On tente d'INTERAGIR (Améliorer)
                    elif batiment_selectionne is None:
                        for b in batiments:
                            # On vérifie la collision avec les coordonnées du monde (mx, my)
                            if b.get_rect().collidepoint(mx, my):
                                # Le bâtiment est cliqué, on lance le menu d'amélioration !
                                afficher_menu_amelioration(ecran, b, sx)
                                break  # On arrête la recherche





        ecran.fill((0, 0, 0))

        largeur_vue = LARGEUR_ECRAN / zoom
        hauteur_vue = (HAUTEUR_ECRAN - HAUTEUR_BARRE) / zoom

        surface_monde = pygame.Surface(
            (math.ceil(largeur_vue), math.ceil(hauteur_vue))
        ).convert()

        dessiner_grille(surface_monde)

        # bâtiments
        for b in batiments:
            image_a_dessiner = images_batiments[b.type][b.niveau]

            x = b.x - camera_x
            y = b.y - camera_y

            surface_monde.blit(image_a_dessiner, (x, y))

        # 👻 FANTÔME
        if batiment_selectionne is not None:
            sx, sy = pygame.mouse.get_pos()

            mx = camera_x + sx / zoom
            my = camera_y + sy / zoom

            mx = int(mx // TAILLE_CASE) * TAILLE_CASE
            my = int(my // TAILLE_CASE) * TAILLE_CASE

            type_batiment = TYPES_BATIMENTS[batiment_selectionne]
            test_batiment = Batiment(type_batiment, mx, my)

            # On prend l'image du niveau 1 par défaut pour le fantôme
            image = images_batiments[type_batiment][1]
            image_fantome = image.copy()

            # collision = rouge
            if collision(batiments, test_batiment):
                image_fantome.fill((255, 0, 0, 120), special_flags=pygame.BLEND_RGBA_MULT)

            surface_monde.blit(
                image_fantome,
                (mx - camera_x, my - camera_y)
            )

        surface_affichee = pygame.transform.smoothscale(
            surface_monde,
            (LARGEUR_ECRAN, HAUTEUR_ECRAN - HAUTEUR_BARRE)
        )

        ecran.blit(surface_affichee, (0, 0))

        pygame.draw.rect(
            ecran,
            (40, 40, 40),
            (0, HAUTEUR_ECRAN - HAUTEUR_BARRE, LARGEUR_ECRAN, HAUTEUR_BARRE)
        )

        for i, rect in enumerate(rects_icones):
            couleur = (200, 200, 80) if i == batiment_selectionne else (100, 100, 100)
            pygame.draw.rect(ecran, couleur, rect.inflate(8, 8))

            type_actuel = TYPES_BATIMENTS[i]
            # On affiche l'image de niveau 1 dans la barre d'icônes
            icone = pygame.transform.smoothscale(
                images_batiments[type_actuel][1], (TAILLE_ICONE, TAILLE_ICONE)
            )
            ecran.blit(icone, rect)

        pygame.display.flip()

    return True
