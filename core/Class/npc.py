import random
import math
import pygame
from heapq import heappush, heappop


class PathFinder:
    def __init__(self, batiments, taille_case):
        self.batiments = batiments
        self.taille_case = taille_case

        from core.Class.batiments import Batiment

        self.tiles = set()

        for b in batiments:
            if b.type == Batiment.TYPE_TILE:
                for y in range(b.y, b.y + b.hauteur):
                    for x in range(b.x, b.x + b.largeur):
                        self.tiles.add((x, y))

    def _neighbors(self, case):
        x, y = case

        for dx, dy in [
            (1, 0),
            (-1, 0),
            (0, 1),
            (0, -1)
        ]:
            voisin = (x + dx, y + dy)

            if voisin in self.tiles:
                yield voisin

    def _case_center(self, case):
        x, y = case

        return (
            (x + 0.5) * self.taille_case,
            (y + 0.5) * self.taille_case
        )

    def cases_autour_batiment(self, batiment):
        cases = []

        x1 = batiment.x
        y1 = batiment.y
        x2 = batiment.x + batiment.largeur - 1
        y2 = batiment.y + batiment.hauteur - 1

        for x in range(x1, x2 + 1):
            cases.append((x, y1 - 1))
            cases.append((x, y2 + 1))

        for y in range(y1, y2 + 1):
            cases.append((x1 - 1, y))
            cases.append((x2 + 1, y))

        return [case for case in cases if case in self.tiles]

    def find_path_between_buildings(self, maison, travail):
        starts = self.cases_autour_batiment(maison)
        goals = set(self.cases_autour_batiment(travail))

        if not starts or not goals:
            return None

        queue = []
        came_from = {}

        for start in starts:
            queue.append(start)
            came_from[start] = None

        goal_found = None

        while queue:
            current = queue.pop(0)

            if current in goals:
                goal_found = current
                break

            for voisin in self._neighbors(current):
                if voisin not in came_from:
                    came_from[voisin] = current
                    queue.append(voisin)

        if goal_found is None:
            return None

        path_cases = []
        cur = goal_found

        while cur is not None:
            path_cases.append(cur)
            cur = came_from[cur]

        path_cases.reverse()

        return [self._case_center(case) for case in path_cases]


