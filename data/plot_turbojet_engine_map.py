import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata, interp1d
from tqdm import tqdm
import csv
from mpl_toolkits.axes_grid1 import make_axes_locatable

# from utils_plot_iso_T3T1 import p_over_pt_from_M, mass_flow_per_area_from_M, M_from_p_over_pt

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))

from src.functions.thermodynamics_functions import (
    calculate_cp, calculate_cp_hot
)


# Constants definition

epsilon_b = 0.96 # [-] Combustor pressure ratio TODO: implement combustor map

epsilon_d = 0.97 # [-] Air intake pressure ratio TODO: implement air intake map

M0 = 0.75 # [-] Assumed aircraft Mach number (actually is an input from the game)

gamma_air = 1.4 # [-] Air specific heat ratio cp/cv

gamma_hot = 1.33 # [-] Exhaust gases specific heat ratio cp/cv

alpha0 = 40 # [-] Air-to-fuel ratio first guess

eff_mech_comp = 0.95
eff_mech_turb = 0.95


def read_table(file_path):
    df = pd.read_csv(file_path, delim_whitespace=True, header=None)  # keep old style
    col_vals = df.iloc[0,1:].values
    row_vals = df.iloc[1:,0].values
    central_vals = df.iloc[1:,1:].values
    return col_vals, row_vals, central_vals

folder = "compressor_map"

# the beta and the speed are sampled at the same points for mass flow, pressure ratios, and iso-efficiencies
beta_comp, speed_comp, mf_comp = read_table(f"{folder}/formatted_mass_flow.txt")
_, _, pr_comp = read_table(f"{folder}/formatted_iso_pressure_ratio.txt")
_, _, eff_comp = read_table(f"{folder}/formatted_iso_efficiency.txt")

surge_df = pd.read_csv(f"{folder}/formatted_surge_line.txt", delim_whitespace=True, header=None)


# -----------------------------
# Flatten arrays for interpolation
# -----------------------------
n_rows, n_cols = len(speed_comp), mf_comp.shape[1]

# Matrices:
mf_flat_comp = mf_comp.flatten()
eff_flat_comp = eff_comp.flatten()
pr_flat_comp = pr_comp.flatten()

# Vector:
speed_flat_comp = np.repeat(speed_comp, n_cols)   # repeat speed along columns

num_steps = 100

mf_grid_comp, pr_grid_comp = np.meshgrid(
    np.linspace(mf_flat_comp.min(), mf_flat_comp.max(), num_steps),
    np.linspace(pr_flat_comp.min(), pr_flat_comp.max(), num_steps)
)


# -----------------------------
# Interpolation on grid
# -----------------------------
eff_grid_comp = griddata((mf_flat_comp, pr_flat_comp), eff_flat_comp, (mf_grid_comp, pr_grid_comp), method='cubic')
speed_grid_comp = griddata((mf_flat_comp, pr_flat_comp), speed_flat_comp, (mf_grid_comp, pr_grid_comp), method='cubic')

# -----------------------------
# Surge line mask
# -----------------------------
surge_vals = surge_df.values.flatten()
n = len(surge_vals)//2
surge_mf, surge_pr = surge_vals[:n], surge_vals[n:]
surge_interp = interp1d(surge_pr, surge_mf, bounds_error=False, fill_value="extrapolate")
mf_grid_surge = surge_interp(pr_grid_comp[:, 0])
mf_grid_mask = mf_grid_comp <= mf_grid_surge[np.newaxis, :]   # broadcast mask

# Apply mask
eff_grid_mask_comp = np.where(mf_grid_mask, eff_grid_comp, np.nan)
speed_grid_mask_comp = np.where(mf_grid_mask, speed_grid_comp, np.nan)


mf_grid_comp_preopt = np.zeros((len(speed_comp), num_steps), dtype = np.float64)
pr_grid_comp_preopt = np.zeros((len(speed_comp), num_steps), dtype  = np.float64)
eff_grid_comp_preopt = np.zeros((len(speed_comp), num_steps), dtype = np.float64)

