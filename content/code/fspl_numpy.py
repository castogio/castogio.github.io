import matplotlib.pyplot as plt
import numpy as np

P_TX = 30
LAMBDA = 0.06

LOG_PATH_LOSS_CONST = 2 * (np.log10(LAMBDA) - np.log10(2 * np.pi))
print(LOG_PATH_LOSS_CONST)

# reference signal
d = np.arange(.05, 5, .1)
p_rx = P_TX + LOG_PATH_LOSS_CONST - 2 * np.log10(d)
# print(2 * np.log10(d))

plt.plot(d, p_rx, 'r--', label='received power')
plt.grid(linestyle='-', linewidth=2)
plt.legend(loc="upper right")

plt.title("Received power decay due to FSPL")
plt.xlabel("distance [m]")
plt.ylabel("P\N{Latin Subscript Small Letter T}\N{Latin Subscript Small Letter X} [dBm]")

plt.show()