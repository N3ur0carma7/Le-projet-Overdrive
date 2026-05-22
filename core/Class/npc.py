import random
import math
import pygame


class Npc:
    # Classe pour les villageois avec cycle de vie

    ETAT_ERRANCE      = "errance"
    ETAT_VERS_TRAVAIL = "vers_travail"
    ETAT_AU_TRAVAIL   = "au_travail"
    ETAT_VERS_MAISON  = "vers_maison"

    # Durées en secondes (avant : en frames @ 60fps)
    DUREE_TRAVAIL_MIN = 8.0
    DUREE_TRAVAIL_MAX = 20.0
    DUREE_ERRANCE_MIN = 5.0
    DUREE_ERRANCE_MAX = 15.0

    VITESSE          = 72.0  # pixels monde / seconde (1.2 px/frame * 60 fps)
    RAYON_ERRANCE    = 80    # rayon errance autour de la maison en pixels monde
    TAILLE_AFFICHAGE = 64    # hauteur sprite en pixels écran (fixe)

    def __init__(self, batiment, taille_case=225, player=None):
        self.maison = batiment
        self.taille_case = taille_case
        self.player = player

        self.lieu_travail = None
        self.etat = self.ETAT_ERRANCE

        # Spawn au centre de la maison (en pixels)
        cx, cy = self._centre_pixels(batiment)
        angle = random.uniform(0, 2 * math.pi)
        dist  = random.uniform(0, self.RAYON_ERRANCE * 0.3)
        self.monde_x = cx + math.cos(angle) * dist
        self.monde_y = cy + math.sin(angle) * dist

        # Chemin courant : liste de (px, py) monde
        self.chemin = []

        # timer en secondes
        self.timer = random.uniform(self.DUREE_ERRANCE_MIN / 2, self.DUREE_ERRANCE_MAX)

        # Première cible d'errance
        self.cible_x, self.cible_y = self._nouvelle_cible_errance()

    # ------------------------------------------------------------------
    # Helpers coordonnées
    # ------------------------------------------------------------------

    def _centre_pixels(self, batiment):
        """Retourne le centre d'un bâtiment en pixels monde."""
        px = batiment.x * self.taille_case + (batiment.largeur * self.taille_case) // 2
        py = batiment.y * self.taille_case + (batiment.hauteur * self.taille_case) // 2
        return px, py

    def _nouvelle_cible_errance(self):
        cx, cy = self._centre_pixels(self.maison)
        angle = random.uniform(0, 2 * math.pi)
        dist  = random.uniform(20, self.RAYON_ERRANCE)
        return cx + math.cos(angle) * dist, cy + math.sin(angle) * dist

    # ------------------------------------------------------------------
    # Déplacement
    # ------------------------------------------------------------------

    def _construire_chemin_direct(self, dest_x, dest_y):
        """Chemin en ligne droite vers la destination, découpé en waypoints."""
        dx = dest_x - self.monde_x
        dy = dest_y - self.monde_y
        dist = math.hypot(dx, dy)
        if dist < 1:
            return [(dest_x, dest_y)]

        # Un waypoint tous les ~taille_case pixels pour animation fluide
        nb = max(1, int(dist // self.taille_case))
        chemin = []
        for i in range(1, nb + 1):
            t = i / nb
            chemin.append((self.monde_x + dx * t, self.monde_y + dy * t))
        chemin[-1] = (dest_x, dest_y)
        return chemin

    def _avancer_vers(self, tx, ty, dt):
        """Avance en ligne directe vers (tx, ty). Retourne True si atteint."""
        dx = tx - self.monde_x
        dy = ty - self.monde_y
        dist = math.hypot(dx, dy)
        step = self.VITESSE * dt
        if dist <= step:
            self.monde_x = tx
            self.monde_y = ty
            return True
        self.monde_x += dx / dist * step
        self.monde_y += dy / dist * step
        return False

    def _avancer_chemin(self, dt):
        """Suit le chemin waypoint par waypoint. Retourne True si arrivé."""
        if not self.chemin:
            return True
        atteint = self._avancer_vers(*self.chemin[0], dt)
        if atteint:
            self.chemin.pop(0)
        return len(self.chemin) == 0

    # ------------------------------------------------------------------
    # Machine à états
    # ------------------------------------------------------------------

    def assigner_travail(self, batiment):
        self.lieu_travail = batiment

    def update(self, dt: float = 1/60):
        """Met à jour le NPC.
        dt : delta time en secondes (indépendant des FPS).
        """
        if self.etat == self.ETAT_ERRANCE:
            self._update_errance(dt)
        elif self.etat == self.ETAT_VERS_TRAVAIL:
            self._update_vers_travail(dt)
        elif self.etat == self.ETAT_AU_TRAVAIL:
            self._update_au_travail(dt)
        elif self.etat == self.ETAT_VERS_MAISON:
            self._update_vers_maison(dt)

    def _update_errance(self, dt):
        atteint = self._avancer_vers(self.cible_x, self.cible_y, dt)
        if atteint:
            self.cible_x, self.cible_y = self._nouvelle_cible_errance()

        self.timer -= dt
        if self.timer <= 0 and self.lieu_travail is not None:
            dest = self._centre_pixels(self.lieu_travail)
            self.chemin = self._construire_chemin_direct(*dest)
            self.etat = self.ETAT_VERS_TRAVAIL

    def _update_vers_travail(self, dt):
        if self.lieu_travail is None:
            self._rentrer()
            return
        if self._avancer_chemin(dt):
            self.etat = self.ETAT_AU_TRAVAIL
            self.timer = random.uniform(self.DUREE_TRAVAIL_MIN, self.DUREE_TRAVAIL_MAX)

    def _update_au_travail(self, dt):
        self.timer -= dt
        if self.timer <= 0:
            self._rentrer()

    def _rentrer(self):
        dest = self._centre_pixels(self.maison)
        self.chemin = self._construire_chemin_direct(*dest)
        self.etat = self.ETAT_VERS_MAISON

    def _update_vers_maison(self, dt):
        if self._avancer_chemin(dt):
            self.etat = self.ETAT_ERRANCE
            self.timer = random.uniform(self.DUREE_ERRANCE_MIN, self.DUREE_ERRANCE_MAX)
            self.cible_x, self.cible_y = self._nouvelle_cible_errance()

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

    def dessiner_monde(self, surface, camera_x, camera_y, image):
        """Dessin sur surface_monde. Le NPC est invisible quand au travail."""
        if self.etat == self.ETAT_AU_TRAVAIL:
            return
        x = int(self.monde_x - camera_x)
        y = int(self.monde_y - camera_y)
        orig_w, orig_h = image.get_size()
        h = self.TAILLE_AFFICHAGE
        w = int(orig_w * h / orig_h)
        sprite = pygame.transform.smoothscale(image, (w, h))
        surface.blit(sprite, (x - w // 2, y - h))