import numpy as np
import matplotlib.pyplot as plt
from finesse import Model
from finesse.components import Laser
from scipy.constants import c as light_speed

import tomllib
with open("inventory.toml", "rb") as f:
    data = tomllib.load(f)
mirrors = data["mirrors"]

import setup

r_775_AR = (0.5542967916 + 0.7906019092)/2/100
t_775_AR = 1 - r_775_AR
r_775_SR = (73.6692276 + 73.37778473)/2/100
t_775_SR = 1 - r_775_SR


r_1550_AR = (0.03732781857 + 0.01831459068)/2/100
t_1550_AR = 1 - r_1550_AR
t_1550_SR = (0.01168449409 + 0.01315236464)/2/100
r_1550_SR = 1 - t_1550_SR

mirror_1550_props = {
    "input_r": mirrors["newport"]["1550"]["AR"]["r"],
    "input_t": mirrors["newport"]["1550"]["AR"]["t"],
    "input_Rc": -1,
    "output_r": 0.99,#r_1550_SR,
    "output_t": 0.01,#t_1550_SR,
    "output_Rc": np.inf,
}

mirror_775_props = {
    "input_r": r_775_SR,
    "input_t": t_775_SR,
    "input_Rc": -1,
    "output_r": 0.97,#r_775_SR,
    "output_t": 0.03,#t_775_SR,
    "output_Rc": np.inf,
}

print(mirror_775_props)
distances = {
    "to_mirror": 0,
    "mi_mo": 25e-3,
}
f_1550 = light_speed/1550e-9
f_775 = light_speed/775e-9

M_775 = Model()
M_1550 = Model()

M_775.add(Laser("source", P=1, f=f_775))
M_1550.add(Laser("source", P=1, f=f_1550))

cavity_775 = setup.add_basic_cavity(M_775, M_775.source.p1, mirror_775_props, distances)
cavity_1550 = setup.add_basic_cavity(M_1550, M_1550.source.p1, mirror_1550_props, distances)
#sol = Model.run(setup.move_piezo(Model.s_mi_mo, -10e-6))
sol_775 = cavity_775.run(setup.move_piezo(cavity_775.s_mi_mo, 2.5e-6))
sol_1550 = cavity_1550.run(setup.move_piezo(cavity_1550.s_mi_mo, 2.5e-6))

f, ax = plt.subplots(1)

ax.plot((-distances["mi_mo"]+sol_775.x[0])*1e6, np.log10(sol_775["cav_refl"]), color="tab:blue", label="775nm")
#ax.plot((-distances["mi_mo"]+sol_1550.x[0])*1e6, np.log10(sol_1550["cav_refl"]), color="tab:red", label="1550nm")

plt.ticklabel_format(style="sci", axis="x")
plt.xlabel(r"Distance Piezo is Moved By, $\Delta x [\mu m]$", fontsize=18)
plt.ylabel(r"Tansmitted Power, $\log_{10}(P)$", fontsize=18)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
plt.title(f"Transmission of 775nm & 1550nm \n through a {distances['mi_mo']}m Cavity \n with Supermirrors coated for 1550nm")
plt.legend()

plt.show()
