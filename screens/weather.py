import pygame
import random
import math

# ── Constantes de météo ──────────────────────────────────────
WEATHER_SUNNY  = "sunny"
WEATHER_CLOUDY = "cloudy"
WEATHER_WINDY  = "windy"
WEATHER_RAIN   = "rain"
WEATHER_STORM  = "storm"

# Matrice de transition probabiliste entre météos
_TRANSITIONS = {
    WEATHER_SUNNY:  {WEATHER_SUNNY: 40, WEATHER_CLOUDY: 35, WEATHER_WINDY: 15, WEATHER_RAIN:  8, WEATHER_STORM:  2},
    WEATHER_CLOUDY: {WEATHER_SUNNY: 25, WEATHER_CLOUDY: 35, WEATHER_WINDY: 20, WEATHER_RAIN: 15, WEATHER_STORM:  5},
    WEATHER_WINDY:  {WEATHER_SUNNY: 20, WEATHER_CLOUDY: 25, WEATHER_WINDY: 25, WEATHER_RAIN: 20, WEATHER_STORM: 10},
    WEATHER_RAIN:   {WEATHER_SUNNY: 10, WEATHER_CLOUDY: 20, WEATHER_WINDY: 20, WEATHER_RAIN: 35, WEATHER_STORM: 15},
    WEATHER_STORM:  {WEATHER_SUNNY:  5, WEATHER_CLOUDY: 20, WEATHER_WINDY: 20, WEATHER_RAIN: 30, WEATHER_STORM: 25},
}

# Durée (min, max) en secondes pour chaque météo
_DURATION = {
    WEATHER_SUNNY:  (60, 150),
    WEATHER_CLOUDY: (45, 120),
    WEATHER_WINDY:  (30,  90),
    WEATHER_RAIN:   (40, 100),
    WEATHER_STORM:  (30,  80),
}

# Vitesse multiplicateur des nuages par météo
_WIND_FACTOR = {
    WEATHER_SUNNY:  1.0,
    WEATHER_CLOUDY: 1.2,
    WEATHER_WINDY:  3.5,
    WEATHER_RAIN:   1.8,
    WEATHER_STORM:  2.2,
}

# Nombre de gouttes de pluie par météo
_RAIN_DROPS_COUNT = {
    WEATHER_SUNNY:  0,
    WEATHER_CLOUDY: 0,
    WEATHER_WINDY:  0,
    WEATHER_RAIN:   220,
    WEATHER_STORM:  420,
}

# Teinture ciel additionnelle (R, G, B, A) — None = aucune
_SKY_TINT = {
    WEATHER_SUNNY:  None,
    WEATHER_CLOUDY: (80,  80, 100,  25),
    WEATHER_WINDY:  None,
    WEATHER_RAIN:   (50,  65, 90,   55),
    WEATHER_STORM:  (25,  25, 55,  100),
}

# Labels affichés dans le HUD
_LABELS = {
    WEATHER_SUNNY:  "Ensoleille",
    WEATHER_CLOUDY: "Nuageux",
    WEATHER_WINDY:  "Venteux",
    WEATHER_RAIN:   "Pluie",
    WEATHER_STORM:  "Orage",
}


def _pick_next(current: str) -> str:
    choices = _TRANSITIONS[current]
    keys    = list(choices.keys())
    weights = list(choices.values())
    return random.choices(keys, weights=weights)[0]


# ── Goutte de pluie ──────────────────────────────────────────

class RainDrop:
    """Une goutte de pluie dans l'espace monde."""

    def __init__(self, map_min: int, map_max: int):
        self.map_min = map_min
        self.map_max = map_max
        self._randomize()

    def _randomize(self):
        self.x       = random.randint(self.map_min, self.map_max)
        self.y       = random.randint(self.map_min, self.map_max)
        self.speed_y = random.uniform(350, 520)
        self.speed_x = random.uniform(-50, -15)    # inclinaison vent
        self.length  = random.randint(7, 20)
        self.alpha   = random.randint(70, 160)

    def reset_top(self):
        """Replacer en haut de la zone après avoir dépassé le bas."""
        self.x = random.randint(self.map_min, self.map_max)
        self.y = self.map_min
        self.speed_y = random.uniform(350, 520)
        self.speed_x = random.uniform(-50, -15)
        self.length  = random.randint(7, 20)
        self.alpha   = random.randint(70, 160)

    def update(self, dt: float):
        self.x += self.speed_x * dt
        self.y += self.speed_y * dt
        if self.y > self.map_max:
            self.reset_top()

    def draw(self, surface: pygame.Surface, camera_x: float, camera_y: float):
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)

        # Culling simple
        sw, sh = surface.get_size()
        if sx < -40 or sx > sw + 40 or sy < -40 or sy > sh + 40:
            return

        ex = int(sx + self.speed_x * 0.05)
        ey = int(sy + self.length)
        try:
            pygame.draw.line(surface, (160, 200, 255), (sx, sy), (ex, ey), 1)
        except Exception:
            pass


# ── Éclair (orage) ───────────────────────────────────────────

class Lightning:
    """Produit un flash blanc bref lors d'un orage."""

    def __init__(self):
        self.active  = False
        self._timer  = 0.0
        self._max    = 0.25

    def trigger(self):
        self.active = True
        self._max   = random.uniform(0.08, 0.28)
        self._timer = self._max

    def update(self, dt: float):
        if self.active:
            self._timer -= dt
            if self._timer <= 0:
                self.active = False

    def apply_flash(self, surface: pygame.Surface):
        if not self.active:
            return
        ratio = max(0.0, self._timer / self._max)
        alpha = int(200 * ratio)
        flash = pygame.Surface(surface.get_size())
        flash.fill((240, 240, 255))
        flash.set_alpha(alpha)
        surface.blit(flash, (0, 0))


