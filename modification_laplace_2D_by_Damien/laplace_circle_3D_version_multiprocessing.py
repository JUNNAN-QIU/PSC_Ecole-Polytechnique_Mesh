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
imageSample = 64


# Functions
##########################


# Helper function: Norm of a 2D vector (x,y)
def norm(p):
    return math.sqrt(p[0]*p[0]+p[1]*p[1]+p[2]*p[2])

# User-defined fonction providing the value of the boundary at a given position p (this is the function g(x))
def functionBoundary(p):
    # Example of function, but can be anything
    if p[2]>0:
        return 10
    else:
        return 0

# Implementation of the solver
def solve(p0, F):

    sum = 0
    for walk in range(walkSamples): # Monte Carlo

        p = p0 # Start at the initial position

        # Walk as long as the point remains far from the boundary
        while( norm(p)<circleRadius-epsilon ):
            
            internalRadius = circleRadius-norm(p)
            theta = 2*np.pi * np.random.rand() 
            phi = np.pi * np.random.rand()

            # generate a new point on a circle centered at p and touching the boundary
            p = (p[0]+internalRadius*math.sin(theta)*math.cos(phi), p[1]+internalRadius*math.sin(theta)*math.sin(phi), \
                p[2]+internalRadius*math.cos(theta))
            
        # Integration
        sum += F(p)/walkSamples

    return sum



def image_task(kx,ky,kz):
    # Initial position in [-1,1]
    p0 = (2*kx/(imageSample-1)-1, 2*ky/(imageSample-1)-1, 2*kz/(imageSample-1)-1)

    if norm(p0)<circleRadius: # solve the system only for points inside the circle
        return [kx,ky,kz,solve(p0, functionBoundary)]

    




if __name__ == '__main__':

    # Generate the picture from all the initial positions in a grid
    res1 = np.zeros((imageSample,imageSample))
    res2 = np.zeros((imageSample,imageSample))
    res3 = np.zeros((imageSample,imageSample))
    waiting_work_list = []
    for kx in range(imageSample):
        for ky in range(imageSample):
            for kz in range(imageSample):
                waiting_work_list.append((kx,ky,kz))



    pool = multiprocessing.Pool(6)
    print(len(waiting_work_list))
    # pool = multiprocessing.Pool(multiprocessing.cpu_count())

#################################
    result = []
    for kx,ky,kz in waiting_work_list:
        result.append(pool.apply_async(func=image_task,args=(kx,ky,kz)))
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
                res1[kx,ky] = re
            if ky == imageSample//2:
                res2[kx,kz] = re
            if kx == imageSample//2:
                res3[ky,kz] = re

    # Display the results
    plt.figure(1)
    plt.gray()
    plt.imshow(res1)
    plt.show()
    plt.figure(2)
    plt.gray()
    plt.imshow(res2)
    plt.show()
    plt.figure(3)
    plt.gray()
    plt.imshow(res3)
    plt.show()