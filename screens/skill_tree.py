import pygame
import sys
from core.Class.player import Player
from core.Class.batiments import Batiment

from core.Class.skill_levels import get_max_level, set_max_level, MAX_LEVELS

SKILLS_DATA = {
    "combat": {
        "name": "Combat",
        "color": (220, 50, 50),
        "skills": [
            {
                "id": "new_building_tower",
                "name": "Tour de Defense",
                "description": "Debloque une nouvelle tour de defense.",
                "cost": 1000,
                "prerequisites": [],
                "effect": "unlock_new_building",
                "building_type": "tower",
                "pos": (0.75, 0.40),  # RIGHT branch root
                "large": True,
            }
        ]
    },

    "production": {
        "name": "Production",
        "color": (50, 220, 80),
        "skills": [

            {
                "id": "building_upgrade_residential_2",
                "name": "Maison Niv.2",
                "description": "Permet de construire des maisons niveau 2.",
                "cost": 100,
                "prerequisites": [],
                "effect": "unlock_building_upgrade",
                "building_type": Batiment.TYPE_RESIDENTIEL,
                "max_level": 2,
                "pos": (0.35, 0.40),  # LEFT root
                "large": True,
            },

            {
                "id": "building_upgrade_gen_2",
                "name": "Generateur Niv.2",
                "description": "Permet de construire des generateurs niveau 2.",
                "cost": 100,
                "prerequisites": ["building_upgrade_residential_2"],
                "effect": "unlock_building_upgrade",
                "building_type": Batiment.TYPE_GENERATEUR,
                "max_level": 2,
                "pos": (0.25, 0.30),
            },
            {
                "id": "building_upgrade_farm_2",
                "name": "Ferme Niv.2",
                "description": "Permet de construire des fermes niveau 2.",
                "cost": 100,
                "prerequisites": ["building_upgrade_residential_2"],
                "effect": "unlock_building_upgrade",
                "building_type": Batiment.TYPE_FARM,
                "max_level": 2,
                "pos": (0.25, 0.45),
            },
            {
                "id": "building_upgrade_mine_2",
                "name": "Mine Niv.2",
                "description": "Permet de construire des mines niveau 2.",
                "cost": 100,
                "prerequisites": ["building_upgrade_residential_2"],
                "effect": "unlock_building_upgrade",
                "building_type": Batiment.TYPE_MINE,
                "max_level": 2,
                "pos": (0.25, 0.60),
            },

            {
                "id": "building_upgrade_gen_3",
                "name": "Generateur Niv.3",
                "description": "Permet de construire des generateurs niveau 3.",
                "cost": 300,
                "prerequisites": ["building_upgrade_gen_2"],
                "effect": "unlock_building_upgrade",
                "building_type": Batiment.TYPE_GENERATEUR,
                "max_level": 3,
                "pos": (0.15, 0.25),
            },
            {
                "id": "building_upgrade_farm_3",
                "name": "Ferme Niv.3",
                "description": "Permet de construire des fermes niveau 3.",
                "cost": 300,
                "prerequisites": ["building_upgrade_farm_2"],
                "effect": "unlock_building_upgrade",
                "building_type": Batiment.TYPE_FARM,
                "max_level": 3,
                "pos": (0.15, 0.45),
            },
            {
                "id": "building_upgrade_mine_3",
                "name": "Mine Niv.3",
                "description": "Permet de construire des mines niveau 3.",
                "cost": 300,
                "prerequisites": ["building_upgrade_mine_2"],
                "effect": "unlock_building_upgrade",
                "building_type": Batiment.TYPE_MINE,
                "max_level": 3,
                "pos": (0.13, 0.80),
            },
            {
                "id": "building_upgrade_residential_3",
                "name": "Maison Niv.3",
                "description": "Permet de construire des maisons niveau 3.",
                "cost": 300,
                "prerequisites": ["building_upgrade_residential_2"],
                "effect": "unlock_building_upgrade",
                "building_type": Batiment.TYPE_RESIDENTIEL,
                "max_level": 3,
                "pos": (0.35, 0.25),
            },
            {
                "id": "mine_upgrade",
                "name": "Mine Avancee",
                "description": "Augmente la production des mines de 50%",
                "cost": 300,
                "prerequisites": ["building_upgrade_mine_2"],
                "effect": "boost_production",
                "building_type": Batiment.TYPE_MINE,
                "boost": 1.5,
                "pos": (0.05, 0.65),
            },
            {
                "id": "farm_upgrade",
                "name": "Ferme Efficace",
                "description": "Reduit le cout des fermes et augmente la production.",
                "cost": 400,
                "prerequisites": ["building_upgrade_farm_3"],
                "effect": "modify_building_cost",
                "building_type": Batiment.TYPE_FARM,
                "cost_modifier": 0.8,
                "production_boost": 1.2,
                "pos": (0.05, 0.45),
            },
            {
                "id": "centrale_nourriture_upgrade",
                "name": "Boost Centrale",
                "description": "Augmente le boost accorde par la centrale respective de +5%",
                "cost": 1000,
                "prerequisites": ["farm_upgrade"],
                "effect": "unlock_building_upgrade",
                "building_type": Batiment.TYPE_CENTRALE_NOURRITURE,
                "max_level": 2,
                "pos": (0.05, 0.25),
            },
            {
                "id": "centrale_argent_upgrade",
                "name": "Boost Centrale",
                "description": "Augmente le boost accorde par la centrale respective de +5%",
                "cost": 1000,
                "prerequisites": ["mine_upgrade", "building_upgrade_mine_3"],
                "effect": "unlock_building_upgrade",
                "building_type": Batiment.TYPE_CENTRALE_ARGENT,
                "max_level": 2,
                "pos": (0.05, 0.80),
            },
            {
                "id": "centrale_vapeur_upgrade",
                "name": "Boost Centrale",
                "description": "Augmente le boost accorde par la centrale respective de +5%",
                "cost": 1000,
                "prerequisites": ["building_upgrade_gen_3"],
                "effect": "unlock_building_upgrade",
                "building_type": Batiment.TYPE_CENTRALE_VAPEUR,
                "max_level": 2,
                "pos": (0.05, 0.15),
            },
        ]
    },

    "others": {
        "name": "Autres",
        "color": (240, 190, 40),
        "skills": [
            {
                "id": "health_upgrade",
                "name": "Sante Amelioree",
                "description": "Augmente la sante maximale du joueur de 50.",
                "cost": 200,
                "prerequisites": [],
                "effect": "player_stat",
                "stat": "hp_max",
                "value": 50,
                "pos": (0.50, 0.65),  # CENTER DOWN
                "large": True,
            },
            {
                "id": "pet_unlock",
                "name": "Animal de Compagnie",
                "description": "Debloque un animal de compagnie qui aide dans le jeu.",
                "cost": 300,
                "prerequisites": ["health_upgrade"],
                "effect": "unlock_pet",
                "pos": (0.50, 0.85),
            },
        ]
    },
}

