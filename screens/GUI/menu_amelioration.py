import pygame
import sys
from core.Class.batiments import Batiment
from core.Class.buttons import BoutonImage
import screens.jeu
import core.sounds as sound
import screens.jeu as jeu

def afficher_menu_amelioration(ecran, batiment, clic_x, player):
    en_menu = True
    horloge = pygame.time.Clock()
    police = pygame.font.Font("assets/fonts/Minecraft.ttf", 35)

    largeur_ecran = ecran.get_width()

    #placement du menu
    menu_x = -50
    menu_y = 270
    offset_block = 40 #tkt c'est pour la science

    # chargement image menu
    image_fond = pygame.image.load("assets/buttons/upgrade_menu_interface.png").convert_alpha()
    image_fond = pygame.transform.scale_by(image_fond, 1 )

#tous les différents boutons
    btn_fermer = BoutonImage(
        menu_x + 400 + offset_block, menu_y +32+ offset_block , 90, 90,
        "assets/buttons/close_button.png", "assets/buttons/close_button.png",
        ""
    )
    btn_sell = BoutonImage(
        menu_x + 270+ offset_block, menu_y + 180+ offset_block, 180, 85,
        "assets/buttons/sell_button.png", "assets/buttons/sell_button.png",
        ""
    )
    if  batiment.est_max_level() or player.money <= batiment.get_upgrade_cost():
        btn_ameliorer = BoutonImage(menu_x + 70+ offset_block, menu_y + 180+ offset_block, 200, 85,
                                    "assets/buttons/upgrade_impossible_button.png",
                                    "assets/buttons/upgrade_impossible_button.png",
                                    f"")
    else:
        btn_ameliorer = BoutonImage(
            menu_x + 70+ offset_block, menu_y + 180+ offset_block, 210, 85,
            "assets/buttons/upgrade_available_button.png", "assets/buttons/upgrade_available_button.png",
            f""
        )

    while en_menu:
        ecran.blit(image_fond, (menu_x, menu_y))

        # Textes d'information
        police_stat = pygame.font.Font("assets/fonts/Minecraft.ttf", 25)

        val_suivante = "MAX"
        unite = "/min"

        if batiment.type == Batiment.TYPE_RESIDENTIEL:
            info = "Population"
            val_actuelle = batiment.get_population()
            unite = ""
            if not batiment.est_max_level():
                val_suivante = Batiment.DATA[batiment.type][batiment.niveau + 1]["population"]
        elif batiment.type == Batiment.TYPE_MINE:
            info = "Argent"
            val_actuelle = batiment.get_production()
            if not batiment.est_max_level():
                val_suivante = Batiment.DATA[batiment.type][batiment.niveau + 1]["argent"]
        elif batiment.type == Batiment.TYPE_FARM:
            info = "Nourriture"
            val_actuelle = batiment.get_production()
            if not batiment.est_max_level():
                val_suivante = Batiment.DATA[batiment.type][batiment.niveau + 1]["nourriture"]
        elif batiment.type == Batiment.TYPE_GENERATEUR:
            info = "Vapeur"
            val_actuelle = batiment.get_production()
            if not batiment.est_max_level():
                val_suivante = Batiment.DATA[batiment.type][batiment.niveau + 1]["vapeur"]
        else:
            info = "Production"
            val_actuelle = batiment.get_production()
            if not batiment.est_max_level():
                val_suivante = Batiment.DATA[batiment.type][batiment.niveau + 1].get("production", "?")

        stat_info = police_stat.render(info, True, (0, 0, 0))
        number = police_stat.render(f"{val_actuelle}{unite}", True, (0, 0, 0))

        couleur_next = (0, 0, 0) if not batiment.est_max_level() else (0, 0, 0)
        new_number = police_stat.render(f"{val_suivante}{unite}", True, couleur_next)

        # cout upgrade
        police_cout = pygame.font.Font("assets/fonts/Minecraft.ttf", 22)
        menu_centre_x = menu_x + 612 // 2
        if batiment.est_max_level():
            texte_cout = police_cout.render("Niveau MAX", True, (150, 40, 40))
        else:
            cout_val = batiment.get_upgrade_cost()
            texte_cout = police_cout.render(f"Upgrade : {cout_val} gold", True, (180, 130, 0))
        ecran.blit(texte_cout, (menu_centre_x - texte_cout.get_width() // 2, menu_y + offset_block + 72))

    #affichage c'est TRES TRES sale mais vs inquietez pas c'est temporaire
        ecran.blit(stat_info, (menu_x + 60+ offset_block+ offset_block, menu_y + 70+ offset_block+ offset_block))
        ecran.blit(number, (menu_x + 75+ offset_block+ offset_block, menu_y + 100+ offset_block+ offset_block))
    #valeur du niveau d'après
        ecran.blit(stat_info, (menu_x + 265+ offset_block+ offset_block, menu_y + 70+ offset_block+ offset_block))
        ecran.blit(new_number, (menu_x + 280+ offset_block+ offset_block, menu_y + 100+ offset_block+ offset_block))

        # Clics
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_fermer.clic():
                    en_menu = False

                if btn_ameliorer and btn_ameliorer.clic():
                    if batiment.niveau < 3:
                        if player.money >= batiment.get_upgrade_cost():

                            sound.son_upgrade.play()
                            player.money -= batiment.get_upgrade_cost()
                            batiment.upgrade()
                            return "upgrade"


                    en_menu = False
                if btn_ameliorer and btn_sell.clic():
                    return "supprimer"

        # Affichage boutons
        btn_fermer.afficher(ecran)
        btn_sell.afficher(ecran)
        if btn_ameliorer:
            btn_ameliorer.afficher(ecran)

        pygame.display.flip()
        horloge.tick(60)