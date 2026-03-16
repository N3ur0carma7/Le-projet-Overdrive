import pygame
import json
import os

class Bouton:
    def __init__(self, texte, x, y, largeur, hauteur):
        self.rect = pygame.Rect(x, y, largeur, hauteur)
        self.texte = texte
        self.couleur_base = (100, 100, 100)
        self.couleur_hover = (200, 200, 80)
        self.police = pygame.font.SysFont(None, 40)

    def afficher(self, ecran):
        souris = pygame.mouse.get_pos()
        if self.rect.collidepoint(souris):
            couleur = self.couleur_hover
        else:
            couleur = self.couleur_base
        pygame.draw.rect(ecran, couleur, self.rect)
        txt_surface = self.police.render(self.texte, True, (0, 0, 0))
        txt_rect = txt_surface.get_rect(center=self.rect.center)
        ecran.blit(txt_surface, txt_rect)

    def clic(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

def menu_principal(ecran, horloge, FPS):
    LARGEUR_ECRAN, HAUTEUR_ECRAN = ecran.get_size()
    en_cours = True
    etat_suivant = "menu"

    # créer les boutons
    boutons = [
        Bouton("Commencer", LARGEUR_ECRAN//2 - 100, 200, 200, 50),
        Bouton("Continuer", LARGEUR_ECRAN // 2 - 100, 300, 200, 50),
        Bouton("Rejoindre", LARGEUR_ECRAN//2 - 100, 400, 200, 50),
        Bouton("Paramètres", LARGEUR_ECRAN//2 - 100, 500, 200, 50),
        Bouton("Quitter", LARGEUR_ECRAN//2 - 100, 600, 200, 50)
    ]

    while en_cours:
        horloge.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return etat_suivant, False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if boutons[0].clic():  # Jouer
                    if os.path.exists("save/save.json"): # Check si une sauvegarde existe déjà
                        from screens.ecraserSauvegarde import confirmation_ecraser
                        etat_confirmation = confirmation_ecraser(ecran, horloge, FPS)
                        if etat_confirmation is False:
                            return etat_suivant, False
                        elif etat_confirmation == "menu":
                            return etat_confirmation, True
                        elif etat_confirmation == "jeu":
                            return etat_confirmation, True
                    else:
                        return "jeu", True
                if boutons[1].clic():
                    if os.path.exists("save/save.json"):
                        return "jeu", True
                if boutons[2].clic():  # Rejoindre
                    print("Fonction rejoindre LAN à implémenter")
                if boutons[3].clic():  # Paramètres
                    print("Ouvrir menu paramètres")
                if boutons[4].clic():  # Quitter
                    return etat_suivant, False

        ecran.fill((50, 50, 50))
        for btn in boutons:
            btn.afficher(ecran)

        font = pygame.font.SysFont("Arial", 100)
        text_surface = font.render("Overdrive", True,
                                   (255, 255, 255))
        ecran.blit(text_surface, (LARGEUR_ECRAN // 2 - 225, 70))

        pygame.display.flip()
