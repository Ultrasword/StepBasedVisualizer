
import stepvis

import pygame
from pygame.math import Vector2
import random

pygame.init()

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

points = [vec2(random.randint(100, 700), random.randint(100, 400)) for _ in range(20)]
scheduler = stepvis.StepVisScheduler({"freq": 10})

# --------------------------- #

def render_points(points, color=(255, 255, 255), r=3):
    for p in points:
        pygame.draw.circle(window, color, p, r)

# --------------------------- #
LINES = []
UP = []
DOWN = []
INSIDE = []
SPECIAL = []

def min_max_points(ps):
    ps.sort(key= lambda p: (p.x, p.y))
    return ps[0], ps[-1]

def get_min_max_dis(ps, st, en):
    ln = en-st
    ps.sort(key=lambda p: (p).dot(ln))
    return ps[0], ps[-1]

def get_above_and_below(ps, st, en):
    # ln = line.from_points(st, en)
    ln = en-st
    # lbi = ln.inverse()
    a, b = [], []
    for p in ps:
        # lp = line.from_m_point(lbi, p)
        # li = lp.intersect(ln)
        # d = vec2(li).distance_to(p)
        a.append(p) if p-st and ln.cross(p-st) > 0 else b.append(p)
    return a, b

def findhull(ps, p, q, t=True):
    if not ps: return
    u, d = get_above_and_below(ps, p, q)
    cm, cM = get_min_max_dis(ps, p, q)

    return cm, cM

def project(point, axis):
    """distnace between vector and another vector"""
    return point.dot(axis)


# --------------------------- #

pm, pM = min_max_points(points)
LINES.append((pm, pM))
up, down = get_above_and_below(points, pm, pM)
# print(up, down)
UP += up
DOWN += down

# print(UP, DOWN, INSIDE)
SPECIAL += list(findhull(up, pm, pM))
SPECIAL += list(findhull(down, pM, pm))

# scheduler.running = False

# --------------------------- #


font = pygame.font.SysFont("Arial", 32)

scheduler.start()
while scheduler.running:
    window.fill((0, 0, 0))
    window.blit(font.render(str(len(scheduler)), False, (255, 255, 255)), (0, 0))

    render_points(points, (255, 255, 255))
    render_points(INSIDE, (0, 0, 255))
    render_points(UP, (0, 255, 0))
    render_points(DOWN, (0, 255, 0))
    render_points(SPECIAL, (255, 0, 0))

    for line in LINES:
        pygame.draw.line(window, (0, 0, 255), line[0], line[1])

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            scheduler.running = False
        elif e.type == pygame.KEYDOWN:
            # add task
            # scheduler.push_task(add_point)
            pass

    pygame.display.update()
    clock.tick(30)

pygame.quit()
scheduler.attempt_join()






