import math
import pygame
import random


def _build_monster_frames() -> list:
    """
    Génère 6 frames d'animation procédurale pour le monstre (sprite pixel-art).
    """
    SIZE = 36
    frames = []
    for i in range(6):
        surf = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))

        bob = int(math.sin(i * math.pi / 3) * 2)

        # Ombre
        pygame.draw.ellipse(surf, (0, 0, 0, 60),
                            pygame.Rect(6, SIZE - 7 + bob, SIZE - 12, 5))

        # Corps
        body_rect = pygame.Rect(4, 10 + bob, SIZE - 8, SIZE - 14)
        pygame.draw.ellipse(surf, (160, 30, 30), body_rect)
        pygame.draw.ellipse(surf, (210, 70, 70),
                            pygame.Rect(8, 12 + bob, 10, 7))

        # Tête
        head_y = 2 + bob
        pygame.draw.circle(surf, (180, 40, 40), (SIZE // 2, head_y + 8), 9)
        pygame.draw.circle(surf, (220, 80, 80), (SIZE // 2 - 3, head_y + 5), 3)

        # Cornes
        pygame.draw.polygon(surf, (120, 20, 20), [
            (SIZE // 2 - 6, head_y + 2),
            (SIZE // 2 - 10, head_y - 5),
            (SIZE // 2 - 3, head_y + 1),
        ])
        pygame.draw.polygon(surf, (120, 20, 20), [
            (SIZE // 2 + 6, head_y + 2),
            (SIZE // 2 + 10, head_y - 5),
            (SIZE // 2 + 3, head_y + 1),
        ])

        # Yeux
        eye_y = head_y + 8
        if i == 4:
            pygame.draw.line(surf, (20, 20, 20),
                             (SIZE // 2 - 5, eye_y), (SIZE // 2 - 2, eye_y), 2)
            pygame.draw.line(surf, (20, 20, 20),
                             (SIZE // 2 + 2, eye_y), (SIZE // 2 + 5, eye_y), 2)
        else:
            pygame.draw.circle(surf, (255, 255, 60), (SIZE // 2 - 4, eye_y), 3)
            pygame.draw.circle(surf, (255, 255, 60), (SIZE // 2 + 4, eye_y), 3)
            pygame.draw.circle(surf, (10, 10, 10), (SIZE // 2 - 4, eye_y + 1), 1)
            pygame.draw.circle(surf, (10, 10, 10), (SIZE // 2 + 4, eye_y + 1), 1)

        # Bouche
        mouth_y = head_y + 14
        pygame.draw.arc(surf, (20, 0, 0),
                        pygame.Rect(SIZE // 2 - 5, mouth_y - 2, 10, 6),
                        math.pi, 2 * math.pi, 2)
        pygame.draw.polygon(surf, (240, 240, 240), [
            (SIZE // 2 - 3, mouth_y + 1),
            (SIZE // 2 - 1, mouth_y + 4),
            (SIZE // 2 + 1, mouth_y + 1),
        ])

        frames.append(surf)
    return frames


def _build_attack_frames() -> list:
    """4 frames d'animation d'attaque (griffes qui s'agrandissent)."""
    SIZE = 36
    frames = []
    for i in range(4):
        surf = pygame.Surface((SIZE + 20, SIZE), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))

        cx = (SIZE + 20) // 2

        pygame.draw.ellipse(surf, (160, 30, 30),
                            pygame.Rect(cx - (SIZE - 8) // 2, 10, SIZE - 8, SIZE - 14))
        pygame.draw.circle(surf, (180, 40, 40), (cx, 10), 9)

        claw_ext = i * 5
        pygame.draw.polygon(surf, (220, 200, 50), [
            (cx - 14 - claw_ext, 15),
            (cx - 8, 18),
            (cx - 8, 22),
            (cx - 16 - claw_ext, 23),
        ])
        pygame.draw.polygon(surf, (220, 200, 50), [
            (cx + 14 + claw_ext, 15),
            (cx + 8, 18),
            (cx + 8, 22),
            (cx + 16 + claw_ext, 23),
        ])

        pygame.draw.circle(surf, (255, 50, 50), (cx - 4, 10), 3)
        pygame.draw.circle(surf, (255, 50, 50), (cx + 4, 10), 3)

        frames.append(surf)
    return frames


def _build_hit_flash():
    """Surface blanche pour l'effet de coup reçu."""
    SIZE = 36
    surf = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
    pygame.draw.ellipse(surf, (255, 255, 255, 180), pygame.Rect(2, 4, SIZE - 4, SIZE - 6))
    return surf


class Monster:
    """
    Monstre PVE avec sprite animé (idle + attaque).
    Se dirige vers le joueur le plus proche et l'attaque au contact.
    Le joueur peut l'attaquer avec un clic gauche.
    """

    SPEED           = 80
    HP_MAX          = 30
    ATTACK_DAMAGE   = 3
    ATTACK_RANGE    = 40
    ATTACK_COOLDOWN = 1.0
    ATTACK_DAMAGE_DELAY = 0.15
    SIZE            = 36

    ANIM_FPS_IDLE   = 6
    ANIM_FPS_ATTACK = 10

    _idle_frames   = None
    _attack_frames = None
    _hit_flash     = None

    @classmethod
    def load_sprites(cls):
        if cls._idle_frames is None:
            cls._idle_frames   = _build_monster_frames()
            cls._attack_frames = _build_attack_frames()
            cls._hit_flash     = _build_hit_flash()

    def __init__(self, monde_x: float, monde_y: float):
        Monster.load_sprites()

        self.x = monde_x
        self.y = monde_y
        self.hp = self.HP_MAX
        self.alive = True

        self._attack_timer = 0.0

        self._anim_frame  = 0
        self._anim_timer  = 0.0
        self._is_attacking = False
        self._attack_anim_timer    = 0.0
        self._attack_anim_duration = 0.4
        self._attack_damage_applied = False

        self._hit_flash_timer    = 0.0
        self._hit_flash_duration = 0.15

        self._anim_phase  = random.uniform(0, 1)
        self._facing_left = False

    def update(self, players: list, dt: float):
        if not self.alive:
            return

        self._attack_timer    = max(0.0, self._attack_timer - dt)
        self._hit_flash_timer = max(0.0, self._hit_flash_timer - dt)

        target     = None
        best_dist  = float("inf")
        for p in players:
            if p.hp <= 0:
                continue
            dx = p.pos[0] - self.x
            dy = p.pos[1] - self.y
            d  = math.hypot(dx, dy)
            if d < best_dist:
                best_dist = d
                target    = p

        if target is None:
            self._update_anim(dt, moving=False)
            return

        dx   = target.pos[0] - self.x
        dy   = target.pos[1] - self.y
        dist = math.hypot(dx, dy)

        if dx != 0:
            self._facing_left = dx < 0

        if self._is_attacking:
            self._attack_anim_timer -= dt

            if not self._attack_damage_applied:
                time_since_start = self._attack_anim_duration - self._attack_anim_timer
                if time_since_start >= self.ATTACK_DAMAGE_DELAY:
                    target.hurt(self.ATTACK_DAMAGE)
                    self._attack_damage_applied = True

            if self._attack_anim_timer <= 0:
                self._is_attacking = False
                self._attack_damage_applied = False
                self._anim_frame   = 0

        if dist <= self.ATTACK_RANGE:
            if self._attack_timer <= 0.0:
                self._attack_timer = self.ATTACK_COOLDOWN
                self._is_attacking = True
                self._attack_anim_timer = self._attack_anim_duration
                self._attack_damage_applied = False
                self._anim_frame = 0
            self._update_anim(dt, moving=False)
        else:
            if dist > 0:
                self.x += (dx / dist) * self.SPEED * dt
                self.y += (dy / dist) * self.SPEED * dt
            self._update_anim(dt, moving=True)

    def _update_anim(self, dt: float, moving: bool):
        if self._is_attacking:
            fps = self.ANIM_FPS_ATTACK
            nb  = len(self._attack_frames)
        else:
            fps = self.ANIM_FPS_IDLE
            nb  = len(self._idle_frames)

        self._anim_timer += dt
        period = 1.0 / fps
        if self._anim_timer >= period:
            self._anim_timer -= period
            self._anim_frame  = (self._anim_frame + 1) % nb

    def take_damage(self, amount: float):
        self.hp -= amount
        self._hit_flash_timer = self._hit_flash_duration
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def get_screen_rect(self, camera_x: float, camera_y: float) -> pygame.Rect:
        """Retourne le rect écran du monstre (pour la détection de clic)."""
        sx = int(self.x - camera_x) - self.SIZE // 2
        sy = int(self.y - camera_y) - self.SIZE // 2
        return pygame.Rect(sx, sy, self.SIZE, self.SIZE)

    def draw(self, surface: pygame.Surface, camera_x: float, camera_y: float):
        if not self.alive:
            return

        sw, sh = surface.get_size()
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)

        if sx > sw + 80 or sx < -80 or sy > sh + 80 or sy < -80:
            return

        if self._is_attacking:
            frames = self._attack_frames
        else:
            frames = self._idle_frames

        frame_idx = min(self._anim_frame, len(frames) - 1)
        sprite = frames[frame_idx]

        if self._facing_left:
            sprite = pygame.transform.flip(sprite, True, False)

        fw, fh = sprite.get_size()
        draw_x = sx - fw // 2
        draw_y = sy - fh

        surface.blit(sprite, (draw_x, draw_y))

        # Flash blanc si coup reçu
        if self._hit_flash_timer > 0:
            flash = self._hit_flash
            if self._facing_left:
                flash = pygame.transform.flip(flash, True, False)
            fsx = sx - flash.get_width() // 2
            fsy = sy - fh + (fh - flash.get_height()) // 2
            surface.blit(flash, (fsx, fsy))

        # Barre de vie
        bar_w    = self.SIZE
        bar_h    = 4
        hp_ratio = max(0.0, self.hp / self.HP_MAX)
        bar_x    = sx - bar_w // 2
        bar_y    = sy - fh - 7
        pygame.draw.rect(surface, (80, 0, 0),    (bar_x, bar_y, bar_w, bar_h))
        if hp_ratio > 0:
            if hp_ratio > 0.5:
                bar_color = (50, 200, 50)
            elif hp_ratio > 0.25:
                bar_color = (220, 180, 30)
            else:
                bar_color = (220, 50, 50)
            pygame.draw.rect(surface, bar_color, (bar_x, bar_y, int(bar_w * hp_ratio), bar_h))
        pygame.draw.rect(surface, (180, 180, 180), (bar_x, bar_y, bar_w, bar_h), 1)


#------------------------------------------------------------------------------
# PAS TOUCHE !!!!!!!!

    def to_dict(self):
        return {
        "x":                      self.x,
        "y":                      self.y,
        "hp":                     self.hp,
        "alive":                  self.alive,
        "_attack_timer":          self._attack_timer,
        "_anim_frame":            self._anim_frame,
        "_anim_timer":            self._anim_timer,
        "_is_attacking":          self._is_attacking,
        "_attack_anim_timer":     self._attack_anim_timer,
        "_attack_anim_duration":  self._attack_anim_duration,
        "_attack_damage_applied": self._attack_damage_applied,
        "_hit_flash_timer":       self._hit_flash_timer,
        "_hit_flash_duration":    self._hit_flash_duration,
        "_anim_phase":            self._anim_phase,
        "_facing_left":           self._facing_left,
        }

    @classmethod
    def from_dict(cls, d):
        obj = cls(d["x"], d["y"])

        obj.hp = d.get("hp", obj.HP_MAX)
        obj.alive = d.get("alive", True)
        obj._attack_timer = d.get("_attack_timer", 0.0)
        obj._anim_frame = d.get("_anim_frame", 0)
        obj._anim_timer = d.get("_anim_timer", 0.0)
        obj._is_attacking = d.get("_is_attacking", False)
        obj._attack_anim_timer = d.get("_attack_anim_timer", 0.0)
        obj._attack_anim_duration = d.get("_attack_anim_duration", 0.4)
        obj._attack_damage_applied = d.get("_attack_damage_applied", False)
        obj._hit_flash_timer = d.get("_hit_flash_timer", 0.0)
        obj._hit_flash_duration = d.get("_hit_flash_duration", 0.15)
        obj._anim_phase = d.get("_anim_phase", 0.0)
        obj._facing_left = d.get("_facing_left", False)
        return obj
