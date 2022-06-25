import time

import sim
from Simulation import Simulation_globalvariables as g
from Simulation import Simulation_gripper as grip
from Simulation import Simulation_moveL as mL


# NOTE: CAN ONLY ROTATE GRIPPER IF THERE IS ALSO A TRANSLATION (X,Y,Z) - Need To Fix moveL function

def grab_cup(cX, cY, angle, ID):
    cupID = str(ID)
    errorCode, cupH = sim.simxGetObjectHandle(g.clientID, 'Cup' + cupID, sim.simx_opmode_blocking)

    target_pos = [cX, cY, g.z_pCup, 0, 0, angle]
    # Moving to position (on top of cup with correct orientation then down)
    mL.move_L(g.clientID, g.target, target_pos, g.kFinal)
    time.sleep(0.5)
    target_pos[2] = g.z_gCup
    mL.move_L(g.clientID, g.target, target_pos, g.kFinal)
    time.sleep(2)

    # Fake Grasping Motion
    sim.simxSetObjectParent(g.clientID, cupH, g.connector, True, sim.simx_opmode_blocking)

    # Closing gripper
    grip.closeGripper(g.clientID)
    time.sleep(1)

    # Moving object Up
    target_pos[2] = g.z_pCup
    mL.move_L(g.clientID, g.target, target_pos, g.kFinal)
    time.sleep(2)

def place_cup(cX, cY, angle, ID):
    cupID = str(ID)
    errorCode, cupH = sim.simxGetObjectHandle(g.clientID, 'Cup' + cupID, sim.simx_opmode_blocking)

    target_pos = [cX, cY, g.z_pCup, 0, 0, angle]
    # Moving to position (on top of cup with correct orientation then down)
    mL.move_L(g.clientID, g.target, target_pos, g.kFinal)
    time.sleep(0.5)
    target_pos[2] = g.z_gCup
    mL.move_L(g.clientID, g.target, target_pos, g.kFinal)
    time.sleep(2)

    # Release Cup
    sim.simxSetObjectParent(g.clientID, cupH, -1, True, sim.simx_opmode_blocking)  # Resets Cup Parent to the Scene-"No longer grasping"

    # Open gripper
    grip.openGripper(g.clientID)
    time.sleep(1)

    # Moving object Up
    target_pos[2] = g.z_pCup
    mL.move_L(g.clientID, g.target, target_pos, g.kFinal)
    time.sleep(2)

