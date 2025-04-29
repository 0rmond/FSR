import finesse
from finesse import Model
from finesse.components import Laser, Mirror, Space, Beamsplitter, Modulator
from finesse.detectors import PowerDetector
from finesse.analysis.actions import Xaxis, Series, Change

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from scipy.constants import c as light_speed

finesse.configure(plotting=True)
M = Model()

# Two lasers, one for locking. You can change this to 775nm if you wish #
# NOTE: I have set the f so that we are at the correct wavelength #

lambda_1550 = 1550e-9
lambda_1548 = 1548e-9
L1550, L1548 = [
    Laser("L1550", P=100e-6, f=(light_speed)/(lambda_1550)),
    Laser("L1548", P=0, f=(light_speed)/(lambda_1548)) #right now I have P=0 because I don't care about it.
]

# bs1 overlaps the two lasers, bs2 is to tap off some of the input and reflected signal #
bs1, bs2 = [
    Beamsplitter("bs1", R=0.5, T=0.5),
    Beamsplitter("bs2", R=0.1, T=0.9),
]

# input mirror #
input_mirror_r = 0.99
input_mirror_t = 1 - input_mirror_r
input_mirror_Rc = 1 # in metres

# output mirror #
output_mirror_r = 0.99
output_mirror_t = 1 - output_mirror_r
output_mirror_Rc = 1 # in metres

m1, m2 = [
    Mirror("m1", R=input_mirror_r, T=input_mirror_t, Rc=input_mirror_Rc),
    Mirror("m2", R=output_mirror_r, T=output_mirror_t, Rc=output_mirror_Rc),
]

# for locking #
eom = Modulator("eom", 100e6, 10)

M.add([L1550, L1548, eom, bs1, bs2, m1, m2,])

cavity_length = 0.15
# You will probably need to adjust the lengths if you care about modelling transverse modes #
spaces = [
    Space("L1550_bs1", portA=L1550.p1, portB=bs1.p1, L=1),
    Space("L1548_bs1", portA=L1548.p1, portB=bs1.p4, L=1),
    Space("bs1_eom", portA=bs1.p3, portB=eom.p1, L=0.5),
    Space("eom_bs2", portA=eom.p2, portB=bs2.p1, L=0.5),
    Space("bs1_bs2", portA=bs1.p3, portB=bs2.p1, L=1),
    Space("bs2_m1", portA=bs2.p3, portB=m1.p1, L=1),
    Space("m1_m2", portA=m1.p2, portB=m2.p1, L=0.3),
]

M.add([*spaces])

# I would recommend you check the documentation on the BS object to see what ports are input and output ports #
detectors = [
    PowerDetector("init", bs2.p2.o),
    PowerDetector("refl", bs2.p4.o),
    PowerDetector("circ", m2.p1.i),
    PowerDetector("trans", m2.p2.o),
]

M.add(detectors)

print(M.component_tree(show_detectors=True)) # check if anything is broken :/

# create a Series if you are interested in changing more than one thing #
sweep_phi = Xaxis("m1.phi", "lin", -180, 180, 10_000)
series_of_sols = Series(
    sweep_phi,
)


sols = M.run(series_of_sols)

f,a = plt.subplots()
# adjust the list to below to change what you want to see #
detectors_to_view = ["init", "refl", "circ", "trans"]
for det in detectors_to_view:
    xs = sols.x[0]
    ys = sols[det]
    a.plot(xs, ys, label=det)

a.set_xlabel("Phase Angle, degrees", fontsize=20)
a.set_ylabel("Normalised Power", fontsize=20)
plt.legend()
plt.tick_params(labelsize=16)

plt.show()

# NOTE: UNCOMMENT (and maybe fix!) IF YOU ARE INTERESTED IN LOOKING AT THE PDH SIGNAL
"""
pdh_phase = []
for phase in np.linspace(0, 90, endpoint=True, num=9):
    pdh_phase.append(f"pdh{phase:.0f}")
    M.parse(f"pd1 pdh{phase:.0f} node=m1.p1.o f=eom.f phase={phase:.0f}")

sol = M.run(sweep_phi)
fig, axs = plt.subplots()
axs.plot(sol.x[0], sol["circ"])
axs.set_xlabel("Phase Angle, degrees", fontsize=20)
axs.set_ylabel("Power, W", fontsize=20)
plt.suptitle("Circulating light in a 30cm optical cavity \n with two frequencies at 1550nm and 1548nm", fontsize=22)
plt.show()
"""

