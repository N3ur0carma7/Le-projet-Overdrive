import pygame
import math
from screens.utils import collision, souris_vers_case, joueur_a_portee
from core.Class.batiments import Batiment

def charger_spritesheet_construction(path):
    sheet = pygame.image.load(path).convert_alpha()

    cols = 4
    rows = 4
    frame_w = sheet.get_width() // cols
    frame_h = sheet.get_height() // rows

    frames = []

    for row in range(rows):
        for col in range(cols):
            rect = pygame.Rect(
                col * frame_w,
                row * frame_h + 32,
                frame_w,
                frame_h - 32
            )

            frame = sheet.subsurface(rect).copy()
            frame.set_colorkey((0, 0, 0))
            frames.append(frame)

    return frames

import screens.game_logic as gl
def corriger_transparence(surface):
    width, height = surface.get_size()
    for x in range(width):
        for y in range(height):
            color = surface.get_at((x, y))
            if color.a < 20:
                surface.set_at((x, y), (0, 0, 0, 0))
    return surface

def _scale_contain(img: pygame.Surface, max_w: int, max_h: int) -> pygame.Surface:
    iw, ih = img.get_size()
    if iw <= 0 or ih <= 0 or max_w <= 0 or max_h <= 0:
        return img
    scale = min(max_w / iw, max_h / ih)
    new_w = max(1, int(round(iw * scale)))
    new_h = max(1, int(round(ih * scale)))
    if new_w == iw and new_h == ih:
        return img
    return pygame.transform.smoothscale(img, (new_w, new_h))


def _get_scaled_batiment_image(images_batiments, type_batiment, niveau, footprint_w_px, footprint_h_px, cache,
                               bat_obj=None):
    from core.Class.batiments import Batiment

    type_tourelle = getattr(Batiment, "TYPE_TOURELLE", "tourelle")
    direction = getattr(bat_obj, "direction", "E") if type_batiment == type_tourelle else "E"

    key = (type_batiment, niveau, footprint_w_px, footprint_h_px, direction)
    if key in cache:
        return cache[key]

    facteur = 1.0
    if type_batiment in Batiment.DATA:
        facteur = Batiment.DATA[type_batiment].get("scale_visuel", 1.0)

    if type_batiment == type_tourelle:
        try:
            base = images_batiments[type_batiment][niveau][direction]
        except (KeyError, TypeError):
            img_dict = images_batiments[type_batiment][niveau]
            base = img_dict if not isinstance(img_dict, dict) else (img_dict.get("S") or list(img_dict.values())[0])
    else:
        base = images_batiments[type_batiment][niveau]

    largeur_max_visuelle = int(footprint_w_px * facteur)
    hauteur_max_visuelle = int(footprint_h_px * facteur)


    scaled = _scale_contain(base, largeur_max_visuelle, largeur_max_visuelle)

    cache[key] = scaled
    return scaled

