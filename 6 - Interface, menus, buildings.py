import pygame as pg
import numpy as np
from enum import Enum

# 1. STATE MACHINE: Replaces the 'running, pause, options' flags
class GameState(Enum):
    SPLASH = 0
    MENU = 1
    PLAYING = 2
    OPTIONS = 3
    GAMEOVER = 4

# 2. DICTIONARY: Replaces dozens of individual surface variables
class AssetManager:
    def __init__(self):
        self.textures = {}
        self.sounds = {}

    def load_ui(self):
        # Using a dict to map state to an image
        self.textures['menu_bg'] = pg.image.load('Assets/Textures/menu.png').convert_alpha()
        self.textures['hearts'] = pg.image.load('Assets/Textures/hearts.png').convert_alpha()

def main():
    pg.init()
    screen = pg.display.set_mode((800, 600))
    state = GameState.SPLASH
    assets = AssetManager()
    assets.load_ui()
    
    # Resolution/Buffer Data
    hres, halfvres = 250, 93 # 250 * 0.375
    
    running = True
    while running:
        mouse_pos = pg.mouse.get_pos()
        click = False

        for event in pg.event.get():
            if event.type == pg.QUIT: running = False
            if event.type == pg.MOUSEBUTTONDOWN: click = True
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                state = GameState.MENU

        # State Dispatcher (The "Switch")
        if state == GameState.SPLASH:
            draw_splash(screen)
            if click: state = GameState.MENU

        elif state == GameState.MENU:
            state = handle_menu(screen, mouse_pos, click, assets)

        elif state == GameState.PLAYING:
            # Here you would call the raycasting loop from previous scripts
            screen.fill((0, 0, 0))
            draw_hud(screen, assets)

        pg.display.flip()

def handle_menu(screen, mouse, click, assets):
    screen.blit(assets.textures['menu_bg'], (0, 0))
    # 3. LIST/RECTS: Checking button collisions efficiently
    play_button = pg.Rect(0, 200, 500, 65)
    
    if play_button.collidepoint(mouse):
        pg.draw.rect(screen, (150, 250, 150), play_button, 2)
        if click: return GameState.PLAYING
    
    return GameState.MENU

def draw_splash(screen):
    screen.fill((50, 50, 50))
    # Placeholder for splash logic

def draw_hud(screen, assets):
    # Example: Drawing the health bar from the dictionary
    screen.blit(assets.textures['hearts'], (20, 20))

if __name__ == '__main__':
    main()
    pg.quit()