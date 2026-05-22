import pygame

def collision(batiments, nouveau):
    for b in batiments:
        if (nouveau.x < b.x + b.largeur and
                nouveau.x + nouveau.largeur > b.x and
                nouveau.y < b.y + b.hauteur and
                nouveau.y + nouveau.hauteur > b.y):
            return True
    return False

def calculer_rects_icones(dims, hauteur_barre, taille_icone, slide_offset=0):
    """
    slide_offset : décalage vertical vers le bas (0 = visible, hauteur_barre = caché).
    """
    rects = []
    marge = 20
    for i in range(6):
        rect = pygame.Rect(
            marge + i * (taille_icone + marge),
            dims[1] - hauteur_barre + (hauteur_barre - taille_icone) // 2 + slide_offset,
            taille_icone,
            taille_icone
        )
        rects.append(rect)
    return rects

def souris_vers_case(pos, camera_x, camera_y, zoom, taille_case):
    sx, sy = pos
    mx = camera_x + sx / zoom
    my = camera_y + sy / zoom
    return int(mx // taille_case), int(my // taille_case)

def joueur_a_portee(case, player, taille_case, distance_max=2, width=1, height=1):
    """
    case: (x, y) en coordonnées grille.
    width/height: footprint de la cible en cases (permet 3x3, etc.).
    Vérifie la distance jusqu'à la case la plus proche dans le rectangle cible.
    """
    joueur_case_x = int(player.pos[0] // taille_case)
    joueur_case_y = int(player.pos[1] // taille_case)

    x0, y0 = case
    x1 = x0 + max(1, int(width)) - 1
    y1 = y0 + max(1, int(height)) - 1

    nearest_x = min(max(joueur_case_x, x0), x1)
    nearest_y = min(max(joueur_case_y, y0), y1)

    dx = abs(joueur_case_x - nearest_x)
    dy = abs(joueur_case_y - nearest_y)
    return dx <= distance_max and dy <= distance_max

def dessiner_grille(surface, camera_x, camera_y, dims, hauteur_barre, zoom, grass, taille_case):
    surface.fill((58, 44, 32))

def dessiner_grille_overlay(surface, camera_x, camera_y, dims, hauteur_barre, zoom, taille_case):
    couleur_grille = (92, 72, 44)
    epaisseur = 1 if zoom < 1.0 else 2

    debut_x = int(camera_x // taille_case) * taille_case
    debut_y = int(camera_y // taille_case) * taille_case
    largeur_vue = dims[0] / zoom
    hauteur_vue = (dims[1] - hauteur_barre) / zoom

    x_fin = debut_x + int(largeur_vue) + taille_case
    y_fin = debut_y + int(hauteur_vue) + taille_case

    for x in range(debut_x, x_fin + 1, taille_case):
        screen_x = int((x - camera_x) * zoom)
        pygame.draw.line(surface, couleur_grille, (screen_x, 0), (screen_x, dims[1] - hauteur_barre), epaisseur)

    for y in range(debut_y, y_fin + 1, taille_case):
        screen_y = int((y - camera_y) * zoom)
        pygame.draw.line(surface, couleur_grille, (0, screen_y), (dims[0], screen_y), epaisseur)

def dessiner_grille_overlay_ecran(ecran, camera_x, camera_y, dims, hauteur_ui, zoom, taille_case):
    """
    Dessine la grille directement en pixels écran (après scaling du monde).
    Ça évite les artefacts quand on scale une grille fine à des zooms non entiers.
    hauteur_ui: hauteur (en px écran) occupée par l'UI en bas (on ne dessine pas dessus).
    """
    couleur_grille = (150, 120, 84)
    epaisseur = 1

    w, h = int(dims[0]), int(dims[1])
    h_monde = max(0, h - int(hauteur_ui))
    if h_monde <= 0:
        return

    step = taille_case * zoom
    if step <= 2:
        return

    offset_x = (-camera_x * zoom) % step
    offset_y = (-camera_y * zoom) % step

    x = offset_x
    while x <= w:
        sx = int(round(x))
        pygame.draw.line(ecran, couleur_grille, (sx, 0), (sx, h_monde), epaisseur)
        x += step

    y = offset_y
    while y <= h_monde:
        sy = int(round(y))
        pygame.draw.line(ecran, couleur_grille, (0, sy), (w, sy), epaisseur)
        y += step


def dessiner_grille_overlay_monde(surface_monde, camera_x, camera_y, taille_case):
    """
    Variante "monde" (sans zoom) : dessine la grille directement sur surface_monde
    pour qu'elle passe derrière le joueur / les sprites.
    """
    couleur_grille = (150, 120, 84)
    epaisseur = 1

    largeur_vue, hauteur_vue = surface_monde.get_size()
    debut_x = int(camera_x // taille_case) * taille_case
    debut_y = int(camera_y // taille_case) * taille_case

    x_fin = debut_x + int(largeur_vue) + taille_case
    y_fin = debut_y + int(hauteur_vue) + taille_case

    for x in range(debut_x, x_fin + 1, taille_case):
        sx = int(x - camera_x)
        pygame.draw.line(surface_monde, couleur_grille, (sx, 0), (sx, hauteur_vue), epaisseur)

    for y in range(debut_y, y_fin + 1, taille_case):
        sy = int(y - camera_y)
        pygame.draw.line(surface_monde, couleur_grille, (0, sy), (largeur_vue, sy), epaisseur)