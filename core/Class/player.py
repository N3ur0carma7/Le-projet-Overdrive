import math
import random

class Player:
    def __init__(self):
        self.hp_max = 100
        self.hp = 100
        self.crit_chance = 20
        self.crit_damage = 10
        self.raw_damage = 1
        self.defense = 0
        self.health_regen = 1
        self.money = 0
        self.pos = (0, 0)
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
    def move(self, dest: tuple) -> bool:
        pass # En attente du pathfinding