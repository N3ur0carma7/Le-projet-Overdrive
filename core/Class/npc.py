import random
import math
import pygame
from heapq import heappush, heappop


class PathFinder:
    """
    Classe pour trouver un chemin valide entre deux points en utilisant A*.
    Les chemins valides passent par les tiles (TYPE_TILE) ou les bâtiments résidentiels.
    """
    
    def __init__(self, batiments, taille_case):
        self.batiments = batiments
        self.taille_case = taille_case


        # Construire une grille walkable basée sur les bâtiments
        # Déterminer les dimensions de la grille
        self.max_x = 0
        self.max_y = 0
        for b in batiments:
            self.max_x = max(self.max_x, b.x + b.largeur)
            self.max_y = max(self.max_y, b.y + b.hauteur)
        
        # Ajouter une marge de sécurité
        self.max_x += 10
        self.max_y += 10
        
        # Grille walkable: True = on peut marcher, False = obstacle
        self.walkable = [[True for _ in range(self.max_x)] for _ in range(self.max_y)]
        
        # Marquer les tiles (chemins) et bâtiments résidentiels comme walkable, tout le reste comme non-walkable
        # Commencer par marquer tout comme non-walkable
        for y in range(self.max_y):
            for x in range(self.max_x):
                self.walkable[y][x] = False
        
        # Marquer les tiles, bâtiments résidentiels ET bâtiments de production comme walkable
        # Les tiles sont le chemin, les bâtiments résidentiels/production sont les sources/destinations
        from core.Class.batiments import Batiment
        TYPES_WALKABLE = (Batiment.TYPE_TILE, Batiment.TYPE_RESIDENTIEL,
                          Batiment.TYPE_GENERATEUR, Batiment.TYPE_MINE, Batiment.TYPE_FARM)
        for b in batiments:
            if b.type in TYPES_WALKABLE:
                x_start = max(int(b.x), 0)
                y_start = max(int(b.y), 0)
                x_end = min(int(b.x + b.largeur), self.max_x)
                y_end = min(int(b.y + b.hauteur), self.max_y)

                if x_start >= x_end or y_start >= y_end:
                    continue

                for y in range(y_start, y_end):
                    for x in range(x_start, x_end):
                        self.walkable[y][x] = True
    
    def _heuristique(self, pos1, pos2):
        """Distance Manhattan comme heuristique pour A*."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def _get_neighbors(self, pos):
        """Retourne les cases voisines walkable."""
        x, y = pos
        neighbors = []
        # 4-directional movement (haut, bas, gauche, droite)
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.max_x and 0 <= ny < self.max_y and self.walkable[ny][nx]:
                neighbors.append((nx, ny))
        return neighbors
    
    def _pixels_to_grid(self, px, py):
        """Convertir des coordonnées pixels en coordonnées grille."""
        gx = int(px / self.taille_case)
        gy = int(py / self.taille_case)
        gx = max(0, min(gx, self.max_x - 1))
        gy = max(0, min(gy, self.max_y - 1))
        return gx, gy
    
    def _grid_to_pixels(self, gx, gy):
        """Convertir des coordonnées grille en centre de case (pixels)."""
        px = (gx + 0.5) * self.taille_case
        py = (gy + 0.5) * self.taille_case
        return px, py
    
    def find_path(self, start_px, start_py, end_px, end_py):
        """
        Trouve un chemin entre deux points en pixels.
        Retourne une liste de points (px, py) ou None si pas de chemin.
        """
        start_grid = self._pixels_to_grid(start_px, start_py)
        end_grid = self._pixels_to_grid(end_px, end_py)
        
        # Si on peut pas atteindre la destination (elle est non-walkable)
        if not self.walkable[end_grid[1]][end_grid[0]]:
            return None
        
        # A* pathfinding
        open_set = []
        heappush(open_set, (0, start_grid))
        came_from = {}
        g_score = {start_grid: 0}
        f_score = {start_grid: self._heuristique(start_grid, end_grid)}
        
        closed_set = set()
        
        while open_set:
            _, current = heappop(open_set)
            
            if current == end_grid:
                # Chemin trouvé - reconstruire
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start_grid)
                path.reverse()
                
                # Convertir en pixels et lisser le chemin
                pixel_path = [self._grid_to_pixels(gx, gy) for gx, gy in path]
                return pixel_path
            
            closed_set.add(current)
            
            for neighbor in self._get_neighbors(current):
                if neighbor in closed_set:
                    continue
                
                tentative_g = g_score[current] + 1
                
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self._heuristique(neighbor, end_grid)
                    heappush(open_set, (f_score[neighbor], neighbor))
        
        # Pas de chemin trouvé
        return None


class Npc:
    # Classe pour les villageois avec cycle de vie
    @staticmethod
    def load_sprites():
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
    DUREE_TRAVAIL_MIN = 8.0
    DUREE_TRAVAIL_MAX = 20.0
    DUREE_ERRANCE_MIN = 5.0
    DUREE_ERRANCE_MAX = 15.0

    VITESSE          = 72.0  # pixels monde / seconde (1.2 px/frame * 60 fps)
    RAYON_ERRANCE    = 80    # rayon errance autour de la maison en pixels monde
    TAILLE_AFFICHAGE = 64    # hauteur sprite en pixels écran (fixe)

    def __init__(self, batiment, taille_case=225, player=None, batiments_list=None):
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
        """Construit un chemin valide vers la destination en utilisant le pathfinder.
        Retourne None si pas de chemin valide."""
        if self.pathfinder is None:
            return None
        
        # Utiliser le pathfinder pour trouver un chemin
        chemin = self.pathfinder.find_path(self.monde_x, self.monde_y, dest_x, dest_y)
        return chemin
    
    def _chemin_vers_travail_existe(self):
        """Vérifie si un chemin valide existe vers le lieu de travail.
        Retourne True si un chemin existe, False sinon."""
        if self.lieu_travail is None:
            return False
        
        if self.pathfinder is None:
            # Sans pathfinder, on accepte tous les chemins
            return True
        
        dest_x, dest_y = self._centre_pixels(self.lieu_travail)
        chemin = self.pathfinder.find_path(self.monde_x, self.monde_y, dest_x, dest_y)
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
        elif self.etat == self.ETAT_CHEMIN_BLOQUE:
            self._update_chemin_bloque(dt)
        self.update_anim(dt)

    def _update_errance(self, dt):
        atteint = self._avancer_vers(self.cible_x, self.cible_y, dt)
        if atteint:
            self.cible_x, self.cible_y = self._nouvelle_cible_errance()

        self.timer -= dt
        if self.timer <= 0 and self.lieu_travail is not None:
            # Vérifier si un chemin valide existe vers le lieu de travail
            if self._chemin_vers_travail_existe():
                dest = self._centre_pixels(self.lieu_travail)
                self.chemin = self._construire_chemin_valide(*dest)
                if self.chemin:  # Si chemin trouvé
                    self.etat = self.ETAT_VERS_TRAVAIL
                else:  # Pas de chemin trouvé
                    self.etat = self.ETAT_CHEMIN_BLOQUE
                    self.timer = random.uniform(self.DUREE_ERRANCE_MIN, self.DUREE_ERRANCE_MAX)
            else:
                # Pas de chemin valide vers le lieu de travail
                self.etat = self.ETAT_CHEMIN_BLOQUE
                self.timer = random.uniform(self.DUREE_ERRANCE_MIN, self.DUREE_ERRANCE_MAX)

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
        """Reste en errance et attend, le lieu de travail reste non-accessible."""
        # Juste attendre et errer autour de la maison
        self.timer -= dt
        if self.timer <= 0:
            # Vérifier à nouveau si un chemin a été créé (par exemple, un nouveau tile)
            if self._chemin_vers_travail_existe():
                dest = self._centre_pixels(self.lieu_travail)
                self.chemin = self._construire_chemin_valide(*dest)
                if self.chemin:
                    self.etat = self.ETAT_VERS_TRAVAIL
                    return
            # Continuer en errance
            self.etat = self.ETAT_ERRANCE
            self.timer = random.uniform(self.DUREE_ERRANCE_MIN / 2, self.DUREE_ERRANCE_MAX)
            self.cible_x, self.cible_y = self._nouvelle_cible_errance()

    def _rentrer(self):
        dest = self._centre_pixels(self.maison)
        self.chemin = self._construire_chemin_direct(*dest)  # Toujours en ligne droite pour retour à la maison
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
        sprite = pygame.transform.scale(image, (affichage_w, affichage_h))
        ecran.blit(sprite, (ex - affichage_w // 2, ey - affichage_h))

    def dessiner_monde(self, surface, camera_x, camera_y, image=None):
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

        sprite = pygame.transform.smoothscale(
            sprite,
            (w, h)
        )

        surface.blit(
            sprite,
            (x - w // 2, y - h)
        )