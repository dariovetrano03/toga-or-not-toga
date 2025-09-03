import pygame
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from scipy.interpolate import interp1d, griddata
import os

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
W, H = 1200, 700
screen = pygame.display.set_mode((W,H))
pygame.display.set_caption("Minigioco Compressore + Riattaccata")

font = pygame.font.SysFont("consolas", 22)
bigfont = pygame.font.SysFont("consolas", 32, bold=True)
clock = pygame.time.Clock()

# --- Funzioni compressore ---

def fun_iso_throttle():
    data = np.loadtxt(r".\data\iso_throttle_comp_map.csv", delimiter=",", skiprows=1)

    t_all = np.array(data[:,0])
    x_all = np.array(data[:,1])
    y_all = np.array(data[:,2])

    t_all_unique =  np.unique(t_all)

    idx = np.argsort(x_all)

    x_all = x_all[idx]
    y_all = y_all[idx]
    
    t_q = np.linspace(80, 100, 6, endpoint=True)

    # x_all_plot = np.zeros(n_plot * len(t_all_unique))
    # y_all_plot = np.zeros(n_plot * len(t_all_unique))

    delta_x = 0.5
    delta_y = 0.5
    x_plot = np.linspace(x_all.min() - delta_x, x_all.max() + delta_x, 100)
    y_plot = np.linspace(y_all.min() - delta_y, y_all.max() + delta_y, 100)

    X_plot, Y_plot = np.meshgrid(x_plot, y_plot)

    surf_N = griddata((x_all, y_all), t_all, (X_plot, Y_plot), method = "linear", fill_value = np.nan)

    cp = plt.contour(X_plot, Y_plot, surf_N, levels=t_q, colors="r")
    plt.clabel(cp, inline=True, fontsize=8, fmt="%.0f")

    return X_plot, Y_plot, surf_N

def fun_surge_line(m_dot):
    data = np.loadtxt(r".\data\surge_line_comp_map.csv", delimiter=",", skiprows=1)
    x = data[:,0]; y = data[:,1]
    return interp1d(x,y,kind="cubic",fill_value="extrapolate")(m_dot)

def fun_working_line(m_dot, A_exit):
    data = np.loadtxt(r".\data\working_line_comp_map.csv", delimiter=",", skiprows=1)
    x = np.sort(data[:,0]); y = np.sort(data[:,1])
    m_dot = np.array(m_dot)
    w_line = np.zeros_like(m_dot)
    x0 = x[-2]
    coeff = np.polyfit(x[-3:-1], y[-3:-1], 1)
    f_linear = np.poly1d(coeff)
    f_spline = interp1d(x[:-1], y[:-1], kind='cubic', fill_value='extrapolate')
    mask_linear = m_dot > x0
    mask_spline = m_dot <= x0
    w_line[mask_linear] = f_linear(m_dot[mask_linear])/A_exit
    w_line[mask_spline] = f_spline(m_dot[mask_spline])/A_exit
    return w_line

def plot_compressor_map(throttle, A_exit, N, stall, riattaccata_curve=None, blue_point=None):
    wc_plot = np.linspace(12.75, 20, 200)
    surge_line = fun_surge_line(wc_plot)
    working_line = fun_working_line(wc_plot, A_exit)
    # punto operativo
    throttle_min, throttle_max = 84, 100
    alpha = (throttle - throttle_min)/(throttle_max-throttle_min)
    alpha = np.clip(alpha,0,1)
    idx = int(alpha*(len(wc_plot)-1))
    wc_point = wc_plot[idx]
    PR_point = working_line[idx]
    PR_surge_point = fun_surge_line(wc_point)
    margin = PR_surge_point - PR_point

    fig, ax = plt.subplots(figsize=(6,6))
    ax.plot(wc_plot, surge_line, 'r--', label="Surge line")
    ax.plot(wc_plot, working_line, 'orange', label="Working line")
    ax.plot(wc_point, PR_point, 'bo', markersize=8)
    fun_iso_throttle()

    if stall:
        ax.text(13,7,"STALL!",color="red",fontsize=16,weight="bold")
    # curva riattaccata magenta
    if riattaccata_curve is not None:
        ax.plot(riattaccata_curve[:,0], riattaccata_curve[:,1], 'm-', linewidth=2)
    # punto blu che percorre la curva
    if blue_point is not None:
        ax.plot(blue_point[0], blue_point[1], 'bo', markersize=10)

    ax.set_xlabel(r"$\dot m p_1^0/\sqrt{T_1^0}$")
    ax.set_ylabel(r"$\beta_C$")
    ax.set_xlim(wc_plot[0], wc_plot[-1])
    ax.set_ylim(surge_line.min(), surge_line.max())
    ax.legend()
    ax.grid()
    canvas = FigureCanvas(fig)
    canvas.draw()
    raw = canvas.buffer_rgba()
    surf = pygame.image.frombuffer(raw, canvas.get_width_height(), "RGBA")
    plt.close(fig)
    return surf, margin, wc_point, PR_point

# --- Disegna aeroplano ---
def draw_plane(screen, x, y, A_exit):
    plane_img = pygame.Surface((60,20), pygame.SRCALPHA)
    pygame.draw.polygon(plane_img,(100,100,255),[(0,0),(60,10),(0,20)])
    plane_scaled = pygame.transform.scale(plane_img,(int(60*A_exit),20))
    screen.blit(plane_scaled,(x,y))

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
            # start riattaccata
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
    map_surf, margin, wc_point, PR_point = plot_compressor_map(throttle, A_exit, N, stall, riattaccata_curve,
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
