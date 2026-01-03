import pygame as pg
import numpy as np
from collections import deque
from numba import njit

class EnemySpawnQueue:
    def __init__(self):
        self.queue = deque()

    def enqueue(self, enemy):
        self.queue.append(enemy)

    def dequeue(self):
        if self.queue:
            return self.queue.popleft()
        return None

    def is_empty(self):
        return len(self.queue) == 0

class ActionStack:
    def __init__(self):
        self.stack = []

    def push(self, action):
        self.stack.append(action)

    def pop(self):
        if self.stack:
            return self.stack.pop()
        return None

# MAIN GAME

def main():
    pg.init()
    screen = pg.display.set_mode((800,600))
    running = True
    clock = pg.time.Clock()
    pg.mouse.set_visible(False)
    pg.event.set_grab(1)

    hres = 250
    halfvres = int(hres*0.375)
    mod = hres/60

    size = 25
    nenemies = size*2
    posx, posy, rot, maph, mapc, exitx, exity = gen_map(size)

    frame = np.random.uniform(0,1, (hres, halfvres*2, 3))
    sky = pg.image.load('skybox2.jpg')
    sky = pg.surfarray.array3d(pg.transform.smoothscale(sky, (720, halfvres*2)))/255
    floor = pg.surfarray.array3d(pg.image.load('floor.jpg'))/255
    wall = pg.surfarray.array3d(pg.image.load('wall.jpg'))/255
    sprites, spsize, sword, swordsp = get_sprites(hres)

    # QUEUE: Enemy spawn
    enemy_spawn_queue = EnemySpawnQueue()
    enemies = np.zeros((0,8))
    for enemy in spawn_enemies(nenemies, maph, size):
        enemy_spawn_queue.enqueue(enemy)

    # STACK: Player actions
    action_stack = ActionStack()

    # MAIN LOOP
    while running:
        ticks = pg.time.get_ticks()/200
        er = min(clock.tick()/500, 0.3)

        # Spawn enemies gradually from Queue
        if len(enemies) < 10 and not enemy_spawn_queue.is_empty():
            new_enemy = enemy_spawn_queue.dequeue()
            enemies = np.vstack((enemies, new_enemy))

        # Win condition
        if int(posx) == exitx and int(posy) == exity:
            if len(enemies) < size:
                print("You got out of the maze!")
                pg.time.wait(1000)
                running = False
            elif int(ticks%10+0.9) == 0:
                print("There is still work to do...")

        # Event handling
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                running = False
            if swordsp < 1 and event.type == pg.MOUSEBUTTONDOWN:
                swordsp = 1
                action_stack.push("ATTACK")  # Stack usage

        # Record movement actions
        keys = pg.key.get_pressed()
        if keys[pg.K_UP] or keys[ord('w')]:
            action_stack.push("MOVE_FORWARD")
        if keys[pg.K_DOWN] or keys[ord('s')]:
            action_stack.push("MOVE_BACKWARD")
        if keys[pg.K_LEFT] or keys[ord('a')]:
            action_stack.push("MOVE_LEFT")
        if keys[pg.K_RIGHT] or keys[ord('d')]:
            action_stack.push("MOVE_RIGHT")

        # Render new frame
        frame = new_frame(posx, posy, rot, frame, sky, floor, hres, halfvres, mod, maph, size,
                          wall, mapc, exitx, exity)
        surf = pg.surfarray.make_surface(frame*255)

        # Enemy sorting
        enemies = sort_sprites(posx, posy, rot, enemies, maph, size, er/5)
        surf, en = draw_sprites(surf, sprites, enemies, spsize, hres, halfvres, ticks, sword, swordsp)

        surf = pg.transform.scale(surf, (800, 600))

        # Handle sword attacks
        if int(swordsp) > 0:
            if swordsp == 1 and enemies[en][3] > 1 and enemies[en][3] < 10:
                enemies[en][0] = 0
                enemies = np.delete(enemies, en, axis=0)
            swordsp = (swordsp + er*5)%4

        screen.blit(surf, (0,0))
        pg.display.update()
        fps = int(clock.get_fps())
        pg.display.set_caption("Enemies remaining: " + str(len(enemies)) + " - FPS: " + str(fps))

        # Movement
        posx, posy, rot = movement(keys, posx, posy, rot, maph, er)

