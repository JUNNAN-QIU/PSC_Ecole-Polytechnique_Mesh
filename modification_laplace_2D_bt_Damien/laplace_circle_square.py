import math
import numpy as np
import matplotlib.pyplot as plt


# Variables globales
########################

# Rayon du cercle utilise en tant que frontiere
side = 1.8

# Nombre d'echantillons de la methode de Monte Carlo (nombre de "marches aleatoire")
walkSamples = 128

# Distance limite en dessous de laquelle on considere que l'on est assez proche du bord
epsilon = 0.01

# Resolution en pixel de l'echantillonnage des positions initiales
imageSample = 256


# Functions
##########################


# Helper function: Norm of a 2D vector (x,y)
def norm(p):
    return math.sqrt(p[0]*p[0]+p[1]*p[1])

# User-defined fonction providing the value of the boundary at a given position p (this is the function g(x))
def functionBoundary(p):
    # Example of function, but can be anything
    if p[0]>0:
        return 10
    else:
        return 0



def justify_whether_in_the_square(p):
    if math.fabs(p[0]) < side / 2 - epsilon and math.fabs(p[1]) < side / 2 - epsilon:
        return True
    else:
        return False

# Implementation of the solver
def solve(p0, F):

    sum = 0
    for walk in range(walkSamples): # Monte Carlo

        p = p0 # Start at the initial position

        # Walk as long as the point remains far from the boundary
        while(justify_whether_in_the_square(p)):
            
            internalRadius = min(abs(abs(p[0])-abs(side/2)),abs(abs(p[1])-abs(side/2)))
            theta = 2*np.pi * np.random.rand() 

            # generate a new point on a circle centered at p and touching the boundary
            p = (p[0]+internalRadius*math.cos(theta), p[1]+internalRadius*math.sin(theta))
            
        # Integration
        sum += F(p)/walkSamples

    return sum






# Generate the picture from all the initial positions in a grid
res = np.zeros((imageSample,imageSample))
for kx in range(imageSample):
    for ky in range(imageSample):

        # Initial position in [-1,1]
        p0 = (2*kx/(imageSample-1)-1, 2*ky/(imageSample-1)-1)

        if math.fabs(p0[0])<side/2 and math.fabs(p0[1])<side/2: # solve the system only for points inside the circle
            res[kx,ky] = solve(p0, functionBoundary)

# Display the results
plt.gray()
plt.imshow(res)
plt.show()