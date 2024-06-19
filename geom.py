from config import *

import numpy as np
#from sys import argv

'''
length = abs(zf - zi)
count = -int(length // -((wi + wf) / 2))
widths = [wi + 2 * (length - count * wi) / count / (count - 1) * i for i in range(count)]
widths = [wi] + [widths[i] - (wf - widths[-1]) / (len(widths) - 2) for i in range(1, len(widths) - 1)] + [wf]
z = [sum([v / 2 * j for v in widths for j in [0, 1, 0, 1]][:i]) for i in range(1, count * 4 + 1)]
unique_z = list(set(z))
unique_z.sort()
inner = list(map(lambda x: (rf - ri) / length * x + ri, unique_z))
outer = list(map(lambda x: (rf + hf - ri - hi) / length * x + ri + hi, unique_z))
r = [l[i] for t in zip(range(0, len(inner) - 1, 2), range(1, len(inner), 2)) for l in (inner, outer) for i in t]
z = list(map(lambda x: x + zi, z))

def owo(x):
    return np.where(x < 3, np.sqrt(-(x-1.5)**2 + 2.25) + 1, np.where(x < 8, 1, np.sqrt(-(x-8)**2 + 4)/2))

'''


def lin(zi, zf, ri, rf):
    m = (rf - ri) / (zf - zi)
    return lambda z: m * (z - zf) + rf


def const(c):
    return lambda z: 0 * z + c


def gen_corrugation(zi, zf, bot, per, hei, frc=0.5):
    widths = []
    length = zf - zi
    zee = zi
    while True:
        width = per(zee)
        if width > length:
            break
        length -= width
        zee += width
        widths.append(width)

    widths = [w * f for w in widths for f in (frc, 1 - frc)]
    boundaries = [sum(widths[:i]) for i in range(len(widths) + 1)]
    boundaries = [v + zi for v in boundaries]
    boundaries[-1] = zf
    boundaries = iter(boundaries)
    boundary = next(boundaries)
    boundary = next(boundaries)

    z = []
    r = []
    is_tooth = True

    for zee in np.append(np.arange(zi, zf, HRES), zf):
        if zee > boundary:
            z += [boundary, boundary]
            r += [bot(boundary) + hei(boundary) * int(is_tooth), bot(boundary) + hei(boundary) * int(not is_tooth)]
            boundary = next(boundaries)
            is_tooth = not is_tooth
        z.append(zee)
        r.append(bot(zee) + hei(zee) * int(is_tooth))

    return z, r


def gen_tube(zi, zf, bot, top, per=None, hei=None, frc=0.5):
    z1 = np.append(np.arange(zi, zf, HRES), zf)
    z2 = z1[::-1]

    if per and hei:
        z1, r1 = gen_corrugation(zi, zf, bot, per, hei, frc)
    else:
        r1 = bot(z1)
    
    r2 = top(z2)

    z = np.concatenate([z1, z2])[::-1]
    r = np.concatenate([r1, r2])[::-1]

    return z, r


def gen_wall(zi, zf, f, geom, per=None, hei=None, frc=0.5):
    if per and hei and frc:
        z1, r_corr = gen_corrugation(zi, zf, f, per, hei, frc)
        #r_corr = np.array([r_corr[i] - f(z1[i]) for i in range(len(z1))])
    else:
        z1 = np.append(np.arange(zi, zf, HRES), zf)
        r_corr = f(z1)
    
    mins = [g.zi for g in geom.values()]
    min_z = np.min(mins if mins else [np.inf])
    maxs = [g.zf for g in geom.values()]
    max_z = np.max(maxs if maxs else [-np.inf])
    top_fs = [g.top for g in geom.values()]
    top_fs.append(f)
    max_f = lambda x: np.max([fun(x) for fun in top_fs])

    z, r = [], []
    toggle = True

    for i in range(len(z1)):
        if z1[i] > min_z and z1[i] < max_z:
            if toggle:
                z += [min_z, min_z]
                r += [r_corr[i], max_f(min_z)]
                toggle = not toggle
        if z1[i] > max_z:
            if not toggle:
                z += [max_z, max_z]
                r += [max_f(max_z), r_corr[i]]
                toggle = not toggle

        z.append(z1[i])
        r.append(r_corr[i] if toggle else max_f(z1[i]))

    return z, r