def is_skill_unlocked(skill_id, unlocked_skills):
    return skill_id in unlocked_skills


def apply_skill_effect(skill, player, batiments_data):
    effect = skill["effect"]
    if effect == "unlock_building_upgrade":
        set_max_level(skill["building_type"], skill["max_level"])
        batiments_data[skill["building_type"]]["max_level"] = skill["max_level"]
    elif effect == "unlock_new_building":
        batiments_data[Batiment.TYPE_TOURELLE]["unlocked"] = True
    elif effect == "boost_production":
        building = batiments_data[skill["building_type"]]
        for key, data in building.items():
            if isinstance(data, dict):
                for prod_key in ("vapeur", "argent", "nourriture", "production"):
                    if prod_key in data:
                        data[prod_key] = int(data[prod_key] * skill["boost"])
    elif effect == "modify_building_cost":
        building = batiments_data[skill["building_type"]]
        for key, data in building.items():
            if not isinstance(data, dict):
                continue
            if "cout" in data:
                data["cout"] = int(data["cout"] * skill["cost_modifier"])
            if "production_boost" in skill:
                for prod_key in ("vapeur", "argent", "nourriture", "production", "nourriture"):
                    if prod_key in data:
                        data[prod_key] = int(data[prod_key] * skill["production_boost"])
    elif effect == "player_stat":
        setattr(player, skill["stat"], getattr(player, skill["stat"]) + skill["value"])
    elif effect == "unlock_pet":
        player.has_pet = True


