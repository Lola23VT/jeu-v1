import pygame

# Initialisation des polices (nécessaire avant de définir les variables de police)
pygame.init()

WIDTH, HEIGHT = 800, 600
WHITE, BLACK, RED = (255, 255, 255), (0, 0, 0), (255, 0, 0)
GREEN, BLUE, PURPLE = (0, 255, 0), (0, 100, 255), (128, 0, 128)
YELLOW, CYAN, GRAY = (255, 255, 0), (0, 255, 255), (100, 100, 100)
GOLD = (255, 215, 0)

FONT_UI = pygame.font.Font(None, 32)
FONT_BIG = pygame.font.Font(None, 74)
FONT_SMALL = pygame.font.Font(None, 24)