N_comp_levels = np.linspace(speed_comp.min(), speed_comp.max(), len(speed_comp))

for i, N in enumerate(N_comp_levels):
    mf_grid_comp_N = np.where(np.isclose(speed_grid_mask_comp, N, atol = 1e-2, rtol = 1e-5), mf_grid_comp, np.nan)
    pr_grid_comp_N = np.where(np.isclose(speed_grid_mask_comp, N, atol = 1e-2, rtol = 1e-5), pr_grid_comp, np.nan)
    eff_grid_comp_N = np.where(np.isclose(speed_grid_mask_comp, N, atol = 1e-2, rtol = 1e-5), eff_grid_comp, np.nan)

    mask_valid = ~np.isnan(pr_grid_comp_N)
    mf_vals_comp_N = mf_grid_comp_N[mask_valid]
    pr_vals_comp_N = pr_grid_comp_N[mask_valid]
    eff_vals_comp_N = eff_grid_comp_N[mask_valid]

    sort_idx = np.argsort(pr_vals_comp_N) 
    pr_sorted = pr_vals_comp_N[sort_idx]
    mf_sorted = mf_vals_comp_N[sort_idx]
    eff_sorted = eff_vals_comp_N[sort_idx]

    pr_sorted, unique_idx = np.unique(pr_sorted, return_index=True)
    mf_sorted = mf_sorted[unique_idx]
    eff_sorted = eff_vals_comp_N[unique_idx]
    
    pr_uniform = np.linspace(pr_sorted.min(), pr_sorted.max(), num_steps)
  
    mf_interp = interp1d(pr_sorted, mf_sorted, kind='linear', fill_value="extrapolate")
    eff_interp = interp1d(pr_sorted, eff_sorted, kind='linear', fill_value="extrapolate")
    
    x_data = pr_uniform
    y_data = mf_interp(pr_uniform)
    z_data = eff_interp(pr_uniform)
    
    degree = 2
    coeffs_mf = np.polyfit(x_data, y_data, degree)
    coeffs_eff = np.polyfit(x_data, z_data, degree)

    mf_grid_comp_preopt[i,:] = np.polyval(coeffs_mf, x_data)
    eff_grid_comp_preopt[i, :] = np.polyval(coeffs_eff, x_data)

    pr_grid_comp_preopt[i,:] = pr_uniform

N_comp_num_steps = 150

pr_dense_comp = np.linspace(pr_comp.min(), pr_comp.max(), num_steps)

speed_dense_comp = np.linspace(speed_comp.min(), speed_comp.max(), N_comp_num_steps)
pr_grid_comp_opt = np.tile(pr_dense_comp, (N_comp_num_steps, 1))                                                 
mf_grid_comp_opt = np.zeros_like(pr_grid_comp_opt)

eff_grid_comp_opt = np.zeros_like(pr_grid_comp_opt)

for j, isoPR in enumerate(pr_dense_comp):

    mf_isoPR = mf_grid_comp_preopt[:, j]
    mf_interpolator_comp = interp1d(speed_comp, mf_isoPR, kind = 'cubic', fill_value="extrapolate")
    mf_grid_comp_opt[:, j] = mf_interpolator_comp(speed_dense_comp)

    eff_isoPR = eff_grid_comp_preopt[:, j]
    eff_interpolator_comp = interp1d(speed_comp, eff_isoPR, kind = 'cubic', fill_value="extrapolate")
    eff_grid_comp_opt[:, j] = eff_interpolator_comp(speed_dense_comp)

speed_grid_comp_opt = np.tile(speed_dense_comp, (num_steps, 1)).T

X_grid_surge = surge_interp(pr_dense_comp)
X_grid_mask = mf_grid_comp_opt >= X_grid_surge[np.newaxis, :]   # broadcast mask

eff_grid_comp_opt = np.where(X_grid_mask, eff_grid_comp_opt, np.nan)
speed_grid_comp_opt = np.where(X_grid_mask, speed_grid_comp_opt, np.nan)
mf_grid_comp_opt =  np.where(X_grid_mask, mf_grid_comp_opt, np.nan)

