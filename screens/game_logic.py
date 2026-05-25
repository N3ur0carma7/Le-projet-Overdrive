import pygame
import threading
import time
from core.Class.npc import Npc, PathFinder
import multiplayer.client as client_module
from core.Class.batiments import Batiment
from math import ceil

import core.pve as pve
import screens.jeu as jeu
import core.Class.batiments as bat


stop_event = threading.Event()
batiments = []
players = []
monsters = []
indice = 0
connected = 0
dt = 0.0

_fullscreen = False


assignations_manuelles: dict[int, int] = {}


def marquer_assignation_manuelle(npc, batiment):
    if batiment is None:
        assignations_manuelles.pop(id(npc), None)
    else:
        assignations_manuelles[id(npc)] = id(batiment)


def effacer_toutes_assignations():
    assignations_manuelles.clear()

# ──────────────────────────────────────────────────────────────

def toggle_fullscreen():
    global _fullscreen
    _fullscreen = not _fullscreen
    if _fullscreen:
        pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        pygame.display.set_mode((1280, 720), pygame.RESIZABLE)

def on_message_recu(taille_case=None):
    global batiments, players, indice, connected, monsters
    messageprec = None
    if client_module.CLIENT is not None:
        from multiplayer.client import send_str_client
        send_str_client("pos", client_module.CLIENT)
    while not stop_event.is_set():
        try:
            if client_module.result is not None:
                message, msg_type = client_module.result
                if client_module.result != messageprec:
                    if msg_type == "float":
                        connected = message
                    elif msg_type == "int":
                        indice = message
                    elif msg_type == "liste_batiments":
                        batiments = message
                        for batiment in batiments:
                            batiment.en_construction = False
                    elif msg_type == "liste_monstres":
                        monsters = message

                    elif msg_type == "liste_joueurs":
                        players = message


                    elif msg_type == "raid":
                        jeu.raid_manager = message
                        jeu.raid_manager.leader = False

                    messageprec = client_module.result
            time.sleep(0.05)
        except (OSError, ConnectionError):
            time.sleep(0.1)




def new_player(taille_case):
    global players
    from core.Class.player import Player
    player = Player()
    player.pos = (taille_case / 2, taille_case / 2)
    players.append(player)

def draw_players(surface, camera_x, camera_y):
    global players
    nuber = 0
    if surface is None or camera_x is None or camera_y is None:
        return
    for player in players:
        player.draw_player(surface, camera_x, camera_y)
        nuber = nuber + 1

def synchroniser_npcs(batiments_list, npcs, player, taille_case):

    # Mettre à jour l'état de construction des bâtiments avant toute logique
    for b in batiments_list:
        if hasattr(b, "en_construction") and b.en_construction:
            b.construction_finie()

    # Calculer la population attendue uniquement pour les maisons finies
    population_attendue = {}
    for b in batiments_list:
        if b.type == Batiment.TYPE_RESIDENTIEL:
            population_attendue[id(b)] = 0 if (hasattr(b, "en_construction") and b.en_construction) else b.get_population()



    # Supprimer les NPCs dont la maison n'existe plus
    maisons_valides = {id(b) for b in batiments_list if b.type == Batiment.TYPE_RESIDENTIEL}
    for npc in list(npcs):
        if id(npc.maison) not in maisons_valides:
            # Nettoyer aussi la table d'assignations
            assignations_manuelles.pop(id(npc), None)
            npcs.remove(npc)

    npcs_par_maison = {}

    for npc in npcs:
        cle = id(npc.maison)

        if cle not in npcs_par_maison:
            npcs_par_maison[cle] = []

        npcs_par_maison[cle].append(npc)

    # Créer / supprimer des NPCs selon la population
    for b in batiments_list:
        if b.type != Batiment.TYPE_RESIDENTIEL:
            continue
        cle = id(b)
        actuels = npcs_par_maison.get(cle, [])
        attendus = population_attendue.get(cle, 0)

        while len(actuels) < attendus:
            npc = Npc(b, taille_case, player, batiments_list)
            npcs.append(npc)
            actuels.append(npc)

        while len(actuels) > attendus:
            npc = actuels.pop()
            assignations_manuelles.pop(id(npc), None)
            if npc in npcs:
                npcs.remove(npc)

    # Mettre à jour le pathfinder de tous les NPC (la grille de bâtiments a pu changer)
    for npc in npcs:
        npc.batiments_list = batiments_list

        npc.pathfinder = PathFinder(batiments_list, taille_case)

    bat_by_id = {id(b): b for b in batiments_list}

    for npc in npcs:
        bat_id = assignations_manuelles.get(id(npc))

        if bat_id is None:
            continue

        bat_cible = bat_by_id.get(bat_id)

        if bat_cible is None:
            assignations_manuelles.pop(id(npc), None)
            npc.assigner_travail(None)
            continue

        if npc.lieu_travail is not bat_cible:
            npc.assigner_travail(bat_cible)