class Tube():
    def __init__(self, zi, zf, bot, top, ep, mu, sg, per=None, hei=None, frc=0.5):
        self.zi = zi
        self.zf = zf
        self.bot = bot       
        self.top = top
        self.per = per
        self.hei = hei
        self.frc = frc
        self.ep = ep
        self.mu = mu
        self.sg = sg
        
        self.z, self.r = gen_tube(zi, zf, bot, top, per, hei, frc)


class Wall():
    def __init__(self, zi, zf, f, ep, mu, sg, geom=None, per=None, hei=None, frc=0.5):
        self.zi = zi
        self.zf = zf
        self.f = f
        self.ep = ep
        self.mu = mu
        self.sg = sg
        self.geom = geom
        self.per = per
        self.hei = hei
        self.frc = frc
        
        self.z, self.r = gen_wall(zi, zf, f, geom, per, hei, frc)


class Mesh():
    def __init__(self, lines, dy, dz) -> None:
        self.lines=lines
        self.dy=dy
        self.dz=dz


class Monitor():
    def __init__(self, dir, type, zi, zf, ri, rf, si, sf):
        self.dir = dir
        self.type = type
        self.zi = zi
        self.zf = zf
        self.ri = ri
        self.rf = rf
        self.si = si
        self.sf = sf
        if type == "s":
            self.z = [zi, zf, zf, zi]
            self.r = [ri, ri, rf, rf]
        elif type == "z":
            self.z = [si, sf, sf, si]
            self.r = [ri, ri, rf, rf]


class Chamber():
    def __init__(self, geometries: dict[str, Tube]={}, wall: Wall=None, mesh: Mesh=None, monitors: Monitor=[]):
        self.geometries = geometries
        self.wall = wall
        self.mesh = mesh
        self.monitors = monitors


'''
class Mesh():
    lines = 500 * RES
    step_y = np.min([Tube(0).thickness_i, Tube(0).thickness_f])/RES/5
    step_z = Tube(0).length/lines * 1


class Monitor():
    start_z = (Tube(0).length)  * 1
    start_r = Tube(0).radius_f * 0.1
    start_s = start_z
    length = Mesh().step_z * 10
    radius = Mesh().step_y * 10  #
    dur = Mesh().lines * Mesh().step_z * 3
'''

