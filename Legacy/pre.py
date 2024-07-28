from gen import *
import datetime
import os
import pickle

def piece2(z1, f1, f2):
    return lambda z: np.where(z < z1, f1(z), f2(z))


def piece3(z1, z2, f1, f2, f3):
    return lambda z: np.where(z < z1, f1(z), np.where(z < z2, f2(z), f3(z)))


def const_dielectric(length, radius, thickness, permitivity):
    geometries={}
    geometries["Dielectric"] = Tube(length * 0.1, length * 1.1, const(radius), const(radius + thickness), permitivity, 1.0, 0.0)
    #geometries["Dielectric"].z = geometries["Dielectric"].z[::-1]
    #geometries["Dielectric"].r = geometries["Dielectric"].r[::-1]

    monitors = []
    monitors.append(Monitor("Ez", "s", length * 1.1, length * 1.11, radius * 0.1, radius * 0.9, length * 1.1, length * 3.0))
    monitors.append(Monitor("Ez", "z", 0.0, length * 1.2, 0.0, radius + thickness, -( radius + thickness), radius + thickness))

    mesh = Mesh(1000 * DETAIL, thickness / 2, thickness / 2)

    wall = Wall(0, length * 1.2, const(radius + thickness), 1.0, 1.0, 0.0, geometries)
    
    chamber = Chamber(geometries=geometries,
                      wall=wall,
                      mesh=mesh,
                      monitors=monitors)
    return chamber


def tap_dielectric(length, ri, rf, thickness, permitivity):
    zi = length * 0.3
    zf = zi + length

    geometries={}
    geometries["Dielectric"] = Tube(zi, zf, lin(zi, zf, ri, rf), lin(zi, zf, ri+thickness, rf+thickness), permitivity, 1.0, 0.0)
    #geometries["Dielectric"].z = geometries["Dielectric"].z[::-1]
    #geometries["Dielectric"].r = geometries["Dielectric"].r[::-1]

    monitors = []
    monitors.append(Monitor("Ez", "s", length * 1.3, length * 1.31, rf * 0.1, rf * 0.9, length * 1.3, length * 2.0))
    monitors.append(Monitor("Ez", "z", 0.0, length * 1.3, 0.0, np.max([ri, rf]) + thickness, 0, 4 * (np.max([ri, rf]) + thickness)))

    # 4000 10 10
    mesh = Mesh(2000 * DETAIL, cleave(thickness / 5 / DETAIL, sig=0), cleave(thickness / 5 / DETAIL, sig=0))

    wall = Wall(0, length * 1.6, piece2(zf, const(ri), const(rf)), 1.0, 1.0, 0.0, geometries)
    
    chamber = Chamber(geometries=geometries,
                      wall=wall,
                      mesh=mesh,
                      monitors=monitors)
    return chamber


def tap_corrugated(length, ri, rf, per, hei):
    zi = length * 0.3
    zf = zi + length

    geometries={}

    monitors = []
    monitors.append(Monitor("Ez", "s", length * 1.3, length * 1.31, rf * 0.1, rf * 0.9, length * 1.3, length * 2.0))
    monitors.append(Monitor("Ez", "z", 0.0, length * 1.3, 0.0, np.max([ri, rf]) + hei, 0, 4 * (np.max([ri, rf]) + hei)))

    # 4000 10 10
    mesh = Mesh(2000 * DETAIL, cleave(hei / 20 / DETAIL, sig=0), cleave(hei / 20 / DETAIL, sig=0))

    wall = Wall(0, length * 1.6, piece2(zf, const(ri), const(rf)), 1.0, 1.0, 0.0, geometries, lambda x: per(x-zi), piece3(zi, zf, const(0), const(hei), const(0)), 0.5)
    
    chamber = Chamber(geometries=geometries,
                      wall=wall,
                      mesh=mesh,
                      monitors=monitors)
    return chamber


