import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata, interp1d

# -----------------------------
# Funzione per leggere le tabelle FRMTD_
# -----------------------------
def read_table(file_path):
    df = pd.read_csv(file_path, delim_whitespace=True, header=None)
    col_vals = df.iloc[0,1:].values      # prima riga senza primo valore
    row_vals = df.iloc[1:,0].values      # prima colonna senza primo valore
    central_vals = df.iloc[1:,1:].values # valori centrali
    return col_vals, row_vals, central_vals


folder_name = "compressor_map"

# -----------------------------
# Leggi i file
# -----------------------------
beta_mf, speed_mf, mass_flow_vals = read_table(f"data/{folder_name}/formatted_mass_flow.txt")
beta_ip, speed_ip, iso_press_vals = read_table(f"data/{folder_name}/formatted_iso_pressure_ratio.txt")
beta_ie, speed_ie, iso_eff_vals = read_table(f"data/{folder_name}/formatted_iso_efficiency.txt")
surge_line_df = pd.read_csv(f"data/{folder_name}/formatted_surge_line.txt", delim_whitespace=True, header=None)

# -----------------------------
# Crea array piatti per interpolazione
# -----------------------------
X_vals = mass_flow_vals.flatten()
Y_vals = iso_press_vals.flatten()
Z_eff_vals = iso_eff_vals.flatten()

# -----------------------------
# Griglia regolare per il plot
# -----------------------------
X_unique = np.unique(X_vals)
Y_unique = np.unique(Y_vals)
X_grid, Y_grid = np.meshgrid(X_unique, Y_unique)

# Interpola iso efficiency sulla griglia
Z_eff_grid = griddata((X_vals, Y_vals), Z_eff_vals, (X_grid, Y_grid), method='cubic')

# -----------------------------
# Surge line
# -----------------------------
surge_numbers = surge_line_df.values.flatten()
n = len(surge_numbers)//2
surge_X = surge_numbers[:n]
surge_Y = surge_numbers[n:]
surge_interp = interp1d(surge_X, surge_Y, bounds_error=False, fill_value="extrapolate")
Y_surge_grid = surge_interp(X_grid[0,:])
Y_mask = Y_grid <= Y_surge_grid
Z_eff_masked = np.where(Y_mask, Z_eff_grid, np.nan)

# -----------------------------
# Livelli iso efficiency
# -----------------------------
eff_levels = np.arange(0.6, 0.85+0.001, 0.05)

# -----------------------------
# Plotta iso efficiency
# -----------------------------
plt.figure(figsize=(12,8))
CS_eff = plt.contour(X_grid, Y_grid, Z_eff_masked, levels=eff_levels, colors='blue', linewidths=1.5)
plt.clabel(CS_eff, inline=True, fontsize=8, fmt="%.2f")

# -----------------------------
# Plotta surge line
# -----------------------------
plt.plot(surge_X, surge_Y, 'r--', linewidth=2, label='Surge Line')

# -----------------------------
# Iso numero di giri (prima colonna delle tabelle)
# -----------------------------
iso_n_vals = mass_flow_vals[:,0]  # valori reali dei numeri di giri
Z_n_grid = griddata((X_vals, Y_vals), np.tile(iso_n_vals.reshape(-1,1), (1, mass_flow_vals.shape[1])).flatten(),
                    (X_grid, Y_grid), method='linear')
Z_n_masked = np.where(Y_mask, Z_n_grid, np.nan)
n_levels = np.linspace(iso_n_vals.min(), iso_n_vals.max(), 6)

CS_n = plt.contour(X_grid, Y_grid, Z_n_masked, levels=n_levels, colors='green', linestyles='dashed')
plt.clabel(CS_n, inline=True, fontsize=8, fmt="%.0f")

# -----------------------------
# Labels e grafico finale
# -----------------------------
plt.xlabel("Mass Flow")
plt.ylabel("Iso Pressure Ratio")
plt.title("Compressor Map - Iso Efficiency e Iso Numero di Giri sotto Surge Line")
plt.grid(True)
plt.legend()
plt.show()
