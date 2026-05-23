import pygame

pygame.mixer.init()


son_placement = pygame.mixer.Sound("assets/sounds/FX/placing_building_1.wav")
son_placement.set_volume(0.5)

son_upgrade = pygame.mixer.Sound("assets/sounds/FX/upgrade_building_1.wav")
son_upgrade.set_volume(0.5)

ambient_musics = [
    "assets/sounds/ambient/ambient1.mp3",
    "assets/sounds/ambient/ambient2.mp3",
    "assets/sounds/ambient/ambient3.mp3",
    "assets/sounds/ambient/ambient4.mp3",
    "assets/sounds/ambient/ambient5.mp3",
    "assets/sounds/ambient/ambient6.mp3",
    "assets/sounds/ambient/ambient7.mp3",
    "assets/sounds/ambient/ambient8.mp3",
    "assets/sounds/ambient/ambient9.mp3",
    "assets/sounds/ambient/ambient10.mp3",
    "assets/sounds/ambient/ambient11.mp3"
]

music_enabled = True

def is_music_enabled():
    return music_enabled


def set_music_enabled(enabled):
    global music_enabled
    music_enabled = enabled
    if not enabled:
        pygame.mixer.music.stop()


def play_ambient(index=0, loop=-1):
    if not music_enabled:
        return
    if 0 <= index < len(ambient_musics):
        pygame.mixer.music.load(ambient_musics[index])
        pygame.mixer.music.set_volume(0.1)
        pygame.mixer.music.play(loop)

def stop_ambient():
    pygame.mixer.music.stop()

