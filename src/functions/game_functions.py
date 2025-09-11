import pygame
import numpy as np
import matplotlib.pyplot as plt

from matplotlib.path import Path
import matplotlib.patches as patches

import matplotlib
from scipy.interpolate import interp1d, griddata
# matplotlib.use("Agg")
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import os

import numpy as np

from thermodynamics_functions import calculate_cp, calculate_cp_hot, calculate_T2_tot, calculate_T3_tot, cp_hot0, cp_hot1, cp0, cp1, eta_burner, H_i

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
isStalled = initial_state["stall"]

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

def plot_unsteady_line(steady_point, unsteady_point, ax):
    sx, sy = steady_point
    ux, uy = unsteady_point

    # control points (you can tune these for curvature)
    cx1, cy1 = sx, uy  + 0.64*(uy-sy)
    cx2, cy2 = sx + 0.32*(ux-sx), sy + 0.98*(uy-sy)

    verts = [
        (sx, sy),   # start
        (cx1, cy1), # control point 1
        (cx2, cy2), # control point 2
        (ux, uy)    # end
    ]

    codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
    path = Path(verts, codes)
    patch = patches.PathPatch(path, edgecolor="magenta", facecolor = 'none')
    ax.add_patch(patch)
    
def plot_compressor_map(throttle, A_exit, isStalled, width, height, change_throttle, steady_point0, bg_path = None):
    wc_plot = np.linspace(12.75, 20, 200)
    throttle_min, throttle_max = 84, 100    
    dpi0 = 200
    
    fig, ax = plt.subplots(figsize=(width / dpi0, height / dpi0), dpi = dpi0, layout = 'tight')
    
    if bg_path is None:
        surge_line = fun_surge_line(wc_plot)
       
        ax.plot(wc_plot, surge_line, 'r--', label="Surge line")
       
        # Iso-throttle curves
        fun_iso_throttle()

        canvas = FigureCanvas(fig)
        canvas.draw()
        raw = canvas.buffer_rgba()
        surf = pygame.image.frombuffer(raw, canvas.get_width_height(), "RGBA")

        bg_path = r"img/bg_compressor_map.png"
        pygame.image.save(surf, bg_path)

    ax.axis('off') 

    bg_png = plt.imread(bg_path)  
    ax.imshow(
    bg_png,
    extent=[wc_plot[0], wc_plot[-1], 4, 8.5],  # match compressor map coords
    aspect='auto',
    zorder=0
    )

    working_line = fun_working_line(wc_plot, A_exit)
    ax.plot(wc_plot, working_line, 'orange', label="Working line",  zorder=3)

    if not change_throttle: # condizioni stazionarie 

         # Normalizza throttle (da 84 a 100%)
        alpha = (throttle - throttle_min) / (throttle_max - throttle_min)
        alpha = np.clip(alpha, 0, 1)

        # Trova il punto corrispondente sulla working line
        idx = int(alpha * (len(wc_plot) - 1))
        wc_point = wc_plot[idx]
        PR_point = working_line[idx]
        steady_point0 =  (wc_point, PR_point)
    
    else:
        alpha = (throttle - throttle_min) / (throttle_max - throttle_min)
        alpha = np.clip(alpha, 0, 1)

        # Trova il punto corrispondente sulla working line
        idx = int(alpha * (len(wc_plot) - 1))
        wc_point = wc_plot[idx]
        PR_point = working_line[idx]
        unsteady_point0 = wc_point, PR_point
        ax.plot(*unsteady_point0, 'go',  zorder=3)
        
        plot_unsteady_line(steady_point0, unsteady_point0, ax)
        
    ax.plot(*steady_point0, 'bo', label="Operating point",  zorder=3)

    # Calcolo margine
    PR_surge_point = fun_surge_line(wc_point)
    margin = PR_surge_point - PR_point

    if margin <= 0.5:
        isStalled = True

    if isStalled:
        ax.text(13, 7, "STALL!", color="red", fontsize=16, weight="bold")

    ax.set_xlabel(r"$\dot m \, p_1^0 / \sqrt{T_1^0}$")
    ax.set_ylabel(r"$\beta_C$")
    ax.set_xlim(wc_plot[0], wc_plot[-1])
    ax.set_ylim(4, 8.5)
    # ax.legend()
    ax.grid()

    canvas = FigureCanvas(fig)
    canvas.draw()
    raw = canvas.buffer_rgba()
    surf = pygame.image.frombuffer(raw, canvas.get_width_height(), "RGBA")
    plt.close(fig)

    return surf, isStalled, steady_point0

g = 9.81 # [m/s^2] gravitational acceleration

