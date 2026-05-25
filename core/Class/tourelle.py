import math
import pygame
from core.Class.batiments import Batiment  # Ajustez le chemin selon votre structure


class Tourelle(Batiment):
    def __init__(self, x, y, type_batiment="tourelle"):
        super().__init__(x, y, type_batiment)

        self.portee = 200
        self.degats = 10
        self.cadence_tir = 1.0
        self.dernier_tir = 0

        self.son_tir = pygame.mixer.Sound("assets/sounds/turret.mp3")
        self.son_tir.set_volume(0.35)

    def update_attaque(self, liste_ennemis, TAILLE_CASE=40):
        temps_actuel = pygame.time.get_ticks()

        if temps_actuel - self.dernier_tir < self.cadence_tir * 1000:
            return

        cible_la_plus_proche = None
        distance_min = self.portee

        tourelle_x = self.x * TAILLE_CASE + TAILLE_CASE // 2
        tourelle_y = self.y * TAILLE_CASE + TAILLE_CASE // 2

        for ennemi in liste_ennemis:
            if hasattr(ennemi, "alive") and not ennemi.alive:
                continue

            dx = ennemi.x - tourelle_x
            dy = ennemi.y - tourelle_y
            distance = math.hypot(dx, dy)

            if distance < distance_min:
                distance_min = distance
                cible_la_plus_proche = ennemi

        if cible_la_plus_proche is None:
            return

        if hasattr(cible_la_plus_proche, "recevoir_degats"):
            cible_la_plus_proche.recevoir_degats(self.degats)
        elif hasattr(cible_la_plus_proche, "take_damage"):
            cible_la_plus_proche.take_damage(self.degats)
        else:
            cible_la_plus_proche.pv -= self.degats

        self.son_tir.play()
        self.dernier_tir = temps_actuel
