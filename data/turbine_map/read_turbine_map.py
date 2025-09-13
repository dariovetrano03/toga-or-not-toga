import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ----------------------------
# Funzione per leggere tabella a griglia
# ----------------------------
def read_table(file_path):
    df = pd.read_csv(file_path, delim_whitespace=True, header=None)
    col_vals = df.iloc[0, 1:].to_numpy(dtype=float)       # colonne = PR
    row_vals = df.iloc[1:, 0].to_numpy(dtype=float)       # righe = Speed
    central_vals = df.iloc[1:, 1:].to_numpy(dtype=float)  # valori centrali = Mass Flow o Eff
    return col_vals, row_vals, central_vals

# ----------------------------
# Lettura file
# ----------------------------
folder_name = "turbine_map"
base = f"data/{folder_name}"

mf_file  = os.path.join(base, "FRMTD_mass_flow.txt")

beta_mf, speed_mf, mass_flow = read_table(mf_file)

# ----------------------------
# Plot diretto delle curve raw
# ----------------------------
plt.figure(figsize=(10,7))

for i, N in enumerate(speed_mf):
    plt.plot(mass_flow[i, :], beta_mf, marker='o', label=f"N={N:.2f}")

plt.xlabel("Corrected Mass Flow (Wc)")
plt.ylabel("Pressure Ratio (PR)")
plt.title("Turbine Map - Raw Curves (Mass Flow vs PR) at Different N")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
