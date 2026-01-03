import pygame as pg
import numpy as np
from collections import deque
from numba import njit

# STACK for Game States
class StateStack:
    def __init__(self): self.states = ['PLAY']
    def push(self, s): self.states.append(s)
    def pop(self): return self.states.pop() if len(self.states) > 1 else self.states[0]

# QUEUE for Notifications
class NotificationQueue:
    def __init__(self): self.q = deque()
    def add(self, txt): self.q.append((txt, pg.time.get_ticks()))
    def update(self):
        if self.q and pg.time.get_ticks() - self.q[0][1] > 2000: self.q.popleft()

def main():
    pg.init()
    screen = pg.display.set_mode((800, 600))
    clock = pg.time.Clock()
    pg.mouse.set_visible(False)
    pg.event.set_grab(True)

    # NUMPY ARRAYS for Map and Rendering
    size = 20
    maph = np.random.choice([0, 0, 0, 1], (size, size))
    maph[0,:]=maph[-1,:]=maph[:,0]=maph[:,-1] = 1 # Outer walls
    px, py, rot = 2.0, 2.0, 0.0
    frame = np.zeros((200, 150 * 2, 3)) # Low-res buffer for speed

    states, notes = StateStack(), NotificationQueue()
    notes.add("ESCAPE THE MAZE")

    while True:
        dt = clock.tick(60) / 1000
        notes.update()
        
        for event in pg.event.get():
            if event.type == pg.QUIT: return
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE: states.push('MENU')

        if states.states[-1] == 'PLAY':
            # Movement & Rendering
            keys = pg.key.get_pressed()
            rot += pg.mouse.get_rel()[0] / 200
            if keys[pg.K_w]:
                nx, ny = px + np.cos(rot)*dt*3, py + np.sin(rot)*dt*3
                if not maph[int(nx)][int(ny)]: px, py = nx, ny
            
            # Call JIT Raycaster
            frame = render(px, py, rot, frame, maph, size)
            surf = pg.surfarray.make_surface(frame * 255)
            screen.blit(pg.transform.scale(surf, (800, 600)), (0, 0))

            # UI from Queue
            if notes.q:
                text = pg.font.SysFont("Arial", 30).render(notes.q[0][0], True, (255, 255, 0))
                screen.blit(text, (20, 20))
        
        pg.display.flip()

@njit
def render(px, py, rot, frame, maph, size):
    for i in range(200): # Horizontal rays
        angle = rot + np.deg2rad(i * (60/200) - 30)
        cos, sin = np.cos(angle), np.sin(angle)
        x, y, dist = px, py, 0
        while dist < 20: # Ray march
            x += 0.05 * cos
            y += 0.05 * sin
            dist += 0.05
            if maph[int(x)%size][int(y)%size]: break
        
        h = int(150 / (dist + 0.001)) # Wall height
        for j in range(300): # Vertical pixels
            if 150-h < j < 150+h: 
                frame[i][j] = np.array([0.5, 0.2, 0.1]) / (1 + dist*0.5) # Shaded Wall
            elif j >= 150+h: frame[i][j] = np.array([0.2, 0.2, 0.2]) # Floor
            else: frame[i][j] = np.array([0.4, 0.6, 1.0]) # Sky
    return frame

if __name__ == '__main__':
    main()
    pg.quit()