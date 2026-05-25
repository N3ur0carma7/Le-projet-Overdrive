import pygame
from core.Class.skill_levels import get_max_level

class Batiment:
    TYPE_RESIDENTIEL = "residentiel"
    TYPE_GENERATEUR  = "generateur"
    TYPE_MINE        = "mine"
    TYPE_FARM        = "farm"
    TYPE_TOURELLE    = "tourelle"
    TYPE_TILE        = "tile"
    TYPE_CENTRALE_ARGENT    = "centrale_argent"
    TYPE_CENTRALE_VAPEUR    = "centrale_vapeur"
    TYPE_CENTRALE_NOURRITURE = "centrale_nourriture"
    DATA = {
        TYPE_RESIDENTIEL: {
            "hitbox_l": 5, "hitbox_h": 5, "scale_visuel": 1.0,
            1: {"population": 1, "cout": 125, "temps_construction": 5000},
            2: {"population": 3, "cout": 250,"temps_construction": 15000},
            3: {"population": 5, "cout": 750, "temps_construction": 30000},
        },
        TYPE_GENERATEUR: {
            "hitbox_l": 5, "hitbox_h": 5, "scale_visuel": 1,
            1: {"vapeur": 30, "cout": 200, "temps_construction": 5000},
            2: {"vapeur": 60, "cout": 500,"temps_construction": 15000},
            3: {"vapeur": 120, "cout": 1000, "temps_construction": 30000},
        },
        TYPE_MINE: {
            "hitbox_l": 5 , "hitbox_h": 5, "scale_visuel": 1,
            1: {"argent": 30, "cout": 250, "temps_construction": 5000},
            2: {"argent": 60, "cout": 600,"temps_construction": 15000},
            3: {"argent": 120, "cout": 1200, "temps_construction": 30000},
        },
        TYPE_FARM: {
            "hitbox_l": 3, "hitbox_h": 6, "scale_visuel": 2.0,
            1: {"nourriture": 30, "cout": 150, "temps_construction": 5000},
            2: {"nourriture": 60, "cout": 400, "temps_construction": 15000},
            3: {"nourriture": 120, "cout": 800, "temps_construction": 30000},
        },
        TYPE_TOURELLE: {
            "hitbox_l": 2, "hitbox_h": 2, "scale_visuel": 3,
            1: {"degat": 30, "cout": 150 , "temps_construction": 5000},
            2: {"degat": 60, "cout": 400, "temps_construction": 15000},
            3: {"degat": 120, "cout": 800, "temps_construction": 30000},
        },
        TYPE_TILE: {
            "hitbox_l": 1, "hitbox_h": 1, "scale_visuel": 1,
            1: {"cout": 1, "temps_construction": 1200},
        },
        TYPE_CENTRALE_ARGENT: {
            "hitbox_l": 5, "hitbox_h": 6, "scale_visuel": 1.25,
            1: {"boost": 0.20, "cout": 2000},
            2: {"boost": 0.25, "cout": 3500},
        },
        TYPE_CENTRALE_VAPEUR: {
                "hitbox_l": 6, "hitbox_h": 8, "scale_visuel": 1.6,
                1: {"boost": 0.20, "cout": 2000},
                2: {"boost": 0.25, "cout": 3500},
        },
        TYPE_CENTRALE_NOURRITURE: {
            "hitbox_l": 7, "hitbox_h": 6, "scale_visuel": 1.45,
            1: {"boost": 0.20, "cout": 2000},
            2: {"boost": 0.25, "cout": 3500},
        },
    }

    DEFAULT_FOOTPRINT = 5

    def __init__(self, type_batiment, x, y):
        if type_batiment not in Batiment.DATA:
            raise ValueError("Type de batiment invalide")
        self.type = type_batiment
        self.niveau = 1
        self.x = x
        self.y = y

        self.en_construction = True
        self.debut_construction = pygame.time.get_ticks()
        self.duree_construction = Batiment.DATA[type_batiment][1].get("temps_construction", 5000)

        self.largeur = Batiment.DATA[type_batiment].get("hitbox_l", Batiment.DEFAULT_FOOTPRINT)
        self.hauteur = Batiment.DATA[type_batiment].get("hitbox_h", Batiment.DEFAULT_FOOTPRINT)

    def construction_finie(self):
        if not self.en_construction:
            return True

        temps = pygame.time.get_ticks() - self.debut_construction

        if temps >= self.duree_construction:
            self.en_construction = False

            if hasattr(self, "niveau_en_attente"):
                self.niveau = self.niveau_en_attente
                del self.niveau_en_attente

            return True

        return False

    def progression_construction(self):
        if not self.en_construction:
            return 1

        temps = pygame.time.get_ticks() - self.debut_construction
        return min(temps / self.duree_construction, 1)
    def get_stats(self):
        return Batiment.DATA[self.type][self.niveau]

    def get_rect_pixel(self, TAILLE_CASE):
        return pygame.Rect(
            self.x * TAILLE_CASE,
            self.y * TAILLE_CASE,
            self.largeur * TAILLE_CASE,
            self.hauteur * TAILLE_CASE
        )

    def get_production(self):
        stats = self.get_stats()
        for key in ("vapeur", "argent", "nourriture", "production", "boost"):
            if key in stats:
                return stats[key]
        return 0

    def get_production_type(self):
        stats = self.get_stats()
        for key in ("vapeur", "argent", "nourriture", "boost"):
            if key in stats:
                return key
        return None

    def get_population(self):
        stats = self.get_stats()
        return stats.get("population", 0)

    def get_upgrade_cost(self):
        """Returns the cost to reach the next level, or None if at cap or max."""
        if self.niveau >= 3:
            return None
        next_level = self.niveau + 1
        cap = get_max_level(self.type)
        if next_level > cap:
            return None
        return Batiment.DATA[self.type][next_level]["cout"]

    def upgrade(self):
        """Upgrade by one level, respecting the skill-tree cap."""
        if self.niveau >= 3:
            return
        next_level = self.niveau + 1
        cap = get_max_level(self.type)
        if next_level <= cap:
            self.niveau += 1

    def est_max_level(self):
        type = self.type
        niveau_max = len(Batiment.DATA[type]) - 3
        if self.niveau >= niveau_max:
            return True
        cap = get_max_level(self.type)
        return self.niveau >= cap

    def update_attaque(self, liste_ennemis, TAILLE_CASE):
        import pygame
        import math

        if not hasattr(self, "direction"):
            self.direction = "E"

        temps_actuel = pygame.time.get_ticks()
        stats = self.get_stats()
        degats = stats.get("degat", 30)
        cadence_tir = 1.0  # 1 tir par seconde
        portee = 250

        if not hasattr(self, "dernier_tir"):
            self.dernier_tir = 0

        tourelle_x = self.x * TAILLE_CASE + (self.largeur * TAILLE_CASE) // 2
        tourelle_y = self.y * TAILLE_CASE + (self.hauteur * TAILLE_CASE) // 2

        cible_proche = None
        dist_min = portee

        for ennemi in liste_ennemis:
            if not ennemi.alive:
                continue
            distance = math.hypot(ennemi.x - tourelle_x, ennemi.y - tourelle_y)
            if distance < dist_min:
                dist_min = distance
                cible_proche = ennemi

        if cible_proche is not None:
            dx = cible_proche.x - tourelle_x
            dy = cible_proche.y - tourelle_y

            angle = math.degrees(math.atan2(dy, dx))
            if angle < 0:
                angle += 360

            if 22.5 <= angle < 67.5:
                self.direction = "SE"
            elif 67.5 <= angle < 112.5:
                self.direction = "S"
            elif 112.5 <= angle < 157.5:
                self.direction = "SW"
            elif 157.5 <= angle < 202.5:
                self.direction = "W"
            elif 202.5 <= angle < 247.5:
                self.direction = "NW"
            elif 247.5 <= angle < 292.5:
                self.direction = "N"
            elif 292.5 <= angle < 337.5:
                self.direction = "NE"
            else:
                self.direction = "E"

            if temps_actuel - self.dernier_tir >= cadence_tir * 1000:
                cible_proche.take_damage(degats)
                self.dernier_tir = temps_actuel

    def collision(self, autre):
        return not (
            self.x + self.largeur < autre.x or
            self.x > autre.x + autre.largeur or
            self.y + self.hauteur < autre.y or
            self.y > autre.y + autre.hauteur
        )

    def __str__(self):
        return f"{self.type} (niveau {self.niveau})"

#----------------------------------------------------------------
    # pour convertir pour le serveur
    # PAS TOUCHE !!!
    # SINON AU BUCHER !!!!
    def to_dict(self):
        return {
            "type": self.type,
            "niveau": self.niveau,
            "x": self.x,
            "y": self.y,
            "largeur": self.largeur,
            "hauteur": self.hauteur,
        }

    @classmethod
    def from_dict(cls, d):
        obj = cls(d["type"], d["x"], d["y"])
        obj.niveau = d.get("niveau", 1)


        obj.largeur = Batiment.DATA[obj.type].get("hitbox_l", Batiment.DEFAULT_FOOTPRINT)
        obj.hauteur = Batiment.DATA[obj.type].get("hitbox_h", Batiment.DEFAULT_FOOTPRINT)
        return obj
