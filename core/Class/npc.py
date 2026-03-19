import random
import math
import heapq
import pygame


# ---------------------------------------------------------------------------
# Pathfinding A* (grille de tuiles, pas d'obstacles → chemin en ligne droite
# décomposé en waypoints réguliers pour une animation fluide)
# ---------------------------------------------------------------------------

def astar(debut, fin, taille_case):
    """Retourne une liste de points (coords monde) du début à la fin.

    Comme il n'y a pas d'obstacles, on utilise A* sur une grille fine
    mais on optimise en allant directement en ligne droite via des
    waypoints espacés d'une taille_case. C'est visuellement identique
    à du vrai A* sans murs.
    """
    # On travaille en coordonnées de tuiles
    def vers_tuile(px, py):
        return int(px // taille_case), int(py // taille_case)

    def vers_monde(tx, ty):
        return tx * taille_case + taille_case // 2, ty * taille_case + taille_case // 2

    debut_t = vers_tuile(*debut)
    fin_t = vers_tuile(*fin)

    if debut_t == fin_t:
        return [fin]

    # Heuristique Manhattan
    def h(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    open_set = []
    heapq.heappush(open_set, (h(debut_t, fin_t), 0, debut_t))
    came_from = {}
    g_score = {debut_t: 0}

    while open_set:
        _, g, courant = heapq.heappop(open_set)

        if courant == fin_t:
            # Reconstruction du chemin
            chemin = []
            while courant in came_from:
                chemin.append(vers_monde(*courant))
                courant = came_from[courant]
            chemin.reverse()
            chemin.append(fin)  # point final exact (centre du bâtiment)
            return chemin

        # Voisins 8-directionnels
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1),(-1,1),(1,1)]:
            voisin = (courant[0] + dx, courant[1] + dy)
            cout = 1.414 if dx != 0 and dy != 0 else 1.0
            tentative_g = g_score[courant] + cout

            if tentative_g < g_score.get(voisin, float('inf')):
                came_from[voisin] = courant
                g_score[voisin] = tentative_g
                f = tentative_g + h(voisin, fin_t)
                heapq.heappush(open_set, (f, tentative_g, voisin))

    # Fallback : ligne directe
    return [fin]


# ---------------------------------------------------------------------------
# Machine à états du PNJ
# ---------------------------------------------------------------------------

