import math
import pygame
import multiplayer.client as client_module




FRAME_W = 48
FRAME_H = 48


ANIM_FRAMES = {
    "idle":         4,   # 192 / 48
    "run":          6,   # 288 / 48
    "hand_cannon":  6,   # 288 / 48
    "hit":          3,   # 144 / 48
    "death":        6,   # 288 / 48
}

ANIM_FPS = {
    "idle":        8,
    "run":        10,
    "hand_cannon": 12,
    "hit":         10,
    "death":        8,
}


class Player:
    _sheets: dict = {}   # {name: pygame.Surface}

    MAX_MONEY = 3000
    MAX_FOOD = 100
    MAX_VAPEUR = 100
    START_MONEY  = 1500
    START_FOOD   = 100
    START_VAPEUR = 40

    @classmethod
    def load_sprites(cls):
        if cls._sheets:
            return
        for name in ANIM_FRAMES:
            cls._sheets[name] = pygame.image.load(
                f"assets/player_sprites/{name}.png"
            ).convert_alpha()

    def __init__(self):
        self.hp_max       = 100
        self.hp           = 100
        self.crit_chance  = 20
        self.crit_damage  = 20
        self.raw_damage   = 10
        self.defense      = 0
        self.health_regen = 1
        self.money  = Player.START_MONEY
        self.max_money = Player.MAX_MONEY
        self.food   = Player.START_FOOD
        self.max_food = Player.MAX_FOOD
        self.vapeur = Player.START_VAPEUR
        self.max_vapeur = Player.MAX_VAPEUR
        self.pos    = (0, 0)
        self.path   = []

        self.inventory = {
            "potion_money": 0,
            "potion_food": 0,
            "potion_vapeur": 0,
            "potion_heal": 0
        }

        self.active_effects = {
            "money": 0,
            "food": 0,
            "vapeur": 0,
            "heal": 0
        }

        self.speed = 420
        self.size  = 40

        # Animation
        self.direction  = "right"
        self.anim_state = "idle"
        self.anim_frame = 0
        self.anim_timer = 0.0
        self.is_moving  = False


        self._attack_anim_active   = False
        self._attack_anim_timer    = 0.0
        self._attack_anim_duration = ANIM_FRAMES["hand_cannon"] / ANIM_FPS["hand_cannon"]

        self.sprite_height = 64

    # ------------------------------------------------------------------
    def trigger_attack_anim(self):
        self._attack_anim_active = True
        self._attack_anim_timer  = self._attack_anim_duration
        self.anim_state  = "hand_cannon"
        self.anim_frame  = 0
        self.anim_timer  = 0.0

    def hurt(self, raw_damage: int):
        damage = raw_damage / (self.defense * 0.05 + 1)
        self.hp -= damage
        if self.hp <= 0:
            return None
        return damage

    # ------------------------------------------------------------------
    def update(self, keys_pressed, dt=1/60):

        dir_x = 0
        dir_y = 0

        if keys_pressed.get(pygame.K_z, False):  # Haut
            dir_y = -1
        if keys_pressed.get(pygame.K_s, False):  # Bas
            dir_y = 1
        if keys_pressed.get(pygame.K_q, False):  # Gauche
            dir_x = -1
        if keys_pressed.get(pygame.K_d, False):  # Droite
            dir_x = 1

        if dir_x != 0 or dir_y != 0:
            magnitude = math.hypot(dir_x, dir_y)
            if magnitude > 0:
                dir_x /= magnitude
                dir_y /= magnitude
                
                if abs(dir_x) >= abs(dir_y):
                    self.direction = "right" if dir_x > 0 else "left"
                
                step = self.speed * dt
                self.pos = (self.pos[0] + dir_x * step, self.pos[1] + dir_y * step)
                self.is_moving = True
        else:
            self.is_moving = False


    def update_anim(self, dt):
        if self._attack_anim_active:
            self._attack_anim_timer -= dt
            if self._attack_anim_timer <= 0:
                self._attack_anim_active = False
                self.anim_state = "run" if self.is_moving else "idle"
                self.anim_frame = 0
                self.anim_timer = 0.0
            else:
                self._advance_frame("hand_cannon", dt)
            return

        self.anim_state = "run" if self.is_moving else "idle"
        self._advance_frame(self.anim_state, dt)

    def _advance_frame(self, state, dt):
        fps       = ANIM_FPS[state]
        nb_frames = ANIM_FRAMES[state]
        self.anim_timer += dt
        if self.anim_timer >= 1.0 / fps:
            self.anim_timer = 0.0
            self.anim_frame = (self.anim_frame + 1) % nb_frames
        self.anim_state = state

    def draw_player(self, surface, camera_x, camera_y):
        Player.load_sprites()

        sheet = Player._sheets[self.anim_state]
        frame = min(self.anim_frame, ANIM_FRAMES[self.anim_state] - 1)

        src_rect = pygame.Rect(frame * FRAME_W, 0, FRAME_W, FRAME_H)

        scale = self.sprite_height / FRAME_H
        dst_w = int(FRAME_W * scale)
        dst_h = self.sprite_height

        sub    = sheet.subsurface(src_rect)
        scaled = pygame.transform.scale(sub, (dst_w, dst_h))

        if self.direction == "left":
            scaled = pygame.transform.flip(scaled, True, False)

        draw_x = int(self.pos[0] - camera_x) - dst_w // 2
        draw_y = int(self.pos[1] - camera_y) - dst_h // 2

        surface.blit(scaled, (draw_x, draw_y))
        return True

    # PAS TOUCHE !!!!!!!!
    def to_dict(self):
        return {
            "hp_max": self.hp_max, "hp": self.hp,
            "crit_chance": self.crit_chance, "crit_damage": self.crit_damage,
            "raw_damage": self.raw_damage, "defense": self.defense,
            "health_regen": self.health_regen, "money": self.money,
            "food": self.food, "vapeur": self.vapeur,
            "pos": self.pos, "path": self.path,
            "speed": self.speed, "size": self.size,
            "anim_state": self.anim_state,
            "anim_frame": self.anim_frame,
            "direction": self.direction,
            "is_moving": self.is_moving
        }

    @classmethod
    def from_dict(cls, d):
        obj = cls()
        obj.hp_max       = d.get("hp_max",       100)
        obj.hp           = d.get("hp",            100)
        obj.crit_chance  = d.get("crit_chance",    20)
        obj.crit_damage  = d.get("crit_damage",    10)
        obj.raw_damage   = d.get("raw_damage",      1)
        obj.defense      = d.get("defense",         0)
        obj.health_regen = d.get("health_regen",    1)
        obj.money        = d.get("money",        5000)
        obj.food         = d.get("food",            0)
        obj.vapeur       = d.get("vapeur",          0)
        obj.pos          = d.get("pos",          (0, 0))
        obj.path         = d.get("path",           [])
        obj.speed        = d.get("speed",         420)
        obj.size         = d.get("size",           40)
        obj.anim_state = d.get("anim_state", "idle")
        obj.anim_frame = d.get("anim_frame", 0)
        obj.direction = d.get("direction", "right")
        obj.is_moving = d.get("is_moving", False)
        return obj
