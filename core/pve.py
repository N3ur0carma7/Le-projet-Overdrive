
import math
import random

from core.Class.monster import Monster

import multiplayer.client as client_module


TAILLE_CASE_DEFAULT = 64   # fallback si non transmis
import screens.game_logic as gl

class DamageNumber:
    #Chiffre de dégâts flottant affiché à l'écran.
    DURATION = 1.0   # secondes

    def __init__(self, x: float, y: float, amount: int, is_crit: bool = False):
        self.x = x
        self.y = y
        self.amount = amount
        self.is_crit = is_crit
        self.timer = self.DURATION
        self._font = None

    def update(self, dt: float):
        self.timer -= dt
        self.y -= 30 * dt   # remonte vers le haut

    @property
    def alive(self):
        return self.timer > 0

    def draw(self, surface, camera_x: float, camera_y: float):
        if self._font is None:
            import pygame
            try:
                self._font = pygame.font.Font("assets/fonts/Minecraft.ttf",
                                              18 if self.is_crit else 13)
            except Exception:
                self._font = pygame.font.SysFont("arial", 18 if self.is_crit else 13)

        import pygame
        alpha = int(255 * (self.timer / self.DURATION))
        color  = (255, 220, 0) if self.is_crit else (255, 80, 80)
        text   = f"{'CRIT! ' if self.is_crit else ''}{self.amount}"
        surf   = self._font.render(text, True, color)
        surf.set_alpha(alpha)
        sx = int(self.x - camera_x) - surf.get_width() // 2
        sy = int(self.y - camera_y)
        surface.blit(surf, (sx, sy))


class RaidManager:

    WAVES_PER_RAID   = 4
    MONSTERS_PER_WAVE_MIN = 5
    MONSTERS_PER_WAVE_MAX = 10
    SPAWN_DISTANCE_CASES  = 40   # ~40 cases du joueur
    WAVE_DELAY            = 10.0  # secondes entre vagues
    AUTO_RAID_MIN         = 5 * 60.0   # 1 min
    AUTO_RAID_MAX         = 10 * 60.0   # 2 min

    def __init__(self, taille_case: int = TAILLE_CASE_DEFAULT):
        self.taille_case    = taille_case
        self.monsters: list = gl.monsters
        self.damage_numbers: list = []
        self.leader = False
        self._raid_active   = False
        self._wave_index    = 0          # vague en cours
        self._wave_timer    = 0.0        # temps restant avant prochaine vague
        self._auto_timer    = self._random_auto_delay()
        self._raid_count    = 0          # nombre de raids déclenchés

        # Callbacks optionnels pour log terminal
        self.on_raid_start: callable = None   # fn(raid_num)
        self.on_wave_spawn: callable = None   # fn(wave_num, nb)
        self.on_raid_end:   callable = None   # fn()


    def trigger_raid(self) -> str:
        if self._raid_active:
            return "Un raid est deja en cours !"
        try:
            client_module.send_liste_monstres_client(self.monsters, client_module.CLIENT)
        except Exception as e:
            pass
        self._start_raid()
        return f"RAID #{self._raid_count} DECLENCHE ! Preparez-vous..."

    def update(self, players: list, dt: float):
        # Timer automatique
        if not self._raid_active:
            self._auto_timer -= dt
            if self._auto_timer <= 0:
                self._start_raid()
        old_monsters = self.monsters
        # Mise à jour des monstres vivants
        for m in self.monsters:
            m.update(players, dt)

        # Nettoyer les monstres morts

        self.monsters = [m for m in self.monsters if m.alive]

        if self.monsters != old_monsters:
            try:
                client_module.send_liste_monstres_client(self.monsters, client_module.CLIENT)
            except Exception as e:
                print(e)
        # Mise à jour des chiffres de dégâts
        for dn in self.damage_numbers:
            dn.update(dt)
        self.damage_numbers = [dn for dn in self.damage_numbers if dn.alive]

        # Gestion des vagues actives
        if self._raid_active:
            self._wave_timer -= dt
            if self._wave_timer <= 0:
                if self._wave_index < self.WAVES_PER_RAID and self.leader == True:
                    self._spawn_wave(players)
                else:
                    # Toutes les vagues lancées ; attendre fin des monstres
                    if not self.monsters:
                        self._end_raid()

    #draw
    def draw(self, surface, camera_x: float, camera_y: float):
        for m in self.monsters:
            m.draw(surface, camera_x, camera_y)
        for dn in self.damage_numbers:
            dn.draw(surface, camera_x, camera_y)

    def _start_raid(self):
        self._raid_active = True
        self._wave_index  = 0
        self._wave_timer  = 0.0   # première vague immédiate
        self._raid_count += 1
        if self.on_raid_start:
            self.on_raid_start(self._raid_count)

    def _spawn_wave(self, players: list):
        nb = random.randint(self.MONSTERS_PER_WAVE_MIN, self.MONSTERS_PER_WAVE_MAX)
        self._wave_index += 1
        spawned = 0

        for player in players:
            for _ in range(nb):
                angle = random.uniform(0, 2 * math.pi)
                # Distance
                dist_px = (self.SPAWN_DISTANCE_CASES + random.uniform(-0.5, 0.5)) * self.taille_case
                mx = player.pos[0] + math.cos(angle) * dist_px
                my = player.pos[1] + math.sin(angle) * dist_px
                self.monsters.append(Monster(mx, my))
                spawned += 1

        if self.on_wave_spawn:
            self.on_wave_spawn(self._wave_index, spawned)
        try:
            client_module.send_raid_client(self, client_module.CLIENT)
        except Exception as e:
            print(e)
        # Délai avant la prochaine vague
        self._wave_timer = self.WAVE_DELAY

    def _end_raid(self):
        self._raid_active = False
        self._auto_timer  = self._random_auto_delay()
        if self.on_raid_end:
            self.on_raid_end()

    @property
    def time_to_next_raid(self) -> float:
        return max(0.0, self._auto_timer) if not self._raid_active else 0.0

    @staticmethod
    def _random_auto_delay() -> float:
        return random.uniform(RaidManager.AUTO_RAID_MIN, RaidManager.AUTO_RAID_MAX)

    #----------------------------------------------------------------------------------------------------------------
    def to_dict(self):
        return {
            "taille_case": self.taille_case,
            "leader": self.leader,
            "_raid_active": self._raid_active,
            "_wave_index": self._wave_index,
            "_wave_timer": self._wave_timer,
            "_auto_timer": self._auto_timer,
            "_raid_count": self._raid_count,
            "monsters": [m.to_dict() for m in self.monsters],
        }

    @classmethod
    def from_dict(cls, d):
        obj = cls(d.get("taille_case", TAILLE_CASE_DEFAULT))
        obj.leader = d.get("leader", False)
        obj._raid_active = d.get("_raid_active", False)
        obj._wave_index = d.get("_wave_index", 0)
        obj._wave_timer = d.get("_wave_timer", 0.0)
        obj._auto_timer = d.get("_auto_timer", 0.0)
        obj._raid_count = d.get("_raid_count", 0)
        obj.monsters = [Monster.from_dict(m) for m in d.get("monsters", [])]

        return obj