import math


# takes in xyz coords, returns the two rotational values of pitch and yaw servos
def calcRotation(coords):
    # coords from kinect
    kinect_x = coords[0]
    kinect_y = coords[1]
    kinect_z = coords[2]
    # kinect rotation angle, translation dist
    p = 0 # determine
    trans = -11 # determine

    # coords for inverse kinematics
    x = kinect_x
    y = kinect_y*math.cos(p) - kinect_z*math.sin(p) - trans
    z = kinect_y*math.sin(p) + kinect_z*math.cos(p)

    # calculate angles
    pitch = math.atan2(y,math.sqrt(x**2+z**2))
    yaw = math.atan2(x,z)

    # convert to degrees for serialization
    pitch = int(pitch*180/math.pi)
    yaw = int(yaw*180/math.pi)

    return pitch, yaw