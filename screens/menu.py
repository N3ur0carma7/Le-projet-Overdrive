import pygame

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
        Bouton("Jouer", LARGEUR_ECRAN//2 - 100, 200, 200, 50),
        Bouton("Rejoindre", LARGEUR_ECRAN//2 - 100, 300, 200, 50),
        Bouton("Paramètres", LARGEUR_ECRAN//2 - 100, 400, 200, 50),
        Bouton("Quitter", LARGEUR_ECRAN//2 - 100, 500, 200, 50)
    ]

    while en_cours:
        horloge.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return etat_suivant, False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if boutons[0].clic():  # Jouer
                    return "jeu", True
                if boutons[1].clic():  # Rejoindre
                    print("Fonction rejoindre LAN à implémenter")
                if boutons[2].clic():  # Paramètres
                    print("Ouvrir menu paramètres")
                if boutons[3].clic():  # Quitter
                    return etat_suivant, False

        ecran.fill((50, 50, 50))
        for btn in boutons:
            btn.afficher(ecran)

        pygame.display.flip()
