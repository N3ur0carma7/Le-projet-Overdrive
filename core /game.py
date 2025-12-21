import pygame
from screens.jeu import boucle_jeu

class Game:
    def __init__(self):
        pygame.init()

        self.LARGEUR_ECRAN = 1280
        self.HAUTEUR_ECRAN = 720

        self.ecran = pygame.display.set_mode(
            (self.LARGEUR_ECRAN, self.HAUTEUR_ECRAN)
        )
        pygame.display.set_caption("Jeu")

        self.horloge = pygame.time.Clock()
        self.FPS = 60

        self.etat = "jeu"
        self.en_cours = True

    def run(self):
        while self.en_cours:
            if self.etat == "jeu":
                self.en_cours = boucle_jeu(
                    self.ecran,
                    self.horloge,
                    self.FPS
                )

        pygame.quit()