def draw_glow_line(surface, color, start, end, width=3, alpha=180):
    glow_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    r, g, b = color
    pygame.draw.line(glow_surf, (r, g, b, 40), start, end, width + 8)
    pygame.draw.line(glow_surf, (r, g, b, 80), start, end, width + 4)
    pygame.draw.line(glow_surf, (r, g, b, alpha), start, end, width)
    surface.blit(glow_surf, (0, 0))


def draw_glow_circle(surface, color, center, radius, alpha=220):
    glow_surf = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
    cx, cy = radius * 2, radius * 2
    r, g, b = color
    pygame.draw.circle(glow_surf, (r, g, b, 25), (cx, cy), radius + 10)
    pygame.draw.circle(glow_surf, (r, g, b, 50), (cx, cy), radius + 6)
    pygame.draw.circle(glow_surf, (r, g, b, 90), (cx, cy), radius + 3)
    pygame.draw.circle(glow_surf, (15, 15, 25, 230), (cx, cy), radius)
    pygame.draw.circle(glow_surf, (r, g, b, alpha), (cx, cy), radius, 3)
    surface.blit(glow_surf, (center[0] - radius * 2, center[1] - radius * 2))


def draw_dim_circle(surface, center, radius):
    glow_surf = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
    cx, cy = radius * 2, radius * 2
    pygame.draw.circle(glow_surf, (60, 60, 70, 180), (cx, cy), radius)
    pygame.draw.circle(glow_surf, (100, 100, 110, 160), (cx, cy), radius, 2)
    surface.blit(glow_surf, (center[0] - radius * 2, center[1] - radius * 2))


