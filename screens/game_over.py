
import pygame
import math


def afficher_game_over(ecran: pygame.Surface, player=None, font_path: str = "assets/fonts/Minecraft.ttf") -> str:
    dims = ecran.get_size()
    W, H = dims

    try:
        font_big   = pygame.font.Font(font_path, 52)
        font_small = pygame.font.Font(font_path, 18)
    except Exception:
        font_big   = pygame.font.SysFont("arial", 52, bold=True)
        font_small = pygame.font.SysFont("arial", 18)

    clock = pygame.time.Clock()

    screenshot = ecran.copy()

    btn_restart_img      = pygame.image.load("assets/buttons/menu/continuer_normal.png").convert_alpha()
    btn_restart_hover    = pygame.image.load("assets/buttons/menu/continuer_hover.png").convert_alpha()
    btn_menu_img         = pygame.image.load("assets/buttons/menu/menu_principal_normal.png").convert_alpha()
    btn_menu_hover       = pygame.image.load("assets/buttons/menu/menu_principal_hover.png").convert_alpha()

    btn_restart_img   = pygame.transform.scale(btn_restart_img, (260, 70))
    btn_restart_hover = pygame.transform.scale(btn_restart_hover, (260, 70))
    btn_menu_img      = pygame.transform.scale(btn_menu_img, (260, 70))
    btn_menu_hover    = pygame.transform.scale(btn_menu_hover, (260, 70))

    btn_restart = btn_restart_img.get_rect(center=(W // 2, H // 2 + 160))
    btn_menu    = btn_menu_img.get_rect(center=(W // 2, H // 2 + 240))

    t = 0.0

    particles = []

    def _spawn_particles():
        import random
        cx, cy = W // 2, H // 2 - 80
        for _ in range(60):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(40, 180)
            life  = random.uniform(0.8, 2.5)
            r = random.randint(180, 255)
            g = random.randint(0, 60)
            b = random.randint(0, 40)
            particles.append([cx, cy,
                               math.cos(angle) * speed,
                               math.sin(angle) * speed,
                               life, life, (r, g, b)])

    spawned = False

    while True:
        dt = clock.tick(60) / 1000.0
        t += dt

        if t > 0.3 and not spawned:
            _spawn_particles()
            spawned = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    from screens import game_logic
                    game_logic.toggle_fullscreen()
                elif event.key in (pygame.K_RETURN, pygame.K_r):
                    return "restart"
                elif event.key == pygame.K_ESCAPE:
                    return "menu"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                if btn_restart.collidepoint(mx, my):
                    return "restart"
                if btn_menu.collidepoint(mx, my):
                    return "menu"


        overlay = screenshot.copy()

        dark = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.blit(dark, (0, 0))

        red_tint = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.blit(red_tint, (0, 0))

        ecran.blit(overlay, (0, 0))

        for p in particles[:]:
            p[0] += p[2] * dt
            p[1] += p[3] * dt
            p[3] += 120 * dt
            p[4] -= dt

            if p[4] <= 0:
                particles.remove(p)
                continue

            life_ratio = p[4] / p[5]
            r = max(2, int(3 * life_ratio))

            s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            ecran.blit(s, (int(p[0]) - r, int(p[1]) - r))

        pulse = 1.0 + 0.03 * math.sin(t * 4)


        title_alpha = int(255 * max(0.0, (t - 0.5) / 0.8))

        title = font_big.render("VOUS ETES MORT", True, (220, 40, 40))
        title.set_alpha(title_alpha)
        ecran.blit(title, (W // 2 - title.get_width() // 2, H // 2 - 10))


        if t > 1.2:
            blink = int((math.sin(t * 3) + 1) / 2 * 180) + 60
            sub = font_small.render(
                "Vos batiments ont resiste... pour l'instant.",
                True, (blink, blink, blink)
            )
            ecran.blit(sub, (W // 2 - sub.get_width() // 2, H // 2 + 40))

            # pénalité
            penalty_surf = font_small.render(
                "PENALITE : -30% de toutes vos ressources",
                True, (220, 100, 30)
            )
            ecran.blit(penalty_surf, (W // 2 - penalty_surf.get_width() // 2, H // 2 + 68))

            if player is not None:
                res_font = pygame.font.Font(font_path, 13) if True else font_small
                or_val   = max(0, int(player.money  * 0.70))
                food_val = max(0, int(player.food   * 0.70))
                vap_val  = max(0, int(player.vapeur * 0.70))
                res_txt  = f"Or : {player.money} -> {or_val}    Nourriture : {player.food} -> {food_val}    Vapeur : {player.vapeur} -> {vap_val}"
                res_surf = res_font.render(res_txt, True, (180, 180, 180))
                ecran.blit(res_surf, (W // 2 - res_surf.get_width() // 2, H // 2 + 92))

        if t > 1.0:
            mx, my = pygame.mouse.get_pos()

            img = btn_restart_hover if btn_restart.collidepoint(mx, my) else btn_restart_img
            ecran.blit(img, btn_restart.topleft)

            img = btn_menu_hover if btn_menu.collidepoint(mx, my) else btn_menu_img
            ecran.blit(img, btn_menu.topleft)

        pygame.display.flip()

