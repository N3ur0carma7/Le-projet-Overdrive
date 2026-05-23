import pygame
import core.Class.batiments as Batiment
import math
from screens.utils import collision, souris_vers_case, joueur_a_portee
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

    if type_batiment == type_tourelle:
        try:
            base = images_batiments[type_batiment][niveau][direction]
        except (KeyError, TypeError):
            img_dict = images_batiments[type_batiment][niveau]
            base = img_dict if not isinstance(img_dict, dict) else (img_dict.get("S") or list(img_dict.values())[0])

        footprint_w_px = int(footprint_w_px * 1.5)
        footprint_h_px = int(footprint_h_px * 1.5)
    else:
        base = images_batiments[type_batiment][niveau]

    scaled = _scale_contain(base, footprint_w_px, footprint_h_px)
    cache[key] = scaled
    return scaled

def dessiner_monde(surface_monde, batiments, images_batiments, camera_x, camera_y, TAILLE_CASE, batiment_selectionne, TYPES_BATIMENTS, players, npcs, image_pnj, dt, zoom, raid_manager=None):
    from screens.utils import collision, souris_vers_case, joueur_a_portee
    from core.Class.batiments import Batiment

    # Cache par frame pour éviter de rescaler en boucle
    scaled_cache = {}
    player = players[gl.indice]
    for B in batiments:
        footprint_w_px = B.largeur * TAILLE_CASE
        footprint_h_px = B.hauteur * TAILLE_CASE
        image = _get_scaled_batiment_image(
            images_batiments, B.type, B.niveau, footprint_w_px, footprint_h_px, scaled_cache, bat_obj=B
        )
        x = B.x * TAILLE_CASE - camera_x + (footprint_w_px - image.get_width()) / 2
        y = B.y * TAILLE_CASE - camera_y + (footprint_h_px - image.get_height()) / 2
        surface_monde.blit(image, (x, y))

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
        if collision(batiments, test_batiment):
            image_fantome.fill((255, 0, 0, 120), special_flags=pygame.BLEND_RGBA_MULT)
        elif not joueur_a_portee((grid_x, grid_y), player, TAILLE_CASE, distance_max=10, width=test_batiment.largeur, height=test_batiment.hauteur):
            image_fantome.fill((255, 140, 0, 120), special_flags=pygame.BLEND_RGBA_MULT)

        x = grid_x * TAILLE_CASE - camera_x + (footprint_w_px - image.get_width()) / 2
        y = grid_y * TAILLE_CASE - camera_y + (footprint_h_px - image.get_height()) / 2

        surface_monde.blit(image_fantome, (x, y))
    for player in players:
        player.draw_player(surface_monde, camera_x, camera_y)


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

