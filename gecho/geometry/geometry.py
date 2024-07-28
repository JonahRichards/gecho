import pickle

import numpy as np
import sympy as sp
from sympy.core.sympify import SympifyError


class Geometry:
    class Boundary:
        def __init__(self):
            self.zi = 0.0
            self.zf = 0.1

    class PointBoundary(Boundary):
        def __init__(self):
            super().__init__()
            self.zs = [self.zi, 0.02, 0.04, 0.06, 0.08, self.zf]
            self.rs = [0.01, 0.02, 0.01, 0.02, 0.01, 0.02]

        def new_zi(self, new_zi):
            if self.zf - new_zi > 0:
                scale_factor = (self.zf - new_zi) / (self.zf - self.zi)
                self.zs = [(z - self.zi) * scale_factor + new_zi for z in self.zs]
                self.zi = new_zi

        def new_zf(self, new_zf):
            if new_zf - self.zi > 0:
                scale_factor = (new_zf - self.zi) / (self.zf - self.zi)
                self.zs = [(z - self.zf) * scale_factor + new_zf for z in self.zs]
                self.zf = new_zf

    class EquationBoundary(Boundary):
        def __init__(self):
            super().__init__()
            self.equation_text = "0.1 * z + 0.01"
            self.num_points = 10

            self.symbols = sp.symbols('z')

            self.zs = []
            self.rs = []

            self.gen_function()

        def gen_function(self):
            if self.num_points > 0:
                try:
                    equation = sp.sympify(self.equation_text)
                    equation_function = sp.lambdify(self.symbols, equation, 'numpy')

                    self.zs = np.linspace(self.zi, self.zf, self.num_points, endpoint=True)
                    rs = equation_function(self.zs)
                    if isinstance(rs, np.ndarray) and len(rs) == len(self.zs) and rs.dtype == float:
                        self.rs = rs
                    else:
                        return
                except (SympifyError, TypeError):
                    pass

        def new_zi(self, new_zi):
            if self.zf - new_zi > 0:
                self.zi = new_zi
                self.gen_function()

        def new_zf(self, new_zf):
            if new_zf - self.zi > 0:
                self.zf = new_zf
                self.gen_function()

    class Layer:
        def __init__(self):
            self.name = "New Layer"

            self.ep = 1.0
            self.mu = 1.0
            self.sg = 0.0

            self.bot_type = "points"
            self.bot = Geometry.PointBoundary()

            self.top_type = "points"
            self.top = Geometry.PointBoundary()
            self.top.rs = [r + 0.01 for r in self.top.rs]

        def new_zi(self, zi):
            self.top.new_zi(zi)
            self.bot.new_zi(zi)

        def new_zf(self, zf):
            self.top.new_zf(zf)
            self.bot.new_zf(zf)

    class Wall:
        def __init__(self):
            self.name = "Chamber Wall"

            self.ep = 1.0
            self.mu = 1.0
            self.sg = 0.0

            self.bot_type = "points"
            self.bot = Geometry.PointBoundary()

            self.bot.rs = [r + 0.01 for r in self.bot.rs]

        def new_zi(self, zi):
            self.bot.new_zi(zi)

        def new_zf(self, zf):
            self.bot.new_zf(zf)

        def set_bot_function(self):
            self.bot = Geometry.EquationBoundary()
            self.bot_type = "function"

        def set_bot_points(self):
            self.bot = Geometry.PointBoundary()
            self.bot_type = "points"

    class Mesh:
        name = "Mesh"

        def __init__(self):
            self.mesh_length = 1000
            self.start_position = 0
            self.time_steps = -1
            self.step_y = 0.0001
            self.step_z = 0.0001
            self.n_steps_in_conductive = 10
            self.adjust_mesh = 0

    class Beam:
        name = "Beam"

        def __init__(self):
            self.bunch_sigma = 0.0001
            self.offset = 0
            self.injection_time_step = 0

    class Model:
        name = "Model"

        def __init__(self):
            self.wake_int_method = "ind"
            self.modes = [0]
            self.particle_motion = 0
            self.particle_field = 1
            self.current_filter = 0
            self.particle_loss = 0

    class Monitor:
        def __init__(self):
            self.name = "New Monitor"
            self.field_component = "Ez"
            self.type = "z"
            self.z_0 = 0.0
            self.z_1 = 0.01
            self.r_0 = 0.0
            self.r_1 = 0.01
            self.s_0 = 0.0
            self.s_1 = 0.01

            self.n = 1

    def __init__(self):
        self.mesh = Geometry.Mesh()
        self.beam = Geometry.Beam()
        self.model = Geometry.Model()
        self.wall = Geometry.Wall()
        self.layers = []
        self.monitors = []

        self.path = ""

    def new_layer(self):
        self.layers.append(Geometry.Layer())
        self.save()

    def new_monitor(self):
        self.monitors.append(Geometry.Monitor())
        self.save()

    def save(self):
        try:
            with open(self.path, 'wb') as file:
                pickle.dump(self, file)
                file.close()
        except FileNotFoundError:
            pass
