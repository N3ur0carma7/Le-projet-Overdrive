import pygame
import math
import os
import threading
from multiplayer.serveur import *
import multiplayer.client as client_module
from multiplayer.client import send_list_client, receive_loop, send_batiment_client, send_liste_batiments_client, \
    send_liste_joueurs_client, CLIENT, send_str_client, is_connected
from core.Class.batiments import *
import time
import random
from screens.environment import CloudManager
from screens.game_logic import stop_event, on_message_recu, new_player, draw_players
from screens.render import corriger_transparence
import screens.game_logic as gl

from core.Class.player import Player
from core.Class.batiments import Batiment
from core.Class.npc import Npc
from core.saves import load_save

from screens.tutorial import run_tutorial
from screens.terminal import Terminal
from screens.utils import collision, calculer_rects_icones, souris_vers_case, joueur_a_portee, dessiner_grille, dessiner_grille_overlay, dessiner_grille_overlay_monde, dessiner_grille_overlay_ecran
from screens.game_logic import synchroniser_npcs, calculer_production
from screens.render import dessiner_monde, dessiner_hud
from core.pve import RaidManager

from screens.GUI.menu_amelioration import MenuAmelioration
from screens.GUI.menu_travail import afficher_menu_travail
import core.sounds as sound
from screens.floating_messages import FloatingMessageManager

