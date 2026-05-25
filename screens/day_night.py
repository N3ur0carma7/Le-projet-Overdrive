import pygame
import math

# ── Durées du cycle ──────────────────────────────────────────
DAY_DURATION   = 180.0   # secondes (3 min)
NIGHT_DURATION = 180.0   # secondes (3 min)
CYCLE_TOTAL    = DAY_DURATION + NIGHT_DURATION  # 360 s

# ── Keyframes de couleur overlay (RGBA) ─────────────────────
# phase 0.0 = aube  →  0.5 = début de nuit  →  1.0 = retour aube
# R, G, B = teinte  /  A = opacité (0 = invisible, 255 = opaque)
_KEYFRAMES = [
    (0.00, (  0,   0,   0,   0)),   # plein jour (transparent)
    (0.40, (  0,   0,   0,   0)),   # encore jour
    (0.47, (220, 100,  20, 100)),   # coucher de soleil (orange)
    (0.52, ( 15,  15,  70, 190)),   # tombée de la nuit
    (0.55, ( 10,  10,  50, 210)),   # nuit profonde
    (0.93, ( 10,  10,  50, 210)),   # nuit profonde (fin)
    (0.97, ( 90,  50, 120, 130)),   # lever du soleil (mauve)
    (1.00, (  0,   0,   0,   0)),   # retour jour
]


def _lerp(a, b, t):
    return a + (b - a) * t


def _lerp_color(c1, c2, t):
    return tuple(int(_lerp(a, b, t)) for a, b in zip(c1, c2))


def _overlay_color(phase):
    """Retourne (R, G, B, A) interpolé selon la phase [0, 1[."""
    for i in range(len(_KEYFRAMES) - 1):
        p0, c0 = _KEYFRAMES[i]
        p1, c1 = _KEYFRAMES[i + 1]
        if p0 <= phase < p1:
            t = (phase - p0) / (p1 - p0)
            return _lerp_color(c0, c1, t)
    return (0, 0, 0, 0)


class DayNightCycle:
    """
    Gère le cycle jour / nuit.

    Utilisation dans jeu.py :
        day_night = DayNightCycle()

        # dans la boucle :
        day_night.update(dt)

        # après ecran.blit(surface_affichee, (0, 0)) :
        day_night.apply(ecran)

        # dans le HUD :
        day_night.draw_clock(ecran, x, y, font)
    """

    def __init__(self, start_phase: float = 0.0):
        """
        start_phase : position initiale dans le cycle (0.0 = aube, 0.5 = minuit).
        """
        self.time = start_phase * CYCLE_TOTAL
        self._overlay_surface = None   # Surface SRCALPHA réutilisée

    # ── Propriétés ──────────────────────────────────────────

    @property
    def phase(self) -> float:
        """Phase dans le cycle, entre 0.0 et 1.0."""
        return (self.time % CYCLE_TOTAL) / CYCLE_TOTAL

    @property
    def is_night(self) -> bool:
        p = self.phase
        return 0.52 <= p < 0.97

    @property
    def is_day(self) -> bool:
        return not self.is_night

    @property
    def is_sunset(self) -> bool:
        p = self.phase
        return 0.40 <= p < 0.52

    @property
    def is_sunrise(self) -> bool:
        p = self.phase
        return 0.93 <= p < 1.0

    @property
    def brightness(self) -> float:
        """
        Luminosité ambiante entre 0.0 (nuit noire) et 1.0 (plein jour).
        Utile pour moduler la production ou les effets sonores.
        """
        color = _overlay_color(self.phase)
        alpha = color[3] / 255.0
        return max(0.0, 1.0 - alpha * 0.85)

    @property
    def time_label(self) -> str:
        """
        Heure simulée sur 24 h affichée sous forme '06:00'.
        Le cycle commence à l'aube (06:00).
        """
        minutes_total = (self.phase * 24 * 60 + 6 * 60) % (24 * 60)
        h = int(minutes_total // 60)
        m = int(minutes_total % 60)
        return f"{h:02d}:{m:02d}"

    # ── Mise à jour ──────────────────────────────────────────

    def update(self, dt: float):
        self.time = (self.time + dt) % CYCLE_TOTAL

    # ── Rendu overlay ────────────────────────────────────────

    def apply(self, surface: pygame.Surface):
        """
        Superpose l'overlay coloré (jour/nuit/coucher) sur la surface donnée.
        Appeler APRÈS ecran.blit(surface_affichee, (0, 0)).
        """
        color = _overlay_color(self.phase)
        alpha = color[3]
        if alpha == 0:
            return

        w, h = surface.get_size()

        # Réutiliser ou recréer la surface si la taille a changé
        if self._overlay_surface is None or self._overlay_surface.get_size() != (w, h):
            self._overlay_surface = pygame.Surface((w, h), pygame.SRCALPHA)

        self._overlay_surface.fill((*color[:3], alpha))
        surface.blit(self._overlay_surface, (0, 0),
                     special_flags=pygame.BLEND_RGBA_MULT if alpha < 10 else 0)

    # ── Affichage HUD ────────────────────────────────────────

    def draw_clock(self, ecran: pygame.Surface, x: int, y: int,
                   font: pygame.font.Font):
        """
        Dessine l'heure simulée avec une icône soleil/lune dans le HUD.
        """
        if self.is_night:
            icon = "☽"
            color = (160, 180, 255)
        elif self.is_sunset or self.is_sunrise:
            icon = "🌅"
            color = (255, 200, 100)
        else:
            icon = "☀"
            color = (255, 240, 100)

        label = f"{icon}  {self.time_label}"
        surf  = font.render(label, True, color)

        # Fond semi-transparent pour lisibilité
        pad = 6
        bg  = pygame.Surface((surf.get_width() + pad * 2,
                               surf.get_height() + pad * 2), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 100))
        ecran.blit(bg,   (x - pad, y - pad))
        ecran.blit(surf, (x, y))