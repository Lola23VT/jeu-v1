import pygame
import random
from settings import *
from entities import Player, Projectile, Enemy, Boss
from utils import *

# Initialisation
pygame.init()
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shape Shooter: Orda's Final Stand")

def run_game():
    while True:
        player_type = start_menu(window)
        player = Player(player_type)
        projectiles, enemies, b_projs, damage_texts = [], [], [], []
        wave, score, currency_points, enemies_left = 1, 0, 0, 5
        boss, clock = None, pygame.time.Clock()
        game_running = True

        while game_running:
            clock.tick(60)
            now = pygame.time.get_ticks()
            window.fill(WHITE)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                    if player.has_overload_unlocked and not player.overload_active:
                        player.overload_active = True
                        player.overload_timer = 300

            # --- LOGIQUE DE TIR ---
            is_shooting = pygame.mouse.get_pressed()[0] or pygame.key.get_pressed()[pygame.K_SPACE]
            
            if is_shooting and now - player.last_shot_time > player.shoot_delay:
                is_g = player.player_class == "Grenadier"
                projectiles.append(Projectile(player.rect.centerx, player.rect.top, 0, -12, YELLOW if is_g else BLACK, is_grenade=is_g, piercing=player.piercing))
                player.last_shot_time = now

            if is_shooting and player.diag_auto_level > 0:
                if now - player.last_diag_shot > 550:
                    projectiles.append(Projectile(player.rect.left, player.rect.top, -3, -12, CYAN, piercing=player.piercing))
                    projectiles.append(Projectile(player.rect.right, player.rect.top, 3, -12, CYAN, piercing=player.piercing))
                    player.last_diag_shot = now

            if player.has_canon and now - player.last_canon_shot > 2000:
                projectiles.append(Projectile(player.rect.centerx, player.rect.top, 0, -5, RED, is_canon=True))
                player.last_canon_shot = now

            if player.turret_level > 0 and now - player.last_turret_shot > (1000 // player.turret_level):
                projectiles.append(Projectile(player.rect.centerx, player.rect.top, 0, -15, BLUE))
                player.last_turret_shot = now

            player.update_position(pygame.mouse.get_pos()[0], window.get_rect())

            # --- Vagues et Boss ---
            if wave % 10 == 0:
                if not boss: 
                    boss = Boss(wave)
                    enemies.clear()
                    enemies_left = 0
                boss.update(player, b_projs, player_take_damage)
                if boss.hp <= 0:
                    currency_points = shop_menu(window, player, currency_points)
                    boss = None
                    wave += 1
                    enemies_left = 5 + wave
            else:
                if enemies_left > 0:
                    if random.randint(1, 40) == 1:
                        enemies.append(Enemy(wave, random.random() < 0.15))
                        enemies_left -= 1
                elif len(enemies) == 0: 
                    wave += 1
                    enemies_left = 5 + wave

            # --- Update Projectiles ---
            for p in projectiles[:]:
                p.move()
                if p.rect.bottom < 0: projectiles.remove(p)
                elif boss and p.rect.colliderect(boss.rect):
                    if p.is_canon: 
                        damage_texts.append({"text": "IMMUNE !", "pos": [boss.rect.centerx, boss.rect.top - 10], "life": 40})
                    else: 
                        currency_points += 10
                        boss.hp -= (5 if p.is_grenade else 1)
                    if not p.is_canon: projectiles.remove(p)

            # --- Update Ennemis ---
            for e in enemies[:]:
                e.move()
                if e.rect.top > HEIGHT: enemies.remove(e)
                elif e.rect.colliderect(player.rect):
                    if not e.is_bonus: player_take_damage(player, 1)
                    enemies.remove(e)
                else:
                    for p in projectiles[:]:
                        if p.rect.colliderect(e.rect):
                            if e.is_bonus: 
                                enemies.remove(e); currency_points += 100
                                upgrade_menu(window, player)
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

            # --- Rendu ---
            player.draw(window)
            if boss: boss.draw(window)
            for x in projectiles + enemies + b_projs: x.draw(window)
            for dt in damage_texts[:]:
                window.blit(FONT_SMALL.render(dt["text"], True, RED), dt["pos"]); dt["pos"][1] -= 1; dt["life"] -= 1
                if dt["life"] <= 0: damage_texts.remove(dt)
            
            window.blit(FONT_UI.render(f"SCORE: {score}  POINTS: {int(currency_points)}  MANCHE: {wave}", True, BLACK), (10, 10))
            window.blit(FONT_UI.render(f"HP: {int(player.hp)}  SHIELD: {int(player.shield)}", True, RED if player.hp < 2 else BLACK), (10, 40))
            
            if player.hp <= 0: game_running = False
            pygame.display.flip()

        show_leaderboard_screen(window, score)

if __name__ == "__main__":
    run_game()