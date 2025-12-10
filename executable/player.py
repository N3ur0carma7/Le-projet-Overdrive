class Player:
    def __init__(self):
        self.hp_max = 100 # Vie max du joueur
        self.hp = 100 # Vie actuelle du joueur
        self.crit_chance = 20 # chance d'effectuer un coup critique (MAX: 100)
        self.crit_damage = 10 # pourcentage de dégats supplémentaire si le joueur fait un coup critique (ex : 10 crit damage = 10% de dégats en plus des dégats de base)
        self.raw_damage = 1 # dégats de base pouvant être augmentés avec : des armures, des armes, des niveaux.
        self.defense = 0 # utilisation dans la formule des dégâts subis
        self.health_regen = 1 # +x hp par seconde
    def damagePlayer(self, damage: int) -> float:
        pass
