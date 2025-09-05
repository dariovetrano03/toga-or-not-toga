import numpy as np

import matplotlib.pyplot as plt
import matplotlib

gamma = 1.4

M1 = np.linspace(0.01, 4, 1000)

sonic_idx = np.argmin(np.abs(M1 - 1))

idx1 = int(sonic_idx / 2)

print(idx1)
M2 = np.sqrt( (1 + (gamma - 1) / 2 * M1**2) / (gamma * M1**2 - (gamma - 1) / 2))

f_mach = np.sqrt(gamma) * M1 * (1 + (gamma - 1) / 2 * M1**2) ** (- ((gamma + 1 )/ 2 / ( gamma - 1 )))

term1 = ((gamma + 1) * M1**2) / ((gamma - 1) * M1**2 + 2)
term2 = ( (gamma + 1) / (2 * gamma * M1**2 - (gamma - 1)) )

epsilon_d = term1**(gamma/(gamma-1)) * term2**(1/(gamma-1))


plt.figure(figsize=(5,5))
plt.plot(M1, f_mach)
plt.plot(M1[sonic_idx:], f_mach[sonic_idx:] / epsilon_d[sonic_idx:])
plt.axvline(x=M1[idx1], color='r', linestyle='--', label="M1")
plt.axvline(x=M2[idx1], color='r', linestyle='--', label="M2")
plt.axhline(y = f_mach[idx1])
plt.show()