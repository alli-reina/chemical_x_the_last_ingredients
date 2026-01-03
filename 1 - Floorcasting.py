import pygame as pg
import numpy as np
from collections import deque
from numba import njit

# LINKED LIST: Simple Node-based structure for Waypoints
class Waypoint:
    def __init__(self, pos):
        self.pos = pos
        self.next = None

class WaypointList:
    def __init__(self): self.head = None
    def add(self, pos):
        new_node = Waypoint(pos)
        new_node.next = self.head
        self.head = new_node

# QUEUE: To log recent movement inputs (FIFO)
class MoveLog:
    def __init__(self): self.queue = deque(maxlen=5)
    def log(self, cmd): self.queue.append(cmd)

def main():
    pg.init()
    screen = pg.display.set_mode((800, 600))
    clock = pg.time.Clock()

    hres, halfvres = 120, 100
    mod = hres / 60
    posx, posy, rot = 0.0, 0.0, 0.0
    
    # ARRAY: NumPy Arrays for textures and frames
    frame = np.zeros((hres, halfvres * 2, 3))
    floor_tex = np.random.rand(100, 100, 3) # Placeholder for floor.jpg
    sky_tex = np.random.rand(360, halfvres * 2, 3) # Placeholder for skybox2.jpg

    waypoints = WaypointList()
    moves = MoveLog()
    
    running = True
    while running:
        dt = clock.tick()
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                running = False
            # Drop a Waypoint (Linked List) when Space is pressed
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                waypoints.add((posx, posy))
                moves.log("DROP_MARKER")

        # Update Frame & Movement
        keys = pg.key.get_pressed()
        posx, posy, rot = movement(posx, posy, rot, keys, dt, moves)
        
        frame = render_floor(posx, posy, rot, frame, sky_tex, floor_tex, hres, halfvres, mod)
        
        # Display
        surf = pg.surfarray.make_surface(frame * 255)
        screen.blit(pg.transform.scale(surf, (800, 600)), (0, 0))
        
        # Simple Debug Text for Queue and List
        font = pg.font.SysFont("Arial", 18)
        log_txt = font.render(f"Last Move: {list(moves.queue)}", True, (255, 255, 255))
        screen.blit(log_txt, (10, 10))
        
        pg.display.update()

def movement(px, py, rot, keys, dt, moves):
    if keys[pg.K_a]: 
        rot -= 0.002 * dt
        moves.log("LEFT")
    if keys[pg.K_d]: 
        rot += 0.002 * dt
        moves.log("RIGHT")
    
    speed = 0.005 * dt
    if keys[pg.K_w]:
        px, py = px + np.cos(rot) * speed, py + np.sin(rot) * speed
        moves.log("FORWARD")
        
    return px, py, rot

@njit()
def render_floor(posx, posy, rot, frame, sky, floor, hres, halfvres, mod):
    for i in range(hres):
        angle = rot + np.deg2rad(i/mod - 30)
        cos, sin = np.cos(angle), np.sin(angle)
        cos_f = np.cos(np.deg2rad(i/mod - 30))
        
        # Sky background
        frame[i][:] = sky[int(np.rad2deg(angle) % 359)][:]
        
        # Floor casting
        for j in range(halfvres):
            # Distance to floor pixel
            dist = (halfvres / (halfvres - j)) / cos_f
            x, y = posx + cos * dist, posy + sin * dist
            
            xx, yy = int(x * 2 % 1 * 99), int(y * 2 % 1 * 99)
            shade = 0.2 + 0.8 * (1 - j / halfvres)
            frame[i][halfvres * 2 - j - 1] = shade * floor[xx][yy]
            
    return frame

if __name__ == '__main__':
    main()
    pg.quit()