rho_sl = 1.225 # [kg/m^3] air density

MTOM = 25e3 # [kg] Maximum Take-Off Mass

clalpha = 5 # [1/rad]

cd0 = 0.02 # [1/rad]

AR = 2.8 # [-] Aspect ratio

e_osw = 0.7 # [-] Oswald's factor 

T_sl = 273.15 + 15 # [K] air temperature

gamma = 1.4 # [-] heat capacities ratio of air cp/cv

R = 287 # [J/kg/K] specific gas constant for air 

c_sound = np.sqrt(gamma * R * T_sl) # [m/s] sound speed
 
S_wing = 50 # [m^2] projected wing surface

delta = (gamma - 1) / 2 # [-] dimensionless ratio for calculating total (or stagnation) pressure and temperature
 
p_sl = 101325 # [Pa]

alpha_st = 14.8 # [-] stoichiometric air-to-fuel ratio

AFT = 2200 # [K] Adiabatic Flame Temperature (Equivalence Ratio = 1, Combustion completion = 100 %)

epsilon_burner = 0.95 # [-] Pressure ratio across the main burner

ER = 0.8 # [-] Equivalence ratio = (fuel-to-air ratio)_st / (fuel-to-air ratio) 

""" FLIGHT MECHANICS IMPLEMENTATION """

def acceleration_calculator(M0, beta_c, m_corr, aoa, eta_turb = 0.98, eta_comp = 0.98): # TODO eta_turb from map turbine

    V0 = M0 * c_sound

    T1_tot = T_sl * ( 1 + delta * M0 )
    p1_tot = p_sl * ( 1 + delta * M0 ) ** ( gamma / ( gamma - 1 ) )
    
    T2_tot = calculate_T2_tot(beta_c, T1_tot, eta_comp = eta_comp, gamma = gamma, max_iter = 5, tol = 1e-4)

    # TODO: implement some sort of iteration to calculate alpha0 when T3_tot changes
    #       ...this doesn't converge :( 

    # alpha0 = np.linspace(0, 60, 100)
    # alpha1 = 0    
    # idx_min = 0
    # delta_min = 100

    # for i in range(len(alpha0)):

    #     T3_tot = calculate_T3_tot(T2_tot, alpha0[i])
            
    #     cp_hot = calculate_cp_hot(T3_tot, alpha0[i])

    #     alpha1 = ( eta_burner * H_i / ( T3_tot - T2_tot ) - ( cp_hot0 + cp_hot1 * T3_tot ) * ( 1 + alpha_st ) ) / calculate_cp(T2_tot) 

    #     if alpha1 - alpha0[i] <= delta_min:
    #         delta_min = alpha1 - alpha0[i]
    #         idx_min = i

    T3_tot =  T3_tot = calculate_T3_tot(T2_tot)

    cp_hot = calculate_cp_hot(T3_tot)

    m_dot = m_corr / p1_tot * np.sqrt(T1_tot) 

    w_e = np.sqrt( 2 * eta_turb * cp_hot * T1_tot * ( beta_c ** ( ( gamma - 1 ) / gamma ) - 1 ) ) 

    thrust = m_dot * ( w_e - V0 )

    lift = 0.5 * rho_sl * V0 ** 2 * clalpha * aoa * S_wing
    
    drag = 0.5 * rho_sl * V0 ** 2 * S_wing * (cd0 + (clalpha * aoa) ** 2 / (e_osw * np.pi * AR))

    weight = MTOM * g

    print(f"thrust {thrust:.2e}")
    print(f"drag {drag:.2e}")
    print(f"lift {lift:.2e}")
    print(f"weight {weight:.2e}")

    x_ddot = ( thrust - drag ) / MTOM
    y_ddot = ( lift - weight ) / MTOM

    return x_ddot, y_ddot, m_dot

M0_vec = np.linspace(0, 1, 1000)
thrust_vec = np.zeros_like(M0_vec)

T1_tot_vec = T_sl * ( 1 + delta * M0_vec )
p1_tot_vec = p_sl * ( 1 + delta * M0_vec ) ** ( gamma / ( gamma - 1 ) )



for i, M0 in enumerate(M0_vec):
    acc_x, acc_y, thrust_vec[i] = acceleration_calculator(M0, 9, 1, 3 * np.pi / 180, eta_turb = 0.98, eta_comp = 0.98)
    print(acc_x, acc_y)


plt.figure(figsize = (5,5))

plt.plot(M0_vec, p1_tot_vec / np.sqrt(T1_tot_vec) * (1 - M0_vec))
# plt.savefig("thrust_plot.png", dpi=300)
plt.show()

    