def high_dielectric(length, ri, rf, thickness, permitivity):
    zi = length * 0.3
    zf = zi + length

    geometries={}
    geometries["Dielectric"] = Tube(zi, zf, lin(zi, zf, ri, rf), lin(zi, zf, ri+thickness, rf+thickness), permitivity, 1.0, 0.0)

    monitors = []
    monitors.append(Monitor("Ez", "s", length * 1.3, length * 1.31, rf * 0.1, rf * 0.9, length * 1.3, length * 2.0))
    monitors.append(Monitor("Ez", "z", 0.0, length * 1.3, 0.0, np.max([ri, rf]) + thickness, 0, 4 * (np.max([ri, rf]) + thickness)))

    # 4000 10 10
    mesh = Mesh(2000 * DETAIL / 2, cleave(thickness / 5 / DETAIL * 2, sig=0), cleave(thickness / 5 / DETAIL * 2, sig=0))

    wall = Wall(0, length * 1.6, piece2(zf, const(ri), const(rf)), 1.0, 1.0, 0.0, geometries)
    
    chamber = Chamber(geometries=geometries,
                      wall=wall,
                      mesh=mesh,
                      monitors=monitors)
    return chamber


def con_phal(length, radius):
    z2 = length * 2.0
    z3 = z2 + length * 0.3
    z4 = z3 + length * 0.5
    z5 = z4 + radius

    def bound(x):
        return np.where(x < z2, const(radius)(x),
                        np.where(x < z3, np.sqrt(-(x - z2 - length * 0.15)**2 + (length * 0.15)**2) + 2 * radius,
                                 np.where(x < z4, const(2 * radius)(x),
                                          np.where(x < z5, np.sqrt(-(x - z4)**2 + radius**2) + radius, const(radius)(x)))))

    geometries={}

    monitors = []
    monitors.append(Monitor("Ez", "s", length * 3.0, length * 3.01, radius * 0.1, radius * 0.9, length * 3.0, length * 5.0))
    monitors.append(Monitor("Ez", "z", 0.0, length * 5.0, 0.0, radius * 4.5, 0, 4 * radius * 3.0))

    # 4000 10 10
    mesh = Mesh(2000 * DETAIL, cleave(radius / 30 / DETAIL, sig=0), cleave(radius / 30 / DETAIL, sig=0))

    wall = Wall(0, length * 5.0, bound, 1.0, 1.0, 0.0, geometries)
    
    chamber = Chamber(geometries=geometries,
                      wall=wall,
                      mesh=mesh,
                      monitors=monitors)
    return chamber


def bump(length, radius):
    z1 = length
    z2 = z1 + length / 10

    def bound(x):
        return np.where(x < z1, const(radius)(x),
                        np.where(x < z2, -0.5 * np.sqrt(-(x - z1 - length / 20)**2 + (length / 20)**2) + radius, const(radius)(x)))
                                 
    geometries={}

    monitors = []
    monitors.append(Monitor("Ez", "s", length * 1.1, length * 1.2, radius * 0.1, radius * 0.9, length * 1.1, length * 2.0))
    monitors.append(Monitor("Ez", "z", 0.0, length * 2.1, 0.0, radius, 0, 4 * radius))

    # 4000 10 10
    mesh = Mesh(2000 * DETAIL, cleave(radius / 50 / DETAIL, sig=0), cleave(radius / 50 / DETAIL, sig=0))

    wall = Wall(0, length * 2.1, bound, 1.0, 1.0, 0.0, geometries)
    
    chamber = Chamber(geometries=geometries,
                      wall=wall,
                      mesh=mesh,
                      monitors=monitors)
    return chamber


CHAMBERS = {
    #"cor_con": tap_corrugated(0.04, 0.7e-3, 0.7e-3, lin(0, 0.04, 0.5e-3, 0.5e-3), 0.5e-3),
    #"die_con": tap_dielectric(0.04, 2.0e-3, 2.0e-3, 225e-6, 3.8),
    #"die_high": high_dielectric(0.04, 1.0e-3, 1.0e-3, 1e-6, 1.1),
    #"die_tap": tap_dielectric(0.04, 1.95e-3, 2.05e-3, 225e-6, 3.8),
    #"con_phal": con_phal(0.03, 2e-3),
    #"bump": bump(0.03, 2e-3)
}


