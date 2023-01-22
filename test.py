
import stepvis

import numpy as np
import pygame
from pygame.math import Vector2
import random

pygame.init()

print("THERE IS MASSIVE ERROR IN CODE?????")

window = pygame.display.set_mode([800, 500], 0, 32)
clock = pygame.time.Clock()

class line:
    @classmethod
    def from_points(cls, p1, p2):
        dx = p2.x-p1.x
        if dx == 0: dx = 1/1e9
        m = (p2.y-p1.y)/dx
        return cls(m, p1.y - m * p1.x)

    @classmethod
    def from_m_point(cls, m, p):
        return cls(m, p.y - m * p.x)

    def __init__(self, m, b):
        self.m = m
        self.b = b
    
    def inverse(self):
        return -1/self.m
    
    def value(self, x): 
        return self.m * x + self.b

    def above(self, p):
        return p.y > self.value(p.x)
    
    def below(self, p):
        return p.y < self.value(p.x)
    
    def intersect(self, otherline):
        dm = (otherline.m - self.m)
        if dm == 0:
            dm = 1/1e9
        x = (self.b - otherline.b) / dm
        return (x, self.value(x))

class vec2(Vector2):
    def __init__(self, *args):
        super().__init__(*args)
    
    def __hash__(self):
        return int(self.x * 1e9 + self.y)

POINTS = [vec2(random.randint(100, 700), random.randint(100, 400)) for _ in range(1000)]
r = vec2()
for i in POINTS:
    r += i
avg = r/len(POINTS)

scheduler = stepvis.StepVisScheduler({"freq": 1000})

# --------------------------- #

def render_points(points, color=(255, 255, 255), r=3):
    for p in points:
        pygame.draw.circle(window, color, p, r)

# --------------------------- #
LINES = []
HULL = []
UP = []
DOWN = []
INSIDE = []
SPECIAL = []


def quick_hull(pk, asyn=False):
    """Quick hull algorithm"""
    # define resulting convex hull list
    result = []

    # find leftmost and rightmost point
    pk.sort(key=lambda p: (p.x , p.y))
    pm, pM = pk[0], pk[-1]
    result += [pm, pM]

    # call hull determiningn algorithm
    if asyn:
        scheduler.push_task(target=find_hull, args=(pk, pm, pM, asyn,))
        scheduler.push_task(target=find_hull, args=(pk, pM, pm, asyn,))
        update_hull()
    else:
        upper = find_hull(pk, pm, pM)
        lower = find_hull(pk, pM, pm)
        return upper + lower + result

def find_hull(pk, st, en, asyn=False):
    """Find the convex hull of a set of points"""
    # base case for recursion
    if not pk: return []
    global INSIDE
    upper = []
    result = []
    # find c -- furthest from line
    max_dis = 0
    c = pk[0]
    for p in pk:
        # if p == c: continue
        if is_left(p, st, en):
            upper.append(p)
            pdis = find_distance(p, st, en)
            if pdis > max_dis:
                max_dis = pdis
                c = p
        else:
            INSIDE.append(p)

    # add furthest to hull
    if c: result.append(c)
    # if async then yeet
    if asyn:
        scheduler.push_task(target=find_hull, args=(upper, st, c, asyn,))
        scheduler.push_task(target=find_hull, args=(upper, c, en, asyn,))
        # print(upper, result)
        global HULL
        HULL += result
        update_hull()
    else:
        reg1 = find_hull(upper, st, c)
        reg2 = find_hull(upper, c, en)
        return reg1 + reg2 + result

def is_left(p, st, en):
    """Check if point c is left of line ab"""
    # cross product ya
    ln = en - st
    return ln.cross(p-st) > 0

def find_distance(p, st, en):
    """Find the distance of a point from a line"""
    # find dot product
    ln = en - st
    return ln.dot(p - st)

def update_hull():
    global HULL
    # print(HULL)
    HULL.sort(key=lambda p: avg.angle_to(p-avg))


# inter = quick_hull(points, asyn=True)
# HULL = quick_hull(POINTS)
# HULL = inter

update_hull()

# --------------------------- #


font = pygame.font.SysFont("Arial", 32)

running = True
# scheduler.start()
# while scheduler.running:
while running:
    window.fill((0, 0, 0))
    window.blit(font.render(str(len(scheduler)), False, (255, 255, 255)), (0, 0))

    render_points(POINTS, (255, 255, 255))
    render_points(INSIDE, (0, 0, 255))
    render_points(UP, (0, 255, 0))
    render_points(DOWN, (0, 255, 0))
    render_points(SPECIAL, (255, 0, 0))

    if len(HULL) > 2:
        pygame.draw.polygon(window, (100, 100, 255), HULL, 1)
    for line in LINES:
        pygame.draw.line(window, (0, 0, 255), line[0], line[1])

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            scheduler.running = False
            running = False
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_SPACE:
                # update hull
                scheduler._task_queue.clear()
                INSIDE.clear()
                SPECIAL.clear()
                HULL = quick_hull(POINTS)
                update_hull()
            elif e.key == pygame.K_k:
                POINTS.clear()
                HULL.clear()
                INSIDE.clear()
                SPECIAL.clear()
                scheduler._task_queue.clear()
            elif e.key == pygame.K_d:
                scheduler.run_task()
        elif e.type == pygame.MOUSEBUTTONDOWN:
            if e.button == 1:
                POINTS.append(vec2(pygame.mouse.get_pos()))

    pygame.display.update()
    clock.tick(30)

pygame.quit()
scheduler.attempt_join()






