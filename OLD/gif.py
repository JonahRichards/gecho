from config import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
import glob
import os
import cmasher as cmr
import pickle


COLRS2 = {"Dielectric":         "yellow",
          "Corrugated Tube":    "silver",
          "Substrate":          "goldenrod"}


def make_gif(image_directory):
    def key_func(path):
        # Split the path into parts
        parts = path.split("/")
        # Extract the number from the file name and convert it to an integer
        number = int(parts[-1].split(".")[0])
        return number

    # Create a list of image file paths
    image_files = sorted(glob.glob(os.path.join(image_directory, '*.png')), key=key_func)

    # Create a figure and axes
    fig, ax = plt.subplots()

    # Initialize an empty list to store the image frames
    frames = []

    plt.axis("off")
    plt.subplots_adjust(left=0.0, right=1.0, bottom=0.0, top=1.0)

    # Iterate over the image files and append each image to the frames list
    for image_file in image_files:
        img = plt.imread(image_file)
        frame = plt.imshow(img, animated=True)
        frames.append([frame])

    # Create the animation
    animation_object = animation.ArtistAnimation(fig, frames, interval=20, blit=True, repeat_delay=0)

    # Set the number of frames per second (optional)
    frames_per_second = 50
    animation_object.save('animation.gif', fps=frames_per_second, writer='ffmpeg')

#make_gif(f"{IMG_DIR}/temp")
#raise Exception("...")

res = {}
with open(f"{DAT_DIR}/Monitor_m00_N02.txt") as fp:
    for i in range(4):
        line = fp.readline().strip()
        params = [v for v in line.split(" ") if "=" in v]
        for param in params:
            tup = param.split("=")
            res[tup[0]] = tup[1]
for k, v, in res.items():
    try:
        res[k] = float(v)
    except ValueError:
        pass
res["k_r"], res["k_s"] = int(res["k_r"]), int(res["k_s"])

dim=res["k_r"]*res["k_s"] + 1


def plot(z: list, r: list, label, c1, c2="white", linestyle="-", alpha=1, ref=True):
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


def color(name):
    if name in COLRS2.keys():
        return COLRS2[name]
    else:
        return "gray"

with open("geom.pkl", 'rb') as file:
    geoms = pickle.load(file)

with open("mon.pkl", 'rb') as file:
    bounds = pickle.load(file)

files = os.listdir(f"{IMG_DIR}/temp/")

# Iterate through the list of files and delete each one
for file in files:
    file_path = os.path.join(f"{IMG_DIR}/temp/", file)
    if os.path.isfile(file_path):
        os.remove(file_path)

df = pd.read_csv(f"{DAT_DIR}/Monitor_m00_N02.txt", skiprows=4 + 0, header=0, names=range(dim+1), sep=" ", chunksize=1)

for c, chunk in enumerate(df):
    for index, row in chunk.iterrows():
        
        frame = row.values[1:-1].reshape(res["k_r"], res["k_s"])

        max = np.max([np.abs(frame.min()), np.max(frame)])

        frame = frame[:, ::-1]
        frame = frame[::-1]

        frame = np.vstack((frame, frame[::-1]))

        extent = [bounds[0] + row[0], bounds[1] + row[0], -bounds[3], bounds[3]]

        plt.imshow(frame, cmap=cmr.wildfire, extent=extent, vmin=-max, vmax=max)

        offset = 0#2.48e-3

        for k, v in geoms.items():
            if k != "Wall":
                plot(np.array([val + offset for val in v[0]]), v[1], k, color(k))
                pass
            else:
                x = np.array([val + offset for val in v[0]])
                y = np.array(v[1])
                plt.plot(x, y, "c", label="Chamber Wall")
                plt.plot(x, -y, "c")

        #plt.plot([extent[1]], [0], "mo")

        plt.xlim([extent[0], extent[1] + (extent[1] - extent[0]) / 1.0])
        plt.ylim([-bounds[3] * 1.1, bounds[3] * 1.1])

        plt.axis("off")

        #plt.savefig(f"{IMG_DIR}/temp/{index}.png", bbox_inches="tight", pad_inches=0.0, facecolor="black")
        plt.savefig(f"test.png", bbox_inches="tight", pad_inches=0.0, facecolor="black")
        
        plt.close()

        break
    break

#make_gif(f"{IMG_DIR}/temp")
