import copy

import move_robot
import geometry
import math
import Case3

# misc. hyperparameters
rMax = 0.156 + 0.05  # maximum radius to check if cups obstruct the gripper (usually go for 1.3 times the gripper dy
dCups = 0.19 # distance between each cup in the end position
xLoc = -0.11
yLoc = 0.235
rCups = 0.055 * 1.5


def simple_pouring(listCups):

    listCups_endlocations = []
    listCups_moved = []

    # initialize list tables
    for i, obj in enumerate(listCups, 0):
        alpha = geometry.get_angle(obj.center, obj.edge)
        obj.orientation = alpha
        listCups_moved.append(False)
        listCups_endlocations.append([xLoc, yLoc+(i)*dCups])

    """
    for i, obj in enumerate(listCups, 0):
        print(obj.ID, obj.orientation, sep=' ')
    """
    position_cups(listCups_moved, listCups, listCups_endlocations)

    #pouring_cups(listCups_moved, listCups_center, listCups_alpha, listCups_endlocations)
    return


def position_cups(listCups_moved, listCups, listCups_endlocations):
    # cycle through all cups and check if they can and should be moved
    while not (check(listCups_moved)):
        for i in range(len(listCups)):
            # check if there is any obstruction
            nb_obst, id_obst = check_obstruction(i, listCups)
            print("Number of Obstructions",listCups[i].ID, nb_obst)

            # Case 1: No Obstruction
            if nb_obst == 0:
                print("No Detected Obstruction")
                # Grab cup with fixed robot wrist angle
                angle = math.pi
                move_robot.grab_cup(listCups[i].center[0], listCups[i].center[1], angle)
                move_robot.place_cup(listCups_endlocations[i][0], listCups_endlocations[i][1])

                # change the center position in the list & update alpha
                listCups[i].center = listCups_endlocations[i]
                listCups_moved[i] = True
                listCups[i].orientation -= math.pi/2
                print("alpha")
                print(listCups[i].orientation)



            # Case 2: 1 Obstruction
            if nb_obst == 1:
                print("1 Detected Obstruction")
                # calculate the angle for which the gripper needs to grab the cup properly
                # Here we just make it grab at the opposite of the other cup
                angle = geometry.get_angle(listCups[i].center, listCups[id_obst[0]].center)
                move_robot.grab_cup(listCups[i].center[0], listCups[i].center[1], angle)
                move_robot.place_cup(listCups_endlocations[i][0], listCups_endlocations[i][1])

                listCups[i].center = listCups_endlocations[i]
                listCups_moved[i] = True
                listCups[i].orientation -= math.pi / 2 + angle

            # Case 3: 2 or more Obstructions
            if nb_obst > 1:
                print("2 Detected Obstruction")
               # Case3.case3_algorithm(listCups)


        print(listCups_moved)
    return

def pouring_cups(listCups_moved, listCups_center,listCups_alpha, listCups_endlocations):

    #Pour cup 1 into cup 2
    print("Pouring cups")
    x = 0
    angle = math.pi/2
    move_robot.grab_cup(listCups_center[x][0], listCups_center[x][1], angle)
    move_robot.place_cupP(0.2, 0.5)
    listCups_alpha[x] += angle
    #angle that wrist is supposed to take
    print(listCups_alpha[x])

    move_robot.grab_cupP(0.2, 0.5, listCups_alpha[x])
    move_robot.pouring(listCups_endlocations[1][0],listCups_endlocations[1][1])
    return

def check_obstruction(i, listCups):
    obstruction = 0
    obstruction_id = []
    obstruction_dist = []
    for j in range(len(listCups)):
        if i != j:
            dist = geometry.calculate_distance(listCups[i].center, listCups[j].center)
            if dist < rMax:
                obstruction += 1
                obstruction_id.append(j)
                obstruction_dist.append(dist)
        else:
            continue

    print()

    #Make obstruction_id list in descending order based on the distance
    obstruction_order = copy.copy(obstruction_dist)
    obstruction_order.sort(reverse=True)
    for j in range(len(obstruction_order)):
        for k in range(len(obstruction_order)):
            if obstruction_dist[j] == obstruction_order[k]:
                obstruction_dist[j] = k

    obstruction_id = [obstruction_id[j] for j in obstruction_dist]

    return obstruction, obstruction_id

def check(list):
    for item in list:
        if item == False:
            return False
    return True