def dessiner_monde(surface_monde, batiments, images_batiments, camera_x, camera_y, TAILLE_CASE, batiment_selectionne, TYPES_BATIMENTS, players, npcs, image_pnj, dt, zoom, raid_manager=None, construction_gear=None, ressources_sol=None, images_ressources_sol=None, active_player=None):
    from screens.utils import collision, souris_vers_case, joueur_a_portee
    from core.Class.batiments import Batiment

    scaled_cache = {}

    if ressources_sol is not None and images_ressources_sol is not None:
        for res in ressources_sol:
            img = images_ressources_sol[res["type"]]

            if res["type"] == "coffre":
                taille = int(TAILLE_CASE * 1.2)
            else:
                taille = int(TAILLE_CASE * 0.75)

            img_scaled = pygame.transform.smoothscale(
                img,
                (taille, taille)
            )

            rx = res["x"] * TAILLE_CASE - camera_x + (TAILLE_CASE - taille) / 2
            ry = res["y"] * TAILLE_CASE - camera_y + (TAILLE_CASE - taille) / 2

            surface_monde.blit(img_scaled, (rx, ry))

    for B in batiments:
        footprint_w_px = B.largeur * TAILLE_CASE
        footprint_h_px = B.hauteur * TAILLE_CASE

        if hasattr(B, "en_construction") and B.en_construction:
            B.construction_finie()

            image = pygame.Surface((footprint_w_px, footprint_h_px), pygame.SRCALPHA)

            angle = (pygame.time.get_ticks() * 0.12) % 360
            gear_size = int(min(footprint_w_px, footprint_h_px) * 0.7)

            gear = pygame.transform.smoothscale(
                construction_gear,
                (gear_size, gear_size)
            )

            gear_rotated = pygame.transform.rotate(gear, angle)
        else:
            image = _get_scaled_batiment_image(
                images_batiments, B.type, B.niveau,
                footprint_w_px, footprint_h_px,
                scaled_cache, bat_obj=B
            )
            gear_rotated = None

        x = B.x * TAILLE_CASE - camera_x + (footprint_w_px - image.get_width()) / 2
        y = B.y * TAILLE_CASE - camera_y + (footprint_h_px - image.get_height()) / 2

        surface_monde.blit(image, (x, y))

        if hasattr(B, "en_construction") and B.en_construction and gear_rotated is not None:
            gx = B.x * TAILLE_CASE - camera_x + (footprint_w_px - gear_rotated.get_width()) / 2
            gy = B.y * TAILLE_CASE - camera_y + (footprint_h_px - gear_rotated.get_height()) / 2

            surface_monde.blit(gear_rotated, (gx, gy))

        if hasattr(B, "en_construction") and B.en_construction:
            progression = B.progression_construction()

            barre_w = footprint_w_px
            barre_h = 6
            barre_x = B.x * TAILLE_CASE - camera_x
            barre_y = B.y * TAILLE_CASE - camera_y - 10

            pygame.draw.rect(surface_monde, (40, 40, 40), (barre_x, barre_y, barre_w, barre_h))
            pygame.draw.rect(surface_monde, (80, 220, 80), (barre_x, barre_y, barre_w * progression, barre_h))

    # fantome
    if batiment_selectionne is not None:
        sx, sy = pygame.mouse.get_pos()
        case = souris_vers_case((sx, sy), camera_x, camera_y, zoom, TAILLE_CASE)
        type_batiment = TYPES_BATIMENTS[batiment_selectionne]
        test_batiment = Batiment(type_batiment, case[0], case[1])
        grid_x = case[0] - (test_batiment.largeur // 2)
        grid_y = case[1] - (test_batiment.hauteur // 2)
        test_batiment.x = grid_x
        test_batiment.y = grid_y
        footprint_w_px = test_batiment.largeur * TAILLE_CASE
        footprint_h_px = test_batiment.hauteur * TAILLE_CASE
        image = _get_scaled_batiment_image(
            images_batiments, type_batiment, 1, footprint_w_px, footprint_h_px, scaled_cache, bat_obj=test_batiment
        )
        image_fantome = image.copy()
        collision_ressource = False

        if ressources_sol is not None:
            test_rect = pygame.Rect(
                test_batiment.x,
                test_batiment.y,
                test_batiment.largeur,
                test_batiment.hauteur
            )

            for res in ressources_sol:
                res_rect = pygame.Rect(
                    res["x"],
                    res["y"],
                    1,
                    1
                )

                if test_rect.colliderect(res_rect):
                    collision_ressource = True
                    break

        tourelle_bloquee = (
                type_batiment == Batiment.TYPE_TOURELLE
                and not Batiment.DATA[Batiment.TYPE_TOURELLE].get("unlocked", False)
        )

        if collision(batiments, test_batiment) or collision_ressource or tourelle_bloquee:
            image_fantome.fill((255, 0, 0, 120), special_flags=pygame.BLEND_RGBA_MULT)
        else:
            player_for_range = active_player
            if player_for_range is None:
                if isinstance(players, (list, tuple)) and players:
                    player_for_range = players[0]
                else:
                    player_for_range = players
            if player_for_range is not None and not joueur_a_portee((grid_x, grid_y), player_for_range, TAILLE_CASE, distance_max=10, width=test_batiment.largeur, height=test_batiment.hauteur):
                image_fantome.fill((255, 140, 0, 120), special_flags=pygame.BLEND_RGBA_MULT)

        x = grid_x * TAILLE_CASE - camera_x + (footprint_w_px - image.get_width()) / 2
        y = grid_y * TAILLE_CASE - camera_y + (footprint_h_px - image.get_height()) / 2

        surface_monde.blit(image_fantome, (x, y))
    actual_players = players
    if actual_players is None:
        actual_players = []
    elif not isinstance(actual_players, (list, tuple)):
        actual_players = [actual_players]

    for player_obj in actual_players:
        player_obj.draw_player(surface_monde, camera_x, camera_y)


    for npc in npcs:
        npc.update(dt)
        nx = int(npc.monde_x - camera_x)
        ny = int(npc.monde_y - camera_y)
        sw, sh = surface_monde.get_size()
        if -80 < nx < sw + 80 and -80 < ny < sh + 80:
            npc.dessiner_monde(surface_monde, camera_x, camera_y, image_pnj)

    # Monstres PVE
    if raid_manager is not None:
        raid_manager.draw(surface_monde, camera_x, camera_y)


def dessiner_hud(ecran, dims, hauteur_barre, rects_icones, batiment_selectionne, images_batiments, TYPES_BATIMENTS,
                 taille_icone, player, font_argent, hud_or_img, hud_food_img, hud_vapeur_img, hud_pop_img,
                 save_done_img, save_done_timer, barre_ouverte=True, slide_offset=0, btn_batiments_rect=None,
                 skill_btn_rect=None, inventory_btn_rect=None, raid_manager=None, batiments_list=None):
    # 1. Dessin de la barre du bas
    if slide_offset < hauteur_barre:
        barre_surf = pygame.Surface((dims[0], hauteur_barre), pygame.SRCALPHA)
        barre_surf.fill((30, 30, 30, 210))
        ecran.blit(barre_surf, (0, dims[1] - hauteur_barre + slide_offset))

    # 2. Dessin des icônes de construction dans la barre
    for i, rect in enumerate(rects_icones):
        couleur = (200, 200, 80) if i == batiment_selectionne else (100, 100, 100)
        pygame.draw.rect(ecran, couleur, rect.inflate(8, 8))

        type_actuel = TYPES_BATIMENTS[i]
        img_base = images_batiments[type_actuel][1]
        if isinstance(img_base, dict):
            img_base = img_base.get("S") or list(img_base.values())[0]

        icone = pygame.transform.smoothscale(img_base, (taille_icone, taille_icone))
        ecran.blit(icone, rect)
        nom = TYPES_BATIMENTS[i]
        cout = Batiment.DATA[nom][1]["cout"]

        font_small = pygame.font.Font("assets/fonts/Minecraft.ttf", 10)

        texte_nom = font_small.render(nom, True, (255, 255, 255))
        texte_prix = font_small.render(str(cout) + " or", True, (255, 220, 80))

        ecran.blit(texte_nom, (
            rect.centerx - texte_nom.get_width() // 2,
            rect.y - 18
        ))

        ecran.blit(texte_prix, (
            rect.centerx - texte_prix.get_width() // 2,
            rect.bottom + 4
        ))

    # 3. Préparation de la police pour les ressources
    try:
        font_ressources = pygame.font.Font("assets/fonts/Minecraft.ttf", 22)
    except Exception:
        font_ressources = pygame.font.SysFont("arial", 22, bold=True)

    marge_hud = 15

    # 4. Récupération de la population via la liste synchronisée
    if batiments_list is not None:
        total_villageois = sum(
            b.get_population()
            for b in batiments_list
            if b.type == Batiment.TYPE_RESIDENTIEL and not (hasattr(b, "en_construction") and b.en_construction)
        )
    else:
        total_villageois = 0

    ressources_hud = [
        (str(total_villageois), (180, 220, 255), hud_pop_img, 52),
        (str(int(player.money)), (255, 235, 80), hud_or_img, 64),
        (str(int(player.food)), (255, 235, 80), hud_food_img, 64),
        (str(int(player.vapeur)), (255, 235, 80), hud_vapeur_img, 64)
    ]

    marge_inter_icones = 140

    for i, (valeur, couleur, img, taille_icone_custom) in enumerate(ressources_hud):
        icone_calibree = pygame.transform.smoothscale(img, (taille_icone_custom, taille_icone_custom))
        iw, ih = icone_calibree.get_size()

        hud_x = dims[0] - 160 - (len(ressources_hud) - 1 - i) * marge_inter_icones

        if i == 0:
            hud_x += 35
            y_ajuste = marge_hud - 16
        else:
            y_ajuste = marge_hud + (32 - taille_icone_custom) // 2

        ecran.blit(icone_calibree, (hud_x, y_ajuste))

        texte = font_ressources.render(valeur, True, couleur)
        tx = hud_x + iw + 6

        text_height = texte.get_height()
        ty = marge_hud + (32 - text_height) // 2

        ecran.blit(texte, (tx, ty))
    # 6. Bouton toggle barre bâtiments (BUILD / CLOSE)
    BTN_SIZE = 80
    BTN_MARGE = 12
    btn_x = dims[0] - BTN_SIZE - BTN_MARGE
    btn_y = dims[1] - BTN_SIZE - BTN_MARGE

    btn_couleur = (160, 90, 30) if barre_ouverte else (40, 140, 40)
    pygame.draw.rect(ecran, btn_couleur, pygame.Rect(btn_x, btn_y, BTN_SIZE, BTN_SIZE), border_radius=10)
    pygame.draw.rect(ecran, (220, 220, 180), pygame.Rect(btn_x, btn_y, BTN_SIZE, BTN_SIZE), 3, border_radius=10)

    btn_font = pygame.font.Font("assets/fonts/Minecraft.ttf", 11)
    label = "CLOSE" if barre_ouverte else "BUILD"
    lbl_surf = btn_font.render(label, True, (255, 255, 255))
    lbl_x = btn_x + (BTN_SIZE - lbl_surf.get_width()) // 2
    lbl_y = btn_y + (BTN_SIZE - lbl_surf.get_height()) // 2
    ecran.blit(lbl_surf, (lbl_x, lbl_y))

    if btn_batiments_rect is not None:
        btn_batiments_rect.update(btn_x, btn_y, BTN_SIZE, BTN_SIZE)

    # 7. Bouton skill tree (SKILLS)
    skill_btn_x = btn_x - BTN_SIZE - BTN_MARGE
    skill_btn_y = btn_y
    skill_btn_couleur = (100, 100, 200)
    pygame.draw.rect(ecran, skill_btn_couleur, pygame.Rect(skill_btn_x, skill_btn_y, BTN_SIZE, BTN_SIZE),
                     border_radius=10)
    pygame.draw.rect(ecran, (220, 220, 180), pygame.Rect(skill_btn_x, skill_btn_y, BTN_SIZE, BTN_SIZE), 3,
                     border_radius=10)

    skill_label = "SKILLS"
    skill_lbl_surf = btn_font.render(skill_label, True, (255, 255, 255))
    skill_lbl_x = skill_btn_x + (BTN_SIZE - skill_lbl_surf.get_width()) // 2
    skill_lbl_y = skill_btn_y + (BTN_SIZE - skill_lbl_surf.get_height()) // 2
    ecran.blit(skill_lbl_surf, (skill_lbl_x, skill_lbl_y))

    if skill_btn_rect is not None:
        skill_btn_rect.update(skill_btn_x, skill_btn_y, BTN_SIZE, BTN_SIZE)
    # 8. Bouton inventaire (INV)
    inv_btn_x = skill_btn_x - BTN_SIZE - BTN_MARGE
    inv_btn_y = btn_y
    inv_btn_couleur = (140, 90, 180)

    pygame.draw.rect(ecran, inv_btn_couleur, pygame.Rect(inv_btn_x, inv_btn_y, BTN_SIZE, BTN_SIZE), border_radius=10)
    pygame.draw.rect(ecran, (220, 220, 180), pygame.Rect(inv_btn_x, inv_btn_y, BTN_SIZE, BTN_SIZE), 3, border_radius=10)

    inv_label = "INV"
    inv_lbl_surf = btn_font.render(inv_label, True, (255, 255, 255))
    inv_lbl_x = inv_btn_x + (BTN_SIZE - inv_lbl_surf.get_width()) // 2
    inv_lbl_y = inv_btn_y + (BTN_SIZE - inv_lbl_surf.get_height()) // 2
    ecran.blit(inv_lbl_surf, (inv_lbl_x, inv_lbl_y))

    if inventory_btn_rect is not None:
        inventory_btn_rect.update(inv_btn_x, inv_btn_y, BTN_SIZE, BTN_SIZE)

    # 8. Affichage de la notification de sauvegarde (popup dessinée)
    if save_done_timer > 0:
        popup_font = pygame.font.Font("assets/fonts/Minecraft.ttf", 14)
        popup_text = "Partie sauvegardee !"
        text_surf = popup_font.render(popup_text, True, (255, 255, 200))
        padding_x, padding_y = 14, 10
        popup_w = text_surf.get_width() + padding_x * 2
        popup_h = text_surf.get_height() + padding_y * 2
        popup_x = (ecran.get_width() - popup_w) // 2   # centré horizontalement
        popup_y = ecran.get_height() - popup_h - 20     # 20px au-dessus du bord bas        # Fond semi-transparent
        popup_bg = pygame.Surface((popup_w, popup_h), pygame.SRCALPHA)
        popup_bg.fill((20, 20, 20, 210))
        ecran.blit(popup_bg, (popup_x, popup_y))
        # Bordure verte
        pygame.draw.rect(ecran, (80, 200, 100), (popup_x, popup_y, popup_w, popup_h), 2, border_radius=4)
        # Texte
        ecran.blit(text_surf, (popup_x + padding_x, popup_y + padding_y))

    # 9. Barre de vie du joueur
    hp_bar_w = 200
    hp_bar_h = 14
    hp_bar_x = 12
    hp_bar_y = 20
    hp_ratio = max(0.0, player.hp / player.hp_max)

    pygame.draw.rect(ecran, (60, 10, 10), (hp_bar_x, hp_bar_y, hp_bar_w, hp_bar_h), border_radius=4)
    if hp_ratio > 0:
        bar_color = (200, 0, 0) if hp_ratio > 0.5 else (220, 180, 30) if hp_ratio > 0.25 else (220, 50, 50)
        pygame.draw.rect(ecran, bar_color, (hp_bar_x, hp_bar_y, int(hp_bar_w * hp_ratio), hp_bar_h), border_radius=4)
    pygame.draw.rect(ecran, (180, 180, 180), (hp_bar_x, hp_bar_y, hp_bar_w, hp_bar_h), 1, border_radius=4)
    hp_txt = font_argent.render(f"HP {int(player.hp)}/{player.hp_max}", True, (255, 255, 255))
    ecran.blit(hp_txt, (hp_bar_x + 4, hp_bar_y - hp_txt.get_height() - 2))

    # 10. Indicateur de raid
    if raid_manager is not None and not raid_manager._raid_active:
        time_left = int(raid_manager.time_to_next_raid)
        minutes = time_left // 60
        seconds = time_left % 60
        raid_txt = f"Prochain raid dans {minutes}:{seconds:02d}"
        raid_surf = font_argent.render(raid_txt, True, (255, 210, 120))
        rx = dims[0] // 2 - raid_surf.get_width() // 2
        ry = 6
        bg = pygame.Surface((raid_surf.get_width() + 16, raid_surf.get_height() + 8), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 160))
        ecran.blit(bg, (rx - 8, ry - 4))
        ecran.blit(raid_surf, (rx, ry))
    elif raid_manager is not None and raid_manager._raid_active:
        nb_monstres = len(raid_manager.monsters)
        wave_txt = f"RAID  Vague {raid_manager._wave_index}/{raid_manager.WAVES_PER_RAID}  Monstres: {nb_monstres}"
        raid_surf = font_argent.render(wave_txt, True, (255, 80, 80))
        rx = dims[0] // 2 - raid_surf.get_width() // 2
        ry = 6
        bg = pygame.Surface((raid_surf.get_width() + 16, raid_surf.get_height() + 8), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 160))
        ecran.blit(bg, (rx - 8, ry - 4))
        ecran.blit(raid_surf, (rx, ry))