#########################################

folder = "turbine_map"

# -----------------------------
# Read turbine mass flow
# -----------------------------
beta_turb, speed_turb, mf_turb = read_table(f"{folder}/formatted_mass_flow.txt")
_, _, eff_turb = read_table(f"{folder}/formatted_iso_efficiency.txt")

#######################################################################################

# Pressure ratio mapping (simple linear scaling, see cell below)    
pr_turb_min, pr_turb_max = 1.01, 3.8
pr_turb = np.linspace(pr_turb_min, pr_turb_max, len(beta_turb))

pr_dense_turb = np.linspace(pr_turb_min, pr_turb_max, num_steps)
pr_grid_turb_preopt = np.tile(pr_dense_turb, (len(speed_turb), 1))                                                 

mf_grid_turb_preopt = np.zeros_like(pr_grid_turb_preopt)
eff_grid_turb_preopt = np.zeros_like(pr_grid_turb_preopt)


for i, isoN in enumerate(speed_turb):
    mf_isoN = mf_turb[i, :]
    mf_interpolator_turb = interp1d(pr_turb, mf_isoN, kind = 'cubic')
    mf_grid_turb_preopt[i, :] = mf_interpolator_turb(pr_dense_turb)

    eff = eff_turb[i, :]
    eff_interpolator_turb = interp1d(pr_turb, eff_turb[i, :], kind = 'cubic')
    eff_grid_turb_preopt[i, :] = eff_interpolator_turb(pr_dense_turb)

#####################################################################################

N_turb_num_steps = 150

# speed_dense_turb = np.linspace(speed_turb.min(), speed_turb.max(), N_turb_num_steps)

speed_dense_turb = np.linspace(0.05, 2, N_turb_num_steps)


pr_grid_turb_opt = np.tile(pr_dense_turb, (N_turb_num_steps, 1))                                                 
mf_grid_turb_opt = np.zeros_like(pr_grid_turb_opt)

eff_grid_turb_opt = np.zeros_like(pr_grid_turb_opt)

for j, isoPR in enumerate(pr_dense_turb):

    mf_isoPR = mf_grid_turb_preopt[:, j]
    mf_interpolator_turb = interp1d(speed_turb, mf_isoPR, kind = 'nearest', fill_value="extrapolate")
    mf_grid_turb_opt[:, j] = mf_interpolator_turb(speed_dense_turb)

    eff_isoPR = eff_grid_turb_preopt[:, j]
    eff_interpolator_turb = interp1d(speed_turb, eff_isoPR, kind = 'nearest', fill_value="extrapolate")
    eff_grid_turb_opt[:, j] = eff_interpolator_turb(speed_dense_turb)


speed_grid_turb_opt = np.tile(speed_dense_turb, (num_steps, 1)).T


# Compressor map pre-processing

indices_comp = np.argwhere(~np.isnan(mf_grid_comp_opt))

# Pre-allocation of the output parameters
best_temp_ratios = np.full(mf_grid_comp_opt.shape, np.nan)
best_differences = np.full(mf_grid_comp_opt.shape, np.nan)

total_points = len(indices_comp)

differences = []
temp_ratios_list = []

T_amb = 288 # [K] ambient temperature
Tt1 = T_amb * ( 1 + (gamma_air - 1) / 2 * M0 ** 2 ) 
cp_air = calculate_cp(Tt1)

temp_ratios = np.arange(1.01, 27, 1)
sqrt_temp_ratios = np.sqrt(temp_ratios)

p_ref = 101325
T_ref = 288.15

pt1 = p_ref

