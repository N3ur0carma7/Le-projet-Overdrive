import pygame
import math

def boucle_jeu(ecran, horloge, FPS):

    LARGEUR_ECRAN, HAUTEUR_ECRAN = ecran.get_size()
    HAUTEUR_BARRE = 100

    # chargement images
    herbe = pygame.image.load("assets/grass.png").convert()
    TAILLE_TUILE = herbe.get_width()

    images_batiments = [
        pygame.image.load("assets/building1.png").convert_alpha(),
        pygame.image.load("assets/building2.png").convert_alpha()
    ]

    TAILLE_ICONE = 64

    batiments_places = []
    batiment_selectionne = None

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

    en_cours = True
    while en_cours:
        horloge.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            # check esc pour menu pause
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                from screens.pause import menu_pause 
                etat_pause = menu_pause(ecran, horloge, FPS)
                if etat_pause == False:
                    return False          # quitter le jeu
                elif etat_pause == "menu":
                    return "menu"         # revenir au menu principal
                # si "jeu", le menu se ferme et on reprend la boucle

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

                clic_barre = False
                for i, rect in enumerate(rects_icones):
                    if rect.collidepoint(sx, sy):
                        if batiment_selectionne == i:
                            batiment_selectionne = None
                        else:
                            batiment_selectionne = i
                        clic_barre = True
                        break

                if not clic_barre and batiment_selectionne is not None and sy < HAUTEUR_ECRAN - HAUTEUR_BARRE:
                    mx = camera_x + sx / zoom
                    my = camera_y + sy / zoom

                    # créer un rect du nouveau bâtiment
                    nouveau_rect = pygame.Rect(mx, my, images_batiments[batiment_selectionne].get_width(),
                                                        images_batiments[batiment_selectionne].get_height())

                    # vérifier collision avec les bâtiments existants
                    collision = False
                    for img, bx, by in batiments_places:
                        rect_existant = pygame.Rect(bx, by, img.get_width(), img.get_height())
                        if nouveau_rect.colliderect(rect_existant):
                            collision = True
                            break

                    if not collision:
                        batiments_places.append(
                            (images_batiments[batiment_selectionne], mx, my)
                        )


        ecran.fill((0, 0, 0))

        largeur_vue = LARGEUR_ECRAN / zoom
        hauteur_vue = (HAUTEUR_ECRAN - HAUTEUR_BARRE) / zoom

        surface_monde = pygame.Surface(
            (math.ceil(largeur_vue), math.ceil(hauteur_vue))
        ).convert()

        debut_x = int(camera_x // TAILLE_TUILE) * TAILLE_TUILE
        debut_y = int(camera_y // TAILLE_TUILE) * TAILLE_TUILE

        for y in range(debut_y, debut_y + int(hauteur_vue) + TAILLE_TUILE, TAILLE_TUILE):
            for x in range(debut_x, debut_x + int(largeur_vue) + TAILLE_TUILE, TAILLE_TUILE):
                surface_monde.blit(herbe, (x - camera_x, y - camera_y))

        for img, mx, my in batiments_places:
            surface_monde.blit(img, (mx - camera_x, my - camera_y))

        sx, sy = pygame.mouse.get_pos()
        if batiment_selectionne is not None and sy < HAUTEUR_ECRAN - HAUTEUR_BARRE:
            mx = camera_x + sx / zoom
            my = camera_y + sy / zoom
            fantome = images_batiments[batiment_selectionne].copy()
            fantome.set_alpha(150)
            surface_monde.blit(fantome, (mx - camera_x, my - camera_y))

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
            icone = pygame.transform.smoothscale(
                images_batiments[i], (TAILLE_ICONE, TAILLE_ICONE)
            )
            ecran.blit(icone, rect)

        pygame.display.flip()

    return True
