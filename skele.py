from pykinect import nui
from pykinect.nui import JointId

import re
import math


class Skeleton:

    def __init__(self, name, present, coords):
        self.name = name
        self.present = present
        self.coords = coords
        self.tries = 0

    def __str__(self):
        return "name: " + str(self.name) + ", present: " + str(self.present) + \
               ", coords: " + str(self.coords) + ", tries: " + str(self.tries)

    def set_skeleton_data(self, skeleton):
        if skeleton.eTrackingState == nui.SkeletonTrackingState.TRACKED:
            self.present = True

            head = skeleton.SkeletonPositions[JointId.Head]
            head_data = re.findall("-?\d+.\d+", str(head))[:3]
            head_data = tuple(float(h) * 38.39 for h in head_data)  # converting to inches
            head_data = head_data + (math.sqrt(head_data[0]**2 + head_data[1]**2 + head_data[2]**2),)  # add distance to data tuple

            self.coords = head_data
        else:
            self.present = False
            self.name = ""
            self.tries = 0

    def set_name(self, name):
        print("setting name to " + name)
        if name == "Unknown":
            self.tries += 1
        self.name = name