def calculer_production(batiments_list, player, delta_time, acc_argent, acc_food, acc_vapeur, npcs=None, raid_manager=None):
    from core.Class.batiments import Batiment

    maintenant = pygame.time.get_ticks()

    money_mult = 2 if getattr(player, "active_effects", {}).get("money", 0) > maintenant else 1
    food_mult = 2 if getattr(player, "active_effects", {}).get("food", 0) > maintenant else 1
    vapeur_mult = 2 if getattr(player, "active_effects", {}).get("vapeur", 0) > maintenant else 1

    total_villageois = sum(
        b.get_population()
        for b in batiments_list
        if b.type == Batiment.TYPE_RESIDENTIEL and not (hasattr(b, "en_construction") and b.en_construction)
    )

    consommation_food = (total_villageois * 6.0) * delta_time / 60.0
    player.food = max(0.0, player.food - consommation_food)

    food_ok = player.food > 0

    # Créer un mapping de bâtiments de production vers nombre de villageois assignés
    batiments_production_accessibles = set()
    if npcs is not None:
        for npc in npcs:
            if npc.lieu_travail is not None and npc.etat == npc.ETAT_AU_TRAVAIL:
                batiments_production_accessibles.add(id(npc.lieu_travail))
    multiplicateur_nourriture = 1
    multiplicateur_vapeur = 1
    multiplicateur_argent = 1 # Application des multiplicateurs
    for b in batiments_list:
        if b.type == Batiment.TYPE_TOURELLE and raid_manager is not None and not b.en_construction:
            b.update_attaque(raid_manager.monsters, TAILLE_CASE=40)

        rtype = b.get_production_type()
        val = b.get_production() * delta_time / 60.0

        if npcs is not None and rtype is not None:
            if id(b) not in batiments_production_accessibles:
                continue

        if rtype == "nourriture":
            acc_food += val * food_mult
        elif not food_ok:
            pass
        elif rtype == "argent":
            acc_argent += val * money_mult
        elif rtype == "vapeur":
            acc_vapeur += val * vapeur_mult
        elif rtype == "boost":
            if b.type == Batiment.TYPE_CENTRALE_ARGENT:
                multiplicateur_argent += val
            elif b.type == Batiment.TYPE_CENTRALE_VAPEUR:
                multiplicateur_vapeur += val
            elif b.type == Batiment.TYPE_CENTRALE_NOURRITURE:
                multiplicateur_nourriture += val

    acc_argent *= multiplicateur_argent
    acc_vapeur *= multiplicateur_vapeur
    acc_food *= multiplicateur_nourriture

    # 3. Application des gains accumulés
    gains_argent = ceil(acc_argent)
    if gains_argent > 0:
        if player.money > player.max_money:
            player.money = player.money # me tappez pas svp
        elif gains_argent + player.money > player.max_money:
            player.money = player.max_money
        else:
            player.money += gains_argent
        acc_argent -= gains_argent

    gains_food = ceil(acc_food)
    if gains_food > 0:
        if player.food > player.max_food:
            player.food = player.food
        elif gains_food + player.food > player.max_food:
            player.food = player.max_food
        else:
            player.food += gains_food
        acc_food -= gains_food

    gains_vapeur = ceil(acc_vapeur)
    if gains_vapeur > 0:
        if player.vapeur > player.max_vapeur:
            player.vapeur = player.vapeur
        elif gains_vapeur + player.vapeur > player.max_vapeur:
            player.vapeur = player.max_vapeur
        else:
            player.vapeur += gains_vapeur
        acc_vapeur -= gains_vapeur

    return acc_argent, acc_food, acc_vapeur