for count, (i, j) in tqdm(enumerate(indices_comp, start=1), desc = "Processing", total=total_points, leave = True): # i = Compressor N_corr, j = Compressor PR
# for count, (i, j) in enumerate(valid_indices[500:600], start=1):

    # print(f"Processing point {count}/{total_points} -> index (i={i}, j={j})")

    differences = []
    temp_ratios_list = []

    mf_cons_comp = mf_grid_comp_opt[i, j]
    pr_cons_comp = pr_grid_comp_opt[i, j]
    speed_cons_comp = speed_dense_comp[i] 
    eff_cons_comp = eff_grid_comp_opt[i, j]   

    mf_true_arr = mf_cons_comp * pt1 / p_ref / sqrt_temp_ratios * np.sqrt(T_ref)

    mf_cons_turb_arr = mf_cons_comp / pr_cons_comp / epsilon_b * sqrt_temp_ratios

    N_cons_turb_arr =  speed_cons_comp / sqrt_temp_ratios

    LHS_power_eq = cp_air * Tt1 / eff_cons_comp / eff_mech_comp * (pr_cons_comp ** ((gamma_air - 1) / gamma_air) - 1)

    found_within_tolerance = False

    for temp_ratio, mf_cons_turb, N_cons_turb in zip(temp_ratios, mf_cons_turb_arr, N_cons_turb_arr):

        failed = []

        if N_cons_turb < speed_dense_turb.min():
            failed.append("N_cons_turb below min(speed_dense_turb)")
        if N_cons_turb > speed_dense_turb.max():
            failed.append("N_cons_turb above max(speed_turb)")
        if mf_cons_turb < mf_turb.min():
            failed.append("mf_cons_turb below min(mf_turb)")
        if mf_cons_turb > mf_turb.max():
            failed.append("mf_cons_turb above max(mf_turb)")

        if failed:
            # print("Failed conditions:", ", ".join(failed))
            differences.append(np.nan)
            temp_ratios_list.append(np.nan)
            
        else:
            # print(f"mf_cons_turbnozz: {mf_cons_turbnozz}")
            # print(f"N_cons_turbnozz: {N_cons_turbnozz}")

            # now we have to find where these mf and N are on the turbine map
            idx_min_N = np.nanargmin(np.abs(N_cons_turb - speed_dense_turb)) # u
            idx_min_mf = np.nanargmin(np.abs(mf_grid_turb_opt[idx_min_N, :] - mf_cons_turb)) # v

            # print(f" Desired value: {N_cons_turb}, Available value: {speed_dense_turb[idx_min_N]}")
            # print(f" Desired value: {mf_cons_turb}, Available value: {mf_grid_turb_opt[idx_min_N, idx_min_mf]}")

            eff_cons_turb = eff_grid_turb_opt[idx_min_N, idx_min_mf]
            pr_cons_turb = pr_grid_turb_opt[idx_min_N, idx_min_mf]
            
            # print(pr_cons_turb)

            Tt3 = Tt1 * temp_ratio

            cp_hot = calculate_cp_hot(Tt3, alpha = alpha0)
            
            # Calculate RHS and LHS of the pressure congruence equation
            # LHS_pressure_eq = ((1 + (gamma - 1) / 2 * M0 ** 2) ** (gamma / (gamma - 1))) * epsilon_d * pr_grid_comp_opt[i, j]
            # RHS_pressure_eq =  pr_grid_turbnozz[idx_min_N, idx_min_mf] / epsilon_b
            # differences.append(abs(LHS_pressure_eq - RHS_pressure_eq))

            # Calculate RHS and LHS of the power congruence equation
            RHS_power_eq = (1 + alpha0) / alpha0 * eff_cons_turb * eff_mech_turb * cp_hot * Tt3 * (1 - pr_cons_turb ** ((1 - gamma_hot) / gamma_hot)) 
            
            rel_diff = abs(LHS_power_eq - RHS_power_eq) / abs(LHS_power_eq) * 100
            differences.append(rel_diff)
            temp_ratios_list.append(temp_ratio)

            if rel_diff < 5.0:  # within 1% tolerance
                best_temp_ratios[i, j] = temp_ratio
                best_differences[i, j] = rel_diff
                found_within_tolerance = True
                break  # skip to next (i, j)
        
    if not found_within_tolerance:
        try:
            
            idx_best_temp_ratio = np.nanargmin(differences)
            if differences[idx_best_temp_ratio] <= 100.0:
                best_temp_ratios[i, j] = temp_ratios_list[idx_best_temp_ratio]
                best_differences[i, j] = differences[idx_best_temp_ratio] # store the difference between LHS and RHS to eventually add constraint on the tolerance 
            else:
                best_temp_ratios[i, j] = np.nan
                best_differences[i, j] = np.nan
        except ValueError:
            best_temp_ratios[i, j] = np.nan
            best_differences[i, j] = np.nan

