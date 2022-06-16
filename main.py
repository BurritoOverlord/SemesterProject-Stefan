import cv2
import imutils
from imutils.video import VideoStream
import time
import math

# My Modules
import marker_cup_detection
import move_robot
import simplePouring as sp

"SETTINGS AND VARIABLES ________________________________________________________________"

# resolution the video capture will be resized to, smaller sizes can speed up detection
video_resolution = (640, 480)

vs = VideoStream(src=1,
                 resolution=video_resolution,
                 framerate=13,
                 meter_mode="backlit",
                 exposure_mode="auto",
                 shutter_speed=8900,
                 exposure_compensation=2,
                 rotation=0).start()
time.sleep(0.2)

"""Initialization ____________________________________________________________________"""
move_robot.initialize_robot()

"""Main Loop ____________________________________________________________________"""


try:
    print("starting loop")

    while True:

        frame = vs.read()
        frame = imutils.resize(frame, width=video_resolution[0], height=video_resolution[1])

        # detected markers are in pixels
        detected_markers, field_corners = marker_cup_detection.findArUcoMarkers(frame)
        # convert to real values
        marker_cup_detection.getRealCoordinates(frame, field_corners, detected_markers)

        cv2.imshow('RobotCamera', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    vs.stream.release()
    cv2.destroyAllWindows()

    # Get Cup Coordinates in robot base reference frame
    listCups_data = marker_cup_detection.getCupCoordinates(detected_markers)
    #Plot the results
    marker_cup_detection.cup_layout(listCups_data)
    #Print the results
    for i, obj in enumerate(listCups_data, 0):
        print(obj.ID, obj.center, obj.orientation, sep=' ')
    #Apply pouring algorithm
    move_robot.grab_cup_orientation(listCups_data[0].center[0],listCups_data[0].center[1], math.pi/2) # grabs cup with desired angle
    #sp.simple_pouring(listCups_data)

    print("exiting loop")
    time.sleep(10)

except KeyboardInterrupt:
    print("closing robot connection")
    vs.stream.release()
    cv2.destroyAllWindows()
except:
    print("closing robot connection")
    print("Check Camera Connection")
    vs.stream.release()
    cv2.destroyAllWindows()