def dessiner_hud(ecran, dims, HAUTEUR_BARRE, rects_icones, batiment_selectionne, images_batiments, TYPES_BATIMENTS, TAILLE_ICONE, player, font_argent, hud_or_img, hud_food_img, hud_vapeur_img, save_done_img, save_done_timer, barre_ouverte=True, slide_offset=0, btn_batiments_rect=None, skill_btn_rect=None, raid_manager=None):
    if slide_offset < HAUTEUR_BARRE:
        barre_surf = pygame.Surface((dims[0], HAUTEUR_BARRE), pygame.SRCALPHA)
        barre_surf.fill((30, 30, 30, 210))
        ecran.blit(barre_surf, (0, dims[1] - HAUTEUR_BARRE + slide_offset))

    for i, rect in enumerate(rects_icones):
        couleur = (200, 200, 80) if i == batiment_selectionne else (100, 100, 100)
        pygame.draw.rect(ecran, couleur, rect.inflate(8, 8))

        type_actuel = TYPES_BATIMENTS[i]
        img_base = images_batiments[type_actuel][1]
        # Si c'est un dictionnaire (comme la tourelle avec ses directions), on prend le Sud ("S")
        if isinstance(img_base, dict):
            img_base = img_base.get("S") or list(img_base.values())[0]

        icone = pygame.transform.smoothscale(img_base, (TAILLE_ICONE, TAILLE_ICONE))
        ecran.blit(icone, rect)

    # bouton toggle barre bâtiments
    BTN_SIZE = 80
    BTN_MARGE = 12
    btn_x = dims[0] - BTN_SIZE - BTN_MARGE
    btn_y = dims[1] - BTN_SIZE - BTN_MARGE

    # Fond du bouton : vert = ouvrir, orange = fermer
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

    # bouton skill tree
    skill_btn_x = btn_x - BTN_SIZE - BTN_MARGE
    skill_btn_y = btn_y
    skill_btn_couleur = (100, 100, 200)  # Bleu pour skills
    pygame.draw.rect(ecran, skill_btn_couleur, pygame.Rect(skill_btn_x, skill_btn_y, BTN_SIZE, BTN_SIZE), border_radius=10)
    pygame.draw.rect(ecran, (220, 220, 180), pygame.Rect(skill_btn_x, skill_btn_y, BTN_SIZE, BTN_SIZE), 3, border_radius=10)

    skill_label = "SKILLS"
    skill_lbl_surf = btn_font.render(skill_label, True, (255, 255, 255))
    skill_lbl_x = skill_btn_x + (BTN_SIZE - skill_lbl_surf.get_width()) // 2
    skill_lbl_y = skill_btn_y + (BTN_SIZE - skill_lbl_surf.get_height()) // 2
    ecran.blit(skill_lbl_surf, (skill_lbl_x, skill_lbl_y))

    if skill_btn_rect is not None:
        skill_btn_rect.update(skill_btn_x, skill_btn_y, BTN_SIZE, BTN_SIZE)

    # hud ressources
    hud_font = font_argent
    marge_hud = 2
    hud_y = marge_hud

    ressources_hud = [
        (str(player.money),  (255, 235,  80), hud_or_img),
        (str(player.food),   ( 255, 235,  80), hud_food_img),
        (str(player.vapeur), (255, 235, 80), hud_vapeur_img),
    ]

    for i, (valeur, couleur, img) in enumerate(ressources_hud):
        iw, ih = img.get_size()
        hud_x = dims[0] - marge_hud - (len(ressources_hud) - i) * (iw + marge_hud)
        ecran.blit(img, (hud_x, hud_y))
        texte = hud_font.render(valeur, True, couleur)
        tx = hud_x + (iw - texte.get_width()) // 2 - 13
        ty = hud_y + (ih - texte.get_height()) // 2 + 2
        ecran.blit(texte, (tx, ty))

    if save_done_timer > 0:
        img_w, img_h = save_done_img.get_size()
        x = 10
        y = 10
        ecran.blit(save_done_img, (x, y))

    # barre de vie du joueur
    hp_bar_w = 200
    hp_bar_h = 14
    hp_bar_x = 12
    hp_bar_y = 20
    hp_ratio = max(0.0, player.hp / player.hp_max)
    # fond
    pygame.draw.rect(ecran, (60, 10, 10), (hp_bar_x, hp_bar_y, hp_bar_w, hp_bar_h), border_radius=4)
    # vie
    if hp_ratio > 0:
        bar_color = (200, 0, 0) if hp_ratio > 0.5 else (220, 180, 30) if hp_ratio > 0.25 else (220, 50, 50)
        pygame.draw.rect(ecran, bar_color, (hp_bar_x, hp_bar_y, int(hp_bar_w * hp_ratio), hp_bar_h), border_radius=4)
    # contour
    pygame.draw.rect(ecran, (180, 180, 180), (hp_bar_x, hp_bar_y, hp_bar_w, hp_bar_h), 1, border_radius=4)
    hp_font = font_argent
    hp_txt = hp_font.render(f"HP {int(player.hp)}/{player.hp_max}", True, (255, 255, 255))
    ecran.blit(hp_txt, (hp_bar_x + 4, hp_bar_y - hp_txt.get_height() - 2))

    # indicateur raid
    if raid_manager is not None and raid_manager._raid_active:
        raid_font = font_argent
        nb_monstres = len(raid_manager.monsters)
        wave_txt = f"RAID  Vague {raid_manager._wave_index}/{raid_manager.WAVES_PER_RAID}  Monstres: {nb_monstres}"
        raid_surf = raid_font.render(wave_txt, True, (255, 80, 80))
        rx = dims[0] // 2 - raid_surf.get_width() // 2
        ry = 6
        bg = pygame.Surface((raid_surf.get_width() + 16, raid_surf.get_height() + 8), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 160))
        ecran.blit(bg, (rx - 8, ry - 4))
        ecran.blit(raid_surf, (rx, ry))