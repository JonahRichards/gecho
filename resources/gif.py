import matplotlib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
import glob
import os
import cmasher as cmr
import pickle as pk

from resources.processing import get_mon_params
from gecho.geometry.geometry import Geometry

matplotlib.use("QtAgg")


def color_gen():
    while True:
        colors = ["#4bb4ff",
                  "#4bffb4",
                  "#ff4bb4",
                  "#b44bff",
                  "#b4ff4b"]
        for c in colors:
            yield c


COLORS = color_gen()


def plot_layer(layer: Geometry.Layer, colors):
    z = np.concatenate([layer.bot.zs, layer.top.zs[::-1], [layer.bot.zs[0]]])
    r = np.concatenate([layer.bot.rs, layer.top.rs[::-1], [layer.bot.rs[0]]])

    c = next(colors)

    plt.fill(z, r, c=c, label=layer.name, alpha=0.5)
    plt.plot(z, r, c="white", linestyle="-", linewidth=1)

    ref = True

    if ref:
        plt.fill(z, -r, c=c, alpha=0.5)
        plt.plot(z, -r, c="white", linestyle="-", linewidth=1)


def plot_monitor(monitor: Geometry.Monitor, colors):
    r = [monitor.r_0, monitor.r_0, monitor.r_1, monitor.r_1]

    if monitor.type == "z":
        z = [monitor.s_0, monitor.s_1, monitor.s_1, monitor.s_0]
    else:
        z = [monitor.z_0, monitor.z_1, monitor.z_1, monitor.z_0]

    c = next(colors)

    plt.fill(z, r, c=c, label=monitor.name, alpha=0.5)
    plt.plot(z, r, c=c, linestyle="dashed", linewidth=1)


def animate(image_directory):
    def key_func(path):
        parts = path.split("\\")
        number = int(parts[-1].split(".")[0])
        return number

    image_files = sorted(glob.glob(os.path.join(image_directory, '*.png')), key=key_func)

    first_image = plt.imread(image_files[0])
    height, width, _ = first_image.shape

    fig, ax = plt.subplots(figsize=(width / 100, height / 100), dpi=100)
    ax.set_position([0, 0, 1, 1])  # Position the axis to fill the figure
    ax.axis('off')

    frames = []

    # plt.axis("off")
    # plt.subplots_adjust(left=0.0, right=1.0, bottom=0.0, top=1.0)

    for image_file in image_files:
        img = plt.imread(image_file)
        frame = plt.imshow(img, animated=True)
        frames.append([frame])

    animation_object = animation.ArtistAnimation(fig, frames, interval=20, blit=True, repeat_delay=0)

    frames_per_second = 50
    animation_object.save(image_directory.split('/')[-1] + "gif", fps=frames_per_second, writer='ffmpeg')


def make_gif(file_path, geometry: Geometry=None, mon_num=0):
    image_directory = "frames/" + file_path.split('\\')[-1][:-3]
    os.makedirs(image_directory, exist_ok=True)

    params = get_mon_params(file_path)

    type = "s" if params["time"] == "z" else "z"

    dim = params["k_r"] * params[f"k_{type}"] + 1

    offset = 0

    df = pd.read_csv(file_path, skiprows=4 + offset, header=0, names=range(dim + 1), sep=" ", chunksize=1)

    for c, chunk in enumerate(df):
        for index, row in chunk.iterrows():
            print(index)

            frame = row.values[1:-1].reshape(params["k_r"], params[f"k_{type}"])

            mx = np.max([np.abs(frame.min()), np.max(frame)])

            frame = frame[::-1]

            frame = frame[..., ::-1] if params["time"] == "z" else frame

            frame = np.vstack((frame, frame[::-1]))

            xmin = params[f"{type}0"]

            if params["time"] == "z":
                # xmin = max(xmin, geometry.mesh.start_position)
                xmin += (offset + index) * params["h_ct"] - params["h_s"] * params["k_s"]

            xmax = xmin + params[f"k_{type}"] * params[f"h_{type}"]
            ymin = params["k_r"] * params["h_r"] * -1
            ymax = params["k_r"] * params["h_r"]

            extent = (xmin, xmax, ymin, ymax)

            plt.imshow(frame, cmap=cmr.wildfire, vmin=-mx, vmax=mx, extent=extent)

            if geometry:
                colors = color_gen()

                for layer in geometry.layers:
                    plot_layer(layer, colors)

                x = np.array(geometry.wall.bot.zs)
                y = np.array(geometry.wall.bot.rs)

                plt.plot(x, y, "r", label=geometry.wall.name)
                plt.plot(x, -y, "r")

                # for mon in geometry.monitors:
                #     plot_monitor(mon, colors)

            plt.xlim([xmin, xmax])
            plt.ylim([ymin, ymax])

            # plt.axis("off")

            # plt.show()

            plt.savefig(f"{image_directory}/{index}.png", bbox_inches="tight", pad_inches=0.0, facecolor="black")

            plt.close()

    animate(image_directory)


def make_gifs(result_dir, geometry=None):
    monitors = [file for file in os.listdir(result_dir) if file.startswith("Monitor")]
    for i, filename in enumerate(monitors):
        file_path = os.path.join(result_dir, filename)
        make_gif(file_path, geometry, i)


if __name__ == "__main__":
    current_dir = os.getcwd()
    geometry_path = "".join(current_dir.split('_')[:-1]) + ".geom"

    with open(geometry_path, "rb") as fp:
        geometry = pk.load(fp)

    make_gifs("round", geometry)
