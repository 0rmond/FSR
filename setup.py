from finesse.components import Laser, Mirror, Space, Cavity, Gauss
from finesse.detectors import PowerDetector
from finesse.analysis.actions import Xaxis, Series, Change

from scipy.constants import c as light_speed
import numpy as np

def create_copies(of_model, of_port):
    of_port_full_name = of_port.full_name
    model_copy = of_model.deepcopy()
    port_copy = [port for port in model_copy.get_open_ports() if port.full_name == of_port_full_name][0]
    return model_copy, port_copy

def add_basic_cavity(to_model, from_port, mirror_props, distances):
    """Adds a simple cavity to a port, as demo'd in the Finesse3 documentation, using a Cavity object.
    """
    to_model_copy, from_port_copy = create_copies(to_model, from_port)

    components = [
        Mirror("m_input", R=mirror_props["input_r"], T=mirror_props["input_t"], Rc=mirror_props["input_Rc"]),
        Mirror("m_output", R=mirror_props["output_r"], T=mirror_props["output_t"], Rc=mirror_props["output_Rc"]),
    ]

    to_model_copy.add(components)

    spaces = [
        Space(f"s_{from_port.full_name.split('.')[0]}_mi", portA=from_port_copy, portB=to_model_copy.m_input.p1, L=distances["to_mirror"]),
        Space("s_mi_mo", portA=to_model_copy.m_input.p2, portB=to_model_copy.m_output.p1, L=distances["mi_mo"]),
    ]

    to_model_copy.add(spaces)

    cavity = Cavity("fabry_perot", source=to_model_copy.m_input.p2)

    to_model_copy.add(cavity)

    detectors = [
        PowerDetector("cav_refl", components[0].p1.o),
        PowerDetector("cav_circ", components[1].p1.i),
        PowerDetector("cav_tran", components[1].p2.o),
    ]

    to_model_copy.add(detectors)

    to_model.modes("even", 4)
    return to_model_copy



def calculate_centre_thickness(edge_thickness, diameter, radius_of_curvature):
    """Uses sagitta formula. All units in mm
    """
    sagitta = radius_of_curvature - np.sqrt(radius_of_curvature**2 - 0.25*(diameter/2)**2)

    centre_thickness = edge_thickness - sagitta
    return centre_thickness


def add_thick_mirror(to_model, from_port, frontface_props, substrate, backface_props):
    """Adds two finesse.components.Mirror objects seperated by a finesse.components.Space of a certain length an refractive index to an existing model.
    Parameters:
    to_model (finesse.Model): Model to add the mirror to.
    from_port (finesse.components.node.Port): The Port node to attach the mirror to.
    name (str): Name of the mirror.
    frontface_props/backface_props (dict): The first and last surfaces that the incident light hits respectively.
        - name (str): Name of the surface's coating.
        - refl (float): Reflectivity.
        - trans (float): Transmissivty.
        - Rc (float): Radius of curvature.
    substrate (dict):
        - name (str): Name of the substrate material.
        - t_c (float): Centre thickness in m.
        - nr (float): Refractive Index.
    """
    to_model_copy, from_port_copy = create_copies(to_model, from_port)

    mirrors = [
        Mirror(f"{frontface_props['name']}_frontface", R=frontface_props["refl"], T=frontface_props["trans"], Rc=-frontface_props["Rc"], misaligned=True),
        Mirror(f"{backface_props['name']}_backface", R=backface_props["refl"], T=backface_props["trans"], Rc=backface_props["Rc"]),
    ]

    to_model_copy.add(mirrors)

    spaces = [
        Space(f"s_{from_port.full_name.split('.')[0]}_{substrate['name']}", nr=substrate["nr"], L=substrate["t_c"], portA=from_port_copy, portB=mirrors[1].p1),
        Space(f"s_{substrate['name']}_substrate", nr=substrate["nr"], L=substrate["t_c"], portA=mirrors[0].p2, portB=mirrors[1].p1),
    ]

    to_model_copy.add(spaces)

    return to_model_copy

def add_thick_lens(to_model, from_port, lens_props):
    """Adds a thick lens from two finesse.components.Mirror objects and a finesse.components.Space object of a certain length and refractive index to an existing model.
    Parameters:
    to_model (finesse.Model): Model to add the mirror to.
    name (str): Name of the Lens.
    lens_prop (dict): Properties of the lens.
        - Rc1 (float): First surface's absolute radius of curvature.
        - Rc2 (float): Second surface's absolute radius of curvature.
        - t_c (float): Centre thickness in m.
        - nr (float): Refractive Index.
    """
    to_model_copy, from_port_copy = create_copies(to_model, from_port)

    surfaces = [
        Mirror(f"{lens_props['name']}_frontface", Rc=-lens_props["Rc1"], T=1, R=0),
        Mirror(f"{lens_props['name']}_backface", Rc=lens_props["Rc2"], T=1, R=0),
    ]

    to_model_copy.add(surfaces)

    spaces = [
        Space(f"s_{from_port.full_name.split('.')[0]}_{lens_props['name']}", nr=lens_props["nr"], L=lens_props["t_c"], portA=from_port_copy, portB=surfaces[0]),
        Space(f"{lens_props['name']}_space", nr=lens_props["nr"], L=lens_props["t_c"], portA=surfaces[0], portB=surfaces[1]),
    ]

    to_model_copy.add(spaces)
    return to_model_copy

def sweep_one_fsr(input_mirror):
    return Xaxis(input_mirror.phi, mode="lin", start=-175, stop=185, steps=10_000, name="fsr")

def move_piezo(cavity_space, move_by):
    """
    Decrease the cavity length by a small amount, as if a Piezo had pushed one of the mirrors inwards
    """
    L = cavity_space.L
    return Xaxis(L, mode="lin", start=L.value, stop=L.value+move_by, steps=10_000, name="piezo")
