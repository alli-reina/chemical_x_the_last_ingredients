from collections import deque
import numpy as np
import pygame as pg

# ENEMY SPAWN WITH ARRAY
def spawn_enemies(number, size, maph, posx, posy):
    enemies = []
    for _ in range(number):
        x, y = np.random.randint(1, size-1), np.random.randint(1, size-1)
        while maph[x][y]: 
            x, y = np.random.randint(1, size-1), np.random.randint(1, size-1)
        enemies.append([x+0.5, y+0.5, 0, 1, np.random.choice([0,1]), np.random.uniform(7,10), 
                        np.random.uniform(0, 2*np.pi), 0, 5, 0, 0])
    return np.array(enemies)  # Array for fast vector ops

# ENEMY AI USING QUEUE
def enemies_ai_queue(posx, posy, enemies, maph):
    enemy_queue = deque(enemies)
    mape = np.zeros((len(maph), len(maph)))
    while enemy_queue:
        en = enemy_queue.popleft()
        if en[8] > 0:  # alive
            dist = np.sqrt((en[0]-posx)**2 + (en[1]-posy)**2)
            if dist < 2:
                en[9] = 1  # aggressive
            enemy_queue.append(en)
            x, y = int(en[0]), int(en[1])
            mape[x-1:x+2, y-1:y+2] += 1
    return np.array(enemy_queue), mape

# DECISION TREE FOR ENEMY AI
class EnemyNode:
    def __init__(self, check=None, yes=None, no=None, action=None):
        self.check = check
        self.yes = yes
        self.no = no
        self.action = action

def traverse_tree(node, enemy):
    if node.action: node.action(enemy)
    elif node.check(enemy):
        traverse_tree(node.yes, enemy)
    else:
        traverse_tree(node.no, enemy)

# Example usage:
def aggressive_check(e): return e[8] > 4
def attack(e): e[9] = 1
def retreat(e): e[9] = 2
tree = EnemyNode(aggressive_check, EnemyNode(action=attack), EnemyNode(action=retreat))

# --- GAME LOOP (simplified) ---
enemies = spawn_enemies(5, 10, np.zeros((10,10)), 5, 5)
enemies, mape = enemies_ai_queue(5,5,enemies, np.zeros((10,10)))
for en in enemies:
    traverse_tree(tree, en)
