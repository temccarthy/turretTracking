from pykinect import nui
from pykinect.nui import JointId

import re


class Skeleton:

    def __init__(self, name, present, coords):
        self.name = name
        self.present = present
        self.coords = coords

    def __str__(self):
        return "name: " + str(self.name) + ", present: " + str(self.present) + ", coords: " + str(self.coords)

    def set_skeleton_data(self, skeleton):
        if skeleton.eTrackingState == nui.SkeletonTrackingState.TRACKED:
            self.present = True

            head = skeleton.SkeletonPositions[JointId.Head]
            head_data = re.findall("-?\d+.\d+", str(head))[:3]
            # head_data = tuple(float(h) * 38.39 for h in head_data) # converting to inches
            self.coords = head_data
        else:
            self.present = False

    def set_name(self, name):
        self.name = name
