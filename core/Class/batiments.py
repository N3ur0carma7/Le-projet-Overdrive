import pygame

class Batiment:
    TYPE_RESIDENTIEL = "residentiel"
    TYPE_GENERATEUR  = "generateur"
    TYPE_MINE        = "mine"
    TYPE_FARM        = "farm"

    DATA = {
        TYPE_RESIDENTIEL: {
            1: {"population": 1, "cout": 125},
            2: {"population": 3, "cout": 250},
            3: {"population": 5, "cout": 750},
        },
        TYPE_GENERATEUR: {
            1: {"vapeur": 30,  "cout": 200},
            2: {"vapeur": 60,  "cout": 500},
            3: {"vapeur": 120, "cout": 1000},
        },
        TYPE_MINE: {
            1: {"argent": 30,  "cout": 250},
            2: {"argent": 60,  "cout": 600},
            3: {"argent": 120, "cout": 1200},
        },
        TYPE_FARM: {
            1: {"nourriture": 30,  "cout": 150},
            2: {"nourriture": 60,  "cout": 400},
            3: {"nourriture": 120, "cout": 800},
        },
    }

    def __init__(self, type_batiment, x, y):
        if type_batiment not in Batiment.DATA:
            raise ValueError("Type de batiment invalide")
        self.type = type_batiment
        self.niveau = 1
        self.x = x
        self.y = y
        self.largeur = 1
        self.hauteur = 1

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
        for key in ("vapeur", "argent", "nourriture", "production"):
            if key in stats:
                return stats[key]
        return 0

    def get_production_type(self):
        stats = self.get_stats()
        for key in ("vapeur", "argent", "nourriture"):
            if key in stats:
                return key
        return None

    def get_population(self):
        stats = self.get_stats()
        return stats.get("population", 0)

    def get_upgrade_cost(self):
        if self.niveau >= 3:
            return None
        return Batiment.DATA[self.type][self.niveau + 1]["cout"]

    def upgrade(self):
        if self.niveau < 3:
            self.niveau += 1

    def est_max_level(self):
        return self.niveau >= 3

    def collision(self, autre):
        return not (
                self.x + self.largeur < autre.x or
                self.x > autre.x + autre.largeur or
                self.y + self.hauteur < autre.y or
                self.y > autre.y + autre.hauteur
        )

    def __str__(self):
        return f"{self.type} (niveau {self.niveau})"

    #pour convertir pour le serveur
    #PAS TOUCHE !!!
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
        obj.largeur = d.get("largeur", 175)
        obj.hauteur = d.get("hauteur", 175)
        return obj
