import matplotlib.pyplot as plt
import numpy as np

A = 1 # amplitude
T = 6 # period
f = 1/T # carrier frequency

BIT_ONE = 1
BIT_ZERO = -1

PL = 0.5 # path loss

# reference signal
exp_x = np.arange(0, 2 * T, 0.1)
exp_y = A * np.cos(2 * np.pi * f * exp_x)


# # reference vs zero transmitted
received_y1 = BIT_ZERO * A * np.cos(2 * np.pi * f * exp_x)


plt.plot(exp_x, exp_y, 'b--', label='reference cosine')
plt.plot(exp_x, received_y1, 'r', label='received ZERO signal')
plt.grid(linestyle='-', linewidth=2)
plt.legend(loc="upper right")

plt.title("Received ZERO Signal vs. Reference")
plt.xlabel("time")
plt.ylabel("signal level")
plt.show()

# windowed pulse from periodic cosine
extended_x = np.linspace(-T, 2 * T, 100)

p = np.zeros(len(extended_x))
for t in range(len(extended_x)):
    if 0 <= extended_x[t] <= T:
        p[t] = 1

print(extended_x)
print(p)

windowed_signal = A * np.cos(2 * np.pi * f * extended_x) * p
periodic_signal = A * np.cos(2 * np.pi * f * extended_x)


plt.plot(extended_x, periodic_signal, 'g--', label='periodic signal')
plt.plot(extended_x, windowed_signal, 'b', label='windowed signal')
plt.grid(linestyle='-', linewidth=2)
plt.legend(loc="upper right")

plt.title("Signal windowing")
plt.xlabel("time")
plt.ylabel("signal level")
plt.show()


# # received signal
x1, x2 = np.split(exp_x, 2)

y1 = BIT_ONE * PL * A * np.cos(2 * np.pi * f * x1)
y2 = BIT_ZERO * PL * A * np.cos(2 * np.pi * f * x2)

plt.plot(exp_x, exp_y, 'b--', label='reference cosine')
plt.plot(exp_x, np.append(y1, y2), 'r', label='received signal')
plt.grid(linestyle='-', linewidth=2)
plt.legend(loc="upper right")

plt.title("Received Signal (with FSPL) vs. Reference")
plt.xlabel("time")
plt.ylabel("signal level")

plt.show()


# BPSK constellation

plt.title("BPSK constellation (reference)")
plt.axvline(x=0, c="black", linestyle='-', linewidth=1)
plt.axhline(y=0, c="black", linestyle='-', linewidth=1)
plt.plot([BIT_ZERO, BIT_ONE], [0, 0], 'xr', linewidth=6)
plt.xlabel("Real part")
plt.ylim([-0.1, 0.1]);
plt.ylabel("Imaginary part")
plt.grid(linestyle='-', linewidth=1)

plt.show()