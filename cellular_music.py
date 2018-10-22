# I really hesitate to call this music.

import pygame.midi as md
import pygame

pygame.init()
pygame.midi.init()

screen = pygame.display.set_mode((1500, 800))

box_x = 0
box_y = 0

grid_x = 12
grid_y = 5

block_size = 100

grid = [[0 for y in range(grid_y)] for x in range(grid_x)]
light_grid = [[0 for y in range(grid_y)] for x in range(grid_x)]
hit_grid = [[0 for y in range(grid_y)] for x in range(grid_x)]

import time, sys, math

i = pygame.midi.Input(1)
p_clock = pygame.time.Clock()

win_font = pygame.font.SysFont("Deja Vu", 20)

player = pygame.midi.Output(0)
player.set_instrument(6)
instrument = 0

while True:
    pygame.draw.rect(screen, (0,0,0), (0,0,500,500))
    pygame.draw.rect(screen, (255,255,255), (99+block_size*box_x, 99+block_size*box_y, 12*block_size+1, 5*block_size+1), 1)

    new_ons = []
    new_offs = []

    for y in range(grid_y):
        for x in range(grid_x):
            light_grid[x][y] = max(grid[x][y], light_grid[x][y], hit_grid[x][y])

            lg = light_grid[x][y]
            c = (50*(1-lg**2), 20+(lg**2)*235, 20+90*(1-lg**2))
            if hit_grid[x][y]: c = (150,255,60)
            pygame.draw.rect(screen, c, (100+ x*block_size, 100 + y*block_size, block_size-2, block_size-2) )
            light_grid[x][y] = 0 if light_grid[x][y]-0.2 < 0 else light_grid[x][y]-0.2

            # Now update the grid.
            neighbors = []
            neighbors.append(grid[grid_x-1 if x-1 < 0 else x-1][y])
            neighbors.append(grid[grid_x-1 if x-1 < 0 else x-1][(y+1)%grid_y])
            neighbors.append(grid[grid_x-1 if x-1 < 0 else x-1][grid_y-1 if y-1 < 0 else y-1])

            neighbors.append(grid[(x+1)%grid_x][y])
            neighbors.append(grid[(x+1)%grid_x][(y+1)%grid_y])
            neighbors.append(grid[(x+1)%grid_x][grid_y-1 if y-1 < 0 else y-1])

            neighbors.append(grid[x][(y+1)%grid_y])
            neighbors.append(grid[x][grid_y-1 if y-1 < 0 else y-1])

            s = sum(neighbors)

            if s < 3: new_offs.append((x,y))
            elif s > 3: new_offs.append((x,y))
            if s == 3: new_ons.append((x,y))

    for (x,y) in new_offs:
        grid[x][y] = 0
        player.note_off(x+12*y+36,127)
    for (x,y) in new_ons:
        player.note_on(x+12*y+36,127)
        grid[x][y] = 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    if i.poll():
        midi_events = i.read(10)
        midi_evs = pygame.midi.midis2events(midi_events, i.device_id)

        for e in midi_evs:
            k = e.data2
            if k>0:
                if k == 127: continue
                grid[(e.data1-36)%12 + box_x][int((e.data1-36)/12) + box_y] = 1
                hit_grid[(e.data1-36)%12 + box_x][int((e.data1-36)/12) + box_y] = 1

                sx = (e.data1-36)%12 + box_x
                sy = int((e.data1-36)/12) + box_y
                grid[sx][(sy+1) % grid_y] = 1

                if sy - 1 > 0:
                    grid[sx][sy-1] = 1
                else:
                    grid[sx][grid_y-1] = 1
                grid[(sx+1) % grid_x][sy] = 1

                if sx - 1 > 0 :
                    grid[sx-1][sy] = 1
                else:
                    grid[grid_x-1][sy] = 1
            else:
                hit_grid[(e.data1-36)%12 + box_x][int((e.data1-36)/12) + box_y] = 0

    pygame.display.flip()
    p_clock.tick(30)