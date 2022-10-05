from sdf_3D import *
import math
import numpy as np
import matplotlib.pyplot as plt
import multiprocessing
from multiprocessing import Process, Pool

# Variables globales
########################

# Rayon du cercle utilise en tant que frontiere
circleRadius = 0.9

# Nombre d'echantillons de la methode de Monte Carlo (nombre de "marches aleatoire")
walkSamples = 32

# Distance limite en dessous de laquelle on considere que l'on est assez proche du bord
epsilon = 0.01

# Resolution en pixel de l'echantillonnage des positions initiales
imageSample = 128

# Functions
##########################


# Helper function: Norm of a 2D vector (x,y)
# def norm(p):
#     return math.sqrt(p[0]*p[0]+p[1]*p[1]+p[2]*p[2])

# User-defined fonction providing the value of the boundary at a given position p (this is the function g(x))
def functionBoundary(p):
    # Example of function, but can be anything
    if p.z > 0:
        return 1
    else:
        return 0.2

# Implementation of the solver


def solve(p0, F, sdf_current):

    sum = 0
    for walk in range(walkSamples):  # Monte Carlo

        p = p0  # Start at the initial position

        # Walk as long as the point remains far from the boundary
        while(sdf_current.distance(p) < -epsilon):

            internalRadius = - sdf_current.distance(p)
            theta = 2*np.pi * np.random.rand()
            phi = np.pi * np.random.rand()

            # generate a new point on a circle centered at p and touching the boundary
            p = vec3(p.x+internalRadius*math.sin(theta)*math.cos(phi), p.y+internalRadius*math.sin(theta)*math.sin(phi),
                     p.z+internalRadius*math.cos(theta))

        # Integration
        sum += F(p)/walkSamples

    return sum


def image_task(kx, ky, kz, sdf_current):
    # Initial position in [-1,1]
    p0 = vec3(2*kx/(imageSample-1)-1, 2*ky /
              (imageSample-1)-1, 2*kz/(imageSample-1)-1)

    # solve the system only for points inside the circle
    if sdf_current.distance(p0) < 0:
        return [kx, ky, kz, solve(p0, functionBoundary, sdf_current)]


if __name__ == '__main__':

    # sdf_current = SDF_sphere_3D(0.9)
    # sdf_current = sdBox(vec3(0.9,0.8,0.7))
    # sdf_current = sdRoundBox(vec3(0.8,0.8,0.7),0.1)
    sdf_current = sdLink(0.5, 0.2, 0.1)

    # Generate the picture from all the initial positions in a grid
    res1 = np.zeros((imageSample, imageSample))
    res2 = np.zeros((imageSample, imageSample))
    res3 = np.zeros((imageSample, imageSample))
    waiting_work_list = []
    for kx in range(imageSample):
        for ky in range(imageSample):
            for kz in range(imageSample):
                waiting_work_list.append((kx, ky, kz))

    pool = multiprocessing.Pool(6)
    print(len(waiting_work_list))
    # pool = multiprocessing.Pool(multiprocessing.cpu_count())

#################################
    result = []
    for kx, ky, kz in waiting_work_list:
        result.append(pool.apply_async(func=image_task,
                      args=(kx, ky, kz, sdf_current)))
    pool.close()
    pool.join()

    for r in result:
        tmp = r.get()
        if tmp == None:
            continue
        else:
            kx = tmp[0]
            ky = tmp[1]
            kz = tmp[2]
            re = tmp[3]
            if kz == imageSample//2:
                res1[kx, ky] = re
            if ky == imageSample//2:
                res2[kx, kz] = re
            if kx == imageSample//2:
                res3[ky, kz] = re

    # Display the results
    plt.figure(1)
    plt.gray()
    plt.imshow(res1)
    # plt.show()
    plt.figure(2)
    plt.gray()
    plt.imshow(res2)
    # plt.show()
    plt.figure(3)
    plt.gray()
    plt.imshow(res3)
    plt.show()
