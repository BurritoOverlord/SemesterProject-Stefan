import numpy as np
import cv2
import cv2.aruco as aruco
import matplotlib.pyplot as plt

# my modules
import geometry

"SETTINGS AND VARIABLES ________________________________________________________________"

video_resolution = (640, 480)  # resolution the video capture will be resized to, smaller sizes can speed up detection

# Environment width and height
r_width = 320
r_height = 197

# Calibration Parameters
calibrationMatrix = np.load('calibration_matrix.npy')
distortionCoefficient = np.load('distortion_coefficients.npy')

# ArUco marker ref origin in the coordinates of the UR5 base ref frame
origin_L = [0.36, 0.4, 0.31504431455331383, -3.13713023885791, 0.08284771453405795,
            -0.009878696005977336]

# misc. hyperparameters
rCups = 0.055  # Cup radius in m
rMax = 0.12
dist1 = 0.02
dist2 = dist1 + rCups

# misc. Terrain Field to be defined at the beginning
xMax = 0.5
yMax = 1
xMin = -0.2

"Classes ________________________________________________________________"
class Marker(object):
    def __init__(self, type, ID, center, edge):
        self.type = type
        self.ID = ID
        self.center = center
        self.edge = edge

class Cup(object):
    def __init__(self, type, ID, center, edge, orientation = None, ingredient = None):
        self.type = type
        self.ID = ID
        self.center = center
        self.edge = edge
        self.orientation = orientation
        self.ingredient = ingredient



def findArUcoMarkers(frame, markerSize=4, totalMarkers=50, draw=True):
    # start by converting to gray scale
    img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    key = getattr(aruco, f'DICT_{markerSize}X{markerSize}_{totalMarkers}')
    arucoDict = aruco.getPredefinedDictionary(key)
    arucoParam = aruco.DetectorParameters_create()
    bbox, ids, rejected = aruco.detectMarkers(img_gray, arucoDict, parameters=arucoParam,
                                              cameraMatrix=calibrationMatrix, distCoeff=distortionCoefficient)

    # Store the "center coordinates" of all marker in detected objects
    # in order from the upper left in the clockwise direction.
    detected_markers = list()  # Storage destination of center coordinates for all detected markers with their ID
    field_corners = np.empty((4, 2))  # detect the corner values of the "play field" ->marker ID: 0-3
    # verify *at least* one ArUco marker was detected
    if len(bbox) > 0:
        # flatten the ArUco IDs list
        ids = ids.flatten()
        # loop over the detected ArUCo corners
        for (markerCorner, markerID) in zip(bbox, ids):
            # extract the marker corners (which are always returned
            # in top-left, top-right, bottom-right, and bottom-left
            # order)
            corners = markerCorner.reshape((4, 2))
            (topLeft, topRight, bottomRight, bottomLeft) = corners
            # convert each of the (x, y)-coordinate pairs to integers
            topRight = (int(topRight[0]), int(topRight[1]))
            bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
            bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
            topLeft = (int(topLeft[0]), int(topLeft[1]))

            # compute and draw the center (x, y)-coordinates of the
            # ArUco marker
            cX = int((topLeft[0] + bottomRight[0]) / 2.0)
            cY = int((topLeft[1] + bottomRight[1]) / 2.0)

            eX = int((topLeft[0] + topRight[0]) / 2.0)
            eY = int((topLeft[1] + topRight[1]) / 2.0)

            if markerID == 0:
                field_corners[markerID] = bottomRight
            if markerID == 1:
                field_corners[markerID] = bottomLeft
            if markerID == 2:
                field_corners[markerID] = topLeft
            if markerID == 3:
                field_corners[markerID] = topRight

            #detected_markers.append(dict(id=markerID, cx=cX, cy=cY, ex=eX, ey=eY))
            if markerID > 3:
                detected_markers.append(Marker('Cup', markerID, (cX, cY), (eX, eY)))
            else:
                detected_markers.append(Marker('Reference', markerID, (cX, cY), (eX, eY)))

    if draw:
        # Draw bbox
        aruco.drawDetectedMarkers(frame, bbox, ids)

    return [detected_markers, field_corners]


def getRealCoordinates(frame, field_corners, detected_markers, p_width=video_resolution[0],
                       p_height=video_resolution[1]):

    # resize frame into the "playing field" coordinate space
    field_corners_vect = np.float32([field_corners[0], field_corners[1], field_corners[2], field_corners[3]])
    true_coordinates = np.float32([[0, 0], [p_width, 0], [p_width, p_height], [0, p_height]])
    trans_mat = cv2.getPerspectiveTransform(field_corners_vect, true_coordinates)

    # show playing field
    #img_trans = cv2.warpPerspective(frame, trans_mat, (p_width, p_height))
    #cv2.imshow("new frame", img_trans)

    # print(detected_markers)
    ##########################################################################q##################
    ############################################################################################
    detected_true_coordinates = np.empty((len(detected_markers), 3))  # create matrix of coordinates

    for i, obj in enumerate(detected_markers, 0):
        # apply the transform matrix to each vector of center coordinates
        detected_true_coordinates[i] = np.dot(trans_mat, (obj.center[0], obj.center[1], 1))
        # change back the values in the detected markers list to have the real coordinates
        a = - detected_true_coordinates[i][0] * r_width / p_width  # x axis is upside down
        b = detected_true_coordinates[i][1] * r_height / p_height
        obj.center = (a, b)
        # apply the transform matrix to each vector of top left coordinates
        detected_true_coordinates[i] = np.dot(trans_mat, (obj.edge[0], obj.edge[1], 1))
        # change back the values in the detected markers list to have the real coordinates
        a = - detected_true_coordinates[i][0] * r_width / p_width  # x axis is upside down
        b = detected_true_coordinates[i][1] * r_height / p_height
        obj.edge = (a, b)

    return


def getCupCoordinates(detected_markers):
    """
    :param detected_markers:
    :return:
    """

    # Create list for Cups
    listCups_data = list()

    # loop over the detected markers to calculate the cup center points and angle
    # For each specific marker ID do move the robot
    for i, obj in enumerate(detected_markers, 0):

        # ignore the reference ArUco markers and store all important values in cupList
        # convert all values to meters

        if obj.type == 'Cup':
            # Get cup edge en center from ArUco markers - in Meters!
            mX = origin_L[0] + obj.center[0] / 1000
            mY = origin_L[1] + obj.center[1] / 1000

            tX = origin_L[0] + obj.edge[0] / 1000
            tY = origin_L[1] + obj.edge[1] / 1000

            (cX, cY) = geometry.segmentExtension((mX, mY), (tX, tY), dist1)
            (eX, eY) = geometry.segmentExtension((mX, mY), (tX, tY), dist2)

            angle = geometry.get_angle((cX, cY), (eX, eY)) #angles range from [-PI,PI] counter-clockwise
            listCups_data.append(Cup('Pouring', obj.ID, (cX, cY), (eX, eY), angle))

    return listCups_data


def cup_layout(listCups):

    figure, ax = plt.subplots()
    # change default range so that new circles will work
    ax.set_xlim((xMin, xMax))
    ax.set_ylim((0, yMax))

    for i, obj in enumerate(listCups, 0):
        # plot circles
        circle = plt.Circle(obj.center, rCups, color='red', ec='black')
        plt.gcf().gca().add_patch(circle)

        # plot cup edge dots
        circle = plt.Circle(obj.edge, rCups / 5, color='blue', ec='black')
        plt.gcf().gca().add_patch(circle)

    plt.title('Cup Layout')
    ax.set_aspect(1)
    plt.show()

    return