'''
class Substrate():
    exists = False
    thickness = np.max([Tube.thickness_i, Tube.thickness_f]) * 0.5
    permty = 0
    permby = 1.0
    condty = 1e6

    class Flare():
        exists = False
        length = Tube.length * 0.5
        radius = (Tube.radius_f + Tube.thickness_f) * 3.0

    if not exists:
        Flare.exists = False
        thickness = 0
    if not Flare.exists:
        Flare.length, Flare.radius = 0, Tube.radius_f


class Vacuum():
    exists = False
    thickness = np.max([Tube.radius_i + Tube.thickness_i, Tube.radius_f + Tube.thickness_f])
    radius = np.max([Tube.radius_i + Tube.thickness_i, Tube.radius_f + Tube.thickness_f]) + Substrate.Flare.radius + Substrate.thickness + thickness
    permty = 1.0
    permby = 1.0
    condty = 0.0


class Wall():
    exists = True
    flush = True
    pre = Tube.length * 0.2
    post = pre
    thickness = np.max([Tube.radius_i + Tube.thickness_i, Tube.radius_f + Tube.thickness_f])
    radius = np.max([Tube.radius_i + Tube.thickness_i, Tube.radius_f + Tube.thickness_f]) + Substrate.Flare.radius + Substrate.thickness + thickness
    permty = 1.0
    permby = 1.0
    condty = 0.0






# Geometries

dielectric_z = [
    Wall.pre,
    Wall.pre + Tube.length,
    Wall.pre + Tube.length,
    Wall.pre
]

dielectric_r = [
    Tube.radius_i,
    Tube.radius_f,
    Tube.radius_f + Tube.thickness_f,
    Tube.radius_i + Tube.thickness_i
]

#widths = [Corrugated.width_i + 2*(Tube.length-Corrugated.count*Corrugated.width_i)/(Corrugated.count)/(Corrugated.count-1) * i for i in range(Corrugated.count)]
#widths = [Corrugated.width_i] + [widths[i] - (Corrugated.width_f - widths[-1]) / (len(widths) - 2) for i in range(1, len(widths) - 1)] + [Corrugated.width_f]
#corrugated_z = [sum([v / 2 * j for v in widths for j in [0, 1, 0, 1]][:i]) for i in range(1, Corrugated.count * 4 + 1)]

#zees = list(set(corrugated_z))
#zees.sort()
#inner = list(map(lambda x: (Tube.radius_f-Tube.radius_i)/Tube.length*x+Tube.radius_i, zees))
#outer = list(map(lambda x: (Tube.radius_f+Corrugated.height_f-Tube.radius_i-Corrugated.height_i)/Tube.length*x+Tube.radius_i+Corrugated.height_i, zees))
#corrugated_r = [l[i] for t in zip(range(0, len(inner) - 1, 2), range(1, len(inner), 2)) for l in (inner, outer) for i in t]

#corrugated_z += [
#    Tube.length,
#    0
#]
#
#corrugated_z = list(map(lambda x: x + Wall.pre, corrugated_z))
#
#corrugated_r += [
#    Tube.radius_f + Tube.thickness_f,
#    Tube.radius_i + Tube.thickness_i
#]


substrate_z = [
    Wall.pre,
    Wall.pre + Tube.length,
    Wall.pre + Tube.length,
    Wall.pre
]

substrate_r = [
    Tube.radius_i + Tube.thickness_i,
    Tube.radius_f + Tube.thickness_f,
    Tube.radius_f + Tube.thickness_f + Substrate.thickness,
    Tube.radius_i + Tube.thickness_i + Substrate.thickness
]

if Substrate.Flare.exists:
    substrate_z[2:2] = [
        Wall.pre + Tube.length + Substrate.Flare.length,
        Wall.pre + Tube.length + Substrate.Flare.length
    ]
    substrate_r[2:2] = [
        Substrate.Flare.radius,
        Substrate.Flare.radius + Substrate.thickness
    ]

vacuum_z = [
    0,
    Tube.length,
    Tube.length,
    0
]

vacuum_r = [
    Tube.radius_i + Tube.thickness_i + Substrate.thickness,
    Tube.radius_f + Tube.thickness_f + Substrate.thickness,
    Vacuum.radius,
    Vacuum.radius
]

if Substrate.Flare.exists:
    vacuum_z[2:2] = [
        Tube.length + Substrate.Flare.length,
        Tube.length + Substrate.Flare.length
    ]
    vacuum_r[2:2] = [
        Substrate.Flare.radius + Substrate.thickness,
        Vacuum.radius
    ]


monitor_z = [
    Monitor.start_z,
    Monitor.start_z + Monitor.length,
    Monitor.start_z + Monitor.length,
    Monitor.start_z
]

monitor_r = [
    Monitor.start_r,
    Monitor.start_r,
    Monitor.start_r + Monitor.radius,
    Monitor.start_r + Monitor.radius
]

wall_z = [
    0,
    Wall.pre,
    Wall.pre,
    Wall.pre + Tube.length,
    Wall.pre + Tube.length + Substrate.Flare.length,
    Wall.pre + Tube.length + Substrate.Flare.length + Wall.post
]

wall_r = [
    Tube.radius_i,
    Tube.radius_i,
    Tube.radius_i + Tube.thickness_i + Substrate.thickness,
    Tube.radius_f + Tube.thickness_f + Substrate.thickness,
    Tube.radius_f,
    Tube.radius_f
]

if Substrate.Flare.exists:
    wall_z[4:4] = [
        Wall.pre + Tube.length + Substrate.Flare.length
    ]
    wall_r[4:4] = [
        Substrate.Flare.radius + Substrate.thickness
    ]

wall_r = [v if Wall.flush else Wall.radius for v in wall_r]
'''