def sin_die(length, radius, thickness, permitivity):
    b1 = lambda x: np.sin(x*200)/5000 + radius
    b2 = lambda x: np.sin(x*200)/5000 + radius + thickness

    geometries={}
    geometries["Dielectric"] = Tube(length * 0.1, length * 1.1, b1, b2, permitivity, 1.0, 0.0)

    monitors = []

    mesh = Mesh(1000 * DETAIL, thickness / 2, thickness / 2)
    wall = Wall(0, length * 1.2, b2, 1.0, 1.0, 0.0, geometries)
    
    chamber = Chamber(geometries=geometries,
                      wall=wall,
                      mesh=mesh,
                      monitors=monitors)
    return chamber

def corr_tube(length, radius, thickness, permitivity, per, hei):
    b1 = const(radius)
    b2 = const(radius + thickness)

    geometries={}
    geometries["Corrugated"] = Tube(length * 0.1, length * 1.1, b1, b2, permitivity, 1.0, 0.0, per, hei)

    monitors = []

    mesh = Mesh(1000 * DETAIL, thickness / 2, thickness / 2)
    wall = Wall(0, length * 1.2, b1, 1.0, 1.0, 0.0, geometries)
    
    chamber = Chamber(geometries=geometries,
                      wall=wall,
                      mesh=mesh,
                      monitors=monitors)
    return chamber


def main():
    chamber = tap_corrugated(0.04, 0.7e-3, 0.7e-3, lin(0, 0.04, 2.0e-3, 2.0e-3), 0.5e-3)
    gen(chamber, "../Projects")

    for name, chamber in CHAMBERS.items():
        tim = datetime.datetime.now().strftime(r"%Y-%m-%d_%H:%M:%S")
        dir = f"{RUN_DIR}/{name}"
        os.makedirs(dir)
        os.makedirs(f"{dir}/figs")
        os.makedirs(f"{dir}/figs/temp")
        gen(chamber, dir)


if __name__ == "__main__":
    
    main()
    '''
    b1 = lambda x: -np.exp(-(50 * x + 1)) / 10000 + 0.1e-3
    b2 = const(2.0e-3)
    b3 = const(2.225e-3)

    dielectric = Tube(0.0, 0.1, b2, b3, 3.8, 1.0, 0.0)
    #substrate = Tube(0, 0.1, b2, b3, 1.0, 1.0, 0.0)

    geometries={"Dielectric":     dielectric}
    
    #geometries = {}

    #wall = Wall(0.0, 0.60,
    #            lambda z: np.where(z < 0.05, const(2e-3)(z), np.where(z > 0.55, const(1e-3)(z), lin(0.05, 0.55, 2e-3, 1e-3)(z))),
    #            1.0, 1.0, 0.0, geometries,
    #            lambda z: np.where(z >= 0.05 and z < 0.55, const(40e-6)(z), const(0.05)(z)),
    #            lambda z: np.where(z > 0.05 and z < 0.55, const(-50e-6)(z), const(0)(z)))
    
    #monitor = Monitor(0.57, 0.6, 0.0, 1e-3, 0.05, 0.1)

    #mesh = Mesh(50000, VRES / DETAIL, HRES / DETAIL)

    wall = Wall(0, 0.12, b2, 1.0, 1.0, 0.0, geometries)
    monitor = Monitor(0.099, 0.1, 0.1e-3, 0.2e-3, 0.09, 0.2)
    mesh = Mesh(int(0.1 / HRES) * DETAIL, VRES / DETAIL, HRES / DETAIL)

    chamber1 = Chamber(geometries=geometries)
    #chamber1.wall = wall
    chamber1.mesh = mesh
    chamber1.monitors = monitor

    #gen(chamber1, "../Projects")
    '''