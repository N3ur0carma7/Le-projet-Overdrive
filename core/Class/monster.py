import math
import pygame
import random


# ──────────────────────────────────────────────
#  Taille d'affichage du Woodcutter
#  Chaque frame source fait 48×48 px.
#  Modifie MONSTER_SCALE pour changer la taille :
#    1.0 → 48×48 px  (taille originale)
#    2.0 → 96×96 px  (plus grand)
#    0.5 → 24×24 px  (plus petit)
MONSTER_SCALE = 1.5
# ──────────────────────────────────────────────

FRAME_SIZE = 48   # taille d'une frame dans les spritesheets (ne pas modifier)


def _load_spritesheet(path: str, nb_frames: int, scale: float) -> list:
    """
    Découpe un spritesheet horizontal en liste de Surfaces pygame.
    Redimensionne selon `scale`.
    """
    sheet = pygame.image.load(path).convert_alpha()
    frames = []
    target_w = int(FRAME_SIZE * scale)
    target_h = int(FRAME_SIZE * scale)
    for i in range(nb_frames):
        rect = pygame.Rect(i * FRAME_SIZE, 0, FRAME_SIZE, FRAME_SIZE)
        raw = sheet.subsurface(rect).copy()
        if scale != 1.0:
            raw = pygame.transform.scale(raw, (target_w, target_h))
        frames.append(raw)
    return frames


class Monster:
    """
    Monstre PVE utilisant le sprite Woodcutter.
    Animations : walk (déplacement) et attack1 (attaque).
    """

    SPEED           = 80
    HP_MAX          = 30
    ATTACK_DAMAGE   = 3
    ATTACK_RANGE    = 40
    ATTACK_COOLDOWN = 1.0
    ATTACK_DAMAGE_DELAY = 0.15

    ANIM_FPS_WALK   = 8
    ANIM_FPS_ATTACK = 10
    ANIM_FPS_IDLE   = 6

    _walk_frames   = None
    _attack_frames = None
    _idle_frames   = None
    _hit_flash     = None

    @classmethod
    def load_sprites(cls):
        if cls._walk_frames is not None:
            return

        scale = MONSTER_SCALE

        cls._walk_frames   = _load_spritesheet("assets/monster/Woodcutter_walk.png",   6, scale)
        cls._attack_frames = _load_spritesheet("assets/monster/Woodcutter_attack1.png", 6, scale)
        cls._idle_frames   = _load_spritesheet("assets/monster/Woodcutter_idle.png",   4, scale)

        # Flash blanc pour coup reçu
        fw = int(FRAME_SIZE * scale)
        fh = int(FRAME_SIZE * scale)
        flash = pygame.Surface((fw, fh), pygame.SRCALPHA)
        flash.fill((255, 255, 255, 160))
        cls._hit_flash = flash

    # ── Taille logique utilisée pour le hit-rect et la barre de vie
    @property
    def SIZE(self):
        return int(FRAME_SIZE * MONSTER_SCALE)

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
        self._attack_anim_duration = 0.5
        self._attack_damage_applied = False

        self._hit_flash_timer    = 0.0
        self._hit_flash_duration = 0.15

        self._anim_phase  = random.uniform(0, 1)
        self._facing_left = False
        self._is_moving   = False

    def update(self, players: list, dt: float):
        if not self.alive:
            return

        self._attack_timer    = max(0.0, self._attack_timer - dt)
        self._hit_flash_timer = max(0.0, self._hit_flash_timer - dt)

        # Trouver la cible la plus proche
        target    = None
        best_dist = float("inf")
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
            self._is_moving = False
            self._update_anim(dt)
            return

        dx   = target.pos[0] - self.x
        dy   = target.pos[1] - self.y
        dist = math.hypot(dx, dy)

        if dx != 0:
            self._facing_left = dx < 0

        # Gestion de l'animation d'attaque en cours
        if self._is_attacking:
            self._attack_anim_timer -= dt
            if not self._attack_damage_applied:
                elapsed = self._attack_anim_duration - self._attack_anim_timer
                if elapsed >= self.ATTACK_DAMAGE_DELAY:
                    target.hurt(self.ATTACK_DAMAGE)
                    self._attack_damage_applied = True
            if self._attack_anim_timer <= 0:
                self._is_attacking = False
                self._attack_damage_applied = False
                self._anim_frame = 0

        # Décision : attaquer ou marcher
        if dist <= self.ATTACK_RANGE:
            self._is_moving = False
            if self._attack_timer <= 0.0:
                self._attack_timer = self.ATTACK_COOLDOWN
                self._is_attacking = True
                self._attack_anim_timer = self._attack_anim_duration
                self._attack_damage_applied = False
                self._anim_frame = 0
        else:
            self._is_moving = True
            if dist > 0:
                self.x += (dx / dist) * self.SPEED * dt
                self.y += (dy / dist) * self.SPEED * dt

        self._update_anim(dt)

    def _update_anim(self, dt: float):
        if self._is_attacking:
            fps = self.ANIM_FPS_ATTACK
            nb  = len(self._attack_frames)
        elif self._is_moving:
            fps = self.ANIM_FPS_WALK
            nb  = len(self._walk_frames)
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
        size = self.SIZE
        sx = int(self.x - camera_x) - size // 2
        sy = int(self.y - camera_y) - size // 2
        return pygame.Rect(sx, sy, size, size)

    def draw(self, surface: pygame.Surface, camera_x: float, camera_y: float):
        if not self.alive:
            return

        sw, sh = surface.get_size()
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)

        margin = self.SIZE + 20
        if sx > sw + margin or sx < -margin or sy > sh + margin or sy < -margin:
            return

        # Choisir la bonne liste de frames
        if self._is_attacking:
            frames = self._attack_frames
        elif self._is_moving:
            frames = self._walk_frames
        else:
            frames = self._idle_frames

        frame_idx = min(self._anim_frame, len(frames) - 1)
        sprite = frames[frame_idx]

        # Retourner si le monstre va à gauche
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
            surface.blit(flash, (draw_x, draw_y), special_flags=pygame.BLEND_RGBA_MULT)

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


# ──────────────────────────────────────────────
#  PAS TOUCHE !!!!!!!!

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
        obj.hp                       = d.get("hp", obj.HP_MAX)
        obj.alive                    = d.get("alive", True)
        obj._attack_timer            = d.get("_attack_timer", 0.0)
        obj._anim_frame              = d.get("_anim_frame", 0)
        obj._anim_timer              = d.get("_anim_timer", 0.0)
        obj._is_attacking            = d.get("_is_attacking", False)
        obj._attack_anim_timer       = d.get("_attack_anim_timer", 0.0)
        obj._attack_anim_duration    = d.get("_attack_anim_duration", 0.4)
        obj._attack_damage_applied   = d.get("_attack_damage_applied", False)
        obj._hit_flash_timer         = d.get("_hit_flash_timer", 0.0)
        obj._hit_flash_duration      = d.get("_hit_flash_duration", 0.15)
        obj._anim_phase              = d.get("_anim_phase", 0.0)
        obj._facing_left             = d.get("_facing_left", False)
        return obj