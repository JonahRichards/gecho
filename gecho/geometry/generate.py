from gecho.geometry.geometry import Geometry
import numpy as np

INPUT_SOURCE_FILE = ""


def cleave(x, sig=5):
    return round(x, -int(np.log(np.abs(x))) + sig) if float(x) != 0.0 else x


def att_format(name: str):
    return name.replace("_", " ").title().replace(" ", "")


def to_string(val):
    match str(type(val)):
        case '<class \'list\'>':
            return ' '.join(map(str, val))
        case '<class \'float\'>':
            return str(cleave(val))
        case _:
            return str(val)


def generate_geometry_file(geometry: Geometry(), dir):
    def write(fp, layer):
        try:
            z = np.concatenate([layer.top.zs, layer.bot.zs[::-1]])
            r = np.concatenate([layer.top.rs, layer.bot.rs[::-1]])
        except AttributeError:
            z = layer.bot.zs
            r = layer.bot.rs

        z = [cleave(v) for v in z]
        r = [cleave(v) for v in r]

        fp.write("% Number of elements in metal with conductive walls, permeability, permitivity, cond.\n")
        fp.write(f"{len(z)} {cleave(layer.ep)} {cleave(layer.mu)} {cleave(layer.sg)}\n")
        fp.write(f"% Segments of lines and elipses with wall conductivity\n")
        for i1 in range(len(z)):
            i2 = np.mod(i1 + 1, len(z))
            fp.write(f"{z[i1]} {r[i1]} {z[i2]} {r[i2]} 0 0 0 0 0 {layer.sg}\n")

    with open(f"{dir}/geom.txt", "w") as fp:
        fp.write(f"% Number of materials\n{len(geometry.layers) + 1}\n")
        write(fp, geometry.wall)
        for layer in geometry.layers:
            write(fp, layer)


def generate_input_file(geometry: Geometry(), dir):
    component_names = ["model", "mesh", "beam"]
    components = [getattr(geometry, name) for name in component_names]
    atts = {att_format(k): v for comp in components for k, v in comp.__dict__.items()}

    with open(f"resources/input_in.txt", "r") as fp:
        lines = fp.readlines()

    for i in reversed(range(len(lines))):
        att_name = lines[i].split("=")[0]
        if att_name in atts.keys():
            lines[i] = f"{att_name}={to_string(atts[att_name])}\n"
        if att_name in ("FieldMonitor", r"%FieldMonitor"):
            lines.remove(lines[i])

    for mon in geometry.monitors:
        lines.append(f"FieldMonitor={'{'} '{mon.field_component}' '{mon.type}' {cleave(mon.z_0)} {cleave(mon.z_1)} {cleave(mon.r_0)} {cleave(mon.r_1)} {cleave(mon.s_0)} {cleave(mon.s_1)} {mon.n}{'}'}\n")

    with open(f"{dir}/input_in.txt", "w") as fp:
        fp.writelines(lines)