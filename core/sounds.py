import pygame

pygame.mixer.init()


son_placement = pygame.mixer.Sound("assets/sounds/FX/placing_building_1.wav")
son_placement.set_volume(1.6)

son_upgrade = pygame.mixer.Sound("assets/sounds/FX/upgrade_building_1.wav")
son_upgrade.set_volume(0.5)

ambient_musics = [
    "assets/sounds/ambient/game_ambient.mp3",
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

