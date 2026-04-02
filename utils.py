import pygame
import json
import os
import random
from settings import *

def save_score(new_score):
    leaderboard = load_leaderboard()
    leaderboard.append(new_score)
    leaderboard.sort(reverse=True)
    leaderboard = leaderboard[:5]
    with open("leaderboard.json", "w") as f:
        json.dump(leaderboard, f)

def load_leaderboard():
    if not os.path.exists("leaderboard.json"):
        return []
    try:
        with open("leaderboard.json", "r") as f:
            return json.load(f)
    except:
        return []

def player_take_damage(player, amount):
    if player.shield > 0:
        player.shield -= amount
        if player.shield < 0: player.hp += player.shield; player.shield = 0
    else: player.hp -= amount

def shop_menu(window, player, points):
    items = [{"name": "Soin (+2 HP)", "cost": 1500, "type": "heal"},
             {"name": "Bouclier", "cost": 3000, "type": "shield"},
             {"name": "Balles Pierçantes", "cost": 5000, "type": "pierce"},
             {"name": "Surcharge (E)", "cost": 4000, "type": "overload"}]
    pygame.time.delay(200); pygame.event.clear()
    while True:
        window.fill((30, 0, 50))
        pts_txt = FONT_UI.render(f"Points: {int(points)}", True, GOLD)
        window.blit(pts_txt, (WIDTH//2 - pts_txt.get_width()//2, 100))
        btns = []
        for i, it in enumerate(items):
            r = pygame.Rect(WIDTH//2 - 200, 180 + i*75, 400, 60)
            pygame.draw.rect(window, GREEN if points >= it['cost'] else RED, r, 2)
            t = FONT_UI.render(f"{it['name']} ({it['cost']})", True, WHITE)
            window.blit(t, (r.centerx - t.get_width()//2, r.centery - t.get_height()//2))
            btns.append((r, it))
        ex_r = pygame.Rect(WIDTH//2 - 100, 500, 200, 50); pygame.draw.rect(window, GRAY, ex_r)
        window.blit(FONT_UI.render("RETOUR", True, WHITE), (ex_r.centerx-45, ex_r.centery-10))
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

def start_menu(window):
    classes = ["Normal", "Rapide", "Tank", "Grenadier"]
    while True:
        window.fill((20, 20, 20))
        title = FONT_BIG.render("SHAPE SHOOTER", True, WHITE)
        window.blit(title, (WIDTH//2 - title.get_width()//2, 80))
        btns = []
        for i, c in enumerate(classes):
            r = pygame.Rect(WIDTH//2 - 100, 220 + i*70, 200, 50); pygame.draw.rect(window, WHITE, r, 2)
            txt = FONT_UI.render(c, True, WHITE); window.blit(txt, (r.centerx - txt.get_width()//2, r.centery - txt.get_height()//2))
            btns.append((r, c))
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.MOUSEBUTTONDOWN:
                for r, c in btns:
                    if r.collidepoint(e.pos): return c
            if e.type == pygame.QUIT: pygame.quit(); exit()

def upgrade_menu(window, player):
    opts = ["Tourelle", "Cadence", "Tir Diagonal"]
    if not player.has_canon: opts.append("Canon")
    sel = random.sample(opts, min(len(opts), 3)); pygame.time.delay(150); pygame.event.clear()
    while True:
        window.fill((10, 10, 30))
        btns = []
        for i, o in enumerate(sel):
            r = pygame.Rect(WIDTH//2 - 150, 250 + i*80, 300, 50); pygame.draw.rect(window, BLUE, r)
            txt = FONT_UI.render(o, True, WHITE); window.blit(txt, (r.centerx - txt.get_width()//2, r.centery - txt.get_height()//2))
            btns.append((r, o))
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.MOUSEBUTTONDOWN:
                for r, o in btns:
                    if r.collidepoint(e.pos):
                        if o == "Tourelle": player.turret_level += 1
                        if o == "Cadence": 
                            player.base_shoot_delay = max(50, player.base_shoot_delay - 50)
                            player.shoot_delay = player.base_shoot_delay
                        if o == "Tir Diagonal": player.diag_auto_level += 1
                        if o == "Canon": player.has_canon = True
                        return
            if e.type == pygame.QUIT: pygame.quit(); exit()

def show_leaderboard_screen(window, current_score):
    save_score(current_score)
    scores = load_leaderboard()
    while True:
        window.fill((15, 15, 15))
        title = FONT_BIG.render("GAME OVER", True, RED)
        window.blit(title, (WIDTH//2 - title.get_width()//2, 80))
        score_now = FONT_UI.render(f"Ton Score: {current_score}", True, GOLD)
        window.blit(score_now, (WIDTH//2 - score_now.get_width()//2, 160))
        window.blit(FONT_UI.render("--- TOP 5 ---", True, WHITE), (WIDTH//2 - 70, 230))
        for i, s in enumerate(scores):
            txt = FONT_UI.render(f"{i+1}. {s} pts", True, CYAN)
            window.blit(txt, (WIDTH//2 - 60, 270 + i*40))
        prompt = FONT_SMALL.render("Appuyez sur ENTRÉE pour rejouer ou ESC pour quitter", True, GRAY)
        window.blit(prompt, (WIDTH//2 - prompt.get_width()//2, HEIGHT - 80))
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN: return
                if e.key == pygame.K_ESCAPE: pygame.quit(); exit()