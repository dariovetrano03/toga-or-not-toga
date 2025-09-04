import pygame
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from scipy.interpolate import interp1d, griddata
import os
from src.functions import plot_compressor_map

pygame.init()

# --- Stato iniziale ---
initial_state = {
    "throttle_0": 89,
    "wc_0": 17,
    "beta_c_0": 5.5, 
    "A_exit": 1,
    "N": 0.5,
    "score": 0,
    "stall": False
}

throttle = initial_state["throttle_0"]
A_exit = initial_state["A_exit"]
N = initial_state["N"]
score = initial_state["score"]
stall = initial_state["stall"]

# --- Setup pygame ---
W, H = 1000, 700
screen = pygame.display.set_mode((W,H))
pygame.display.set_caption("To GA or not to GA?")

font = pygame.font.SysFont("consolas", 22)
bigfont = pygame.font.SysFont("consolas", 32, bold=True)
clock = pygame.time.Clock()


# --- Loop principale ---
riattaccata_mode = False
riattaccata_curve = None
blue_idx = 0
hold_up_time = 0

while True:
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            pygame.quit(); sys.exit()

    keys = pygame.key.get_pressed()
    if not stall:
        if not riattaccata_mode:
            # normale controllo throttle
            if keys[pygame.K_UP]:
                throttle = min(100, throttle + 1)
            if keys[pygame.K_DOWN]:
                throttle = max(84, throttle - 1)
            if keys[pygame.K_RIGHT]:
                A_exit = min(1.3, A_exit + 0.05)
            if keys[pygame.K_LEFT]:
                A_exit = max(0.9, A_exit - 0.05)

            if keys[pygame.K_i]:
                riattaccata_mode = True
                # determina raggio in base a hold_up_time
                radius = 0.5 + hold_up_time*0.02
                # centro semicirconferenza = punto blu + offset verticale per raggio
                surf, margin, wc_point, PR_point = plot_compressor_map(throttle, A_exit, N, stall)
                center = np.array([wc_point, PR_point + radius])
                # crea semicirconferenza magenta
                angles = np.linspace(-np.pi/2, np.pi/2, 50)
                riattaccata_curve = np.zeros((len(angles),2))
                riattaccata_curve[:,0] = center[0] + radius*np.cos(angles)
                riattaccata_curve[:,1] = center[1] + radius*np.sin(angles)
                blue_idx = 0
        else:
            # in riattaccata, solo UP aumenta indice curva
            if keys[pygame.K_UP]:
                blue_idx = min(blue_idx+1, len(riattaccata_curve)-1)
            # termina riattaccata
            if keys[pygame.K_r]:
                riattaccata_mode = False
                riattaccata_curve = None
                blue_idx = 0
                hold_up_time = 0

    # calcola hold_up_time
    if keys[pygame.K_UP] and not riattaccata_mode:
        hold_up_time += 1

    # aggiorna mappa compressore
    map_surf, margin, wc_point, PR_point = plot_compressor_map(throttle, A_exit, stall, riattaccata_curve,
                                                              riattaccata_curve[blue_idx] if riattaccata_curve is not None else None)
    # controllo pompaggio
    if margin<0: stall=True

    # disegna
    screen.fill((240,240,255))
    hud_x,hud_y = 40,60
    screen.blit(bigfont.render("ENGINE HUD", True, (0,0,0)), (hud_x,hud_y))
    screen.blit(font.render(f"Throttle {throttle:.2f}", True,(0,0,200)),(hud_x,hud_y+50))
    screen.blit(font.render(f"Nozzle A_exit {A_exit:.2f}", True,(0,0,200)),(hud_x,hud_y+80))
    screen.blit(font.render(f"Score {score}", True,(150,0,150)),(hud_x,hud_y+110))
    if stall:
        screen.blit(bigfont.render("STALL DETECTED! Press R to reset", True,(200,0,0)),(hud_x,hud_y+160))
    # disegna compressore
    screen.blit(map_surf,(W//2,100))
    # disegna piano
    draw_plane(screen, 100, H//2, A_exit)

    pygame.display.flip()
    clock.tick(30)
