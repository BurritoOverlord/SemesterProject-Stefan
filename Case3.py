import shapely.geometry as sg
import shapely.ops as so
import matplotlib.pyplot as plt
import math

import move_robot as mr
import geometry as g

#Misc
gs_dx = 0.10  # gripper surface 0.5 width
gs_dy = 0.05  # gripper length from end effector to edge of gripper arms
gs_dy2 = 0.04  # gripper length from tool center point to the back of gripper
r_cup = 0.055


def algorithm(listCups, id_cup, id_obst):

    shape_obst = []
    for obj in listCups:
        if obj.ID == id_cup:
            cX = obj.center[0]
            cY = obj.center[1]

        for i, ID in enumerate(id_obst, 0):
            if obj.ID == ID:
                shape_obst.append(sg.Point((obj.center[0], obj.center[1])).buffer(r_cup))

    new_shape = so.unary_union(shape_obst)

    fig, axs = plt.subplots()
    axs.set_aspect('equal', 'datalim')
    for geom in new_shape.geoms:
        xs, ys = geom.exterior.xy
        axs.fill(xs, ys, alpha=0.5, fc='r', ec='black')

    origin = (cX, cY)
    r_origin = (cX, cY - mr.grip_dy)

    ptA = (origin[0] - gs_dx, origin[1] + gs_dy)
    ptB = (origin[0] + gs_dx, origin[1] + gs_dy)
    ptC = (r_origin[0] + gs_dx, r_origin[1] - 0.02)
    ptD = (r_origin[0] - gs_dx, r_origin[1] - 0.02)

    grab = False
    angle = 0
    while angle < 2 * math.pi:
        ptA = g.rotate(origin[0], origin[1], ptA[0], ptA[1], angle)
        ptB = g.rotate(origin[0], origin[1], ptB[0], ptB[1], angle)
        ptC = g.rotate(origin[0], origin[1], ptC[0], ptC[1], angle)
        ptD = g.rotate(origin[0], origin[1], ptD[0], ptD[1], angle)
        r_origin = g.rotate(origin[0], origin[1], r_origin[0], r_origin[1], angle)

        r1 = sg.Polygon([ptA, ptB, ptC, ptD])
        isIntersection = r1.intersection(new_shape)
        print("intersection", isIntersection)

        if isIntersection:
            angle += math.pi / 10
        else:
            grab = True
            print("Grabing Cup with angle", angle)
            break

    print("angle", angle, " grab", grab)
    xs, ys = r1.exterior.xy
    axs.fill(xs, ys, alpha=0.5, fc='green', ec='black')

    circle = plt.Circle(origin, 0.055, color='blue', ec='black')
    plt.gcf().gca().add_patch(circle)
    circle = plt.Circle(r_origin, 0.005, color='black', ec='black')
    plt.gcf().gca().add_patch(circle)
    if grab:
        plt.title('Cup is grabbed')
        plt.show()
        return angle
    else:
        plt.title('Cannot grab Cup')
        plt.show()
        return None


