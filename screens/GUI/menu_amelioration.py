import pygame
import sys
from core.Class.batiments import Batiment
from core.Class.buttons import BoutonImage


def afficher_menu_amelioration(ecran, batiment, clic_x):
    en_menu = True
    horloge = pygame.time.Clock()
    police = pygame.font.SysFont(None, 40)

    largeur_ecran = ecran.get_width()

    if clic_x < largeur_ecran / 2:
        menu_x = largeur_ecran - 450
    else:
        menu_x = 50
    menu_y = 50


    # chargement image menu
    image_fond = pygame.image.load("assets/buttons/upgrade_menu.png").convert_alpha()
    image_fond = pygame.transform.smoothscale(image_fond, (400, 250))


    btn_fermer = BoutonImage(
        menu_x + 100, menu_y + 200, 200, 75,
        "assets/buttons/close_button.png", "assets/buttons/close_button.png",
        ""
    )

    btn_ameliorer = None
    if not batiment.est_max_level():
        cout = batiment.get_upgrade_cost()
        btn_ameliorer = BoutonImage(
            menu_x + 100, menu_y-12 ,200, 85,
            "assets/buttons/upgrade_available_button.png", "assets/buttons/upgrade_available_button.png",
            f""
        )

    while en_menu:
        ecran.blit(image_fond, (menu_x, menu_y))

        # Textes d'information
        titre = police.render(f"Bâtiment : {batiment.type.capitalize()}", True, (255, 215, 0))
        niveau = police.render(f"Niveau : {batiment.niveau} / 3", True, (255, 255, 255))

        if batiment.type == Batiment.TYPE_RESIDENTIEL:
            stat = police.render(f"Population : {batiment.get_population()}", True, (150, 255, 150))
        else:
            stat = police.render(f"Production : {batiment.get_production()}", True, (150, 255, 150))

        ecran.blit(titre, (menu_x + 50, menu_y + 50))
        ecran.blit(niveau, (menu_x + 50, menu_y + 110))
        ecran.blit(stat, (menu_x + 50, menu_y + 170))

        # Clics
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_fermer.clic():
                    en_menu = False

                if btn_ameliorer and btn_ameliorer.clic():
                    batiment.upgrade()
                    print(f"{batiment.type} amélioré au niveau {batiment.niveau} !")
                    en_menu = False

        # Affichage boutons
        btn_fermer.afficher(ecran)
        if btn_ameliorer:
            btn_ameliorer.afficher(ecran)

        pygame.display.flip()
        horloge.tick(60)