import pygame
import random
import math

# Initialisation
pygame.init()
WIDTH, HEIGHT = 800, 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shape Shooter: Orda's Final Stand")

# Couleurs
WHITE, BLACK, RED = (255, 255, 255), (0, 0, 0), (255, 0, 0)
GREEN, BLUE, PURPLE = (0, 255, 0), (0, 100, 255), (128, 0, 128)
YELLOW, CYAN, GRAY = (255, 255, 0), (0, 255, 255), (100, 100, 100)
GOLD = (255, 215, 0)

font_ui = pygame.font.Font(None, 32)
font_big = pygame.font.Font(None, 74)
font_small = pygame.font.Font(None, 24)

# --- CLASSES ---

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

    def update_position(self, x):
        self.rect.centerx = x
        self.rect.clamp_ip(window.get_rect())
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
        # Vitesse minimum assurée de 2.0 pour éviter les blocages
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

    def update(self, player, b_projs):
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
            if abs(self.rect.centerx - player.rect.centerx) < 30: player_take_damage(player, 0.05)
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
                if self.rect.left < player.rect.centerx < self.rect.right: player_take_damage(player, 0.2)

    def draw(self, surface):
        color = (100, 0, 100) if self.phase < 3 else (255, 0, 0)
        if self.phase == 4: color = (255, 255, 0) if self.timer % 10 < 5 else RED
        pygame.draw.rect(surface, color, self.rect, 0, 12)
        pygame.draw.rect(surface, GRAY, (WIDTH//2 - 150, 20, 300, 15))
        pygame.draw.rect(surface, GREEN if self.phase == 1 else (YELLOW if self.phase == 2 else RED), (WIDTH//2 - 150, 20, (self.hp/self.max_hp)*300, 15))
        if self.phase == 4:
            cycle = self.timer % 180
            if 100 < cycle < 130: pygame.draw.rect(surface, RED, (self.rect.left, self.rect.bottom, self.rect.width, HEIGHT), 1)
            elif cycle >= 130: pygame.draw.rect(surface, YELLOW, (self.rect.left, self.rect.bottom, self.rect.width, HEIGHT))

# --- SYSTEMES ---

def player_take_damage(player, amount):
    if player.shield > 0:
        player.shield -= amount
        if player.shield < 0: player.hp += player.shield; player.shield = 0
    else: player.hp -= amount

def shop_menu(player, points):
    items = [{"name": "Soin (+2 HP)", "cost": 1500, "type": "heal"},
             {"name": "Bouclier", "cost": 3000, "type": "shield"},
             {"name": "Balles Pierçantes", "cost": 5000, "type": "pierce"},
             {"name": "Surcharge (E)", "cost": 4000, "type": "overload"}]
    pygame.time.delay(200); pygame.event.clear()
    while True:
        window.fill((30, 0, 50))
        pts_txt = font_ui.render(f"Points: {int(points)}", True, GOLD)
        window.blit(pts_txt, (WIDTH//2 - pts_txt.get_width()//2, 100))
        btns = []
        for i, it in enumerate(items):
            r = pygame.Rect(WIDTH//2 - 200, 180 + i*75, 400, 60)
            pygame.draw.rect(window, GREEN if points >= it['cost'] else RED, r, 2)
            t = font_ui.render(f"{it['name']} ({it['cost']})", True, WHITE)
            window.blit(t, (r.centerx - t.get_width()//2, r.centery - t.get_height()//2))
            btns.append((r, it))
        ex_r = pygame.Rect(WIDTH//2 - 100, 500, 200, 50); pygame.draw.rect(window, GRAY, ex_r)
        window.blit(font_ui.render("RETOUR", True, WHITE), (ex_r.centerx-45, ex_r.centery-10))
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.MOUSEBUTTONDOWN:
                if ex_r.collidepoint(e.pos): return points
                for r, it in btns:
                    if r.collidepoint(e.pos) and points >= it['cost']:
                        points -= it['cost']
                        if it['type'] == "heal": player.hp = min(player.max_hp, player.hp + 2)
                        if it['type'] == "shield": player.shield += 2
                        if it['type'] == "pierce": player.piercing = True
                        if it['type'] == "overload": player.has_overload_unlocked = True
            if e.type == pygame.QUIT: pygame.quit(); exit()

def start_menu():
    classes = ["Normal", "Rapide", "Tank", "Grenadier"]
    while True:
        window.fill((20, 20, 20))
        btns = []
        for i, c in enumerate(classes):
            r = pygame.Rect(WIDTH//2 - 100, 200 + i*70, 200, 50); pygame.draw.rect(window, WHITE, r, 2)
            txt = font_ui.render(c, True, WHITE); window.blit(txt, (r.centerx - txt.get_width()//2, r.centery - txt.get_height()//2))
            btns.append((r, c))
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.MOUSEBUTTONDOWN:
                for r, c in btns:
                    if r.collidepoint(e.pos): return c
            if e.type == pygame.QUIT: pygame.quit(); exit()

def upgrade_menu(player):
    opts = ["Tourelle", "Cadence", "Tir Diagonal"]
    if not player.has_canon: opts.append("Canon")
    sel = random.sample(opts, 3); pygame.time.delay(150); pygame.event.clear()
    while True:
        window.fill((10, 10, 30))
        btns = []
        for i, o in enumerate(sel):
            r = pygame.Rect(WIDTH//2 - 150, 250 + i*80, 300, 50); pygame.draw.rect(window, BLUE, r)
            txt = font_ui.render(o, True, WHITE); window.blit(txt, (r.centerx - txt.get_width()//2, r.centery - txt.get_height()//2))
            btns.append((r, o))
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.MOUSEBUTTONDOWN:
                for r, o in btns:
                    if r.collidepoint(e.pos):
                        if o == "Tourelle": player.turret_level += 1
                        if o == "Cadence": player.shoot_delay = max(50, player.shoot_delay - 50); player.base_shoot_delay = player.shoot_delay
                        if o == "Tir Diagonal": player.diag_auto_level += 1
                        if o == "Canon": player.has_canon = True
                        return
            if e.type == pygame.QUIT: pygame.quit(); exit()

# --- JEU ---

player = Player(start_menu())
projectiles, enemies, b_projs, damage_texts = [], [], [], []
wave, score, currency_points, running, enemies_left = 1, 0, 0, True, 5
boss, clock = None, pygame.time.Clock()

while running:
    clock.tick(60); now = pygame.time.get_ticks(); window.fill(WHITE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            if player.has_overload_unlocked and not player.overload_active:
                player.overload_active = True; player.overload_timer = 300

    if (pygame.mouse.get_pressed()[0] or pygame.key.get_pressed()[pygame.K_SPACE]) and now - player.last_shot_time > player.shoot_delay:
        is_g = player.player_class == "Grenadier"
        projectiles.append(Projectile(player.rect.centerx, player.rect.top, 0, -12, YELLOW if is_g else BLACK, is_grenade=is_g, piercing=player.piercing))
        player.last_shot_time = now

    player.update_position(pygame.mouse.get_pos()[0])

    # Vagues et Spawn (Correction du blocage)
    if wave % 10 == 0:
        if not boss: boss = Boss(wave); enemies.clear(); enemies_left = 0
        boss.update(player, b_projs)
        if boss.hp <= 0:
            currency_points = shop_menu(player, currency_points)
            boss = None; wave += 1; enemies_left = 5 + wave
    else:
        if enemies_left > 0:
            if random.randint(1, 40) == 1:
                enemies.append(Enemy(wave, random.random() < 0.15))
                enemies_left -= 1
        elif len(enemies) == 0: # Plus d'ennemis à l'écran, on passe à la suite
            wave += 1
            enemies_left = 5 + wave

    # Update Projectiles
    for p in projectiles[:]:
        p.move()
        if p.rect.bottom < 0: projectiles.remove(p)
        elif boss and p.rect.colliderect(boss.rect):
            if p.is_canon: damage_texts.append({"text": "IMMUNE !", "pos": [boss.rect.centerx, boss.rect.top - 10], "life": 40})
            else: currency_points += 10; boss.hp -= (5 if p.is_grenade else 1)
            if not p.is_canon: projectiles.remove(p)

    # Update Ennemis (Correction nettoyage automatique)
    for e in enemies[:]:
        e.move()
        if e.rect.top > HEIGHT: # Sortie de l'écran
            enemies.remove(e)
        elif e.rect.colliderect(player.rect):
            if not e.is_bonus: player_take_damage(player, 1)
            enemies.remove(e)
        else:
            for p in projectiles[:]:
                if p.rect.colliderect(e.rect):
                    if e.is_bonus: enemies.remove(e); currency_points += 100; upgrade_menu(player)
                    else:
                        currency_points += 10; e.hp -= (5 if p.is_grenade else (100 if p.is_canon else 1))
                        if e.hp <= 0:
                            if e in enemies: enemies.remove(e); score += 10; currency_points += 100
                    if p.piercing and not p.is_canon and not p.is_grenade:
                        p.hits += 1
                        if p.hits > 2: projectiles.remove(p)
                    elif not p.is_canon:
                        if p in projectiles: projectiles.remove(p)
                    break

    for bp in b_projs[:]:
        bp.move()
        if bp.rect.colliderect(player.rect): player_take_damage(player, 1); b_projs.remove(bp)
        elif bp.rect.top > HEIGHT: b_projs.remove(bp)

    # Rendu
    player.draw(window)
    if boss: boss.draw(window)
    for x in projectiles + enemies + b_projs: x.draw(window)
    for dt in damage_texts[:]:
        window.blit(font_small.render(dt["text"], True, RED), dt["pos"]); dt["pos"][1] -= 1; dt["life"] -= 1
        if dt["life"] <= 0: damage_texts.remove(dt)
    
    window.blit(font_ui.render(f"SCORE: {score}  POINTS: {int(currency_points)}  MANCHE: {wave}", True, BLACK), (10, 10))
    window.blit(font_ui.render(f"HP: {int(player.hp)}  SHIELD: {int(player.shield)}", True, RED if player.hp < 2 else BLACK), (10, 40))
    
    if player.hp <= 0: running = False
    pygame.display.flip()

pygame.quit()