# MOVEMENT
def movement(pressed_keys, posx, posy, rot, maph, et):
    x, y, diag = posx, posy, 0
    if pg.mouse.get_focused():
        p_mouse = pg.mouse.get_rel()
        rot = rot + np.clip((p_mouse[0])/200, -0.2, .2)

    if pressed_keys[pg.K_UP] or pressed_keys[ord('w')]:
        x, y, diag = x + et*np.cos(rot), y + et*np.sin(rot), 1
    elif pressed_keys[pg.K_DOWN] or pressed_keys[ord('s')]:
        x, y, diag = x - et*np.cos(rot), y - et*np.sin(rot), 1
    if pressed_keys[pg.K_LEFT] or pressed_keys[ord('a')]:
        et = et/(diag+1)
        x, y = x + et*np.sin(rot), y - et*np.cos(rot)
    elif pressed_keys[pg.K_RIGHT] or pressed_keys[ord('d')]:
        et = et/(diag+1)
        x, y = x - et*np.sin(rot), y + et*np.cos(rot)

    # collision check
    if not(maph[int(x-0.2)][int(y)] or maph[int(x+0.2)][int(y)] or
           maph[int(x)][int(y-0.2)] or maph[int(x)][int(y+0.2)]):
        posx, posy = x, y
    elif not(maph[int(posx-0.2)][int(y)] or maph[int(posx+0.2)][int(y)] or
             maph[int(posx)][int(y-0.2)] or maph[int(posx)][int(y+0.2)]):
        posy = y
    elif not(maph[int(x-0.2)][int(posy)] or maph[int(x+0.2)][int(posy)] or
             maph[int(x)][int(posy-0.2)] or maph[int(x)][int(posy+0.2)]):
        posx = x

    return posx, posy, rot

# MAP GENERATION
def gen_map(size):
    mapc = np.random.uniform(0,1, (size,size,3)) 
    maph = np.random.choice([0,0,0,0,1,1], (size,size))
    maph[0,:], maph[size-1,:], maph[:,0], maph[:,size-1] = (1,1,1,1)

    posx, posy, rot = 1.5, np.random.randint(1, size-1)+.5, np.pi/4
    x, y = int(posx), int(posy)
    maph[x][y] = 0
    count = 0
    while True:
        testx, testy = (x, y)
        if np.random.uniform() > 0.5:
            testx += np.random.choice([-1, 1])
        else:
            testy += np.random.choice([-1, 1])
        if testx > 0 and testx < size-1 and testy > 0 and testy < size-1:
            if maph[testx][testy] == 0 or count > 5:
                count = 0
                x, y = (testx, testy)
                maph[x][y] = 0
                if x == size-2:
                    exitx, exity = (x, y)
                    break
            else:
                count += 1
    return posx, posy, rot, maph, mapc, exitx, exity

# FRAME, ENEMIES, SPRITES

@njit()
def new_frame(posx, posy, rot, frame, sky, floor, hres, halfvres, mod, maph, size, wall, mapc, exitx, exity):
    for i in range(hres):
        rot_i = rot + np.deg2rad(i/mod - 30)
        frame[i][:] = sky[int(np.rad2deg(rot_i)*2%718)][:]  # simplified
    return frame

@njit()
def sort_sprites(posx, posy, rot, enemies, maph, size, er):
    for en in range(len(enemies)):
        enemies[en][3] = np.random.uniform(0.1, 5)  # distance placeholder
    enemies = enemies[enemies[:, 3].argsort()]
    return enemies

def spawn_enemies(number, maph, msize):
    enemies = []
    for i in range(number):
        x, y = np.random.uniform(1, msize-2), np.random.uniform(1, msize-2)
        angle2p, invdist2p, dir2p = 0, 0, 0
        entype = np.random.choice([0,1])
        direction = np.random.uniform(0, 2*np.pi)
        size = np.random.uniform(7,10)
        enemies.append([x, y, angle2p, invdist2p, entype, size, direction, dir2p])
    return np.asarray(enemies)

def get_sprites(hres):
    sheet = pg.Surface((96,400))  # placeholder
    sprites = [[],[]]
    sword = [pg.Surface((hres, int(hres*0.75))) for _ in range(4)]
    spsize = np.array([32,100])
    return sprites, spsize, sword, 0

def draw_sprites(surf, sprites, enemies, spsize, hres, halfvres, ticks, sword, swordsp):
    return surf, len(enemies)-1

# RUN
if __name__ == '__main__':
    main()
    pg.quit()