surface_monde, camera_x, camera_y = None, None, None
TAILLE_CASE = None
batiments = []
def boucle_jeu(ecran, horloge, FPS, online: bool = False, dev_mode: bool = False):
    global batiments
    global TAILLE_CASE
    global surface_monde, camera_x, camera_y, dt
    HAUTEUR_BARRE = 100
    LARGEUR_ECRAN, HAUTEUR_ECRAN = ecran.get_size()
    dims = [LARGEUR_ECRAN, HAUTEUR_ECRAN]  # mutable pour mise a jour au resize
    players = []
    indice = 0
    herbe = None

    herbe = pygame.image.load("assets/environment/ground.png").convert()
    TAILLE_CASE = 40
    def _pos_centre_case(cx: int, cy: int):
        return ((cx + 0.5) * TAILLE_CASE, (cy + 0.5) * TAILLE_CASE)

    # S'assurer qu'un joueur existe avant tout accès à players[indice]
    if not players:
        Player.load_sprites()
        p = Player()
        p.pos = _pos_centre_case(5, 5)
        players.append(p)
        indice = 0

    images_batiments = {
        Batiment.TYPE_RESIDENTIEL: {
            1: pygame.image.load("assets/buildings/house_lvl1.png").convert_alpha(),
            2: pygame.image.load("assets/buildings/house_lvl2.png").convert_alpha(),
            3: pygame.image.load("assets/buildings/house_lvl3.png").convert_alpha()
        },
        Batiment.TYPE_GENERATEUR: {
            1: pygame.image.load("assets/buildings/generateur_lvl1.png").convert_alpha(),
            2: pygame.image.load("assets/buildings/generateur_lvl2.png").convert_alpha(),
            3: pygame.image.load("assets/buildings/generateur_lvl3.png").convert_alpha()
        },
        Batiment.TYPE_MINE: {
            1: pygame.image.load("assets/buildings/mine_lvl1.png").convert_alpha(),
            2: pygame.image.load("assets/buildings/mine_lvl2.png").convert_alpha(),
            3: pygame.image.load("assets/buildings/mine_lvl3.png").convert_alpha()
        },
        Batiment.TYPE_FARM: {
            1: corriger_transparence(pygame.image.load("assets/buildings/farm_lvl1.png").convert_alpha()),
            2: corriger_transparence(pygame.image.load("assets/buildings/farm_lvl2.png").convert_alpha()),
            3: corriger_transparence(pygame.image.load("assets/buildings/farm_lvl3.png").convert_alpha())
        },
        Batiment.TYPE_TOURELLE: {
            1: {
                "S": pygame.image.load("assets/buildings/tourelles_orientation/tourelle_centre_bas.png").convert_alpha(),
                "N": pygame.image.load("assets/buildings/tourelles_orientation/tourelle_centre_haut.png").convert_alpha(),
                "E": pygame.image.load("assets/buildings/tourelles_orientation/tourelle_droite.png").convert_alpha(),
                "W": pygame.image.load("assets/buildings/tourelles_orientation/tourelle_gauche.png").convert_alpha(),
                "NE": pygame.image.load("assets/buildings/tourelles_orientation/tourelle_droite_haut.png").convert_alpha(),
                "NW": pygame.image.load("assets/buildings/tourelles_orientation/tourelle_gauche_haut.png").convert_alpha(),
                "SE": pygame.image.load("assets/buildings/tourelles_orientation/tourelle_droite_bas.png").convert_alpha(),
                "SW": pygame.image.load("assets/buildings/tourelles_orientation/tourelle_gauche_bas.png").convert_alpha(),
            }
        },
        Batiment.TYPE_TILE: {
            1: pygame.image.load("assets/buildings/Tile.png").convert_alpha(),
        }
    }

    # Maintenant que images_batiments existe à 100%, on copie en toute sécurité le dictionnaire d'images
    # pour les niveaux d'amélioration suivants :
    images_batiments[Batiment.TYPE_TOURELLE][2] = {k: v for k, v in images_batiments[Batiment.TYPE_TOURELLE][1].items()}
    images_batiments[Batiment.TYPE_TOURELLE][3] = {k: v for k, v in images_batiments[Batiment.TYPE_TOURELLE][1].items()}

    TYPES_BATIMENTS = [
        Batiment.TYPE_RESIDENTIEL,
        Batiment.TYPE_GENERATEUR,
        Batiment.TYPE_MINE,
        Batiment.TYPE_FARM,
        Batiment.TYPE_TOURELLE,
        Batiment.TYPE_TILE,
    ]

    TAILLE_ICONE = 64
    npcs = []
    if not dev_mode and client_module.CLIENT != None:
        time.sleep(1)
        update = threading.Thread(target=on_message_recu, args=(TAILLE_CASE,), daemon=True)
        update.start()
        time.sleep(1)

    players = gl.players
    batiments = gl.batiments
    indice = gl.indice


    image_pnj = pygame.image.load("assets/pnj.png").convert_alpha()
    font_argent = pygame.font.Font("assets/fonts/Minecraft.ttf", 15)
    hud_or_img     = pygame.image.load("assets/icones/argent_icone.png").convert_alpha()
    hud_food_img   = pygame.image.load("assets/icones/nourriture_icone.png").convert_alpha()
    hud_vapeur_img = pygame.image.load("assets/icones/vapeur_icone.png").convert_alpha()
    hud_pop_img = pygame.image.load("assets/pnj.png").convert_alpha()
    save_done_img = pygame.image.load("assets/save_done.png").convert_alpha()

    cloud_manager = CloudManager(
        -4000, 4000,
        -4000, 4000
    )
    cloud_manager.load_images()
    cloud_manager.generate_clouds(count=80)

    is_new_game = not os.path.exists("save/save.json")
    if not dev_mode and os.path.exists("save/save.json"):
        if not players or indice < 0 or indice >= len(players):
            Player.load_sprites()
            p = Player()
            p.pos = _pos_centre_case(5, 5)
            players[:] = [p]
            indice = 0
        if not load_save(batiments, players[indice]):
            print("ERREUR CRITIQUE: Lecture du fichier save/save.json")
            return False

    if dev_mode:
        if not players:
            Player.load_sprites()
            p = Player()
            p.pos = _pos_centre_case(5, 5)
            players.append(p)
        players[indice].money = 5000
        players[indice].food = 5000
        players[indice].vapeur = 5000

    player = players[indice]

    synchroniser_npcs(batiments, npcs, players[indice], TAILLE_CASE)

    # Camera et zoom
    camera_x = player.pos[0] - dims[0] / 2
    camera_y = player.pos[1] - (dims[1] - HAUTEUR_BARRE) / 2
    zoom = 1.0


    if is_new_game and not dev_mode:
        def _draw_tuto_background():
            ecran.fill((0, 0, 0))
            lw, lh = dims[0], dims[1]
            largeur_vue = lw / 1.0
            hauteur_vue = (lh - HAUTEUR_BARRE) / 1.0
            surf_tuto = pygame.Surface(
                (math.ceil(largeur_vue), math.ceil(hauteur_vue))
            ).convert()
            # Sol steampunk + grille fine
            couleur_sol = (58, 44, 32)
            couleur_grille = (92, 72, 44)
            epaisseur = 2
            debut_x = int(camera_x // TAILLE_CASE) * TAILLE_CASE
            debut_y = int(camera_y // TAILLE_CASE) * TAILLE_CASE
            for ty in range(debut_y, debut_y + int(hauteur_vue) + TAILLE_CASE, TAILLE_CASE):
                for tx in range(debut_x, debut_x + int(largeur_vue) + TAILLE_CASE, TAILLE_CASE):
                    surf_tuto.fill(couleur_sol, pygame.Rect(tx - camera_x, ty - camera_y, TAILLE_CASE, TAILLE_CASE))
                    pygame.draw.rect(surf_tuto, couleur_grille,
                        (tx - camera_x, ty - camera_y, TAILLE_CASE, TAILLE_CASE), epaisseur)
            players[indice].draw_player(surf_tuto, camera_x, camera_y)
            ecran.blit(surf_tuto, (0, 0))
            pygame.draw.rect(
                ecran, (40, 40, 40),
                (0, dims[1] - HAUTEUR_BARRE, dims[0], HAUTEUR_BARRE)
            )

        result = run_tutorial(ecran, horloge, FPS, draw_background_fn=_draw_tuto_background)
        if result is False:
            stop_event.set()
            return False

    batiment_selectionne = None
    unlocked_skills = set()
    menu_amelioration = None

    terminal = Terminal(dev_mode=dev_mode)

    # Fonction utilitaire : tenter de placer un bâtiment aux coordonnées monde (mx, my)
    def _essayer_placer_batiment(sx, sy, mx, my):
        if batiment_selectionne is None:
            return
        case_x = int(mx // TAILLE_CASE)
        case_y = int(my // TAILLE_CASE)
        type_batiment = TYPES_BATIMENTS[batiment_selectionne]
        nouveau = Batiment(type_batiment, case_x, case_y)
        grid_x = case_x - (nouveau.largeur // 2)
        grid_y = case_y - (nouveau.hauteur // 2)
        nouveau.x = grid_x
        nouveau.y = grid_y
        cout = Batiment.DATA[type_batiment][1]["cout"]
        nb_villageois = sum(b.get_population() for b in batiments if b.type == Batiment.TYPE_RESIDENTIEL)
        nb_production = sum(
            1 for b in batiments
            if b.type not in (Batiment.TYPE_RESIDENTIEL, Batiment.TYPE_TILE)
        )
        production_pleine = (
            type_batiment not in (Batiment.TYPE_RESIDENTIEL, Batiment.TYPE_TILE)
            and nb_production >= nb_villageois
        )
        if not joueur_a_portee((grid_x, grid_y), players[indice], TAILLE_CASE, distance_max=10, width=nouveau.largeur, height=nouveau.hauteur):
            float_msg.error("Trop loin ! Rapprochez-vous", sx, sy - 30, player_id=indice)
        elif production_pleine:
            float_msg.warning("Pas assez de villageois !", sx, sy - 30, player_id=indice)
        elif not collision(batiments, nouveau) and players[indice].money >= cout:
            players[indice].money -= cout
            batiments.append(nouveau)
            sound.son_placement.play()
            synchroniser_npcs(batiments, npcs, players[indice], TAILLE_CASE)
            if client_module.CLIENT is not None and online:
                send_liste_batiments_client(batiments, client_module.CLIENT)
        elif collision(batiments, nouveau):
            float_msg.error("Emplacement occupe !", sx, sy - 30, player_id=indice)
        else:
            float_msg.warning(f"Pas assez d'or ! (cout : {cout})", sx, sy - 30, player_id=indice)

    # PVE
    raid_manager = RaidManager(taille_case=TAILLE_CASE)

    def _log_raid_start(n):
        terminal._log(f"[RAID] RAID #{n} en approche ! Defendez-vous !")

    def _log_wave(wave, nb):
        terminal._log(f"  [VAGUE] Vague {wave}/{RaidManager.WAVES_PER_RAID} - {nb} monstre(s) spawne(s)")

    def _log_raid_end():
        terminal._log("[OK] Raid termine. Vous avez survecu !")

    raid_manager.on_raid_start = _log_raid_start
    raid_manager.on_wave_spawn = _log_wave
    raid_manager.on_raid_end   = _log_raid_end

    float_msg = FloatingMessageManager()

    ZOOM_MIN = 0.3
    ZOOM_MAX = 2.5
    VITESSE_ZOOM = 0.1

    barre_ouverte = False
    SLIDE_SPEED = 400
    slide_offset = HAUTEUR_BARRE
    mouse_held_placing = False  # True quand le clic gauche est maintenu en mode placement
    btn_batiments_rect = pygame.Rect(0, 0, 60, 60)
    skill_btn_rect = pygame.Rect(0, 0, 60, 60)

    rects_icones = calculer_rects_icones(dims, HAUTEUR_BARRE, TAILLE_ICONE, slide_offset)
    en_cours = True
    acc_argent   = 0.0
    acc_food     = 0.0
    acc_vapeur   = 0.0
    save_done_timer = 0.0
    attack_cooldown = 0.0
    ATTACK_COOLDOWN_MAX = 0.6  # secondes entre chaque attaque

    ambient_playlist = list(range(len(sound.ambient_musics)))
    random.shuffle(ambient_playlist)
    current_playlist_index = 0
    ambient_delay_timer = 0.0

    surface_monde = None
    surface_monde_size = None  # (w, h) en px monde (avant scaling écran)

    while en_cours:
        dt = horloge.tick(FPS) / 1000.0
        save_done_timer = max(0, save_done_timer - dt)
        attack_cooldown = max(0.0, attack_cooldown - dt)

        if players != gl.players:
            players = gl.players
        if batiments != gl.batiments:
            batiments = gl.batiments
        if indice != gl.indice:
            indice = gl.indice

        prec = (players[indice].pos, players[indice].path)

        """# Si l'indice joueur change (online) ou si la liste joueurs est mise à jour
        if not players:
            Player.load_sprites()
            p = Player()
            p.pos = _pos_centre_case(5, 5)
            players.append(p)
            indice = 0
        elif indice < 0 or indice >= len(players):
            indice = max(0, min(indice, len(players) - 1))"""
        player = players[indice]

        # animation d'ouverture/fermeture de la barre de batiments
        cible_offset = 0 if barre_ouverte else HAUTEUR_BARRE
        if slide_offset < cible_offset:
            slide_offset = min(cible_offset, slide_offset + SLIDE_SPEED * dt)
        elif slide_offset > cible_offset:
            slide_offset = max(cible_offset, slide_offset - SLIDE_SPEED * dt)
        rects_icones[:] = calculer_rects_icones(dims, HAUTEUR_BARRE, TAILLE_ICONE, int(slide_offset))

        if not pygame.mixer.music.get_busy():
            if ambient_delay_timer > 0:
                ambient_delay_timer -= dt
            else:
                index = ambient_playlist[current_playlist_index]
                sound.play_ambient(index, loop=0)
                current_playlist_index += 1
                if current_playlist_index >= len(ambient_playlist):
                    random.shuffle(ambient_playlist)
                    current_playlist_index = 0
                ambient_delay_timer = 3.0

        acc_argent, acc_food, acc_vapeur = calculer_production(batiments, players[indice], dt, acc_argent, acc_food, acc_vapeur, npcs=npcs, raid_manager=raid_manager)
        cloud_manager.update(dt)

        camera_x = player.pos[0] - (dims[0] / zoom) / 2
        camera_y = player.pos[1] - ((dims[1] - HAUTEUR_BARRE) / zoom) / 2


        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                stop_event.set()
                return False

            if event.type == pygame.VIDEORESIZE:
                dims[0], dims[1] = event.w, event.h
                rects_icones[:] = calculer_rects_icones(dims, HAUTEUR_BARRE, TAILLE_ICONE, int(slide_offset))

            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                from screens import game_logic
                game_logic.toggle_fullscreen()
                continue

            # terminal toggle (mode dev uniquement)
            if event.type == pygame.KEYDOWN and event.unicode == "²" and dev_mode:
                terminal.toggle()
                continue

            if terminal.visible:
                if terminal.handle_event(event, player, batiments, extra_ctx={"raid_manager": raid_manager}):
                    continue
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    terminal.toggle()
                    continue
                continue

            if menu_amelioration:
                result = menu_amelioration.handle_event(event)
                if result == "close":
                    menu_amelioration = None
                    continue
                if result == "supprimer":
                    batiments.remove(menu_amelioration.batiment)
                    cashback = 0
                    for k in range(menu_amelioration.batiment.niveau):
                        cashback += Batiment.DATA[menu_amelioration.batiment.type][1+k]["cout"]
                    players[indice].money += cashback
                    synchroniser_npcs(batiments, npcs, players[indice], TAILLE_CASE)
                    if client_module.CLIENT is not None and online:
                        send_liste_batiments_client(batiments, client_module.CLIENT)
                    menu_amelioration = None
                    continue
                if result == "upgrade":
                    synchroniser_npcs(batiments, npcs, players[indice], TAILLE_CASE)
                    if client_module.CLIENT is not None and online:
                        send_liste_batiments_client(batiments, client_module.CLIENT)
                    menu_amelioration = None
                    continue
                continue

            # assignation manuelle des villageois
            if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
                afficher_menu_travail(ecran, batiments, npcs, players[indice])
                continue

            # Sélection rapide de bâtiment avec les touches 1-9
            if event.type == pygame.KEYDOWN and pygame.K_1 <= event.key <= pygame.K_9:
                index_touche = event.key - pygame.K_1  # 0-based
                if index_touche < len(TYPES_BATIMENTS):
                    if batiment_selectionne == index_touche:
                        batiment_selectionne = None  # désélectionner si déjà actif
                        mouse_held_placing = False
                    else:
                        batiment_selectionne = index_touche
                        barre_ouverte = True  # ouvrir la barre automatiquement
                continue

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                from screens.pause import menu_pause
                screenshot = ecran.copy()
                if online:
                    etat_pause = menu_pause(ecran, horloge, FPS, batiments, online, players[indice], screenshot)
                    pass
                else:
                    etat_pause = menu_pause(ecran, horloge, FPS, batiments, online, players[indice], screenshot)
                if etat_pause == "jeu_save_done":
                    save_done_timer = 1.5  # show for 1.5 seconds
                elif not etat_pause:
                    stop_event.set()
                    return False
                elif etat_pause == "menu":
                    stop_event.set()
                    return True

            if event.type == pygame.MOUSEWHEEL:
                ancien_zoom = zoom
                zoom += event.y * VITESSE_ZOOM
                zoom = max(ZOOM_MIN, min(ZOOM_MAX, zoom))

                sx, sy = pygame.mouse.get_pos()
                souris_monde_x = camera_x + sx / ancien_zoom
                souris_monde_y = camera_y + sy / ancien_zoom
                camera_x = souris_monde_x - sx / zoom
                camera_y = souris_monde_y - sy / zoom

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_held_placing = False

            #clic droit
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                if batiment_selectionne is not None:
                    batiment_selectionne = None
                    print("Selection annulee")

                else:
                    sx, sy = pygame.mouse.get_pos()
                    case = souris_vers_case((sx, sy), camera_x, camera_y, zoom, TAILLE_CASE)
                    limite_ui = HAUTEUR_ECRAN - (HAUTEUR_BARRE - slide_offset)
                    if sy < limite_ui:
                        if not players[indice].a_star(case, TAILLE_CASE):
                            sx2, sy2 = pygame.mouse.get_pos()
                            float_msg.info("Chemin bloque", sx2, sy2 - 30, player_id=indice)



# Clic gauche
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if batiment_selectionne is not None:
                    mouse_held_placing = True  # démarrer le placement continu

                sx, sy = pygame.mouse.get_pos()

                if btn_batiments_rect.collidepoint(sx, sy):
                    barre_ouverte = not barre_ouverte
                    if not barre_ouverte:
                        batiment_selectionne = None
                    continue

                if skill_btn_rect.collidepoint(sx, sy):
                    from screens.skill_tree import afficher_skill_tree
                    unlocked_skills = afficher_skill_tree(ecran, player, unlocked_skills, Batiment.DATA)
                    continue

                clic_barre = False
                # N'autoriser le clic sur les icones que si la barre est visible
                if barre_ouverte and slide_offset < HAUTEUR_BARRE:
                    for i, rect in enumerate(rects_icones):
                        if rect.collidepoint(sx, sy):
                            batiment_selectionne = None if batiment_selectionne == i else i
                            clic_barre = True
                            break


                # attaque
                monster_clicked = False
                if not clic_barre and raid_manager is not None and attack_cooldown <= 0.0:
                    world_sx = camera_x + sx / zoom
                    world_sy = camera_y + sy / zoom
                    for m in raid_manager.monsters:
                        if not m.alive:
                            continue
                        # Calcul de la distance joueur-monstre
                        dist_joueur = ((player.pos[0] - m.x) ** 2 + (player.pos[1] - m.y) ** 2) ** 0.5
                        PORTEE_ATTAQUE_JOUEUR = 80  # px — réduit pour le hand_cannon (corps à corps)
                        if dist_joueur > PORTEE_ATTAQUE_JOUEUR:
                            continue
                        # Rect en coordonnées écran
                        m_screen_rect = m.get_screen_rect(camera_x, camera_y)
                        zoomed_rect = pygame.Rect(
                            int(m_screen_rect.x * zoom),
                            int(m_screen_rect.y * zoom),
                            int(m_screen_rect.width * zoom),
                            int(m_screen_rect.height * zoom),
                        )
                        # Agrandir la hitbox pour faciliter le clic
                        zoomed_rect.inflate_ip(12, 12)
                        if zoomed_rect.collidepoint(sx, sy):
                            # Déclencher l'animation d'attaque
                            player.trigger_attack_anim()
                            # Orienter le joueur vers le monstre
                            if m.x < player.pos[0]:
                                player.direction = "left"
                            else:
                                player.direction = "right"
                            # Calcul des dégâts avec critique
                            import random as _rnd
                            dmg = player.raw_damage
                            is_crit = _rnd.randint(1, 100) <= player.crit_chance
                            if is_crit:
                                dmg = int(dmg * (1 + player.crit_damage / 100))
                            m.take_damage(dmg)
                            attack_cooldown = ATTACK_COOLDOWN_MAX
                            # Afficher le chiffre de dégâts
                            from core.pve import DamageNumber
                            raid_manager.damage_numbers.append(
                                DamageNumber(m.x, m.y - 20, dmg, is_crit)
                            )
                            monster_clicked = True


                # Placement du bâtiment sur la grille
                limite_ui = HAUTEUR_ECRAN - (HAUTEUR_BARRE - slide_offset)
                if not clic_barre and not monster_clicked and sy < limite_ui:
                    mx = camera_x + sx / zoom
                    my = camera_y + sy / zoom

                    if batiment_selectionne is not None:
                        _essayer_placer_batiment(sx, sy, mx, my)

                    else:
                        for B in batiments:
                            rect = B.get_rect_pixel(TAILLE_CASE)
                            rect.x -= camera_x
                            rect.y -= camera_y
                            mx = camera_x + sx / zoom
                            my = camera_y + sy / zoom

                            rect = B.get_rect_pixel(TAILLE_CASE)

                            if rect.collidepoint(mx, my):
                                if not joueur_a_portee((B.x, B.y), players[indice], TAILLE_CASE, distance_max=10, width=B.largeur, height=B.hauteur):
                                    float_msg.error("Trop loin ! Rapprochez-vous", sx, sy - 30, player_id=indice)
                                    break
                                menu_amelioration = MenuAmelioration(ecran, B, sx, players[indice])
                                break
                #Boutton SELL pour vendre les batiments quand c'est selectionné
                mode_sell = False

        player.update(TAILLE_CASE, dt)
        player.update_anim(dt)

        # Placement continu quand le clic est maintenu (drag)
        if mouse_held_placing and batiment_selectionne is not None:
            sx, sy = pygame.mouse.get_pos()
            limite_ui = HAUTEUR_ECRAN - (HAUTEUR_BARRE - slide_offset)
            if sy < limite_ui:
                mx = camera_x + sx / zoom
                my = camera_y + sy / zoom
                _essayer_placer_batiment(sx, sy, mx, my)


        # mort
        if player.hp <= 0:
            from screens.game_over import afficher_game_over
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            result = afficher_game_over(ecran, player)
            if result == "restart":
                # --- Pénalité : perte de 30% des ressources ---
                player.money  = max(0, int(player.money  * 0.70))
                player.food   = max(0, int(player.food   * 0.70))
                player.vapeur = max(0, int(player.vapeur * 0.70))
                # Réinitialiser le joueur et le raid
                player.hp = player.hp_max
                player.path = []
                player.pos = _pos_centre_case(5, 5)
                raid_manager.monsters.clear()
                raid_manager.damage_numbers.clear()
                raid_manager._raid_active = False
                raid_manager._auto_timer = 30.0
                # Message informatif
                W2, H2 = dims[0] // 2, dims[1] // 2
                float_msg.warning("-30% de ressources perdues !", W2, H2 - 40)
                continue
            else:
                stop_event.set()
                sound.stop_ambient()
                return False

        # PVE update
        raid_manager.update(players, dt)

        ecran.fill((0, 0, 0))

        largeur_vue = dims[0] / zoom
        hauteur_vue = dims[1] / zoom

        needed_size = (math.ceil(largeur_vue), math.ceil(hauteur_vue))
        if surface_monde is None or surface_monde_size != needed_size:
            surface_monde = pygame.Surface(needed_size).convert()
            surface_monde_size = needed_size


        dessiner_grille(surface_monde, camera_x, camera_y, dims, 0, zoom, herbe, TAILLE_CASE)

        cloud_manager.draw(surface_monde, camera_x, camera_y)

        dessiner_monde(surface_monde, batiments, images_batiments, camera_x, camera_y, TAILLE_CASE,
                       batiment_selectionne, TYPES_BATIMENTS, players, npcs, image_pnj, dt, zoom,
                       raid_manager=raid_manager)

        if surface_monde_size == (dims[0], dims[1]):
            surface_affichee = surface_monde
        else:
            surface_affichee = pygame.transform.scale(surface_monde, (dims[0], dims[1]))

        ecran.blit(surface_affichee, (0, 0))
        # Grille (mode placement) dessinée en pixels écran pour éviter les artefacts de scaling.
        if batiment_selectionne is not None:
            hauteur_ui = int(HAUTEUR_BARRE - slide_offset)
            dessiner_grille_overlay_ecran(ecran, camera_x, camera_y, dims, hauteur_ui, zoom, TAILLE_CASE)

        mx_cur, my_cur = pygame.mouse.get_pos()
        hover_monster = False
        if raid_manager is not None:
            for m in raid_manager.monsters:
                if not m.alive:
                    continue
                dist_joueur = ((player.pos[0] - m.x) ** 2 + (player.pos[1] - m.y) ** 2) ** 0.5
                if dist_joueur > 80:
                    continue
                m_rect = m.get_screen_rect(camera_x, camera_y)
                zoomed_m_rect = pygame.Rect(
                    int(m_rect.x * zoom), int(m_rect.y * zoom),
                    int(m_rect.width * zoom), int(m_rect.height * zoom)
                )
                zoomed_m_rect.inflate_ip(12, 12)
                if zoomed_m_rect.collidepoint(mx_cur, my_cur):
                    hover_monster = True
                    break
        if hover_monster:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        float_msg.update(dt)

        # === MODIFIEZ CET APPEL TOUT À LA FIN DE .\screens\jeu.py ===
        dessiner_hud(ecran, dims, HAUTEUR_BARRE, rects_icones, batiment_selectionne, images_batiments, TYPES_BATIMENTS,
                     TAILLE_ICONE, player, font_argent, hud_or_img, hud_food_img, hud_vapeur_img, hud_pop_img,
                     save_done_img, save_done_timer, barre_ouverte, int(slide_offset), btn_batiments_rect,
                     skill_btn_rect, raid_manager=raid_manager, batiments_list=batiments)
        float_msg.draw(ecran)

        terminal.draw(ecran, dt)
        if menu_amelioration:
            menu_amelioration.draw(ecran)

        pygame.display.flip()

        if player.pos != prec[0] or player.path != prec[1]:
            print(player)
            try:
                send_liste_joueurs_client(players, client_module.CLIENT)
            except:
                pass

    stop_event.set()
    sound.stop_ambient()
    return True