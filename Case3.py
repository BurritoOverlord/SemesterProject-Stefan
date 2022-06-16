import shapely.geometry as sg
import shapely.ops as so
import matplotlib.pyplot as plt
import math

def rotate(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in radians.
    """
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy

origin = (0.2, 0.6)
r_origin = (0.2 + 0.12, 0.6)

ptA = (origin[0] - 0.07, origin[1]+0.08)
ptB = (origin[0] - 0.07, origin[1]-0.08)
ptC = (r_origin[0]*1.2, r_origin[1]-0.08)
ptD = (r_origin[0]*1.2, r_origin[1]+0.08)

r1 = sg.Polygon([ptA,
   ptB,
   ptC,
   ptD,
])

angle = - math.pi/2
ptA = rotate(origin,ptA,angle)
ptB = rotate(origin,ptB,angle)
ptC = rotate(origin,ptC,angle)
ptD = rotate(origin,ptD,angle)
r_origin = rotate(origin,r_origin,angle)

r1 = sg.Polygon([ptA,
   ptB,
   ptC,
   ptD,
])


r2 = sg.Point((0.05, 0.6)).buffer(0.055)
r3 = sg.Point((0.2, 0.45)).buffer(0.055)
new_shape = so.unary_union([r2, r3])


"""
fig, axs = plt.subplots()
axs.set_aspect('equal', 'datalim')
xs, ys = r2.exterior.xy
axs.fill(xs, ys, alpha=0.5, fc='r', ec='black')



for geom in new_shape.geoms:
    xs, ys = geom.exterior.xy
    axs.fill(xs, ys, alpha=0.5, fc='r', ec='black')
"""

"""
xs, ys = r1.exterior.xy
axs.fill(xs, ys, alpha=0.5, fc='green', ec='black')

circle = plt.Circle(origin, 0.055 , color='blue', ec='black')
plt.gcf().gca().add_patch(circle)
circle = plt.Circle(r_origin, 0.005 , color='black', ec='black')
plt.gcf().gca().add_patch(circle)
plt.title('Case 1: 0 detected obstructions (Grab Cup)')
"""
isIntersection = r1.intersection(r3)

#print(isIntersection)

plt.show()

PointA=(200,300)
origin=(100,100)