# ── Gestionnaire météo principal ─────────────────────────────

class WeatherManager:
    """
    Gère les transitions météo et produit les effets visuels associés.

    Utilisation dans jeu.py :
        weather = WeatherManager()

        # dans la boucle :
        weather.update(dt)
        # adapter la vitesse des nuages :
        for cloud in cloud_manager.clouds:
            cloud.speed_x = cloud._base_speed_x * weather.wind_factor

        # dans le rendu (surface_monde, avant scaling) :
        weather.draw_rain(surface_monde, camera_x, camera_y)

        # après ecran.blit(surface_affichee, (0,0)) et day_night.apply() :
        weather.apply_sky_tint(ecran)
        weather.apply_lightning_flash(ecran)

        # dans le HUD :
        weather.draw_label(ecran, x, y, font)
    """

    MAP_MIN = -4000
    MAP_MAX  =  4000

    def __init__(self, initial: str = WEATHER_SUNNY):
        self.current      = initial
        self._next_timer  = random.uniform(*_DURATION[initial])

        # Paramètres interpolés en douceur
        self._wind_current   = _WIND_FACTOR[initial]
        self._wind_target    = self._wind_current
        self._rain_alpha_cur = 0.0
        self._rain_alpha_tgt = float(_RAIN_DROPS_COUNT[initial] > 0) * 255.0

        # Gouttes
        self._drops: list[RainDrop] = []
        self._ensure_drops(_RAIN_DROPS_COUNT[initial])

        # Éclairs
        self._lightning   = Lightning()
        self._storm_timer = random.uniform(4, 10)

        # Teinture ciel
        self._sky_surf: pygame.Surface | None = None

    # ── Propriétés ──────────────────────────────────────────

    @property
    def wind_factor(self) -> float:
        """Multiplicateur de vitesse des nuages (1.0 = normal)."""
        return self._wind_current

    @property
    def label(self) -> str:
        return _LABELS.get(self.current, self.current)

    @property
    def is_raining(self) -> bool:
        return self.current in (WEATHER_RAIN, WEATHER_STORM)

    # ── Gestion des gouttes ──────────────────────────────────

    def _ensure_drops(self, target_count: int):
        while len(self._drops) < target_count:
            self._drops.append(RainDrop(self.MAP_MIN, self.MAP_MAX))
        while len(self._drops) > target_count:
            self._drops.pop()

    # ── Mise à jour ──────────────────────────────────────────

    def update(self, dt: float):
        # ── Transition météo
        self._next_timer -= dt
        if self._next_timer <= 0:
            self.current     = _pick_next(self.current)
            self._next_timer = random.uniform(*_DURATION[self.current])
            self._wind_target    = _WIND_FACTOR[self.current]
            nb = _RAIN_DROPS_COUNT[self.current]
            self._ensure_drops(nb)
            self._rain_alpha_tgt = 200.0 if nb > 0 else 0.0
            # Réinitialiser le timer d'éclair si on sort de l'orage
            if self.current != WEATHER_STORM:
                self._storm_timer = random.uniform(4, 10)

        # ── Interpolation douce des paramètres
        interp = min(1.0, dt * 1.5)
        self._wind_current    += (self._wind_target    - self._wind_current)    * interp
        self._rain_alpha_cur  += (self._rain_alpha_tgt - self._rain_alpha_cur)  * interp

        # ── Mise à jour des gouttes
        for drop in self._drops:
            drop.update(dt)

        # ── Éclairs (orage uniquement)
        self._lightning.update(dt)
        if self.current == WEATHER_STORM:
            self._storm_timer -= dt
            if self._storm_timer <= 0:
                self._lightning.trigger()
                self._storm_timer = random.uniform(3, 9)

    # ── Rendu pluie (dans surface_monde) ────────────────────

    def draw_rain(self, surface: pygame.Surface, camera_x: float, camera_y: float):
        """
        Dessine les gouttes de pluie sur la surface du monde.
        Appeler après cloud_manager.draw() et ambiance_manager.draw().
        """
        if not self._drops or self._rain_alpha_cur < 5:
            return
        for drop in self._drops:
            drop.draw(surface, camera_x, camera_y)

    # ── Teinture ciel (sur écran, après scaling) ─────────────

    def apply_sky_tint(self, surface: pygame.Surface):
        """
        Applique une teinture colorée sur l'écran selon la météo.
        Appeler après ecran.blit(surface_affichee, (0, 0)).
        """
        tint = _SKY_TINT.get(self.current)
        if tint is None:
            return
        r, g, b, a = tint
        w, h = surface.get_size()
        if self._sky_surf is None or self._sky_surf.get_size() != (w, h):
            self._sky_surf = pygame.Surface((w, h))
        self._sky_surf.fill((r, g, b))
        self._sky_surf.set_alpha(a)
        surface.blit(self._sky_surf, (0, 0))

    # ── Flash éclair ─────────────────────────────────────────

    def apply_lightning_flash(self, surface: pygame.Surface):
        """
        Applique un flash blanc bref lors d'un orage.
        Appeler après apply_sky_tint().
        """
        self._lightning.apply_flash(surface)

    # ── HUD ──────────────────────────────────────────────────

    def draw_label(self, ecran: pygame.Surface, x: int, y: int,
                   font: pygame.font.Font):
        """Affiche le nom de la météo courante avec un fond semi-transparent."""
        surf = font.render(self.label, True, (210, 230, 255))
        pad  = 6
        bg   = pygame.Surface((surf.get_width() + pad * 2,
                                surf.get_height() + pad * 2), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 100))
        ecran.blit(bg,   (x - pad, y - pad))
        ecran.blit(surf, (x, y))