class Npc:
    """Villageois avec cycle maison → travail → pause → retour.

    Pathfinding A* (ligne droite sans obstacles).
    Affiché en taille fixe sur l'écran (indépendant du zoom).
    """

    # États
    ETAT_ERRANCE       = "errance"        # flâne près de la maison
    ETAT_VERS_TRAVAIL  = "vers_travail"   # chemin A* vers le lieu de travail
    ETAT_AU_TRAVAIL    = "au_travail"     # pause sur place au bâtiment
    ETAT_VERS_MAISON   = "vers_maison"   # chemin A* de retour

    # Durée de la pause au travail (en frames à 60 FPS)
    DUREE_TRAVAIL_MIN = 60 * 8   # 8 secondes
    DUREE_TRAVAIL_MAX = 60 * 20  # 20 secondes

    # Durée d'errance à la maison avant de repartir
    DUREE_ERRANCE_MIN = 60 * 5
    DUREE_ERRANCE_MAX = 60 * 15

    VITESSE           = 0.8    # pixels monde / frame
    RAYON_ERRANCE     = 100    # rayon errance autour de la maison
    TAILLE_AFFICHAGE  = 64     # hauteur sprite en pixels écran (fixe)
    TAILLE_CASE       = 175    # taille d'une tuile (doit correspondre à la vraie)

    def __init__(self, batiment):
        self.maison = batiment

        # Spawn au centre de la maison
        cx = batiment.x + batiment.largeur // 2
        cy = batiment.y + batiment.hauteur // 2
        angle = random.uniform(0, 2 * math.pi)
        dist  = random.uniform(0, self.RAYON_ERRANCE * 0.3)
        self.monde_x = cx + math.cos(angle) * dist
        self.monde_y = cy + math.sin(angle) * dist

        self.lieu_travail = None   # bâtiment non-résidentiel assigné
        self.etat = self.ETAT_ERRANCE

        # Chemin A* courant : liste de points (x, y) monde
        self.chemin = []
        self.idx_chemin = 0

        # Compteur de pause
        self.timer = random.randint(self.DUREE_ERRANCE_MIN // 2, self.DUREE_ERRANCE_MAX)

        # Cible d'errance courante
        self._choisir_cible_errance()

    # ------------------------------------------------------------------
    # API publique : assigner un lieu de travail depuis jeu.py
    # ------------------------------------------------------------------

    def assigner_travail(self, batiment):
        """Assigne un bâtiment de travail (peut être None si plus de bâtiment)."""
        self.lieu_travail = batiment

    # ------------------------------------------------------------------
    # Déplacement interne
    # ------------------------------------------------------------------

    def _centre(self, batiment):
        return (
            batiment.x + batiment.largeur // 2,
            batiment.y + batiment.hauteur // 2,
        )

    def _choisir_cible_errance(self):
        cx, cy = self._centre(self.maison)
        angle = random.uniform(0, 2 * math.pi)
        dist  = random.uniform(20, self.RAYON_ERRANCE)
        self.cible_x = cx + math.cos(angle) * dist
        self.cible_y = cy + math.sin(angle) * dist

    def _lancer_astar(self, dest_x, dest_y):
        """Calcule le chemin A* vers (dest_x, dest_y) et initialise le suivi."""
        self.chemin = astar(
            (self.monde_x, self.monde_y),
            (dest_x, dest_y),
            self.TAILLE_CASE
        )
        self.idx_chemin = 0

    def _avancer_chemin(self):
        """Avance d'un step sur le chemin A*. Retourne True si destination atteinte."""
        if self.idx_chemin >= len(self.chemin):
            return True

        cible_x, cible_y = self.chemin[self.idx_chemin]
        dx = cible_x - self.monde_x
        dy = cible_y - self.monde_y
        dist = math.hypot(dx, dy)

        if dist <= self.VITESSE:
            self.monde_x = cible_x
            self.monde_y = cible_y
            self.idx_chemin += 1
            return self.idx_chemin >= len(self.chemin)
        else:
            self.monde_x += dx / dist * self.VITESSE
            self.monde_y += dy / dist * self.VITESSE
            return False

    def _avancer_vers(self, tx, ty):
        """Avance en ligne directe vers (tx, ty). Retourne True si atteint."""
        dx = tx - self.monde_x
        dy = ty - self.monde_y
        dist = math.hypot(dx, dy)
        if dist <= self.VITESSE:
            self.monde_x = tx
            self.monde_y = ty
            return True
        self.monde_x += dx / dist * self.VITESSE
        self.monde_y += dy / dist * self.VITESSE
        return False

    # ------------------------------------------------------------------
    # Machine à états
    # ------------------------------------------------------------------

    def update(self):
        if self.etat == self.ETAT_ERRANCE:
            self._update_errance()
        elif self.etat == self.ETAT_VERS_TRAVAIL:
            self._update_vers_travail()
        elif self.etat == self.ETAT_AU_TRAVAIL:
            self._update_au_travail()
        elif self.etat == self.ETAT_VERS_MAISON:
            self._update_vers_maison()

    def _update_errance(self):
        # Marche vers la cible d'errance
        atteint = self._avancer_vers(self.cible_x, self.cible_y)
        if atteint:
            self._choisir_cible_errance()

        # Décompte avant départ au travail
        self.timer -= 1
        if self.timer <= 0 and self.lieu_travail is not None:
            dest = self._centre(self.lieu_travail)
            self._lancer_astar(*dest)
            self.etat = self.ETAT_VERS_TRAVAIL

    def _update_vers_travail(self):
        if self.lieu_travail is None:
            # Plus de travail → on rentre
            self._rentrer()
            return

        atteint = self._avancer_chemin()
        if atteint:
            self.etat = self.ETAT_AU_TRAVAIL
            self.timer = random.randint(self.DUREE_TRAVAIL_MIN, self.DUREE_TRAVAIL_MAX)

    def _update_au_travail(self):
        self.timer -= 1
        if self.timer <= 0:
            self._rentrer()

    def _rentrer(self):
        dest = self._centre(self.maison)
        self._lancer_astar(*dest)
        self.etat = self.ETAT_VERS_MAISON

    def _update_vers_maison(self):
        atteint = self._avancer_chemin()
        if atteint:
            self.etat = self.ETAT_ERRANCE
            self.timer = random.randint(self.DUREE_ERRANCE_MIN, self.DUREE_ERRANCE_MAX)
            self._choisir_cible_errance()

    # ------------------------------------------------------------------
    # Rendu
    # ------------------------------------------------------------------

    def ecran_pos(self, camera_x, camera_y, zoom):
        ex = (self.monde_x - camera_x) * zoom
        ey = (self.monde_y - camera_y) * zoom
        return int(ex), int(ey)

    def dessiner(self, ecran, image, camera_x, camera_y, zoom):
        ex, ey = self.ecran_pos(camera_x, camera_y, zoom)
        orig_w, orig_h = image.get_size()
        affichage_h = max(4, int(self.TAILLE_AFFICHAGE * zoom))
        affichage_w = int(orig_w * affichage_h / orig_h)
        sprite = pygame.transform.smoothscale(image, (affichage_w, affichage_h))
        ecran.blit(sprite, (ex - affichage_w // 2, ey - affichage_h))