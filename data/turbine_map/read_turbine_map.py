import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import griddata

# ----------------------------
# Funzione per leggere tabella a griglia
# ----------------------------
def read_table(file_path):
    df = pd.read_csv(file_path, delim_whitespace=True, header=None)
    col_vals = df.iloc[0, 1:].to_numpy(dtype=float)       # colonne = Beta parameter
    row_vals = df.iloc[1:, 0].to_numpy(dtype=float)       # righe = Speed / isoN
    central_vals = df.iloc[1:, 1:].to_numpy(dtype=float)  # valori centrali (Mass Flow o Efficiency)
    return col_vals, row_vals, central_vals

# ----------------------------
# Lettura file Mass Flow / N
# ----------------------------
folder_name = "turbine_map"
base = f"data/{folder_name}"

mf_file = os.path.join(base, "formatted_mass_flow.txt")
beta_mf, speed_mf, mass_flow = read_table(mf_file)

# Conversione beta -> Pressure Ratio reale
PR_min, PR_max = 0, 3.8
PR_real = (PR_max - PR_min) / (beta_mf.max() - beta_mf.min()) * (beta_mf - beta_mf.min()) + PR_min

# ----------------------------
# Lettura file Iso-Efficiency
# ----------------------------
ie_file = os.path.join(base, "formatted_iso_efficiency.txt")
beta_eta, speed_eta, iso_eff = read_table(ie_file)
PR_eta_real = (PR_max - PR_min) / (beta_eta.max() - beta_eta.min()) * (beta_eta - beta_eta.min()) + PR_min

# ----------------------------
# Interpolazione Speed N -> Mass Flow per iso-efficiency
# ----------------------------
points = np.array([(PR_real[j], speed_mf[i]) for i in range(len(speed_mf)) for j in range(len(beta_mf))])
values = mass_flow.flatten()

mass_flow_eta = np.zeros_like(iso_eff)
for i, N in enumerate(speed_eta):
    for j, PR in enumerate(PR_eta_real):
        mass_flow_eta[i, j] = griddata(points, values, (PR, N), method='linear')

# Creiamo meshgrid coerente
MF_grid, PR_grid = np.meshgrid(mass_flow_eta[0,:], PR_eta_real)
iso_eff_sorted = iso_eff.T

# ----------------------------
# Plot combinato
# ----------------------------
plt.figure(figsize=(12,8))

# Iso-efficiency: sfondo colorato + linee nere
levels_eff = np.arange(0.6, 0.95, 0.05)
CF = plt.contourf(MF_grid, PR_grid, iso_eff_sorted, levels=levels_eff, cmap="viridis", alpha=0.8)
plt.colorbar(CF, label="Efficiency")
CS = plt.contour(MF_grid, PR_grid, iso_eff_sorted, levels=levels_eff, colors='k')
plt.clabel(CS, inline=True, fontsize=8, fmt="%.2f")

# Iso-Speed N: linee blu
colors = ["red","green","blue","yellow","orange","purple","pink","brown","gray","black","white","cyan","magenta","lime","teal","navy","maroon","olive","silver","gold"]

for i, N in enumerate(speed_mf):
    plt.plot(mass_flow[i, :], PR_real, color=colors[i] , linestyle='--', label=f"N={N:.2f}")

plt.xlabel("Corrected Mass Flow (Wc)")
plt.ylabel("Pressure Ratio (PR)")
plt.title("Turbine Map - Iso-Speed N & Iso-Efficiency")
plt.grid(True)
plt.legend(title="Iso-Speed N", loc='upper left')
plt.tight_layout()
plt.show()
