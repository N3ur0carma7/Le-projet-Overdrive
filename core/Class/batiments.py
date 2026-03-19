import pygame

class Batiment:
    TYPE_RESIDENTIEL = "residentiel"
    TYPE_MINE = "mine"
    TYPE_AGRICOLE = "agricole"

    DATA = {
        TYPE_RESIDENTIEL: {
            1: {"population": 1, "cout": 125},
            2: {"population": 3, "cout": 250},
            3: {"population": 5, "cout": 750},
        },
        TYPE_MINE: {
            1: {"production": 30, "cout": 200},
            2: {"production": 60, "cout": 500},
            3: {"production": 120, "cout": 1000},
        },
        TYPE_AGRICOLE: {
            1: {"production": 30, "cout": 150},
            2: {"production": 60, "cout": 400},
            3: {"production": 120, "cout": 800},
        }
    }

    def __init__(self, type_batiment, x, y):
        if type_batiment not in Batiment.DATA:
            raise ValueError("Type de bâtiment invalide")
        self.type = type_batiment
        self.niveau = 1

        # position
        self.x = x
        self.y = y

        # taille
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
        return stats.get("production", 0)

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