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


import pygame


class BoutonImage:
    # On ajoute largeur et hauteur dans les paramètres
    def __init__(self, x, y, largeur, hauteur, chemin_image_base, chemin_image_hover, texte=""):

        # 1. Chargement brut des images
        img_base_brute = pygame.image.load(chemin_image_base).convert_alpha()
        img_hover_brute = pygame.image.load(chemin_image_hover).convert_alpha()

        # 2. Redimensionnement à la taille voulue
        # Note : On utilise .scale() pour le pixel art pour garder les pixels nets.
        # Si vos images ne sont pas en pixel art, utilisez pygame.transform.smoothscale()
        self.image_base = pygame.transform.scale(img_base_brute, (largeur, hauteur))
        self.image_hover = pygame.transform.scale(img_hover_brute, (largeur, hauteur))

        # 3. Récupération de la nouvelle zone de collision (hitbox)
        self.rect = self.image_base.get_rect()
        self.rect.topleft = (x, y)

        self.texte = texte
        self.police = pygame.font.SysFont(None, 40)

    def afficher(self, ecran):
        souris = pygame.mouse.get_pos()

        if self.rect.collidepoint(souris):
            image_actuelle = self.image_hover
        else:
            image_actuelle = self.image_base

        ecran.blit(image_actuelle, self.rect.topleft)

        if self.texte != "":
            # On dessine le texte par-dessus
            txt_surface = self.police.render(self.texte, True, (255, 255, 255))
            txt_rect = txt_surface.get_rect(center=self.rect.center)
            ecran.blit(txt_surface, txt_rect)

    def clic(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())