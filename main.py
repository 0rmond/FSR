import numpy as np
import matplotlib.pyplot as plt
from finesse import Model
from finesse.components import Laser
from scipy.constants import c as light_speed

import tomllib

import setup

def import_inventory(fname="inventory.toml"):
    with open("inventory.toml", "rb") as f:
        data = tomllib.load(f)
    return data

def main():
    DATA = import_inventory()
    MIRRORS = DATA["mirrors"]

    mirror_775_props = {
        "input_r": MIRRORS["newport"]["775"]["SR"]["r"],
        "input_t": MIRRORS["newport"]["775"]["SR"]["t"],
        "input_Rc": -1,
        "output_r": MIRRORS["thorlabs"]["775"]["P01"]["r"],
        "output_t": MIRRORS["thorlabs"]["775"]["P01"]["t"],
        "output_Rc": np.inf,
    }
    print(mirror_775_props)

    distances = {
        "to_mirror": 0,
        "mi_mo": 20e-3,
    }
    f_775 = light_speed/775e-9

    M_775 = Model()

    M_775.add(Laser("source", P=1, f=f_775))

    cavity_775 = setup.add_basic_cavity(M_775, M_775.source.p1, mirror_775_props, distances)
    print(cavity_775.components[-1].ports[1])
    # cavity_775.modes("even", 8)
    # mismatched = cavity_775.create_mismatch(cavity_775.components[-2].ports[0].i, w0_mm=10, z_mm=100)

    sol_775 = cavity_775.run(setup.move_piezo(cavity_775.s_mi_mo, 2.5e-6))


    f, ax = plt.subplots(1)

    detector = "cav_refl"
    P = sol_775[detector]
    x = -distances["mi_mo"]+sol_775.x[0]
    ax.plot(x*1e6, P, color="tab:blue", label=f"775nm {detector}")

    plt.ticklabel_format(style="sci", axis="x")
    plt.xlabel(r"Distance Piezo is Moved By, $\Delta x [\mu m]$", fontsize=18)
    plt.ylabel(r"Power", fontsize=18)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.legend()

    plt.show()

if __name__ == "__main__":
    main()
