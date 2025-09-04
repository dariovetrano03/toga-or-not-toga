import pygame
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from scipy.interpolate import interp1d, griddata
matplotlib.use("Agg")
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import os

plt.rcParams.update({'font.size': 6})
plt.rcParams.update({'lines.linewidth': 1})
plt.rcParams.update({'contour.linewidth': 1})
plt.rcParams.update({'lines.markersize': 4})

current_dir = os.getcwd()
parent_dir = os.path.dirname(current_dir)

# Stato iniziale
initial_state = {
    "throttle_0": 89,
    "wc_0": 17,
    "beta_c_0": 5.5, 
    "A_exit": 1,
    "N": 0.5,      # velocità normalizzata
    "score": 0,
    "stall": False
}

wc_0 = initial_state["wc_0"]
throttle = initial_state["throttle_0"]
A_exit = initial_state["A_exit"]
N = initial_state["N"]
score = initial_state["score"]
stall = initial_state["stall"]

def fun_surge_line(m_dot):
    data = np.loadtxt(r".\data\surge_line_comp_map.csv", delimiter=",", skiprows=1)
    x = data[:,0]
    y = data[:,1]
    f_surge = interp1d(x, y, kind='cubic', fill_value="extrapolate") 
    return f_surge(m_dot)


def fun_working_line(m_dot : np.array, A_exit):
    """Linea operativa richiesta: funzione di throttle e Ae"""
    
    data = np.loadtxt(r".\data\working_line_comp_map.csv", delimiter=",", skiprows=1)
    x = np.sort(data[:,0])
    y = np.sort(data[:,1])

    m_dot = np.array(m_dot)
    working_line = np.zeros_like(m_dot)
    x0 = x[-2]

    coeff = np.polyfit(x[-3:-1], y[-3:-1], 1)

    f_linear = np.poly1d(coeff)
    f_spline = interp1d(x[:-1], y[:-1], kind='cubic', fill_value="extrapolate")

    mask_linear = m_dot > x0
    mask_spline = m_dot <= x0

    working_line[mask_linear] = f_linear(m_dot[mask_linear]) / A_exit
    working_line[mask_spline] = f_spline(m_dot[mask_spline]) / A_exit

    return working_line

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
    plt.clabel(cp, inline=True, fontsize=4, fmt="%.0f")

    return X_plot, Y_plot, surf_N

# --- Funzione per plottare con matplotlib ---
def plot_compressor_map(throttle, A_exit, stall, width, height):
    wc_plot = np.linspace(12.75, 20, 200)

    surge_line = fun_surge_line(wc_plot)
    working_line = fun_working_line(wc_plot, A_exit)

    # Normalizza throttle (da 84 a 100%)
    throttle_min, throttle_max = 84, 100
    alpha = (throttle - throttle_min) / (throttle_max - throttle_min)
    alpha = np.clip(alpha, 0, 1)

    # Trova il punto corrispondente sulla working line
    idx = int(alpha * (len(wc_plot) - 1))
    wc_point = wc_plot[idx]
    PR_point = working_line[idx]

    # Calcolo margine
    PR_surge_point = fun_surge_line(wc_point)
    margin = PR_surge_point - PR_point

    fig, ax = plt.subplots(figsize=(width / 200, height / 200), dpi = 200, layout = 'tight')
    ax.plot(wc_plot, surge_line, 'r--', label="Surge line")
    ax.plot(wc_plot, working_line, 'orange', label="Working line")

    # Iso-throttle curves
    fun_iso_throttle()

    # Punto operativo
    ax.plot(wc_point, PR_point, 'bo', label="Operating point")
    # ax.text(wc_point+0.05, PR_point, f"Margin={margin:.2f}", fontsize=10)

    if stall:
        ax.text(13, 7, "STALL!", color="red", fontsize=16, weight="bold")

    ax.set_xlabel(r"$\dot m \, p_1^0 / \sqrt{T_1^0}$")
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

    return surf, margin

    
# def plot_compressor_map(throttle, A_exit, stall, riattaccata_curve=None, blue_point=None):
#     wc_plot = np.linspace(12.75, 20, 200)
#     surge_line = fun_surge_line(wc_plot)
#     working_line = fun_working_line(wc_plot, A_exit)
#     # punto operativo
#     throttle_min, throttle_max = 84, 100
#     alpha = (throttle - throttle_min)/(throttle_max-throttle_min)
#     alpha = np.clip(alpha,0,1)
#     idx = int(alpha*(len(wc_plot)-1))
#     wc_point = wc_plot[idx]
#     PR_point = working_line[idx]
#     PR_surge_point = fun_surge_line(wc_point)
#     margin = PR_surge_point - PR_point

#     fig, ax = plt.subplots(figsize=(6,6))
#     ax.plot(wc_plot, surge_line, 'r--', label="Surge line")
#     ax.plot(wc_plot, working_line, 'orange', label="Working line")
#     ax.plot(wc_point, PR_point, 'bo', markersize=8)
#     fun_iso_throttle()

#     if stall:
#         ax.text(13,7,"STALL!",color="red",fontsize=16,weight="bold")
#     # curva riattaccata magenta
#     if riattaccata_curve is not None:
#         ax.plot(riattaccata_curve[:,0], riattaccata_curve[:,1], 'm-', linewidth=2)
#     # punto blu che percorre la curva
#     if blue_point is not None:
#         ax.plot(blue_point[0], blue_point[1], 'bo', markersize=10)

#     ax.set_xlabel(r"$\dot m p_1^0/\sqrt{T_1^0}$")
#     ax.set_ylabel(r"$\beta_C$")
#     ax.set_xlim(wc_plot[0], wc_plot[-1])
#     ax.set_ylim(surge_line.min(), surge_line.max())
#     ax.legend()
#     ax.grid()
#     canvas = FigureCanvas(fig)
#     canvas.draw()
#     raw = canvas.buffer_rgba()
#     surf = pygame.image.frombuffer(raw, canvas.get_width_height(), "RGBA")
#     plt.close(fig)
#     return surf, margin, wc_point, PR_point