import pygame
import math

def boucle_jeu(ecran, horloge, FPS):
    # Taille de l’écran
    LARGEUR_ECRAN, HAUTEUR_ECRAN = ecran.get_size()
    HAUTEUR_BARRE = 100  # barre du bas

    herbe = pygame.image.load("assets/grass.png").convert()
    TAILLE_CASE = herbe.get_width()

    # Chargement des bâtiments
    images_batiments = [
        pygame.image.load("assets/building1.png").convert_alpha(),
        pygame.image.load("assets/building2.png").convert_alpha()
    ]

    TAILLE_ICONE = 64

    batiments = {}

    batiment_selectionne = None

    # Caméra et zoom
    camera_x, camera_y = 0.0, 0.0
    zoom = 1.0

    ZOOM_MIN = 0.5
    ZOOM_MAX = 3.0
    VITESSE_ZOOM = 0.1

    # Déplacement caméra avec bouton du milieu
    deplacement_camera = False
    derniere_souris = (0, 0)

    # Création de la barre d’icônes
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

    # Convertit la position de la souris en coordonnées de case
    def souris_vers_case(pos):
        sx, sy = pos
        mx = camera_x + sx / zoom
        my = camera_y + sy / zoom
        return int(mx // TAILLE_CASE), int(my // TAILLE_CASE)

    # Dessine la grille infinie + l’herbe
    def dessiner_grille(surface):
        largeur_vue = LARGEUR_ECRAN / zoom
        hauteur_vue = (HAUTEUR_ECRAN - HAUTEUR_BARRE) / zoom

        debut_x = int(camera_x // TAILLE_CASE) * TAILLE_CASE
        debut_y = int(camera_y // TAILLE_CASE) * TAILLE_CASE

        for y in range(debut_y, debut_y + int(hauteur_vue) + TAILLE_CASE, TAILLE_CASE):
            for x in range(debut_x, debut_x + int(largeur_vue) + TAILLE_CASE, TAILLE_CASE):
                surface.blit(herbe, (x - camera_x, y - camera_y))
                pygame.draw.rect(
                    surface,
                    (60, 60, 60),
                    (x - camera_x, y - camera_y, TAILLE_CASE, TAILLE_CASE),
                    1
                )

    # Boucle principale du jeu
    en_cours = True
    while en_cours:
        horloge.tick(FPS)

        for event in pygame.event.get():

            # Quitter le jeu
            if event.type == pygame.QUIT:
                return False

            # Menu pause
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                from screens.pause import menu_pause
                etat_pause = menu_pause(ecran, horloge, FPS)
                if etat_pause is False:
                    return False
                elif etat_pause == "menu":
                    return "menu"

            # Zoom souris
            if event.type == pygame.MOUSEWHEEL:
                ancien_zoom = zoom
                zoom += event.y * VITESSE_ZOOM
                zoom = max(ZOOM_MIN, min(ZOOM_MAX, zoom))

                # Zoom centré sur l’écran
                centre_x = camera_x + LARGEUR_ECRAN / (2 * ancien_zoom)
                centre_y = camera_y + HAUTEUR_ECRAN / (2 * ancien_zoom)

                camera_x = centre_x - LARGEUR_ECRAN / (2 * zoom)
                camera_y = centre_y - HAUTEUR_ECRAN / (2 * zoom)

            # Début déplacement caméra
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
                deplacement_camera = True
                derniere_souris = pygame.mouse.get_pos()

            # Fin déplacement caméra
            if event.type == pygame.MOUSEBUTTONUP and event.button == 2:
                deplacement_camera = False

            # Mouvement caméra
            if event.type == pygame.MOUSEMOTION and deplacement_camera:
                sx, sy = pygame.mouse.get_pos()
                dx = sx - derniere_souris[0]
                dy = sy - derniere_souris[1]
                camera_x -= dx / zoom
                camera_y -= dy / zoom
                derniere_souris = (sx, sy)

            # Clic droit : désélection
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                batiment_selectionne = None

            # Clic gauche
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                sx, sy = pygame.mouse.get_pos()

                # Clic sur la barre d’icônes
                clic_barre = False
                for i, rect in enumerate(rects_icones):
                    if rect.collidepoint(sx, sy):
                        batiment_selectionne = None if batiment_selectionne == i else i
                        clic_barre = True
                        break

                # Placement du bâtiment sur la grille
                if not clic_barre and batiment_selectionne is not None and sy < HAUTEUR_ECRAN - HAUTEUR_BARRE:
                    case = souris_vers_case((sx, sy))
                    if case not in batiments:
                        batiments[case] = batiment_selectionne

        # ----- RENDU -----
        ecran.fill((0, 0, 0))

        largeur_vue = LARGEUR_ECRAN / zoom
        hauteur_vue = (HAUTEUR_ECRAN - HAUTEUR_BARRE) / zoom

        surface_monde = pygame.Surface(
            (math.ceil(largeur_vue), math.ceil(hauteur_vue))
        ).convert()

        dessiner_grille(surface_monde)

        # Dessin des bâtiments
        for (x_case, y_case), idx in batiments.items():
            x = x_case * TAILLE_CASE - camera_x
            y = y_case * TAILLE_CASE - camera_y
            surface_monde.blit(images_batiments[idx], (x, y))

        # Application du zoom
        surface_affichee = pygame.transform.smoothscale(
            surface_monde,
            (LARGEUR_ECRAN, HAUTEUR_ECRAN - HAUTEUR_BARRE)
        )
        ecran.blit(surface_affichee, (0, 0))

        # Barre du bas
        pygame.draw.rect(
            ecran,
            (40, 40, 40),
            (0, HAUTEUR_ECRAN - HAUTEUR_BARRE, LARGEUR_ECRAN, HAUTEUR_BARRE)
        )

        # Icônes
        for i, rect in enumerate(rects_icones):
            couleur = (200, 200, 80) if i == batiment_selectionne else (100, 100, 100)
