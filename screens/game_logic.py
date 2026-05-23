import pygame
import threading
import time
from core.Class.npc import Npc
import multiplayer.client as client_module
from core.Class.batiments import Batiment


stop_event = threading.Event()
batiments = []
players = []
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
    global batiments, players, indice, connected
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
                    elif msg_type == "liste_joueurs":
                        players = message
                        for player in players:
                            player.update_anim(dt)
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

    population_attendue = {}
    for b in batiments_list:
        if b.type == Batiment.TYPE_RESIDENTIEL:
            population_attendue[id(b)] = b.get_population()

    npcs_par_maison = {}
    for npc in list(npcs):
        cle = id(npc.maison)
        if cle not in npcs_par_maison:
            npcs_par_maison[cle] = []
        npcs_par_maison[cle].append(npc)

    # Supprimer les NPCs dont la maison n'existe plus
    maisons_valides = {id(b) for b in batiments_list if b.type == Batiment.TYPE_RESIDENTIEL}
    for npc in list(npcs):
        if id(npc.maison) not in maisons_valides:
            # Nettoyer aussi la table d'assignations
            assignations_manuelles.pop(id(npc), None)
            npcs.remove(npc)

    # Créer / supprimer des NPCs selon la population
    for b in batiments_list:
        if b.type != Batiment.TYPE_RESIDENTIEL:
            continue
        cle = id(b)
        actuels = npcs_par_maison.get(cle, [])
        attendus = population_attendue.get(cle, 0)

        while len(actuels) < attendus:
            npc = Npc(b, taille_case, player)
            npcs.append(npc)
            actuels.append(npc)

        while len(actuels) > attendus:
            npc = actuels.pop()
            assignations_manuelles.pop(id(npc), None)
            if npc in npcs:
                npcs.remove(npc)

    bat_by_id = {id(b): b for b in batiments_list}

    lieux_travail = [b for b in batiments_list
                     if b.type not in (Batiment.TYPE_RESIDENTIEL, Batiment.TYPE_TOURELLE)]

    npcs_auto = []
    for npc in npcs:
        bat_id = assignations_manuelles.get(id(npc))
        if bat_id is not None:
            bat_cible = bat_by_id.get(bat_id)
            if bat_cible is not None:
                npc.assigner_travail(bat_cible)
                continue
            else:
                assignations_manuelles.pop(id(npc), None)
        npcs_auto.append(npc)

    for i, npc in enumerate(npcs_auto):
        if lieux_travail:
            npc.assigner_travail(lieux_travail[i % len(lieux_travail)])
        else:
            npc.assigner_travail(None)


def calculer_production(batiments_list, player, delta_time, acc_argent, acc_food, acc_vapeur, raid_manager=None):
    from core.Class.batiments import Batiment

    total_villageois = sum(b.get_population() for b in batiments_list if b.type == Batiment.TYPE_RESIDENTIEL)


    consommation_food = (total_villageois * 6.0) * delta_time / 60.0

    player.food = max(0.0, player.food - consommation_food)

    food_ok = player.food > 0
    for b in batiments_list:
        if b.type == Batiment.TYPE_TOURELLE and raid_manager is not None:
            b.update_attaque(raid_manager.monsters, TAILLE_CASE=40)

        rtype = b.get_production_type()
        val = b.get_production() * delta_time / 60.0

        if rtype == "nourriture":
            acc_food += val
        elif not food_ok:
            pass
        elif rtype == "argent":
            acc_argent += val

        elif rtype == "vapeur":
            acc_vapeur += val

    gains_argent = int(acc_argent)
    if gains_argent > 0:
        player.money += gains_argent
        acc_argent -= gains_argent

    gains_food = int(acc_food)
    if gains_food > 0:
        player.food += gains_food
        acc_food -= gains_food

    gains_vapeur = int(acc_vapeur)
    if gains_vapeur > 0:
        player.vapeur += gains_vapeur
        acc_vapeur -= gains_vapeur

    return acc_argent, acc_food, acc_vapeur