with open('surge_line_comp_map.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['mf', 'pr'])  # intestazione
    for mf, pr in zip(surge_mf, surge_pr):
        writer.writerow([mf, pr])

#############################################################################################

throttle_levels = np.unique(speed_grid_comp_opt)

print(throttle_levels.shape)

targets = np.arange(0.4, 1, 0.1)

indices = np.nanargmin(np.abs(throttle_levels[:, None] - targets), axis = 0)
throttle_levels = throttle_levels[indices]

throttle_list = []
x_list = []
y_list = []

for level in throttle_levels:
    CS = plt.contour(mf_grid_comp_opt, pr_grid_comp_opt, speed_grid_comp_opt, levels=[level])
    # CS.allsegs is a list of lists: allsegs[0] corresponds to level[0]
    for seg in CS.allsegs[0]:
        mf_vals = seg[:, 0]
        pr_vals = seg[:, 1]
        throttle_list.extend([level] * len(mf_vals))
        x_list.extend(mf_vals)
        y_list.extend(pr_vals)

plt.close()

with open('iso_throttle_comp_map.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['throttle','x','y'])
    for t, x, y in zip(throttle_list, x_list, y_list):
        writer.writerow([t, x, y])

    #############################################################################################

    fig, axes = plt.subplots(1, 1, figsize=(10, 6))

# Contour plots
cont_T = axes.contour(mf_grid_comp_opt, pr_grid_comp_opt, np.sqrt(best_temp_ratios),
                      levels=15, cmap='Wistia', vmax=10)
cont_N = axes.contour(mf_grid_comp_opt, pr_grid_comp_opt, speed_grid_comp_opt * 100,
                      levels=10, cmap='winter')
cont_eff = axes.contourf(mf_grid_comp_opt, pr_grid_comp_opt, eff_grid_comp_opt,
                         levels=100, cmap='Reds')

# Divider for colorbar placement
divider = make_axes_locatable(axes)

divider = make_axes_locatable(axes)

cax1 = divider.append_axes("right", size="2%", pad=0.2)   # first cbar
cax2 = divider.append_axes("right", size="2%", pad=0.6)   # second, relative to ax
cax3 = divider.append_axes("right", size="2%", pad=1.0)   # third, relative to ax

fig.colorbar(cont_T, cax=cax1, label=r'$T_3^0 / T_1^0$')
fig.colorbar(cont_N, cax=cax2, label=r'$\frac{N / N_{ref}}{\sqrt{\theta_1}}$')
fig.colorbar(cont_eff, cax=cax3, label=r'$\eta_c$')


fig.colorbar(cont_T, cax=cax1, label=r'$T_3^0 / T_1^0$ [-]')
fig.colorbar(cont_N, cax=cax2, label=r'$\frac{N / N_{ref}}{\sqrt{\theta_1}}$ [%]')
fig.colorbar(cont_eff, cax=cax3, label=r'$\eta_c$ [-]')

# Rest of your plot
axes.plot(surge_mf, surge_pr, 'k--', linewidth=2, label='Surge Line')
axes.legend()
axes.set_ylabel(r'PR compressor $\beta_c$ [-]')
axes.set_xlabel(r'Corrected Mass Flow $\dot m \frac{\sqrt{\theta_1}}{\delta_1}$ [kg/s]')
axes.set_title(r'Turbojet map')
axes.grid()

plt.tight_layout()
plt.savefig("engine_map_plot.png", bbox_inches="tight") 

plt.show()