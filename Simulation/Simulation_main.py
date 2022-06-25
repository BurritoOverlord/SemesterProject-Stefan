"""
Launch this script to test simulation - Initialises with respect to actual cup placement
"""

import cv2
import imutils
from imutils.video import VideoStream
import time

import sim
from Simulation import Simulation_globalvariables as g
from Simulation import Simulation_gripper as grip
from Simulation import Simulation_simplePouring as sp
from Simulation import Simulation_marker_cup_detection as marker_cup_detection

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

# Initialization
g.kFinal = 700/1000  # speed
g.connectionMessage(g.clientID)  # Printing out a successful/unsuccessful remote API connection message



# Functions

def initCups(listCups):
    for obj in listCups:
        cupID = str(obj.ID)
        cup_spawn = [obj.center[0], obj.center[1], g.z_spawn]
        errorCode, cupH = sim.simxGetObjectHandle(g.clientID, 'Cup' + cupID, sim.simx_opmode_blocking)
        sim.simxSetObjectPosition(g.clientID, cupH, -1, cup_spawn, sim.simx_opmode_oneshot)

    grip.openGripperAtStart(g.clientID, g.j1, g.j2, g.p1, g.p2) #Opens gripper at the very beginning before pouring algo
    time.sleep(2)



############################# Python Script ###############################

def main():
    try:
        sim.simxStartSimulation(g.clientID, sim.simx_opmode_oneshot_wait)
        time.sleep(1)  # necessary for simulation to start properly

        ######### Main Functions ##########################################

        print("starting loop")

        # Grabs the current camera frame and detect ArUco markers
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
        marker_cup_detection.cup_layout(listCups_data)  # Plot the results

        initCups(listCups_data) #Spawning a non-dynamic basket to the 'batter and breading machine' platform

        sp.simple_pouring(listCups_data)  # Apply pouring algorithm


    except Exception as e:
        print(e)
        sim.simxFinish(g.clientID)
    finally:
        sim.simxPauseSimulation(g.clientID, sim.simx_opmode_oneshot_wait)


if __name__ == "__main__":
    main()
