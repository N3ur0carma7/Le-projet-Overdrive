import pygame
import sys
from core.Class.batiments import Batiment
from core.Class.buttons import BoutonImage
import core.sounds as sound


class MenuAmelioration:
    def __init__(self, ecran, batiment, clic_x, player):
        self.ecran = ecran
        self.batiment = batiment
        self.player = player
        self.clic_x = clic_x
        self.menu_x = -50
        self.menu_y = 270
        self.offset_block = 40
        self.police_stat = pygame.font.Font("assets/fonts/Minecraft.ttf", 25)
        self.police_cout = pygame.font.Font("assets/fonts/Minecraft.ttf", 22)
        self.image_fond = pygame.image.load("assets/buttons/upgrade_menu_interface.png").convert_alpha()
        self.image_fond = pygame.transform.scale_by(self.image_fond, 1)
        self._build_buttons()

    def _build_buttons(self):
        self.btn_fermer = BoutonImage(
            self.menu_x + 400 + self.offset_block,
            self.menu_y + 32 + self.offset_block,
            90,
            90,
            "assets/buttons/close_button.png",
            "assets/buttons/close_button.png",
            ""
        )
        self.btn_sell = BoutonImage(
            self.menu_x + 270 + self.offset_block,
            self.menu_y + 180 + self.offset_block,
            180,
            85,
            "assets/buttons/sell_button.png",
            "assets/buttons/sell_button.png",
            ""
        )
        upgrade_cost = self.batiment.get_upgrade_cost()
        max_debloque = Batiment.DATA[self.batiment.type].get("max_level", 1)

        if (
                self.batiment.niveau >= max_debloque) or self.batiment.est_max_level() or upgrade_cost is None or self.player.money <= upgrade_cost:
            self.btn_ameliorer = BoutonImage(
                self.menu_x + 70 + self.offset_block,
                self.menu_y + 180 + self.offset_block,
                200,
                85,
                "assets/buttons/upgrade_impossible_button.png",
                "assets/buttons/upgrade_impossible_button.png",
                ""
            )
        else:
            self.btn_ameliorer = BoutonImage(
                self.menu_x + 70 + self.offset_block,
                self.menu_y + 180 + self.offset_block,
                210,
                85,
                "assets/buttons/upgrade_available_button.png",
                "assets/buttons/upgrade_available_button.png",
                ""
            )

    def _build_texts(self):
        val_suivante = "MAX"
        unite = "/min"

        if self.batiment.type == Batiment.TYPE_RESIDENTIEL:
            info = "Population"
            val_actuelle = self.batiment.get_population()
            unite = ""
            if not self.batiment.est_max_level():
                val_suivante = Batiment.DATA[self.batiment.type][self.batiment.niveau + 1]["population"]
        elif self.batiment.type == Batiment.TYPE_MINE:
            info = "Argent"
            val_actuelle = self.batiment.get_production()
            if not self.batiment.est_max_level():
                val_suivante = Batiment.DATA[self.batiment.type][self.batiment.niveau + 1]["argent"]
        elif self.batiment.type == Batiment.TYPE_FARM:
            info = "Nourriture"
            val_actuelle = self.batiment.get_production()
            if not self.batiment.est_max_level():
                val_suivante = Batiment.DATA[self.batiment.type][self.batiment.niveau + 1]["nourriture"]
        elif self.batiment.type == Batiment.TYPE_GENERATEUR:
            info = "Vapeur"
            val_actuelle = self.batiment.get_production()
            if not self.batiment.est_max_level():
                val_suivante = Batiment.DATA[self.batiment.type][self.batiment.niveau + 1]["vapeur"]
        elif self.batiment.type == Batiment.TYPE_TOURELLE:
            info = "Degat"
            val_actuelle = self.batiment.get_stats().get("degat", 30)
            unite = ""
            if not self.batiment.est_max_level():
                val_suivante = Batiment.DATA[self.batiment.type][self.batiment.niveau + 1]["degat"]
        else:
            info = "Production"
            val_actuelle = self.batiment.get_production()
            if not self.batiment.est_max_level():
                val_suivante = Batiment.DATA[self.batiment.type][self.batiment.niveau + 1].get("production", "?")

        stat_info = self.police_stat.render(info, True, (0, 0, 0))
        number = self.police_stat.render(f"{val_actuelle}{unite}", True, (0, 0, 0))

        couleur_next = (0, 0, 0)
        new_number = self.police_stat.render(f"{val_suivante}{unite}", True, couleur_next)

        max_debloque = Batiment.DATA[self.batiment.type].get("max_level", 1)
        existe_niveau_suivant = (self.batiment.niveau + 1) in Batiment.DATA[self.batiment.type]

        if self.batiment.niveau >= 3 or not existe_niveau_suivant:
            texte_cout = self.police_cout.render("Niveau MAX", True, (150, 40, 40))
        elif self.batiment.niveau >= max_debloque:
            texte_cout = self.police_cout.render("Amelioration non debloquee", True, (150, 40, 40))
        else:
            cout_val = self.batiment.get_upgrade_cost()
            texte_cout = self.police_cout.render(f"Upgrade : {cout_val} gold", True, (180, 130, 0))

        return stat_info, number, new_number, texte_cout

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
            from screens import game_logic
            game_logic.toggle_fullscreen()
            return None

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "close"

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._build_buttons()
            if self.btn_fermer.clic():
                return "close"

            if self.btn_ameliorer and self.btn_ameliorer.clic():
                upgrade_cost = self.batiment.get_upgrade_cost()
                max_debloque = Batiment.DATA[self.batiment.type].get("max_level", 1)

                if self.batiment.niveau < max_debloque and upgrade_cost is not None and self.player.money >= upgrade_cost:
                    sound.son_upgrade.play()
                    self.player.money -= upgrade_cost
                    self.batiment.upgrade()
                    return "upgrade"
                return "close"

            if self.btn_sell.clic():
                return "supprimer"

        return None

    def draw(self, ecran):
        self._build_buttons()
        stat_info, number, new_number, texte_cout = self._build_texts()

        ecran.blit(self.image_fond, (self.menu_x, self.menu_y))

        menu_centre_x = self.menu_x + 612 // 2
        ecran.blit(texte_cout, (menu_centre_x - texte_cout.get_width() // 2,
                                 self.menu_y + self.offset_block + 72))

        ecran.blit(stat_info, (self.menu_x + 60 + self.offset_block + self.offset_block,
                                self.menu_y + 70 + self.offset_block + self.offset_block))
        ecran.blit(number, (self.menu_x + 75 + self.offset_block + self.offset_block,
                             self.menu_y + 100 + self.offset_block + self.offset_block))
        ecran.blit(stat_info, (self.menu_x + 265 + self.offset_block + self.offset_block,
                                self.menu_y + 70 + self.offset_block + self.offset_block))
        ecran.blit(new_number, (self.menu_x + 280 + self.offset_block + self.offset_block,
                                 self.menu_y + 100 + self.offset_block + self.offset_block))

        self.btn_fermer.afficher(ecran)
        self.btn_sell.afficher(ecran)
        if self.btn_ameliorer:
            self.btn_ameliorer.afficher(ecran)
