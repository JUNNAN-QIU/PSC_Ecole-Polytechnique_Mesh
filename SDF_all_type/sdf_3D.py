
import numpy as np
from numpy.lib import math


class vec3:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self) -> str:
        return ("x: %f  y: %f z: %f" % (self.x, self.y, self.z))

    def xy(self):
        return np.array(self.x, self.y)

    def yz(self):
        return np.array(self.y, self.z)

    def xz(self):
        return np.array(self.x, self.z)

    def xyz(self):
        return np.array(self.x, self.y, self.z)

    def abs_3D(self):
        new_p = vec3(abs(self.x), abs(self.y), abs(self.z))
        return new_p

    def minus(self, p2):
        rt = vec3(self.x-p2.x, self.y-p2.y, self.z-p2.z)
        return rt


class vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self) -> str:
        return ("x: %f  y: %f" % (self.x, self.y))

    def xy(self):
        return np.array(self.x, self.y)

    def norm2d(self):
        return math.sqrt(self.x**2 + self.y**2)


class SDF_3D:
    def length(self, p):
        return math.sqrt(p.x**2 + p.y**2 + p.z**2)

    def max(self, p, a):
        rt = vec3(max(p.x, a), max(p.y, a), max(p.z, a))
        return rt

    def min(self, p, a):
        rt = vec3(min(p.x, a), min(p.y, a), min(p.z, a))
        return rt


class SDF_sphere_3D(SDF_3D):
    def __init__(self, rayon):
        self.s = rayon

    def distance(self, p):
        return self.length(p)-self.s


class sdBox(SDF_3D):
    def __init__(self, b) -> None:
        self.b = b

    def distance(self, p):
        q = (p.abs_3D()).minus(self.b)
        return self.length(self.max(q, 0.0)) + min(max(q.x, max(q.y, q.z)), 0.0)


class sdRoundBox(SDF_3D):
    def __init__(self, b, r):
        self.b = b
        self.r = r

    def distance(self, p):
        q = (p.abs_3D()).minus(self.b)
        return self.length(self.max(q, 0.0)) + min(max(q.x, max(q.y, q.z)), 0.0) - self.r


class sdLink(SDF_3D):
    def __init__(self, le, r1, r2):
        self.le = le
        self.r1 = r1
        self.r2 = r2

    def distance(self, p):
        q = vec3(p.x, max(abs(p.y)-self.le, 0.0), p.z)
        q_xy = vec2(q.x, q.y)
        return vec2(q_xy.norm2d()-self.r1, q.z).norm2d() - self.r2
