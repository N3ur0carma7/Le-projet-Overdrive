import time
import random

import pygame
import re


_HELLO_PATTERN = re.compile(
    r'print\s*\(\s*["\']?\s*hello[\s,_\-]*world["\']?\s*\)',
    re.IGNORECASE
)


def _is_hello_world(raw: str) -> bool:
    if _HELLO_PATTERN.search(raw.strip()):
        return True
    if re.search(r'hello[\s,_\-]*world', raw.strip(), re.IGNORECASE):
        return True
    return False




class MatrixRain:
    CHARS    = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#$%&"
    DURATION = 4.0
    FADE_IN  = 0.3
    FADE_OUT = 1.0

    def __init__(self, w: int, h: int):
        try:
            self._font = pygame.font.Font("assets/fonts/Minecraft.ttf", 16)
        except Exception:
            self._font = pygame.font.SysFont("monospace", 16)
        self._col_w   = self._font.size("A")[0] + 2
        self._line_h  = self._font.get_linesize()
        self._cols    = max(1, w // self._col_w)
        self._rows    = max(1, h // self._line_h)
        self._w       = w
        self._h       = h
        self._elapsed = 0.0
        self.done     = False
        self._drops   = []
        for _ in range(self._cols):
            self._drops.append({
                "y":            random.uniform(-self._rows, 0),
                "speed":        random.uniform(0.3, 1.0),
                "trail":        random.randint(4, 16),
                "chars":        [random.choice(self.CHARS) for _ in range(self._rows)],
                "mutate_timer": 0.0,
            })

    def update(self, dt: float):
        self._elapsed += dt
        if self._elapsed >= self.DURATION:
            self.done = True
            return
        for drop in self._drops:
            drop["y"] += drop["speed"] * dt * 12
            drop["mutate_timer"] += dt
            if drop["mutate_timer"] > 0.08:
                drop["mutate_timer"] = 0.0
                drop["chars"][random.randint(0, self._rows - 1)] = random.choice(self.CHARS)
            if drop["y"] - drop["trail"] > self._rows:
                drop["y"]     = random.uniform(-6, 0)
                drop["speed"] = random.uniform(0.3, 1.0)
                drop["trail"] = random.randint(4, 16)

    def draw(self, ecran: pygame.Surface):
        if self.done:
            return
        t = self._elapsed
        if t < self.FADE_IN:
            alpha_bg = int(180 * t / self.FADE_IN)
        elif t > self.DURATION - self.FADE_OUT:
            alpha_bg = int(180 * (self.DURATION - t) / self.FADE_OUT)
        else:
            alpha_bg = 180
        bg = pygame.Surface((self._w, self._h), pygame.SRCALPHA)
        bg.fill((0, 0, 0, alpha_bg))
        ecran.blit(bg, (0, 0))
        for ci, drop in enumerate(self._drops):
            head_row = int(drop["y"])
            x = ci * self._col_w
            for offset in range(drop["trail"] + 1):
                row = head_row - offset
                if row < 0 or row >= self._rows:
                    continue
                y = row * self._line_h
                if offset == 0:
                    color, alpha = (220, 255, 220), 255
                else:
                    fade  = 1.0 - offset / drop["trail"]
                    color = (0, int(220 * fade), 0)
                    alpha = int(255 * fade)
                char = drop["chars"][row % len(drop["chars"])]
                try:
                    s = self._font.render(char, True, color)
                    s.set_alpha(alpha)
                    ecran.blit(s, (x, y))
                except Exception:
                    pass



def cmd_godlike(args, player, batiments, **ctx):
    player.money  += 10_000
    player.food   += 10_000
    player.vapeur += 10_000
    return "[OK] +10 000 or, nourriture, vapeur"


def cmd_give(args, player, batiments, **ctx):
    ressources = {"or": "money", "food": "food", "vapeur": "vapeur",
                  "money": "money", "argent": "money"}
    if len(args) < 2:
        return "Usage : give <or|food|vapeur> <quantite>"
    nom = args[0].lower()
    if nom not in ressources:
        return f"Ressource inconnue : {args[0]}."
    try:
        qte = int(args[1])
    except ValueError:
        return "La quantite doit etre un entier."
    setattr(player, ressources[nom], getattr(player, ressources[nom]) + qte)
    return f"+{qte} {args[0]}"


def cmd_set(args, player, batiments, **ctx):
    ressources = {"or": "money", "food": "food", "vapeur": "vapeur",
                  "money": "money", "argent": "money"}
    if len(args) < 2:
        return "Usage : set <or|food|vapeur> <valeur>"
    nom = args[0].lower()
    if nom not in ressources:
        return f"Ressource inconnue : {args[0]}."
    try:
        val = int(args[1])
    except ValueError:
        return "La valeur doit etre un entier."
    setattr(player, ressources[nom], val)
    return f"{args[0]} = {val}"


def cmd_status(args, player, batiments, **ctx):
    return (f"HP {player.hp}/{player.hp_max}  |  "
            f"Or {player.money}  |  Food {player.food}  |  Vapeur {player.vapeur}  |  "
            f"Batiments {len(batiments)}")


def cmd_heal(args, player, batiments, **ctx):
    player.hp = player.hp_max
    return f"[OK] HP restaures a {player.hp_max}"


def cmd_clear(args, player, batiments, **ctx):
    return "__CLEAR__"


def cmd_help(args, player, batiments, **ctx):
    lignes = ["Commandes disponibles :"]
    for name, (fn, desc) in sorted(COMMANDS.items()):
        lignes.append(f"  {name:<14} {desc}")
    return "\n".join(lignes)


def cmd_spawn(args, player, batiments, **ctx):
    if not args:
        return "Usage : spawn <ennemi> [quantite]"
    nom = args[0]
    try:
        qte = int(args[1]) if len(args) > 1 else 1
    except ValueError:
        qte = 1
    if ctx.get("spawn_fn"):
        return ctx["spawn_fn"](nom, qte)
    return f"(PVE non encore implemente) spawn {qte}x {nom}"


def cmd_event(args, player, batiments, **ctx):
    if not args:
        return "Usage : event <nom>"
    nom = args[0]
    if ctx.get("trigger_event_fn"):
        return ctx["trigger_event_fn"](nom)
    return f"(Events non encore implementes) event '{nom}'"


def cmd_trigger_raid(args, player, batiments, **ctx):
    raid_mgr = ctx.get("raid_manager")
    if raid_mgr is None:
        return "Gestionnaire PVE introuvable."
    return raid_mgr.trigger_raid()


def cmd_settime(args, player, batiments, **ctx):
    return "Commande 'settime' desactivee : le systeme jour/nuit a ete supprime."


def cmd_setweather(args, player, batiments, **ctx):
    from screens.weather import WEATHER_SUNNY, WEATHER_CLOUDY, WEATHER_WINDY, WEATHER_RAIN, WEATHER_STORM
    weather = ctx.get("weather")
    if weather is None:
        return "Gestionnaire meteo introuvable."

    if not args:
        return f"Meteo actuelle : {weather.label}  |  Vent {weather.wind_factor:.1f}x"

    weathers = {
        "sunny": WEATHER_SUNNY,
        "cloudy": WEATHER_CLOUDY,
        "windy": WEATHER_WINDY,
        "rain": WEATHER_RAIN,
        "storm": WEATHER_STORM,
        "ensolleille": WEATHER_SUNNY,
        "nuageux": WEATHER_CLOUDY,
        "venteux": WEATHER_WINDY,
        "pluie": WEATHER_RAIN,
        "orage": WEATHER_STORM,
    }

    arg = args[0].lower()
    if arg not in weathers:
        opts = ", ".join(sorted(set(weathers.values())))
        return f"Meteo inconnue : '{arg}'.\nOptions : {opts}"

    new_weather = weathers[arg]
    from screens.weather import _DURATION, _WIND_FACTOR, _RAIN_DROPS_COUNT

    weather.current = new_weather
    weather._next_timer = 60.0
    weather._wind_target = _WIND_FACTOR[new_weather]
    nb = _RAIN_DROPS_COUNT[new_weather]
    weather._ensure_drops(nb)
    weather._rain_alpha_tgt = 200.0 if nb > 0 else 0.0

    if new_weather != WEATHER_STORM:
        weather._storm_timer = 10.0

    return f"[OK] Meteo changee a {weather.label}  |  Vent {weather.wind_factor:.1f}x"


COMMANDS: dict[str, tuple] = {
    "godlike":  (cmd_godlike,  "Donne 10 000 de chaque ressource"),
    "give":     (cmd_give,     "give <ressource> <qte>"),
    "set":      (cmd_set,      "set <ressource> <valeur>"),
    "status":   (cmd_status,   "Affiche l'etat du joueur"),
    "heal":     (cmd_heal,     "Restaure les HP au max"),
    "clear":    (cmd_clear,    "Efface l'historique"),
    "help":     (cmd_help,     "Liste les commandes"),
    "spawn":        (cmd_spawn,        "spawn <ennemi> [qte]  (PVE)"),
    "event":        (cmd_event,        "event <nom>  (Events)"),
    "trigger_raid": (cmd_trigger_raid, "Declenche un raid PVE immediatement"),
    "setweather":   (cmd_setweather,   "setweather [sunny|cloudy|windy|rain|storm]"),
}




class Terminal:

    HISTORIQUE_MAX = 200
    BG_COLOR       = (30, 30, 30)
    TEXT_COLOR     = (220, 220, 220)
    PROMPT_COLOR   = (255, 255, 255)
    INPUT_BG       = (20, 20, 20)

    def __init__(self, dev_mode: bool = False):
        self.dev_mode        = dev_mode
        self.visible         = False
        self.input_text      = ""
        self.historique      = ["Bienvenue dans le terminal Overdrive !",
                                "Tapez 'help' pour la liste des commandes."]
        self.scroll_offset   = 0
        self._font           = None
        self.command_history = []
        self.history_index   = -1
        self._ac_prefix      = None
        self._ac_matches     = []
        self._ac_index       = 0
        self._last_ctx       = {}
        self._matrix_rain    = None
        self._matrix_pending = False

    def _get_font(self):
        if self._font is None:
            try:
                self._font = pygame.font.Font("assets/fonts/Minecraft.ttf", 14)
            except Exception:
                self._font = pygame.font.SysFont("consolas", 14)
        return self._font

    def toggle(self):
        if not self.dev_mode:
            return
        self.visible = not self.visible
        if self.visible:
            self.input_text    = ""
            self.scroll_offset = 0
            self.history_index = -1
            self._ac_prefix    = None
            self._ac_matches   = []
            self._ac_index     = 0

    def handle_event(self, event, player, batiments, extra_ctx=None):
        if not self.visible:
            return False
        self._last_ctx = extra_ctx or {}
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self._executer(player, batiments, extra_ctx or {})
            elif event.key == pygame.K_ESCAPE:
                self.visible = False
                self._ac_prefix = None
                self._ac_matches = []
                self.history_index = -1
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
                self.history_index = -1
                self._ac_prefix = None
            elif event.key == pygame.K_UP:
                if self.command_history:
                    if self.history_index == -1:
                        self.history_index = 0
                    else:
                        self.history_index = min(self.history_index + 1, len(self.command_history) - 1)
                    self.input_text = self.command_history[len(self.command_history) - 1 - self.history_index]
                    self._ac_prefix = None
            elif event.key == pygame.K_DOWN:
                if self.history_index > 0:
                    self.history_index -= 1
                    self.input_text = self.command_history[len(self.command_history) - 1 - self.history_index]
                elif self.history_index == 0:
                    self.history_index = -1
                    self.input_text = ""
                self._ac_prefix = None
            elif event.key == pygame.K_PAGEUP:
                self.scroll_offset = min(self.scroll_offset + 5,
                                         max(0, len(self.historique) - 1))
            elif event.key == pygame.K_PAGEDOWN:
                self.scroll_offset = max(0, self.scroll_offset - 5)
            elif event.key == pygame.K_TAB:
                reverse = bool(event.mod & pygame.KMOD_SHIFT)
                self._autocomplete(reverse=reverse)
            else:
                char = event.unicode
                if char and char.isprintable() and char != "\xb2":
                    self.input_text += char
                    self.history_index = -1
                    self._ac_prefix = None
            return True
        return False

    def _executer(self, player, batiments, extra_ctx):
        raw = self.input_text.strip()
        self.input_text = ""
        if not raw:
            return

        self.command_history.append(raw)
        if len(self.command_history) > 100:
            self.command_history.pop(0)
        self.history_index = -1

        self._log(f"> {raw}")

        if _is_hello_world(raw):
            self._log("hello world")
            time.sleep(0.5)
            self._log("...")
            time.sleep(0.3)
            self._log("Vraiment ?")
            time.sleep(0.2)
            self._log("Bon, petit cadeau :")
            self._matrix_pending = True
            return

        parts = raw.split()
        nom, args = parts[0].lower(), parts[1:]

        if nom not in COMMANDS:
            self._log(f"Commande inconnue : '{nom}'. Tapez 'help'.")
            return

        fn, _ = COMMANDS[nom]
        try:
            resultat = fn(args, player=player, batiments=batiments, **extra_ctx)
        except Exception as e:
            resultat = f"Erreur : {e}"

        if resultat == "__CLEAR__":
            self.historique.clear()
        elif resultat:
            for ligne in resultat.split("\n"):
                self._log(ligne)

    def _autocomplete_candidates(self, parts: list[str], current_index: int) -> list[str]:
        if current_index <= 0:
            return list(COMMANDS.keys())
        cmd = parts[0].lower()
        if cmd in ("give", "set"):
            return ["or", "money", "argent", "food", "vapeur"]
        if cmd == "spawn":
            return ["monster", "monstre", "slime", "goblin", "skeleton"]
        if cmd == "event":
            return ["raid", "wave", "night", "day"]
        raid_mgr = self._last_ctx.get("raid_manager")
        if cmd == "trigger_raid" and raid_mgr is not None:
            return ["now"]
        return []

    def _autocomplete(self, reverse: bool = False):
        raw = self.input_text
        if not raw:
            return

        left = raw.rstrip("\n")
        ends_with_space = left.endswith(" ")
        parts = left.split()

        if ends_with_space:
            parts.append("")

        if not parts:
            return

        current_index = len(parts) - 1
        prefix = parts[current_index]
        prefix_l = prefix.lower()
        candidates = self._autocomplete_candidates(parts, current_index)

        def _filter(cands):
            if prefix_l == "":
                return sorted(set(cands))
            return sorted({c for c in cands if c.lower().startswith(prefix_l)})

        matches = _filter(candidates)

        ac_key = (tuple(parts[:-1]), prefix_l, tuple(matches))
        if self._ac_prefix != ac_key:
            self._ac_prefix = ac_key
            self._ac_matches = matches
            self._ac_index = 0
            if len(matches) > 1:
                self._log("  ".join(matches))

        if not self._ac_matches:
            return

        if reverse:
            self._ac_index = (self._ac_index - 1) % len(self._ac_matches)
        else:
            self._ac_index = (self._ac_index + 1) % len(self._ac_matches) if len(self._ac_matches) > 1 else 0

        chosen = self._ac_matches[self._ac_index]
        parts[current_index] = chosen

        completed = " ".join(parts).rstrip()
        if current_index == 0 and chosen in COMMANDS:
            self.input_text = completed + " "
        else:
            self.input_text = completed

    def _log(self, msg: str):
        self.historique.append(msg)
        if len(self.historique) > self.HISTORIQUE_MAX:
            self.historique.pop(0)
        self.scroll_offset = 0

    def draw(self, ecran, dt: float = 0.016):
        W, H = ecran.get_size()

        if self._matrix_pending:
            self._matrix_rain    = MatrixRain(W, H)
            self._matrix_pending = False

        if self._matrix_rain is not None:
            self._matrix_rain.update(dt)
            self._matrix_rain.draw(ecran)
            if self._matrix_rain.done:
                self._matrix_rain = None

        if not self.visible:
            return

        font = self._get_font()
        term_w = W // 3
        term_h = H // 2
        line_h = font.get_linesize()
        padding = 8
        input_h = line_h + padding * 2

        bg = pygame.Surface((term_w, term_h))
        bg.fill(self.BG_COLOR)
        ecran.blit(bg, (0, 0))

        zone_hist_h = term_h - input_h - padding
        lignes_max = zone_hist_h // line_h

        hist_visible = self.historique[
            max(0, len(self.historique) - lignes_max - self.scroll_offset)
            : len(self.historique) - self.scroll_offset or None
        ]

        y = padding
        for ligne in hist_visible:
            color = self.TEXT_COLOR
            surf_txt = font.render(ligne, True, color)
            ecran.blit(surf_txt, (padding, y))
            y += line_h

        input_y = term_h - input_h
        pygame.draw.rect(ecran, self.INPUT_BG, (0, input_y, term_w, input_h))

        cursor = "_" if (pygame.time.get_ticks() // 500) % 2 == 0 else " "
        texte_input = font.render("> " + self.input_text + cursor, True, self.PROMPT_COLOR)
        ecran.blit(texte_input, (padding, input_y + padding))

        if self.scroll_offset > 0:
            ind = font.render(f"{self.scroll_offset} ligne(s) remontees", True, (150, 150, 150))
            ecran.blit(ind, (W - ind.get_width() - padding, padding))
