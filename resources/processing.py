import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os


c = 3e8


def get_mon_params(path):
    res = {}
    with open(path, 'r') as fp:
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

    res["k_r"] = int(res["k_r"])
    try:
        res["k_z"] = int(res["k_z"])
    except KeyError:
        res["k_s"] = int(res["k_s"])
    return res


def _parse_mons():
    result_dir = "round"
    for filename in os.listdir(result_dir):
        if filename.startswith("Monitor"):
            file_path = os.path.join(result_dir, filename)
            params = get_mon_params(file_path)

            try:
                dim = params["k_r"] * params["k_z"] + 1
            except KeyError:
                dim = params["k_r"] * params["k_s"] + 1

            df = pd.read_csv(file_path, skiprows=4, header=0, names=range(dim + 1), sep=" ")
            df.drop(dim, axis=1, inplace=True)

            z = []
            E = []

            for i, row in df.iterrows():
                z.append(row[0])
                E.append(np.average(row[1:dim]) / 1e6)

            t = [v / c for v in z]
            inc = t[1] - t[0]

            fft = np.fft.rfft(E)
            fft_frq = np.fft.rfftfreq(len(E), inc) / 1e12
            pwr = np.abs(fft)

            z = [-v for v in z]

            # plt.figure(figsize=FIGSIZE)

            plt.plot(z, E, "m", label="Electric Field")
            # plt.title("Electric Field")
            plt.xlabel("Position (m)")
            plt.ylabel("Electric Field (MV/m)")
            # plt.xlim([-0.2, -0.12])

            plt.savefig(f"{filename}_field.png", pad_inches=0.1, bbox_inches="tight")
            plt.close()

            # plt.figure(figsize=FIGSIZE)

            plt.plot(fft_frq, pwr, label="Power Spectrum")
            # plt.title("Power Spectrum of Electric Field")
            plt.xlabel("Frequency (THz)")
            # plt.xlim([0, 0.5])

            plt.savefig(f"{filename}_power.png", pad_inches=0.1, bbox_inches="tight")
            plt.close()


            # # Generate a specctrogram of the chirp and conduct a regression using a linear model
            #
            # from scipy.optimize import curve_fit
            #
            # # Sampling Rate
            # fs = 1 / inc
            # # Window Width
            # nfft = int(len(E) / 10)
            # # Window Overlap
            # novl = nfft / 2
            #
            # plt.figure(figsize=FIGSIZE)
            #
            # spc, frq_spc, tim_spc, _ = plt.specgram(E, Fs=fs, NFFT=nfft, noverlap=novl,
            #                                         xextent=(t[0], t[-1]))  # , #cmap="magma") #"gnuplot2_r"
            #
            # # plt.xlim((tim_spc[0], tim_spc[-1]))
            # # plt.title("Spectrogram")
            # plt.ylabel("Frequency (Hz)")
            # plt.xlabel("Time (s)")
            # ylim = plt.axis()[2], plt.axis()[3]
            # plt.ylim([0, 0.5e12])
            # plt.savefig(f"{IMG_DIR}/spec.png", pad_inches=0.1, bbox_inches="tight")
            # plt.close()

if __name__ == "__main__":
    _parse_mons()

'''
# Compress the pulse by phase shifting each component of its DFT using the model regressed above

# Fourier Transform
fft = np.fft.rfft(sig)
# Power Spectrum
pwr = np.abs(fft) ** 2
#plt.ylim((frq_min * 0.5, frq_max * 1.2))
# Frequencies for DFT
fft_frq = np.fft.rfftfreq(len(sig), d=INC)
# Phase of each component of fft
fft_phs = np.angle(fft)


# Phase of each component calculated from frequencies using above parameters
fft_phs_fit = 2*np.pi*((fft_frq-b)**2/a/2+b*(fft_frq-b)/a)
fft_phs_fit_2 = np.pi*fft_frq**2/a
# Transformation to adjust phase of each component
trs = np.exp(fft_phs_fit * 1j)


# DFT of compressed signal
fft_com = fft * trs
# Frequency bin phases of compressed signal
fft_com_phs = np.angle(fft_com)
# Reconstructed compresed signal
sig_com = np.fft.irfft(fft_com)


# Theoretical maximally compressed DFT
fft_com_max = np.array([abs(v) for v in fft])
# Theoretical maximally compressed signal
sig_com_max = np.fft.irfft(fft_com_max)

#sig_com = np.roll(sig_com, -np.where(sig_com == np.max(sig_com))[0][0] + N // 2)
#sig_com_max = np.roll(sig_com_max, N // 2)

print(fft_frq[0])

plt.figure(figsize=(18, 12))

plt.plot(frq, phs, linestyle=":", linewidth=2, label="Actual Phase")
plt.plot(frq, phs_fit, linestyle=":", linewidth=2, label="Reconstructed Phase")
plt.plot(fft_frq, fft_phs_fit, linestyle=":", linewidth=2, label="Computed Phase of DFT Bins")
plt.plot(fft_frq, fft_phs_fit_2, linestyle=":", linewidth=2, label="Computed Phase of DFT Bins 2")
plt.plot(fft_frq, -np.unwrap(fft_phs), linestyle=":", linewidth=2, label="Actual Phase of DFT Bins")
plt.plot(fft_frq, -np.unwrap(fft_com_phs), linestyle=":", linewidth=2, label="Actual Phase of Compressed DFT Bins")
plt.plot(fft_frq, -np.unwrap(fft_phs)-fft_phs_fit, linestyle=":", linewidth=2, label="Difference Between Phase of Compressed DFT and Computed DFT Phases")
plt.xlim([0, frq_max * 1.3])
plt.ylim([-100,400])
plt.grid()
plt.legend()
plt.show()

plt.figure(figsize=(18, 5))

plt.subplot(121)
plt.plot(fft_frq, pwr, "b")
plt.xlim([frq_min * 0.5, frq_max * 1.3])
plt.title("Power Spectrum")
plt.ylabel("Magnitude")
plt.xlabel("Frequency (Hz)")

plt.subplot(122)
#plt.plot(fft_frq, np.unwrap(fft_phs), "r", linestyle="--", label="Pre Compression")
#plt.plot(fft_frq, fft_phs_fit, "b", linestyle="--", label="Pre Compression Estimated")
plt.plot(fft_frq, fft_com_phs, "m.", linestyle=":", label="Post Compression")
plt.legend()
#plt.xlim([frq_min * 0.5, frq_max * 1.3])
#plt.xlim([0,10])
#plt.ylim([-200,400])
#plt.ylim([-10, 10])
plt.title("Phase over Frequency")
plt.ylabel("Phase (rad)")
plt.xlabel("Frequency (Hz)")

plt.show()

plt.figure(figsize=(15, 8))

plt.plot(tim, sig, "y", linestyle="-", label="Input Signal")
plt.plot(tim, sig_com_max, "m", linestyle=":", linewidth=3, label="Maximum Compression")
plt.plot(tim, sig_com, "b", linestyle="-", label="Actual Compression")
plt.rc('legend', fontsize=14)
plt.rc('axes', titlesize=14)
plt.title("Signal")
plt.legend()

plt.show()
'''