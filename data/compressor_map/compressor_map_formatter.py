import pandas as pd
import numpy as np

# ---------------------------
# 1️⃣ Leggi il file
# ---------------------------
file_path = "data/compressor_map/iso_pressure_ratio.txt"
df = pd.read_csv(file_path, delim_whitespace=True, header=None, skiprows = 1)

# Estrai le due righe di header
header_row1 = df.iloc[0].values
header_row2 = df.iloc[1].values

# Prendi tutte le righe dei dati (da riga 3 in poi)
data_raw = df.iloc[2:].reset_index(drop=True)

# ---------------------------
# 2️⃣ Suddividi righe dispari e pari
# ---------------------------
rows_dispari = data_raw.iloc[0::2].reset_index(drop=True)
rows_pari = data_raw.iloc[1::2].reset_index(drop=True)

# ---------------------------
# 3️⃣ Alterna righe dispari e pari
# ---------------------------
combined_rows = []
for i in range(max(len(rows_dispari), len(rows_pari))):
    if i < len(rows_dispari):
        combined_rows.append(rows_dispari.iloc[i].values)
    if i < len(rows_pari):
        combined_rows.append(rows_pari.iloc[i].values)

# ---------------------------
# 4️⃣ Ricostruisci rettangolo con un numero fisso di colonne
# ---------------------------
n_cols = 10  # numero di colonne desiderate
flat_data = np.array(combined_rows).flatten()
n_rows = int(np.ceil(len(flat_data) / n_cols))

# Riempie solo l’ultimo slot con NaN se necessario
flat_data = np.pad(flat_data, (0, n_rows*n_cols - len(flat_data)), constant_values=np.nan)
rect_data = flat_data.reshape((n_rows, n_cols))

# ---------------------------
# 5️⃣ Prepara header affiancato sopra
# ---------------------------
# Prendi metà colonne da header_row1 e metà da header_row2 per allinearle alle 10 colonne
split = n_cols // 2
header_combined = np.concatenate([header_row1[:split], header_row2[:split]]).reshape(1, n_cols)

# Combina header e dati
final_array = np.vstack([header_combined, rect_data])

# ---------------------------
# 6️⃣ Converti in DataFrame e stampa
# ---------------------------
final_df = pd.DataFrame(final_array)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
print(final_df)


output_file = "data/compressor_map/FRMTD_iso_pressure_ratio.txt"
final_df.to_csv(output_file, sep='\t', index=False, header=False)

print(f"Tabella salvata in {output_file}")

