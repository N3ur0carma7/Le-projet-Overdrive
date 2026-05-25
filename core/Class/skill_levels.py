

MAX_LEVELS = {
    "residentiel": 1,
    "generateur":  1,
    "mine":        1,
    "farm":       1,
    "tourelle":     1,
    "centrale_argent": 1,
    "centrale_vapeur": 1,
    "centrale_nourriture": 1,
}

def get_max_level(building_type):
    return MAX_LEVELS.get(building_type, 1)

def set_max_level(building_type, level):
    MAX_LEVELS[building_type] = level