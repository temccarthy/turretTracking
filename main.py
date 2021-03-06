from pykinect import nui
from skele import Skeleton
from recog import recognize_face, uvMap
from ObservableList import ObservableList
from matrix import calcRotation

import cv2
import numpy as np


def video_handler_function(frame):
	# this might be slow, maybe move to detect face if not showing stream
	video = np.empty((480, 640, 4), np.uint8)
	frame.image.copy_bits(video.ctypes.data)

	for index, skele in enumerate(skeletons_array.value):
		if skele.present:
			if skele.name == "" or (skele.name == "Unknown" and skele.tries < 3):  # if unnamed skeleton
				recognize_face(video, skeletons_array, index)
				skeletons_array.notify_observers()
			else:  # if named skeleton
				uv_coords = uvMap(skeletons_array.value[index].coords)
				# cv2.circle(video, uv_coords, 20, (255, 0, 0), 2)
				x = int(skeletons_array.value[index].coords[0])
				y = int(skeletons_array.value[index].coords[1])
				z = int(skeletons_array.value[index].coords[2])
				

				cv2.putText(video, str(x) + " " + str(y) + " " + str(z), uv_coords,
							cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
		elif not skele.present and skele.name != "":
			print("lost " + skeletons_array.value[index].name + "'s skeleton")
			skeletons_array.value[index].reset_name()
			skeletons_array.notify_observers()

	try:
		if argDict["show_video"]:
			cv2.imshow('KINECT Video Stream', video)
	except cv2.error:
		pass


# NOTE: I had to edit pykinect's __init__.py to fire on all frames, not just when
#  a skeleton is being tracked. Comment line 187 of pykinect/nui/__init__.py to get
#  the same behavior
def skeleton_frame_function(frame):
	for index, skeleton in enumerate(frame.SkeletonData):
		skeletons_array.value[index].set_skeleton_data(skeleton)


def main_loop(argDict):
	print("Initializing Kinect...")
	with nui.Runtime() as kinect:
		kinect.skeleton_engine.set_enabled(True)
		kinect.skeleton_frame_ready += skeleton_frame_function  # async loop 1

		kinect.video_frame_ready += video_handler_function  # async loop 2
		kinect.video_stream.open(nui.ImageStreamType.Video, 2, nui.ImageResolution.Resolution640x480,
								 nui.ImageType.Color)

		cv2.namedWindow('KINECT Video Stream', cv2.WINDOW_AUTOSIZE)

		print("Kinect Initialized")

		run = True
		while run:
			
			if cv2.waitKey(1) & 0xFF == ord('c'):
				shoot_coords = None
				shoot_name = ""
				for index,skele in enumerate(skeletons_array.value):
					if skele.present and skele.name != "":
						shoot_coords, shoot_name = skele.coords, skele.name
						break
				if shoot_coords is not None:
					print("shooting " + shoot_name)
					# calculate necessary pitch and yaw
					pitch, yaw = calcRotation(shoot_coords)
					# send to esp
					
			if cv2.waitKey(1) & 0xFF == ord('q'):
				run = False
			if cv2.waitKey(1) & 0xFF == ord(' '):
				reset_skeletons_array()

		kinect.close()

		print("Exiting")


def reset_skeletons_array():
	print("Resetting skeletons_array")
	del skeletons_array.value[:]
	for i in range(6):
		skeletons_array.value.append(Skeleton("", False, (0, 0, 0)))


# initialize skeletons_array
skeletons_array = ObservableList()
reset_skeletons_array()
argDict = {
	"show_video": True,
	"kinect_error": False
}


if __name__ == "__main__":
	main_loop(argDict)
