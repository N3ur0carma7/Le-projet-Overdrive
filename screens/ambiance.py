import pygame
import random
import math


class Leaf:
    def __init__(self, w, h):
        self.reset(w, h)

    def reset(self, map_min, map_max):
        self.x = random.randint(map_min, map_max)
        self.y = random.randint(map_min, map_max)

        self.speed_x = random.uniform(40, 90)
        self.amplitude = random.uniform(8, 25)
        self.freq = random.uniform(1.0, 3.0)

        self.size = random.randint(20, 38)

        self.angle = random.uniform(0, 360)
        self.rot_speed = random.uniform(-90, 90)

        self.time = random.uniform(0, 10)

    def update(self, dt, map_min, map_max):
        self.time += dt

        self.x += self.speed_x * dt
        self.y += math.sin(self.time * self.freq) * 20 * dt

        self.angle += self.rot_speed * dt

        if self.x > map_max:
            self.reset(map_min, map_max)
            self.x = map_min

    def draw(self, surface, camera_x, camera_y, leaf_img):
        leaf = pygame.transform.smoothscale(
            leaf_img,
            (self.size, self.size)
        )

        leaf = pygame.transform.rotate(leaf, self.angle)

        surface.blit(leaf, (self.x - camera_x, self.y - camera_y))


class AmbianceManager:
    def __init__(self):
        self.map_min = -8000
        self.map_max = 8000
        self.leaf_img = pygame.image.load("assets/environment/leaf.png").convert_alpha()
        self.leaves = [
            Leaf(self.map_min, self.map_max)
            for _ in range(280)
        ]

        self.wind_particles = [
            WindParticle(self.map_min, self.map_max)
            for _ in range(280)
        ]

    def update(self, dt, camera_x=0, camera_y=0, view_w=1920, view_h=1080):
        for leaf in self.leaves:
            leaf.update(dt, self.map_min, self.map_max)
        for wind in self.wind_particles:
            wind.update(dt, self.map_min, self.map_max)

    def draw(self, surface, camera_x, camera_y):
        for wind in self.wind_particles:
            wind.draw(surface, camera_x, camera_y)
        for leaf in self.leaves:
            leaf.draw(surface, camera_x, camera_y, self.leaf_img)

class WindParticle:
    def __init__(self, map_min, map_max):
        self.reset(map_min, map_max)

    def reset(self, map_min, map_max):
        self.x = random.randint(map_min, map_max)
        self.y = random.randint(map_min, map_max)

        self.length = random.randint(30, 90)
        self.speed_x = random.uniform(120, 240)
        self.speed_y = random.uniform(-10, 10)

        self.alpha = random.randint(35, 80)
        self.life = random.uniform(2.0, 4.0)
        self.max_life = self.life

    def update(self, dt, map_min, map_max):
        self.x += self.speed_x * dt
        self.y += self.speed_y * dt
        self.life -= dt

        if self.life <= 0 or self.x > map_max:
            self.reset(map_min, map_max)

    def draw(self, surface, camera_x, camera_y):
        fade = max(0, self.life / self.max_life)
        alpha = int(self.alpha * fade)

        start = (self.x - camera_x, self.y - camera_y)
        end = (self.x - camera_x + self.length, self.y - camera_y - 5)

        pygame.draw.line(surface, (235, 220, 180, alpha), start, end, 2)