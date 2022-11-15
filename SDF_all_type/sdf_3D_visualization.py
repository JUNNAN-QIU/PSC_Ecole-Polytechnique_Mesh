from matplotlib import cm
from sdf_3D_class import *
import math
import numpy as np
import matplotlib.pyplot as plt
import multiprocessing
from multiprocessing import Process, Pool
import yaml
import ipyvolume as ipv
from mpl_toolkits import mplot3d
from pylab import *    # fig = plt.figure(4)
    # ax = fig.add_subplot(111, projection='3d')
    
    
    # # creating the heatmap
    # img = ax.scatter(x_for_plot, y_for_plot, z_for_plot, c=re_for_plot, cmap='Greens')
    
    # # adding title and labels
    # ax.set_title("3D Heatmap")
    # ax.set_xlabel('X-axis')
    # ax.set_ylabel('Y-axis')
    # ax.set_zlabel('Z-axis')
    
    # # displaying plot
    # plt.show()
    # fig = plt.figure(4)
    # ax = fig.add_subplot(111, projection='3d')
    
    
    # # creating the heatmap
    # img = ax.scatter(x_for_plot, y_for_plot, z_for_plot, c=re_for_plot, cmap='Greens')
    
    # # adding title and labels
    # ax.set_title("3D Heatmap")
    # ax.set_xlabel('X-axis')
    # ax.set_ylabel('Y-axis')
    # ax.set_zlabel('Z-axis')
    
    # # displaying plot
    # plt.show()

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
        return 0

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
    path_yaml = "template.yaml"
    dict_yaml = yaml.load(open(path_yaml).read(), Loader=yaml.Loader)

    sdf_current = None  # Just for eliminating the warning
    LOC = "sdf_current = " + dict_yaml["sdf"]
    exec(LOC)

    walkSamples = dict_yaml["walkSamples"]
    epsilon = dict_yaml["epsilon"]
    imageSample = dict_yaml["imageSample"]

    V = np.zeros((imageSample,imageSample,imageSample))
    # Generate the picture from all the initial positions in a grid
    res1 = np.zeros((imageSample, imageSample))
    res2 = np.zeros((imageSample, imageSample))
    res3 = np.zeros((imageSample, imageSample))
    waiting_work_list = []
    for kx in range(imageSample):
        for ky in range(imageSample):
            for kz in range(imageSample):
                waiting_work_list.append((kx, ky, kz))

    # pool = multiprocessing.Pool(6)
    print(len(waiting_work_list))
    pool = multiprocessing.Pool(multiprocessing.cpu_count())

#################################
    result = []
    for kx, ky, kz in waiting_work_list:
        result.append(pool.apply_async(func=image_task,
                      args=(kx, ky, kz, sdf_current)))
    pool.close()
    pool.join()

    x_for_plot = []
    y_for_plot = []
    z_for_plot = []
    re_for_plot = []

    for r in result:
        tmp = r.get()
        if tmp == None:
            continue
        else:
            x_for_plot.append(tmp[0])
            y_for_plot.append(tmp[1])
            z_for_plot.append(tmp[2])
            re_for_plot.append(tmp[3])

            V[tmp[0]][tmp[1]][tmp[2]] = tmp[3]*100//100

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



    # creating figures)
    fig = plt.figure(4)
    ax = fig.add_subplot(111, projection='3d')
    
    
    # creating the heatmap
    img = ax.scatter(x_for_plot, y_for_plot, z_for_plot, c=re_for_plot, cmap='Greens')
    
    # adding title and labels
    ax.set_title("3D Heatmap")
    ax.set_xlabel('X-axis')
    ax.set_ylabel('Y-axis')
    ax.set_zlabel('Z-axis')
    
    # displaying plot
    plt.show()
