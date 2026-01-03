import pygame as pg
import numpy as np
from collections import deque
from numba import njit

# QUEUE: Manages enemies waiting to enter the arena
class EnemyQueue:
    def __init__(self, data): self.items = deque(data)
    def get_next(self): return self.items.popleft() if self.items else None

# STACK: Stores recent player inputs (could be used for combos/undo)
class InputStack:
    def __init__(self): self.history = []
    def push(self, cmd): self.history.append(cmd)
    def pop(self): return self.history.pop() if self.history else None

def main():
    pg.init()
    screen = pg.display.set_mode((800, 600))
    clock = pg.time.Clock()
    pg.mouse.set_visible(False)
    pg.event.set_grab(1)

    # ARRAY (NumPy): 2D/3D grids for map and rendering
    size = 25
    posx, posy, rot, maph, mapc, exitx, exity = gen_map(size)
    hres, halfvres = 250, int(250*0.375)
    frame = np.random.uniform(0, 1, (hres, halfvres*2, 3))
    
    # Initialize our Data Structures
    raw_enemies = spawn_enemies(size*2, maph, size)
    enemy_q = EnemyQueue(raw_enemies) # Queue usage
    active_enemies = np.zeros((0, 8)) 
    inputs = InputStack()             # Stack usage

    running, swordsp = True, 0
    while running:
        er = min(clock.tick()/500, 0.3)
        ticks = pg.time.get_ticks()/200

        # Maintain 5 active enemies using the Queue
        if len(active_enemies) < 5 and len(enemy_q.items) > 0:
            new_en = enemy_q.get_next()
            active_enemies = np.vstack((active_enemies, new_en))

        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                running = False
            if event.type == pg.MOUSEBUTTONDOWN and swordsp < 1:
                swordsp = 1
                inputs.push("ATTACK") # Push to Stack

        # Movement & Rendering (Simplified calls)
        keys = pg.key.get_pressed()
        if keys[pg.K_w]: inputs.push("FORWARD")
        posx, posy, rot = movement(keys, posx, posy, rot, maph, er)
        
        # Fake render logic for demo brevity
        active_enemies = sort_sprites(posx, posy, rot, active_enemies, maph, size, er/5)
        
        # Kill logic
        if swordsp == 1 and len(active_enemies) > 0:
            if active_enemies[-1][3] < 10: # If closest enemy is in range
                active_enemies = np.delete(active_enemies, -1, axis=0)
        
        swordsp = (swordsp + er*5) % 4 if swordsp > 0 else 0
        pg.display.set_caption(f"Enemies in Queue: {len(enemy_q.items)} | Active: {len(active_enemies)}")
        pg.display.update()

# HELPER FUNCTIONS

def movement(keys, px, py, rot, maph, et):
    if pg.mouse.get_focused():
        rot += np.clip(pg.mouse.get_rel()[0]/200, -0.2, 0.2)
    nx, ny = px + (keys[pg.K_w]-keys[pg.K_s])*et*np.cos(rot), py + (keys[pg.K_w]-keys[pg.K_s])*et*np.sin(rot)
    if not maph[int(nx)][int(ny)]: return nx, ny, rot
    return px, py, rot

def gen_map(size):
    maph = np.random.choice([0, 0, 1], (size, size))
    maph[0,:], maph[-1,:], maph[:,0], maph[:,-1] = 1, 1, 1, 1
    return 1.5, 1.5, 0, maph, np.random.rand(size, size, 3), size-2, size-2

def spawn_enemies(n, maph, msize):
    return np.random.rand(n, 8) # Placeholder for enemy data array

@njit()
def sort_sprites(px, py, rot, enemies, maph, size, er):
    # Sorts the Array based on distance to player
    if len(enemies) == 0: return enemies
    for i in range(len(enemies)):
        enemies[i][3] = np.sqrt((enemies[i][0]-px)**2 + (enemies[i][1]-py)**2)
    return enemies[enemies[:, 3].argsort()[::-1]]

if __name__ == '__main__':
    main()
    pg.quit()