import pygame
import json
from core.player import Player

def save_game(buildings: dict, player: Player, online_data):
    """
    :param buildings: dictionnaire des coordonnées des builds accompagné de leur id respectif
    :param player: objet de type Player : c'est le joueur
    :param online_data: à déterminer
    :return: True | False
    """
    try:
        # Convertion de la liste de coordonées en liste d'ID de batiment
        batiments_real = {}
        for k, v in buildings.items():
            if v not in batiments_real:
                batiments_real[v] = []
            batiments_real[v].append(k)
        # Génération de la save
        save_data = {
            "Player": {
                "hp_max": player.hp_max,
                "hp": player.hp,
                "crit_chance": player.crit_chance,
                "crit_damage": player.crit_damage,
                "raw_damage": player.raw_damage,
                "defense": player.defense,
                "health_regen": player.health_regen,
                "money": player.money,
                "pos": player.pos
            },
            "Builds": batiments_real,
            "Online": online_data if online_data is not None else None,
        }
        # Écriture de la save (indent -> plus lisible)
        with open('save/save.json', 'w') as file:
            json.dump(save_data, file, indent=4)
        return True
    except Exception:
        return False


def load_save(buildings: dict, player: Player):
    """
    :param buildings: dictionnaire VIDE qui va contenir les batiments du fichier de sauvegarde
    :param player: objet de classe Player : c'est le joueur qui doit être vide (en gros il viens d'être créé)
    :return: True | False
    """
    try:
        with open('save/save.json', 'r') as file:
            save_data = json.load(file)
        # Loading player data
        player.hp_max = save_data["Player"]["hp_max"]
        player.hp = save_data["Player"]["hp"]
        player.crit_chance = save_data["Player"]["crit_chance"]
        player.crit_damage = save_data["Player"]["crit_damage"]
        player.raw_damage = save_data["Player"]["raw_damage"]
        player.defense = save_data["Player"]["defense"]
        player.health_regen = save_data["Player"]["health_regen"]
        player.money = save_data["Player"]["money"]
        player.pos = save_data["Player"]["pos"]
        # Loading buildings data
        for k, v in save_data["Builds"].items():
            for build in v:
                buildings[(int(build[0]), int(build[1]))] = int(k)
        # Loadign online data | TO DO
        return True
    except Exception:
        return False