
import stepvis

import pygame
import random

pygame.init()

window = pygame.display.set_mode([800, 500], 0, 32)
clock = pygame.time.Clock()


points = []
def add_point():
    global points
    points.append((random.randint(0, 800), random.randint(0, 500)))

font = pygame.font.SysFont("Arial", 32)

scheduler = stepvis.StepVisScheduler({"freq": 10})
scheduler.start()
while scheduler.running:
    window.fill((0, 0, 0))
    for p in points:
        pygame.draw.circle(window, (255, 0, 0), p, 3)
    window.blit(font.render(str(len(scheduler)), False, (255, 255, 255)), (0, 0))

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            scheduler.running = False
        elif e.type == pygame.KEYDOWN:
            # add task
            scheduler.push_task(add_point)

    pygame.display.update()
    clock.tick(30)

pygame.quit()
scheduler.attempt_join()






