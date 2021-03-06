import matplotlib.pyplot as plt
import sys
#from numba import jit  # wonderful optimization compiler.
import numpy as np  # we can't work in python without that in physics (maybe we can if we are not lazy enough)
import random  # we are doing MC simulation after all!!
import time  # for time estimation
from rich.progress import track  # nice progress bar

# Define parameters 

B = 0  # Magnetic field strength
L = 10  # Lattice size (width)
s = np.random.choice([1, -1], size=(L, L))  # Begin with random spin sites with values (+1 or -1) for up or down spins.
n = 100 * L ** 2  # number of MC sweeps
Temperature = np.arange(1.6, 3.25,
                        0.01)  # Initlaize temperature range (the range includes critical temperature) >
# takes form np.arange(start,stop,step)

'''
Energy of the lattice calculations. 
The energy here is simply the sum of interactions between spins divided by the total number of spins
'''


def calcE(s):
    E = 0
    for i in range(L):
        for j in range(L):
            E += -dE(s, i, j) / 2
    return E / L ** 2


'''
Calculate the Magnetization of a given configuration
Magnetization is the sum of all spins divided by the total number of spins

'''


def calcM(s):
    m = np.abs(s.sum())
    return m / L ** 2


# Calculate interaction energy between spins. Assume periodic boundaries
# Interaction energy will be the difference in energy due to flipping spin i,j 
# (Example: 2*spin_value*neighboring_spins)
def dE(s, i, j):  # change in energy function
    # top
    if i == 0:
        t = s[L - 1, j]  # periodic boundary (top)
    else:
        t = s[i - 1, j]
    # bottom
    if i == L - 1:
        b = s[0, j]  # periodic boundary (bottom)
    else:
        b = s[i + 1, j]
    # left
    if j == 0:
        l = s[i, L - 1]  # periodic boundary (left)
    else:
        l = s[i, j - 1]
    # right
    if j == L - 1:
        r = s[i, 0]  # periodic boundary  (right)
    else:
        r = s[i, j + 1]
    return 2 * s[i, j] * (t + b + r + l)  # difference in energy is i,j is flipped


# Monte-carlo sweep implementation
def mc(s, Temp, n):
    for m in range(n):
        i = random.randrange(L)  # choose random row
        j = random.randrange(L)  # choose random column
        ediff = dE(s, i, j)
        if ediff <= 0:  # if the change in energy is negative
            s[i, j] = -s[i, j]  # accept move and flip spin
        elif random.random() < np.exp(-ediff / Temp):  # if not accept it with probability exp^{-dU/kT}
            s[i, j] = -s[i, j]
    return s


# Compute physical quantities
def physics(s, T, n):
    En = 0
    En_sq = 0
    Mg = 0
    Mg_sq = 0
    for p in range(n):
        s = mc(s, T, 1)
        E = calcE(s)
        M = calcM(s)
        En += E
        Mg += M
        En_sq += E * E
        Mg_sq += M * M
    En_avg = En / n
    mag = Mg / n
    CV = (En_sq / n - (En / n) ** 2) / (T ** 2)
    return En_avg, mag, CV


# Inititalize magnetization, average energy and heat capacity
mag = np.zeros(len(Temperature))
En_avg = np.zeros(len(Temperature))
CV = np.zeros(len(Temperature))

start = time.time()

# Simulate at particular temperatures (T) and compute physical quantities (Energy, heat capacity and magnetization)
for ind, T in enumerate(track(Temperature)):
    # Sweeps spins
    s = mc(s, T, n)
    # Compute physical quanitites with 1000 sweeps per spin at temperature T
    En_avg[ind], mag[ind], CV[ind] = physics(s, T, n)
end = time.time()
print("Time it took in seconds is = %s" % (end - start))

time = (end - start) / 60
print('It took ' + str(time) + ' minutes to execute the code')

# It took about 30 minutes on my Mac meachine (not bad) for n =1000* L^2
# and abput 2 hours for n =2000*L^2 with double T points


# ----------------------------------------------------------------------
#  Plotting area
# ----------------------------------------------------------------------


f = plt.figure(figsize=(18, 10))  # plot the calculated values
sp = f.add_subplot(2, 2, 1)
plt.plot(Temperature, En_avg, marker='.', color='IndianRed')
plt.xlabel("Temperature (T)", fontsize=20)
plt.ylabel("Energy ", fontsize=20)
plt.axis('tight')

sp1 = f.add_subplot(2, 2, 2)
plt.plot(Temperature, abs(mag), marker='.', color='RoyalBlue')
plt.xlabel("Temperature (T)", fontsize=20)
plt.ylabel("Magnetization ", fontsize=20), plt.axis('tight')

sp2 = f.add_subplot(2, 2, 3)
plt.plot(Temperature, CV, marker='.', color='IndianRed')
plt.xlabel("Temperature (T)", fontsize=20)
plt.ylabel("Specific Heat ", fontsize=20)
plt.axis('tight')

plt.subplots_adjust(0.12, 0.11, 0.90, 0.81, 0.26, 0.56)
plt.suptitle("Simulation of 2D Ising Model by Metropolis Algorithm\n" + "Lattice Dimension:" + str(L) + "X" + str(
    L) + "\n" + "External Magnetic Field(B)=" + str(B) + "\n" + "Metropolis Step=" + str(n))


plt.show() # function to show the plots
