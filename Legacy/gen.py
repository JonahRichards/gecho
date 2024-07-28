from geom import *
import matplotlib.pyplot as plt
import pickle


# Round to 5 significant digits
def cleave(x, sig=5):
    return round(x, -int(np.log(np.abs(x))) + sig) if float(x) != 0.0 else x


def color(name):
    if name in COLRS2.keys():
        return COLRS2[name]
    else:
        return "gray"


def gen(chamber: Chamber(), dir):

    def write(fp, geometry):
        fp.write("% Number of elements in metal with conductive walls, permeability, permitivity, cond.\n")
        fp.write(f"{len(geometry.z)} {cleave(geometry.ep)} {cleave(geometry.mu)} {cleave(geometry.sg)}\n")
        fp.write(f"% Segments of lines and elipses with wall conductivity\n")
        for i1 in range(len(geometry.z)):
            i2 = np.mod(i1 + 1, len(geometry.z))
            fp.write(f"{cleave(geometry.z[i1])} {cleave(geometry.r[i1])} {cleave(geometry.z[i2])} {cleave(geometry.r[i2])} 0 0 0 0 0 {geometry.sg}\n")

    with open(f"{dir}/geom.txt", "w") as fp:
        fp.write(f"% Number of materials\n{len(chamber.geometries) + int(bool(chamber.wall))}\n")
        if geometry := chamber.wall:
            write(fp, geometry)
        for geometry in chamber.geometries.values():
            write(fp, geometry)


    try:
        with open(f"{dir}/input_in.txt", "r") as fp:
            lines = fp.readlines()
    except FileNotFoundError:
        with open(f"input_in.txt", "r") as fp:
            lines = fp.readlines()
    

    for i in reversed(range(len(lines))):
        match lines[i].split("=")[0]:
            case "Modes":
                lines[i]=f"Modes={''.join(f'{v} ' for v in MODES)}\n"
            case "MeshLength":
                lines[i]=f"MeshLength={chamber.mesh.lines}\n"
            case "StepY":
                lines[i]=f"StepY={cleave(cleave(chamber.mesh.dy))}\n"
            case "StepZ":
                lines[i]=f"StepZ={cleave(cleave(chamber.mesh.dz))}\n"
            case "FieldMonitor" | r"%FieldMonitor":
                lines.remove(lines[i])
            case _:
                pass
    

    for mon in chamber.monitors:
        lines.append(f"FieldMonitor={'{'} '{mon.dir}' '{mon.type}' {cleave(mon.zi)} {cleave(mon.zf)} {cleave(mon.ri)} {cleave(mon.rf)} {cleave(mon.si)} {cleave(mon.sf)} {'1' if mon.type == 's' else '2'}{'}'}\n")


    with open(f"{dir}/input_in.txt", "w") as fp:
        fp.writelines(lines)

    def plot(z: list, r: list, label, c1, c2="k", linestyle="-", alpha=1, ref=True):
        x = np.append(z, z[0])
        y = np.append(r, r[0])

        #x = x[:int(len(x)/1.3)]
        #y = y[:int(len(y)/1.3)]

        plt.fill(x, y, c=c1, label=label, alpha=alpha)
        plt.plot(x, y, c=c2, linestyle=linestyle, linewidth=1)
        #plt.plot(x, y, "r+") 
        if ref:
            plt.fill(x, -y, c=c1, alpha=alpha)
            plt.plot(x, -y, c=c2, linestyle=linestyle, linewidth=1)

    plt.figure(figsize=FIGSIZE)

    for name, geometry in chamber.geometries.items():
        plot(geometry.z, geometry.r, name, color(name))

    if chamber.wall:
        x = np.array(chamber.wall.z)
        y = np.array(chamber.wall.r)

        plt.plot(x, y, "r", label="Chamber Wall")
        plt.plot(x, -y, "r")

    zmon = None
    for mon in chamber.monitors:
        if mon.type == "s":
            plot(mon.z, mon.r, "s-Monitor", c1="magenta", c2="magenta", alpha=0.5, linestyle="-", ref=False)
        if mon.type == "z":
            zmon = mon
            plot(mon.z, mon.r, "z-Monitor", c1="lime", c2="lime", alpha=0.5, linestyle="-", ref=False)

    #plt.title("Geometry")
    plt.ylabel("y-axis (m)")
    plt.xlabel("z-axis (m)")
    plt.legend()
    #plt.grid()
    plt.axis("off")

    plt.savefig(f"{dir}/{IMG_DIR}/geom.png", pad_inches=0.1, bbox_inches="tight")
    plt.close()

    geoms = {}

    for k, v in chamber.geometries.items():
        geoms[k] = (v.z, v.r)

    geoms["Wall"] = (chamber.wall.z, chamber.wall.r)

    with open(f"{dir}/geom.pkl", 'wb') as file:
        pickle.dump(geoms, file)

    if zmon:
        with open(f"{dir}/mon.pkl", 'wb') as file:
            pickle.dump((mon.si, mon.sf, mon.ri, mon.rf), file)