def draw_popup(surface, skill, state, player_vapeur, font_title, font_body, cat_color, W, H):
    PW, PH = 300, 180
    px = min(W - PW - 20, max(20, W // 2 - PW // 2))
    py = H - PH - 20

    shadow = pygame.Surface((PW + 8, PH + 8), pygame.SRCALPHA)
    shadow.fill((0, 0, 0, 120))
    surface.blit(shadow, (px - 4, py - 4))

    panel = pygame.Surface((PW, PH), pygame.SRCALPHA)
    panel.fill((10, 10, 22, 230))
    surface.blit(panel, (px, py))

    pygame.draw.rect(surface, cat_color, (px, py, PW, PH), 2, border_radius=10)

    title_surf = font_title.render(skill["name"], True, cat_color)
    surface.blit(title_surf, (px + 14, py + 12))

    words = skill["description"].split(" ")
    lines, line = [], ""
    for w in words:
        test = (line + " " + w).strip()
        if font_body.size(test)[0] < PW - 28:
            line = test
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)
    for i, l in enumerate(lines[:3]):
        surf = font_body.render(l, True, (180, 180, 200))
        surface.blit(surf, (px + 14, py + 44 + i * 22))

    cost_surf = font_body.render(f"Cout : {skill['cost']} vapeur", True, (240, 190, 40))
    surface.blit(cost_surf, (px + 14, py + PH - 56))

    btn_rect = pygame.Rect(px + 14, py + PH - 34, PW - 28, 26)
    can_buy = (state == "locked" and player_vapeur >= skill["cost"])

    if state == "unlocked":
        btn_color, btn_text, txt_color = (30, 90, 30), "Deja debloquee", (100, 220, 100)
    elif state == "unavailable":
        btn_color, btn_text, txt_color = (40, 40, 50), "Prerequis manquants", (100, 100, 120)
    elif not can_buy:
        btn_color, btn_text, txt_color = (60, 30, 30), "Pas assez de vapeur", (180, 80, 80)
    else:
        btn_color = tuple(max(0, c - 60) for c in cat_color)
        btn_text, txt_color = "Debloquer", cat_color

    pygame.draw.rect(surface, btn_color, btn_rect, border_radius=6)
    pygame.draw.rect(surface, txt_color, btn_rect, 1, border_radius=6)
    lbl = font_body.render(btn_text, True, txt_color)
    surface.blit(lbl, (btn_rect.centerx - lbl.get_width() // 2,
                        btn_rect.centery - lbl.get_height() // 2))

    return btn_rect if can_buy else None


def afficher_skill_tree(ecran, player, unlocked_skills, batiments_data):
    en_menu = True
    horloge = pygame.time.Clock()

    try:
        font_title = pygame.font.Font("assets/fonts/Minecraft.ttf", 22)
        font_body  = pygame.font.Font("assets/fonts/Minecraft.ttf", 16)
        font_small = pygame.font.Font("assets/fonts/Minecraft.ttf", 13)
        font_cat   = pygame.font.Font("assets/fonts/Minecraft.ttf", 18)
    except Exception:
        font_title = pygame.font.SysFont("monospace", 22, bold=True)
        font_body  = pygame.font.SysFont("monospace", 16)
        font_small = pygame.font.SysFont("monospace", 13)
        font_cat   = pygame.font.SysFont("monospace", 18, bold=True)

    W, H = ecran.get_size()

    camera_x, camera_y = 0, 0
    dragging = False
    last_mouse_pos = (0, 0)

    all_skills = []
    for cat_id, cat_data in SKILLS_DATA.items():
        for skill in cat_data["skills"]:
            entry = dict(skill)
            entry["cat_id"] = cat_id
            entry["cat_color"] = cat_data["color"]
            rx, ry = skill.get("pos", (0.5, 0.5))
            entry["screen_pos"] = (int(rx * W), int(ry * H))
            entry["radius"] = 26 if skill.get("large") else 18
            all_skills.append(entry)

    skill_index = {s["id"]: s for s in all_skills}
    selected_skill = None
    buy_btn_rect   = None

    bg_surf = pygame.Surface((W, H), pygame.SRCALPHA)
    bg_surf.fill((0, 0, 0, 200))

    def get_state(skill):
        if skill["id"] in unlocked_skills:
            return "unlocked"
        prereqs_met = all(p in unlocked_skills for p in skill["prerequisites"])
        return "locked" if prereqs_met else "unavailable"

    while en_menu:
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    from screens import game_logic
                    game_logic.toggle_fullscreen()
                elif event.key == pygame.K_ESCAPE:
                    if selected_skill:
                        selected_skill = None
                        buy_btn_rect = None
                    else:
                        en_menu = False


            elif event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 1:  # Clic gauche

                    dragging = False

                    last_mouse_pos = event.pos

                    clicked = False

                    for skill in all_skills:

                        cx = skill["screen_pos"][0] + camera_x

                        cy = skill["screen_pos"][1] + camera_y

                        r = skill["radius"]

                        if (mx - cx) ** 2 + (my - cy) ** 2 <= r ** 2:
                            selected_skill = skill if selected_skill is not skill else None

                            buy_btn_rect = None

                            clicked = True

                            break

                    if selected_skill and buy_btn_rect and buy_btn_rect.collidepoint(mx, my):

                        skill = selected_skill

                        if get_state(skill) == "locked" and player.vapeur >= skill["cost"]:
                            player.vapeur -= skill["cost"]

                            unlocked_skills.add(skill["id"])

                            apply_skill_effect(skill, player, batiments_data)

                            selected_skill = None

                            buy_btn_rect = None


                elif event.button == 3:  # Clic droit

                    if selected_skill is not None:

                        selected_skill = None

                        buy_btn_rect = None


                    else:

                        en_menu = False  # Quitter le skill tree


                    clicked = False
                    for skill in all_skills:
                        cx = skill["screen_pos"][0] + camera_x
                        cy = skill["screen_pos"][1] + camera_y
                        r = skill["radius"]

                        if (mx - cx) ** 2 + (my - cy) ** 2 <= r ** 2:
                            selected_skill = skill if selected_skill is not skill else None
                            buy_btn_rect = None
                            clicked = True
                            break

                    if selected_skill and buy_btn_rect and buy_btn_rect.collidepoint(mx, my):
                        skill = selected_skill
                        if get_state(skill) == "locked" and player.vapeur >= skill["cost"]:
                            player.vapeur -= skill["cost"]
                            unlocked_skills.add(skill["id"])
                            apply_skill_effect(skill, player, batiments_data)
                            selected_skill = None
                            buy_btn_rect = None

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False

            elif event.type == pygame.MOUSEMOTION:
                if dragging:
                    dx = event.pos[0] - last_mouse_pos[0]
                    dy = event.pos[1] - last_mouse_pos[1]
                    camera_x += dx
                    camera_y += dy
                    last_mouse_pos = event.pos

#bouger avec fleches
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            camera_x += 10
        if keys[pygame.K_RIGHT]:
            camera_x -= 10
        if keys[pygame.K_UP]:
            camera_y += 10
        if keys[pygame.K_DOWN]:
            camera_y -= 10

        ecran.blit(bg_surf, (0, 0))

        for skill in all_skills:
            for prereq_id in skill["prerequisites"]:
                if prereq_id not in skill_index:
                    continue

                parent = skill_index[prereq_id]

                px, py = parent["screen_pos"]
                sx, sy = skill["screen_pos"]

                start = (px + camera_x, py + camera_y)
                end   = (sx + camera_x, sy + camera_y)

                both_unlocked = (
                    skill["id"] in unlocked_skills and
                    prereq_id in unlocked_skills
                )

                if both_unlocked:
                    draw_glow_line(ecran, skill["cat_color"], start, end, 4, 200)
                else:
                    pygame.draw.line(ecran, (60, 60, 75), start, end, 2)

        for skill in all_skills:
            cx = skill["screen_pos"][0] + camera_x
            cy = skill["screen_pos"][1] + camera_y
            r = skill["radius"]

            state = get_state(skill)

            if state == "unlocked":
                draw_glow_circle(ecran, skill["cat_color"], (cx, cy), r, 240)
            elif state == "locked":
                draw_glow_circle(ecran, skill["cat_color"], (cx, cy), r, 90)
            else:
                draw_dim_circle(ecran, (cx, cy), r)

            if (mx - cx) ** 2 + (my - cy) ** 2 <= r ** 2:
                pygame.draw.circle(ecran, (255, 255, 255), (cx, cy), r + 4, 2)

            if selected_skill and selected_skill["id"] == skill["id"]:
                pygame.draw.circle(ecran, (255, 255, 255), (cx, cy), r + 5, 2)

#UI
        vapeur_surf = font_body.render(f"Vapeur : {int(player.vapeur)}", True, (240, 190, 40))
        ecran.blit(vapeur_surf, (W - vapeur_surf.get_width() - 20, 16))

        esc_surf = font_small.render("ESC - Fermer", True, (100, 100, 120))
        ecran.blit(esc_surf, (20, 16))

        if selected_skill:
            state = get_state(selected_skill)
            buy_btn_rect = draw_popup(
                ecran, selected_skill, state, player.vapeur,
                font_title, font_body,
                selected_skill["cat_color"], W, H
            )

        pygame.display.flip()
        horloge.tick(60)

    return unlocked_skills