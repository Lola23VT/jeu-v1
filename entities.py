import pygame
import random
import math
from settings import *

class Player:
    def __init__(self, player_class):
        self.rect = pygame.Rect(WIDTH // 2, HEIGHT - 60, 40, 40)
        self.player_class = player_class
        self.max_hp = 6 if player_class == "Tank" else 3
        self.hp = self.max_hp
        self.base_shoot_delay = 333
        if player_class == "Rapide": self.base_shoot_delay = 180
        if player_class == "Tank": self.base_shoot_delay = 500
        if player_class == "Grenadier": self.base_shoot_delay = 650
        self.shoot_delay = self.base_shoot_delay
        
        self.shield = 0
        self.piercing = False
        self.overload_active = False
        self.overload_timer = 0
        self.has_overload_unlocked = False
        
        self.last_shot_time = 0
        self.turret_level = 0
        self.last_turret_shot = 0
        self.diag_auto_level = 0
        self.last_diag_shot = 0
        self.has_canon = False
        self.last_canon_shot = 0

    def update_position(self, x, window_rect):
        self.rect.centerx = x
        self.rect.clamp_ip(window_rect)
        if self.overload_active:
            self.shoot_delay = self.base_shoot_delay // 2
            self.overload_timer -= 1
            if self.overload_timer <= 0:
                self.overload_active = False
                self.shoot_delay = self.base_shoot_delay

    def draw(self, surface):
        colors = {"Normal": BLACK, "Rapide": BLUE, "Tank": GRAY, "Grenadier": (139, 69, 19)}
        pygame.draw.rect(surface, colors.get(self.player_class, BLACK), self.rect)
        if self.shield > 0:
            pygame.draw.rect(surface, CYAN, self.rect, 3)

class Projectile:
    def __init__(self, x, y, dx=0, dy=-12, color=BLACK, is_canon=False, is_grenade=False, piercing=False):
        self.is_canon = is_canon
        self.is_grenade = is_grenade
        self.piercing = piercing
        self.hits = 0
        w, h = (20, 40) if is_canon else (6, 12)
        if is_grenade: w, h = 18, 18
        self.rect = pygame.Rect(x - w//2, y, w, h)
        self.dx, self.dy = dx, dy
        self.color = color
        
    def move(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        
    def draw(self, surface):
        if self.is_grenade: pygame.draw.circle(surface, self.color, self.rect.center, 9)
        else: pygame.draw.rect(surface, self.color, self.rect)

class Enemy:
    def __init__(self, wave, is_bonus=False):
        self.is_bonus = is_bonus
        self.rect = pygame.Rect(random.randint(0, WIDTH-40), -50, 40, 40)
        self.hp = 1 if is_bonus else 1 + (wave // 4)
        self.speed = 1.5 if is_bonus else max(2.0, random.uniform(2, 3) + (wave * 0.05))
        self.color = GREEN if is_bonus else (RED if self.hp <= 1 else (150, 0, 0))
    def move(self): self.rect.y += self.speed
    def draw(self, surface): pygame.draw.rect(surface, self.color, self.rect)

class Boss:
    def __init__(self, wave):
        self.rect = pygame.Rect(WIDTH//2 - 60, -150, 120, 120)
        self.max_hp = 150 + (wave * 25) 
        self.hp = self.max_hp
        self.phase = 1
        self.timer = 0
        self.move_dir = 1
        self.has_revived = False

    def update(self, player, b_projs, player_damage_func):
        self.timer += 1
        if self.rect.y < 70: self.rect.y += 2
        
        if self.hp <= 1 and not self.has_revived:
            self.hp = self.max_hp // 2
            self.has_revived = True
            self.phase = 4
            self.timer = 0
            
        if not self.has_revived:
            hr = self.hp / self.max_hp
            if hr > 0.7: self.phase = 1
            elif hr > 0.3: self.phase = 2
            else: self.phase = 3

        if self.phase == 1 and self.timer % 150 > 100:
            if abs(self.rect.centerx - player.rect.centerx) < 30: player_damage_func(player, 0.05)
        elif self.phase == 2:
            self.rect.x += 4 * self.move_dir
            if self.rect.right > WIDTH or self.rect.left < 0: self.move_dir *= -1
            if self.timer % 30 == 0: b_projs.append(Projectile(self.rect.centerx, self.rect.bottom, random.randint(-3, 3), 5, RED))
        elif self.phase == 3 and self.timer % 15 == 0:
            angle = math.sin(self.timer * 0.2) * 5
            b_projs.append(Projectile(self.rect.centerx, self.rect.bottom, angle, 7, PURPLE))
        elif self.phase == 4:
            cycle = self.timer % 180
            if cycle < 100:
                self.rect.x += 12 * self.move_dir
                if self.rect.right > WIDTH or self.rect.left < 0: self.move_dir *= -1
            elif cycle >= 130:
                if self.rect.left < player.rect.centerx < self.rect.right: player_damage_func(player, 0.2)

    def draw(self, surface):
        color = (100, 0, 100) if self.phase < 3 else (255, 0, 0)
        if self.phase == 4: color = (255, 255, 0) if self.timer % 10 < 5 else RED
        pygame.draw.rect(surface, color, self.rect, 0, 12)
        pygame.draw.rect(surface, GRAY, (WIDTH//2 - 150, 20, 300, 15))
        pygame.draw.rect(surface, GREEN if self.phase == 1 else (YELLOW if self.phase == 2 else RED), (WIDTH//2 - 150, 20, max(0, (self.hp/self.max_hp)*300), 15))
        
        if self.phase == 4:
            cycle = self.timer % 180
            if 100 < cycle < 130:
                pygame.draw.rect(surface, RED, (self.rect.left, self.rect.bottom, self.rect.width, HEIGHT), 2)
            elif cycle >= 130:
                pygame.draw.rect(surface, YELLOW, (self.rect.left, self.rect.bottom, self.rect.width, HEIGHT))