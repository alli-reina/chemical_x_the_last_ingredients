import pygame as pg
import numpy as np
from collections import deque
from numba import njit

# DECISION TREE: Simplified AI Logic
class EnemyAI:
    @staticmethod
    def decide(dist, health, friends):
        if health < 2 and friends < 1: return "RETREAT"
        if dist < 0.6: return "ATTACK"
        if dist < 5: return "CHASE"
        return "WANDER"

# QUEUE: Sound Manager (Prevents sound crashing/lag)
class SoundBuffer:
    def __init__(self):
        self.queue = deque()
    def add(self, sound): self.queue.append(sound)
    def play_next(self):
        if self.queue: self.queue.popleft().play()

def main():
    pg.init()
    pg.mixer.init()
    screen = pg.display.set_mode((800, 600))
    clock = pg.time.Clock()
    
    # Setup Data Structures
    sounds = SoundBuffer()
    # ARRAY: Enemy Data (x, y, dist, type, health, state)
    enemies = np.random.rand(10, 6) 
    enemies[:, 4] = 5 # Set Health to 5
    
    # Asset Placeholders (Replace with your load_sounds logic)
    battle_music = pg.Surface((0,0)) # Placeholder
    swoosh_snd = pg.mixer.Sound(pg.buffer_info_custom_placeholder) # Needs real file

    running = True
    player_hp = 10
    
    while running:
        dt = clock.tick(60) / 1000
        sounds.play_next() # Process one sound per frame

        for event in pg.event.get():
            if event.type == pg.QUIT: running = False
            if event.type == pg.MOUSEBUTTONDOWN:
                sounds.add(swoosh_snd)
                # Simple Combat Check
                for en in enemies:
                    if en[2] < 1.0: # If enemy dist < 1.0
                        en[4] -= 2 # Damage health
        
        # AI Decision Tree usage
        for en in enemies:
            dist = np.linalg.norm(en[:2] - [5, 5]) # Dist to player (placeholder 5,5)
            en[2] = dist
            state = EnemyAI.decide(dist, en[4], 0)
            
            if state == "ATTACK": player_hp -= 0.01
            elif state == "RETREAT": en[0] -= 0.01 # Move away

        # Render Logic
        screen.fill((20, 20, 20))
        # Draw HP bar
        pg.draw.rect(screen, (200, 0, 0), (10, 10, player_hp * 20, 20))
        pg.display.flip()

# UTILITIES

@njit()
def calculate_distances(pos, enemy_array):
    # Fast NumPy distance calculation
    for i in range(len(enemy_array)):
        dx = enemy_array[i, 0] - pos[0]
        dy = enemy_array[i, 1] - pos[1]
        enemy_array[i, 2] = np.sqrt(dx**2 + dy**2)
    return enemy_array

if __name__ == '__main__':
    main()
    pg.quit()