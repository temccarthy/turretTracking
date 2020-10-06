import numpy as np
import math

# takes in skeleton (which has a position)
# returns the two rotational values of both servos
def calcRotation(coords):
    x = coords[0]
    y = coords[1]
    z = coords[2]
    dist = math.sqrt(x**2 + y**2 + z**2)

    pitch = math.atan2(x,math.sqrt(x**2+z**2))
    yaw = math.atan2(y,z)

    # matrix math

    return pitch, yaw