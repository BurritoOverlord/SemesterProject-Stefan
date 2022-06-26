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
xUnstructured = 0.2  # center of unstructured area
yUnstructured = 0.3  # center of unstructured area


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

    pouring_cups(listCups)
    return


def position_cups(listCups_moved, listCups, listCups_endlocations):
    # cycle through all cups and check if they can and should be moved
    while not (check(listCups_moved)):
        cycle = copy.copy(listCups_moved)
        for i in range(len(listCups)):
            if not listCups_moved[i]:
                # check if there is any obstruction
                print("Debug 1")
                nb_obst, id_obst = check_obstruction(i, listCups)
                print("Number of Obstructions for Cup",listCups[i].ID,"is",nb_obst)

                # Case 1: No Obstruction
                if nb_obst == 0:
                    print("Cup", listCups[i].ID, "can be grabbed")
                    # Grab cup with fixed robot wrist orientation
                    angle = 0
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

                    print("Cup", listCups[i].ID, "can be grabbed")
                    # calculate the angle for which the gripper needs to grab the cup properly
                    # Here we just make it grab at the opposite of the other cup
                    for obj in listCups:
                        for ID in id_obst:
                            if obj.ID == ID:
                                angle = geometry.get_angle(listCups[i].center, obj.center)

                    move_robot.grab_cup(listCups[i].center[0], listCups[i].center[1], angle)
                    move_robot.place_cup(listCups_endlocations[i][0], listCups_endlocations[i][1])

                    listCups[i].center = listCups_endlocations[i]
                    listCups_moved[i] = True
                    listCups[i].orientation -= math.pi / 2 + angle

                # Case 2: Obstructions
                if nb_obst > 1:
                    # calculate the angle for which the gripper needs to grab the cup properly
                    angle = Case3.algorithm(listCups, listCups[i].ID, id_obst)

                    if angle is not None:
                        print("Cup",listCups[i].ID,"can be grabbed")
                        move_robot.grab_cup(listCups[i].center[0], listCups[i].center[1], angle)
                        move_robot.place_cup(listCups_endlocations[i][0], listCups_endlocations[i][1])

                        listCups[i].center = listCups_endlocations[i]
                        listCups_moved[i] = True
                        listCups[i].orientation -= math.pi / 2 + angle
                    else:
                        print("Cup", listCups[i].ID, "cannot be grabbed at this loop")

        if cycle == listCups_moved:
            print("Cups are too close together, cannot perform grasping motion")
            return
    return

def pouring_cups(listCups):

    #Pour Cup_ID_5 into Cup_ID_6
    print("Pouring Cup_ID_5 into Cup_ID_6")
    pouring = [False, False]
    xTMP = 0
    yTMP = 0
    xReturn = 0
    yReturn = 0
    for obj in listCups:
        if obj.ID == 4:
            angle = math.pi / 2
            move_robot.grab_cup(obj.center[0], obj.center[1], angle)
            move_robot.place_cupP(xUnstructured, yUnstructured)  # Place Cup in center of Unstructured area
            obj.orientation += angle
            print("Cup_ID_5 Orientation:", obj.orientation)
            move_robot.grab_cupP(xUnstructured, yUnstructured, obj.orientation)
            pouring[0] = True
            xReturn = obj.center[0]
            yReturn = obj.center[1]

        if obj.ID == 5:
            xTMP = obj.center[0]
            yTMP = obj.center[1]
            pouring[1] = True

    if check(pouring):
        move_robot.pouring(xTMP,yTMP)
        move_robot.place_cup(xReturn, yReturn)
    else:
        print("Cannot Perform Specific Process as CUP_ID_5 or 6 is not present in SET-UP")
    return

def check_obstruction(i, listCups):
    obstruction = 0
    obstruction_id = []
    for j in range(len(listCups)):
        if i != j:
            dist = geometry.calculate_distance(listCups[i].center, listCups[j].center)
            if dist < rMax:
                obstruction += 1
                obstruction_id.append(listCups[j].ID)
        else:
            continue

    return obstruction, obstruction_id

def check(list):
    for item in list:
        if item == False:
            return False
    return True
