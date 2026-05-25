import json
from core.Class.player import Player
from core.Class.batiments import Batiment

def save_game(buildings: list, player: Player, online_data, unlocked_skills):
    # Sauvegarde la partie
    try:
        batiments_real = []
        for B in buildings:
            batiments_real.append(B.to_dict())
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
                "food": player.food,
                "vapeur": player.vapeur,
                "pos": player.pos,
                "inventory": getattr(player, "inventory", {}),
                "active_effects": getattr(player, "active_effects", {})
            },
            "Builds": batiments_real,
            "Online": online_data if online_data is not None else None,
            "Skills": unlocked_skills,
        }
        with open('save/save.json', 'w') as file:
            json.dump(save_data, file, indent=4)
        return True
    except Exception:
        return False


def load_save(buildings: list, player: Player, unlocked_skills):
    # Charge la sauvegarde
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
        player.food = save_data["Player"].get("food", 0)
        player.vapeur = save_data["Player"].get("vapeur", 0)
        player.pos = save_data["Player"]["pos"]

        player.inventory = save_data["Player"].get("inventory", {
            "potion_money": 0,
            "potion_food": 0,
            "potion_vapeur": 0,
            "potion_heal": 0
        })

        player.active_effects = save_data["Player"].get("active_effects", {
            "money": 0,
            "food": 0,
            "vapeur": 0,
            "heal": 0
        })
        for b in save_data["Builds"]:
            buildings.append(Batiment.from_dict(b))
        for bat in buildings:
            bat.en_construction = False
        for skill in save_data["Skills"]:
            unlocked_skills.append(skill)
        return True
    except Exception:
        return False