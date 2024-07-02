import pickle

import numpy as np
import sympy as sp

class Geometry:
    class Boundary:
        def __init__(self):
            self.zi = 0.0
            self.zf = 0.1

    class PointBoundary(Boundary):
        def __init__(self):
            super().__init__()
            self.zs = [self.zi, self.zf]
            self.rs = [0.01, 0.01]

    class EquationBoundary(Boundary):
        def __init__(self):
            super().__init__()
            self.equation_text = "0.1 * z + 0.01"
            self.resolution = 0.01

            self.symbols = sp.symbols('z')
            self.equation_function = None

            self.zs = []
            self.rs = []

            self._gen_function()

        def _gen_function(self):
            equation = sp.sympify(self.equation_text)
            self.equation_function = sp.lambdify(self.symbols, equation, 'numpy')

            self.zs = np.linspace(self.zi, self.zf, int((self.zi - self.zi) / self.resolution), endpoint=True)
            self.rs = self.equation_function(self.zs)

    class Layer:
        def __init__(self):
            self.name = "New Layer"

            self.zi = 0.0
            self.zf = 0.1

            self.bottom_type = "point"
            self.bottom = Geometry.PointBoundary()

            self.top_type = "point"
            self.top = Geometry.PointBoundary()
            self.top.rs = [0.02, 0.02]

    class Wall:
        def __init__(self):
            self.name = "Chamber Wall"

            self.zi = 0.0
            self.zf = 0.1

            self.bottom_type = "point"
            self.bottom = Geometry.PointBoundary()

    def __init__(self, path):
        self.layers = []
        self.mesh = None
        self.monitors = []
        self.wall = Geometry.Wall()

        self.path = path

        self.save()

    def new_layer(self):
        self.layers.append(Geometry.Layer())
        self.save()

    def save(self):
        with open(self.path, 'wb') as file:
            pickle.dump(self, file)
            file.close()
