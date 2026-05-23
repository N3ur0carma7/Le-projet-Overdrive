import pygame
import os

STEPS = [
    "Bienvenue dans Overdrive ! Cette ville est a toi. Construit, developpe et prospere.",
    "Utilise la molette pour zoomer. Clique DROIT pour deplacer ton personnage.",
    "Appuie sur ECHAP pour ouvrir le menu pause et sauvegarder ta partie.",
    "Les bâtiments de PRODUCTION (mine, ferme, generateur) necessitent des villageois.",
    "Tu peux assigner des villageois à differents batiments pour faire produire des ressources avec la touche TAB. Plus le niveau du batiment est eleve, plus il peut accueillir de villageois et produire de ressources.",
    "Reste a portee dans un carre de 2 cases pour placer ou interagir avec un bâtiment.",
    "Ouvre la barre de bâtiments en bas, puis clique GAUCHE sur une icône pour selectionner une construction.",
    "Clique GAUCHE sur le sol pour poser le bâtiment selectionne. Maintiens le clic pour placer plusieurs bâtiments rapidement.",
    "Clique DROIT pour annuler la selection de bâtiment si tu changes d'avis.",
    "Tes villageois ont besoin d'une MAISON pour vivre. Commence par en construire une !",
    "Bonne chance, aventurier ! Appuie sur ENTREE pour commencer l'aventure.",
]

# Duree d'affichage de chaque caractere
CHAR_DELAY = 0.032
#tuto
# Dimensions du panneau overlay
PANEL_W = 520
PANEL_H = 220
PANEL_PADDING = 28

# Couleurs
COL_BG      = (15, 10, 5, 220)
COL_BORDER  = (180, 130, 50)
COL_BORDER2 = (220, 170, 70)
COL_TEXT    = (240, 230, 200)
COL_HINT    = (140, 110, 60)
COL_STEP    = (180, 130, 50)
COL_OVERLAY = (0, 0, 0, 110)


def _get_fonts():
    
    font_path = os.path.join("assets", "fonts", "Minecraft.ttf")

    candidates = ["dejavusans", "arial", "liberationsans", "freesans"]
    font_text = None
    for name in candidates:
        try:
            f = pygame.font.SysFont(name, 17)
            if f is not None:
                font_text = f
                break
        except Exception:
            continue
    if font_text is None:
        font_text = pygame.font.SysFont(None, 17)

    try:
        font_hint = pygame.font.Font(font_path, 12)
    except Exception:
        font_hint = pygame.font.SysFont(None, 12)

    return pygame.font.Font(font_path, 15), font_hint


def _wrap_text(text: str, font, max_width: int) -> list[str]:
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split(" ")
        current = ""
        for word in words:
            test = (current + " " + word).strip()
            if font.size(test)[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        lines.append(current)
    return lines


def _draw_panel(surface, panel_rect, font_text, font_hint,
                visible_text: str, step_idx: int, total_steps: int):

    W, H = surface.get_size()
    px, py, pw, ph = panel_rect

    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    overlay.fill(COL_OVERLAY)
    surface.blit(overlay, (0, 0))

    panel_surf = pygame.Surface((pw, ph), pygame.SRCALPHA)
    panel_surf.fill(COL_BG)

    pygame.draw.rect(panel_surf, COL_BORDER2, (0, 0, pw, ph), 3, border_radius=14)
    pygame.draw.rect(panel_surf, COL_BORDER, (4, 4, pw - 8, ph - 8), 1, border_radius=11)

    cs = 10
    for cx2, cy2 in [(0, 0), (pw - cs, 0), (0, ph - cs), (pw - cs, ph - cs)]:
        pygame.draw.rect(panel_surf, COL_BORDER2, (cx2, cy2, cs, cs))

    surface.blit(panel_surf, (px, py))

    inner_w = pw - PANEL_PADDING * 2
    lines = _wrap_text(visible_text, font_text, inner_w)
    text_y = py + PANEL_PADDING
    line_h = font_text.get_linesize()
    for line in lines:
        surf = font_text.render(line, True, COL_TEXT)
        surface.blit(surf, (px + PANEL_PADDING, text_y))
        text_y += line_h

    step_str = f"{step_idx + 1} / {total_steps}"
    step_surf = font_hint.render(step_str, True, COL_STEP)
    surface.blit(step_surf, (px + pw - step_surf.get_width() - PANEL_PADDING,
                              py + ph - step_surf.get_height() - 12))

    hint_space = font_hint.render("[ ENTREE ] passer", True, COL_HINT)
    surface.blit(hint_space, (px + PANEL_PADDING, py + ph - hint_space.get_height() - 12))


def run_tutorial(ecran, horloge, FPS, draw_background_fn=None):
    font_text, font_hint = _get_fonts()

    step_idx = 0
    char_idx = 0
    acc_time = 0.0

    running = True
    while running:
        dt = horloge.tick(FPS) / 1000.0

        current_text = STEPS[step_idx]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    from screens import game_logic
                    game_logic.toggle_fullscreen()
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    char_idx = len(current_text)

                elif event.key == pygame.K_SPACE:
                    if char_idx < len(current_text):
                        char_idx = len(current_text)
                    else:
                        step_idx += 1
                        if step_idx >= len(STEPS):
                            running = False
                            break
                        char_idx = 0
                        acc_time = 0.0

                elif event.key == pygame.K_ESCAPE:
                    running = False
                    break

        if not running:
            break

        # Avancement de l'animation typewriter
        if char_idx < len(current_text):
            acc_time += dt
            while acc_time >= CHAR_DELAY and char_idx < len(current_text):
                char_idx += 1
                acc_time -= CHAR_DELAY

        if draw_background_fn is not None:
            draw_background_fn()
        else:
            ecran.fill((20, 12, 5))

        W, H = ecran.get_size()

        px = W // 2 - PANEL_W // 2
        py = H // 2 - PANEL_H // 2 + H // 6
        py = min(py, H - PANEL_H - 10)
        panel_rect = (px, py, PANEL_W, PANEL_H)

        visible = current_text[:char_idx]
        _draw_panel(ecran, panel_rect, font_text, font_hint,
                    visible, step_idx, len(STEPS))

        if char_idx >= len(current_text):
            tick = pygame.time.get_ticks()
            if (tick // 500) % 2 == 0:
                if step_idx < len(STEPS) - 1:
                    label = "[ ESPACE ] pour continuer"
                else:
                    label = "[ ENTREE ] pour jouer !"
                surf = font_hint.render(label, True, COL_BORDER2)
                sx = W // 2 - surf.get_width() // 2
                sy = py + PANEL_H + 10
                if sy + surf.get_height() < H:
                    ecran.blit(surf, (sx, sy))

        pygame.display.flip()

    return True
