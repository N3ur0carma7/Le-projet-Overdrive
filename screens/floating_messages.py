

import pygame
import math

_FONT = None
_FONT_SMALL = None

def _get_fonts():
    global _FONT, _FONT_SMALL
    if _FONT is None:
        try:
            _FONT       = pygame.font.Font("assets/fonts/Minecraft.ttf", 15)
            _FONT_SMALL = pygame.font.Font("assets/fonts/Minecraft.ttf", 12)
        except Exception:
            _FONT       = pygame.font.SysFont("arial", 15, bold=True)
            _FONT_SMALL = pygame.font.SysFont("arial", 12)
    return _FONT, _FONT_SMALL


class _FloatingMsg:
    DURATION = 1.8
    RISE     = 60  #pixel par seconde vers le haut

    def __init__(self, text: str, x: int, y: int, color=(230, 60, 60), small=False):
        self.text     = text
        self.x        = float(x)
        self.y        = float(y)
        self.color    = color
        self.small    = small
        self.timer    = 0.0
        self.alive    = True
        self.player_id = None

    def update(self, dt: float):
        self.timer += dt
        self.y     -= self.RISE * dt
        if self.timer >= self.DURATION:
            self.alive = False

    def draw(self, surface: pygame.Surface):
        font, font_small = _get_fonts()
        f = font_small if self.small else font

        # opacité
        ratio = self.timer / self.DURATION
        if ratio < 0.15:
            alpha = int(255 * (ratio / 0.15))
        elif ratio > 0.6:
            alpha = int(255 * (1.0 - (ratio - 0.6) / 0.4))
        else:
            alpha = 255

        ox = int(math.sin(self.timer * 6) * 2)

        txt_surf = f.render(self.text, True, self.color)

        shadow = f.render(self.text, True, (0, 0, 0))
        shadow.set_alpha(int(alpha * 0.6))
        txt_surf.set_alpha(alpha)

        cx = int(self.x) - txt_surf.get_width() // 2
        cy = int(self.y) - txt_surf.get_height() // 2

        surface.blit(shadow, (cx + ox + 1, cy + 1))
        surface.blit(txt_surf, (cx + ox, cy))


class FloatingMessageManager:

    COLOR_ERROR   = (230,  60,  60)
    COLOR_WARNING = (255, 165,   0)
    COLOR_INFO    = (100, 200, 255)
    COLOR_SUCCESS = ( 80, 220,  80)

    def __init__(self):
        self._messages: list[_FloatingMsg] = []

    def add(self, text: str, x: int, y: int,
            color=None, small: bool = False, player_id: int = None):
        if color is None:
            color = self.COLOR_ERROR

        if player_id is not None:
            self._messages = [m for m in self._messages if m.player_id != player_id]

        offset = len(self._messages) * 6
        msg = _FloatingMsg(text, x, y - offset, color, small)
        msg.player_id = player_id
        self._messages.append(msg)

    def error(self, text: str, x: int, y: int, player_id: int = None):
        self.add(text, x, y, self.COLOR_ERROR, player_id=player_id)

    def warning(self, text: str, x: int, y: int, player_id: int = None):
        self.add(text, x, y, self.COLOR_WARNING, player_id=player_id)

    def info(self, text: str, x: int, y: int, player_id: int = None):
        self.add(text, x, y, self.COLOR_INFO, player_id=player_id)

    def success(self, text: str, x: int, y: int, player_id: int = None):
        self.add(text, x, y, self.COLOR_SUCCESS, player_id=player_id)

    def update(self, dt: float):
        for m in self._messages:
            m.update(dt)
        self._messages = [m for m in self._messages if m.alive]

    def draw(self, surface: pygame.Surface):
        for m in self._messages:
            m.draw(surface)