class Npc:
    # Classe pour les villageois avec cycle de vie
    @staticmethod
    def load_sprites():
        if hasattr(Npc, 'walk_right'):
            return
        sheet = pygame.image.load(
            "assets/npc_sprite/walk.png"
        ).convert_alpha()

        Npc.walk_right = []
        Npc.walk_left = []

        frame_w = 48
        frame_h = 48

        for i in range(6):
            frame = sheet.subsurface(
                pygame.Rect(i * frame_w, 0, frame_w, frame_h)
            )

            Npc.walk_right.append(frame)

            flipped = pygame.transform.flip(frame, True, False)
            Npc.walk_left.append(flipped)
    ETAT_ERRANCE      = "errance"
    ETAT_VERS_TRAVAIL = "vers_travail"
    ETAT_AU_TRAVAIL   = "au_travail"
    ETAT_VERS_MAISON  = "vers_maison"
    ETAT_CHEMIN_BLOQUE = "chemin_bloque"  # Pas de chemin vers le travail

    # Durées en secondes (avant : en frames @ 60fps)
    DUREE_TRAVAIL_MIN = 30.0
    DUREE_TRAVAIL_MAX = 60.0
    DUREE_ERRANCE_MIN = 5.0
    DUREE_ERRANCE_MAX = 15.0

    VITESSE          = 72.0  # pixels monde / seconde (1.2 px/frame * 60 fps)
    RAYON_ERRANCE    = 80    # rayon errance autour de la maison en pixels monde
    TAILLE_AFFICHAGE = 64    # hauteur sprite en pixels écran (fixe)

    def __init__(self, batiment, taille_case=225, player=None, batiments_list=None):
        Npc.load_sprites()
        self.maison = batiment
        self.taille_case = taille_case
        self.player = player
        self.batiments_list = batiments_list or []
        
        # Pathfinder pour calculer les chemins valides
        self.pathfinder = PathFinder(self.batiments_list, taille_case) if self.batiments_list else None

        self.lieu_travail = None
        self.etat = self.ETAT_ERRANCE

        self.anim_frame = 0
        self.anim_timer = 0
        self.direction = "right"

        # Spawn au centre de la maison (en pixels)
        cx, cy = self._centre_pixels(batiment)
        angle = random.uniform(0, 2 * math.pi)
        dist  = random.uniform(0, self.RAYON_ERRANCE * 0.3)
        self.monde_x = cx + math.cos(angle) * dist
        self.monde_y = cy + math.sin(angle) * dist

        # Chemin courant : liste de (px, py) monde
        self.chemin = []
        self.index_chemin = 0  # Pour tracker la position dans le chemin

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
    # Déplacement et Pathfinding
    # ------------------------------------------------------------------

    def _construire_chemin_direct(self, dest_x, dest_y):
        """Chemin en ligne droite vers la destination, découpé en waypoints.
        Utilisé pour l'errance locale autour de la maison."""
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

    def _construire_chemin_valide(self, dest_x, dest_y):
        if not self.batiments_list:
            return None

        self.pathfinder = PathFinder(self.batiments_list, self.taille_case)

        candidats = [
            (dest_x, dest_y),

            (dest_x + self.taille_case, dest_y),
            (dest_x - self.taille_case, dest_y),
            (dest_x, dest_y + self.taille_case),
            (dest_x, dest_y - self.taille_case),

            (dest_x + self.taille_case, dest_y + self.taille_case),
            (dest_x - self.taille_case, dest_y + self.taille_case),
            (dest_x + self.taille_case, dest_y - self.taille_case),
            (dest_x - self.taille_case, dest_y - self.taille_case),
        ]

        meilleur_chemin = None

        for cx, cy in candidats:
            chemin = self.pathfinder.find_path(
                self.monde_x,
                self.monde_y,
                cx,
                cy
            )

            if chemin is not None:
                if meilleur_chemin is None or len(chemin) < len(meilleur_chemin):
                    meilleur_chemin = chemin

        return meilleur_chemin

    def _chemin_vers_travail_existe(self):
        if self.lieu_travail is None:
            return False

        dest_x, dest_y = self._porte_bas_pixels(self.lieu_travail)

        chemin = self._construire_chemin_valide(dest_x, dest_y)

        return chemin is not None

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
        if dx < 0:
            self.direction = "left"
        else:
            self.direction = "right"
        return False

    def update_anim(self, dt):
        self.anim_timer += dt

        if self.anim_timer >= 0.12:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % 6

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
        if self.lieu_travail is batiment:
            return

        self.lieu_travail = batiment
        self.chemin = []

        if batiment is None:
            self.etat = self.ETAT_ERRANCE
            self.timer = 3.0
            return

        if self.etat == self.ETAT_AU_TRAVAIL or self.etat == self.ETAT_VERS_TRAVAIL:
            self._rentrer()
        else:
            self.etat = self.ETAT_CHEMIN_BLOQUE
            self.timer = 0.1

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
        elif self.etat == self.ETAT_CHEMIN_BLOQUE:
            self._update_chemin_bloque(dt)
        self.update_anim(dt)

    def _update_errance_autour_maison(self, dt):
        atteint = self._avancer_vers(self.cible_x, self.cible_y, dt)

        if atteint:
            self.cible_x, self.cible_y = self._nouvelle_cible_errance()

    def _update_errance(self, dt):
        self._update_errance_autour_maison(dt)

        if self.lieu_travail is not None:
            self.etat = self.ETAT_CHEMIN_BLOQUE
            self.timer = 0.1

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

    def _update_chemin_bloque(self, dt):
        self.timer -= dt

        if self.timer > 0:
            self._update_errance_autour_maison(dt)
            return

        if self.lieu_travail is None:
            self.etat = self.ETAT_ERRANCE
            self.timer = 3.0
            return

        self.pathfinder = PathFinder(self.batiments_list, self.taille_case)

        chemin = self.pathfinder.find_path_between_buildings(
            self.maison,
            self.lieu_travail
        )

        if chemin:
            self.chemin = chemin
            self.etat = self.ETAT_VERS_TRAVAIL
            return

        self.timer = 3.0
        self.cible_x, self.cible_y = self._nouvelle_cible_errance()

    def _rentrer(self):
        dest = self._porte_bas_pixels(self.maison)
        self.chemin = self._construire_chemin_direct(*dest)  # Toujours en ligne droite pour retour à la maison
        self.etat = self.ETAT_VERS_MAISON

    def _update_vers_maison(self, dt):
        if self._avancer_chemin(dt):
            if self.lieu_travail is not None:
                self.etat = self.ETAT_CHEMIN_BLOQUE
                self.timer = 0.1
            else:
                self.etat = self.ETAT_ERRANCE
                self.timer = 3.0

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
        sprite = pygame.transform.scale(image, (affichage_w, affichage_h))
        ecran.blit(sprite, (ex - affichage_w // 2, ey - affichage_h))

    def dessiner_monde(self, surface, camera_x, camera_y, image=None):
        if not hasattr(Npc, "walk_right") or not hasattr(Npc, "walk_left"):
            Npc.load_sprites()

        if self.etat == self.ETAT_AU_TRAVAIL:
            return

        x = int(self.monde_x - camera_x)
        y = int(self.monde_y - camera_y)

        if self.direction == "right":
            sprite = self.walk_right[self.anim_frame]
        else:
            sprite = self.walk_left[self.anim_frame]

        h = self.TAILLE_AFFICHAGE
        w = h

        sprite = pygame.transform.scale(
            sprite,
            (w, h)
        )

        surface.blit(
            sprite,
            (x - w // 2, y - h)
        )