import math
import random
import pygame
import heapq

_COL_BOUNDS = [(18,71),(88,148),(155,221),(232,294),(306,363),(375,430)]
_ROW_BOUNDS = [(32,109),(173,251),(305,388),(428,511)]

def _build_sprite_rects():
    rects = {}
    for row_idx, (ry1, ry2) in enumerate(_ROW_BOUNDS):
        rects[row_idx] = []
        for col_idx, (cx1, cx2) in enumerate(_COL_BOUNDS):
            rects[row_idx].append(pygame.Rect(cx1, ry1, cx2 - cx1, ry2 - ry1))
    return rects

_DIR_ROW = {
    "down":  0,
    "up":    1,
    "right": 2,
    "left":  3,
}


class Player:
    _spritesheet = None
    _sprite_rects = None

    START_MONEY = 1500
    START_FOOD = 100
    START_VAPEUR = 40

    @classmethod
    def load_sprites(cls):
        if cls._spritesheet is None:
            cls._spritesheet = pygame.image.load("assets/player.png").convert_alpha()
            cls._sprite_rects = _build_sprite_rects()

    def __init__(self):
        self.hp_max = 100
        self.hp = 100
        self.crit_chance = 20
        self.crit_damage = 10
        self.raw_damage = 1
        self.defense = 0
        self.health_regen = 1
        self.money = Player.START_MONEY
        self.food = Player.START_FOOD
        self.vapeur = Player.START_VAPEUR
        self.pos = (0, 0)
        self.path = []

        self.speed = 7
        self.size = 40

        # Animation
        self.direction = "down"   # dernière direction de déplacement
        self.anim_frame = 0       # frame courante (0-5)
        self.anim_timer = 0.0     # accumulateur en secondes
        self.anim_fps = 8         # frames par seconde d'animation
        self.is_moving = False

        self.sprite_height = 72
    def hurt(self, raw_damage: int) -> float | None:
        """
        :param raw_damage: dégats du monstre attaquant le joueur
        :return: nombre de dégats pris par le joueur ou None si le joueur est mort
        """
        damage = raw_damage / (self.defense * 0.05 + 1)
        self.hp -= damage
        if self.hp <= 0:
            return None
        else:
            return damage

    def heuristique(self, start: tuple, dest: tuple):
        """
        :param start: coodonnées de départ
        :param dest: coordonnées de destination
        :return: Entier représentant la distance Manhattan du départ jusqu'à la destination
        """
        return abs(start[0] - dest[0]) + abs(start[1] - dest[1])

    def reconstruire_path(self, came_from, current):

        chemin = [current]

        while current in came_from:
            current = came_from[current]
            chemin.append(current)
        chemin.reverse()
        return chemin

    def a_star(self, dest: tuple, taille_case: int):
        """
        :param dest: coordonnées de destination
        :param batiments: liste de coordonnées des batiments sur la carte
        :return: True si il existe un chemin allant de la position du joueur à la destination, False sinon
        """
        start = (
            int(self.pos[0] // taille_case),
            int(self.pos[1] // taille_case)
        )
        open_set = [start]
        closed_set = set()

        came_from = dict()
        g_score = dict()
        f_score = dict()

        g_score[start] = 0
        f_score[start] = self.heuristique(start, dest)

        while open_set:
            current = min(open_set, key=lambda case: f_score.get(case, float('inf')))

            if current == dest:
                self.path = self.reconstruire_path(came_from, current)
                return True

            open_set.remove(current)
            closed_set.add(current)

            voisins = [
                (current[0] + 1, current[1]),
                (current[0], current[1] + 1),
                (current[0] - 1, current[1]),
                (current[0], current[1] - 1),
            ]

            for voisin in voisins:

                if voisin in closed_set:
                    continue

                tentative_g = g_score[current] + 1
                if voisin not in open_set:
                    open_set.append(voisin)
                elif tentative_g >= g_score[voisin]:
                    continue

                came_from[voisin] = current

                g_score[voisin] = tentative_g
                f_score[voisin] = g_score[voisin] + self.heuristique(voisin, dest)
        return False

    def update(self, taille_case: int):
        if not self.path:
            self.is_moving = False
            return

        next_case = self.path[0]

        target_x = next_case[0] * taille_case + taille_case / 2
        target_y = next_case[1] * taille_case + taille_case / 2

        dx = target_x - self.pos[0]
        dy = target_y - self.pos[1]

        distance = math.hypot(dx, dy)

        if abs(dx) >= abs(dy):
            self.direction = "right" if dx > 0 else "left"
        else:
            self.direction = "down" if dy > 0 else "up"

        self.is_moving = True

        if distance < self.speed:
            self.pos = (target_x, target_y)
            self.path.pop(0)
            if not self.path:
                self.is_moving = False
                self.anim_frame = 0
                self.anim_timer = 0.0
                self.direction = "down"
            return

        dx /= distance
        dy /= distance
        self.pos = (self.pos[0] + dx * self.speed, self.pos[1] + dy * self.speed)

    def update_anim(self, dt: float):
        """Avance le timer d'animation. Appeler une fois par frame avec dt en secondes."""
        if self.is_moving:
            self.anim_timer += dt
            if self.anim_timer >= 1.0 / self.anim_fps:
                self.anim_timer = 0.0
                self.anim_frame = (self.anim_frame + 1) % len(_COL_BOUNDS)
        else:
            #idle
            self.anim_frame = 0
            self.anim_timer = 0.0
            self.direction = "down"

    def draw_player(self, surface, camera_x, camera_y) -> bool:
        """
        :param surface: la map
        :param camera_x: la position x de la caméra
        :param camera_y: la position y de la caméra
        :return: True si le joueur s'est correctement dessiné, False sinon.
        """
        Player.load_sprites()

        row = _DIR_ROW[self.direction]
        src_rect = Player._sprite_rects[row][self.anim_frame]

        scale = self.sprite_height / src_rect.height
        dst_w = int(src_rect.width * scale)
        dst_h = self.sprite_height

        sub = Player._spritesheet.subsurface(src_rect)
        scaled = pygame.transform.scale(sub, (dst_w, dst_h))

        draw_x = int(self.pos[0] - camera_x) - dst_w // 2
        draw_y = int(self.pos[1] - camera_y) - dst_h

        surface.blit(scaled, (draw_x, draw_y))
        return True

    def to_dict(self):
        return {
            "hp_max": self.hp_max,
            "hp": self.hp,
            "crit_chance": self.crit_chance,
            "crit_damage" : self.crit_damage,
            "raw_damage" : self.raw_damage,
            "defense" : self.defense,
            "health_regen" : self.health_regen,
            "money": self.money,
            "food": self.food,
            "vapeur": self.vapeur,
            "pos": self.pos,
            "path": self.path,
            "speed": self.speed,
            "size": self.size
        }

    @classmethod
    def from_dict(cls, d):
        obj = cls(d["hp_max"], d["hp"], d["crit_chance"], d["crit_damage"], d["raw_damage"], d["defense"], d["health_regen"], d["money"], d["pos"], d["path"], d["speed"], d["size"])
        obj.hp_max = d.get("hp_max", 100)
        obj.hp = d.get("hp", 100)
        obj.crit_chance = d.get("crit_chance", 20)
        obj.crit_damage = d.get("crit_damage", 10)
        obj.raw_damage = d.get("raw_damage", 1)
        obj.defense = d.get("defense", 0)
        obj.health_regen = d.get("health_regen", 1)
        obj.money = d.get("money", 5000)
        obj.food = d.get("food", 0)
        obj.vapeur = d.get("vapeur", 0)
        obj.pos = d.get("pos", (0, 0))
        obj.path = d.get("path", [])
        obj.speed = d.get("speed", 10)
        obj.size = d.get("size", 40)
        return obj
