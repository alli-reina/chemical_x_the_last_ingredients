import pygame as pg
import numpy as np
from collections import deque
from numba import njit

# STACK: Manages Game States (e.g., 'MENU', 'PLAYING', 'WIN')
class StateStack:
    def __init__(self): self.states = ['PLAYING']
    def push(self, s): self.states.append(s)
    def pop(self): return self.states.pop() if len(self.states) > 1 else self.states[0]
    def current(self): return self.states[-1]

# QUEUE: Manages on-screen notifications
class MessageQueue:
    def __init__(self): self.msgs = deque()
    def add(self, txt): self.msgs.append((txt, pg.time.get_ticks()))
    def update(self): # Remove messages after 2 seconds
        if self.msgs and pg.time.get_ticks() - self.msgs[0][1] > 2000: self.msgs.popleft()

def main():
    pg.init()
    screen = pg.display.set_mode((800, 600))
    clock = pg.time.Clock()
    pg.mouse.set_visible(False)
    pg.event.set_grab(1)

    # ARRAY: Map and Frame data
    size = 25
    px, py, rot, maph, mapc, ex, ey = gen_map(size)
    hres, vres = 200, 150
    frame = np.zeros((hres, vres * 2, 3))
    
    # Load assets (Placeholders)
    sky = np.random.rand(360, vres*2, 3) 
    wall = np.random.rand(100, 100, 3)
    floor = np.random.rand(100, 100, 3)

    game_states = StateStack()
    notifs = MessageQueue()
    notifs.add("Find the exit!")

    running = True
    while running:
        dt = clock.tick() / 500
        notifs.update()

        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                running = False

        if game_states.current() == 'PLAYING':
            # Check Win Condition
            if int(px) == ex and int(py) == ey:
                game_states.push('WIN')
                notifs.add("MAZE ESCAPED!")

            # Rendering & Movement
            frame = render_frame(px, py, rot, frame, sky, floor, hres, vres, maph, size, wall, mapc)
            surf = pg.surfarray.make_surface(frame * 255)
            screen.blit(pg.transform.scale(surf, (800, 600)), (0, 0))
            
            # Display Notification from Queue
            if notifs.msgs:
                font = pg.font.SysFont("Arial", 30)
                txt = font.render(notifs.msgs[0][0], True, (255, 255, 0))
                screen.blit(txt, (20, 20))

            px, py, rot = move(px, py, rot, maph, dt)
        
        pg.display.update()

# UTILITIES

def move(px, py, rot, maph, dt):
    keys = pg.key.get_pressed()
    rot += np.clip(pg.mouse.get_rel()[0]/200, -0.2, 0.2)
    # Forward/Back logic
    move_dir = (keys[pg.K_w] - keys[pg.K_s])
    nx, ny = px + move_dir * dt * np.cos(rot), py + move_dir * dt * np.sin(rot)
    if not maph[int(nx)][int(ny)]: return nx, ny, rot
    return px, py, rot

def gen_map(size):
    maph = np.random.choice([0, 0, 0, 1], (size, size))
    maph[0,:], maph[-1,:], maph[:,0], maph[:,-1] = 1, 1, 1, 1
    return 1.5, 1.5, 0, maph, np.random.rand(size, size, 3), size-2, size-2

@njit()
def render_frame(px, py, rot, frame, sky, floor, hres, vres, maph, size, wall, mapc):
    for i in range(hres):
        angle = rot + np.deg2rad(i * (60/hres) - 30)
        cos, sin = np.cos(angle), np.sin(angle)
        
        # Simple Raycasting
        x, y = px, py
        while not maph[int(x) % size][int(y) % size]:
            x += 0.02 * cos
            y += 0.02 * sin
        
        dist = np.sqrt((x-px)**2 + (y-py)**2)
        h = int(vres / (dist + 0.001))
        
        # Color column
        col = mapc[int(x)%size][int(y)%size] * (1/(1 + dist*0.5))
        for j in range(vres*2):
            if j > vres-h and j < vres+h: frame[i][j] = col
            elif j >= vres+h: frame[i][j] = [0.2, 0.2, 0.2] # Floor
            else: frame[i][j] = [0.4, 0.6, 1.0] # Sky
    return frame

if __name__ == '__main__':
    main()
    pg.quit()