from pykinect import nui
from skele import Skeleton
from image import recognize_face, uvMap, known_face_names
from ObservableList import ObservableList
from matrix import calcRotation
import kinectserial as ks
from adafruit import Fruit
import random

import cv2
import numpy as np


def reset_skeletons_array():
	print("Resetting skeletons_array")
	del skeletons_array.value[:]
	for i in range(6):
		skeletons_array.value.append(Skeleton("", False, (0, 0, 0)))


def draw_skele_data(skele, video):
	uv_coords = uvMap(skele.coords)
	# cv2.circle(video, uv_coords, 20, (255, 0, 0), 2)
	x = int(skele.coords[0])
	y = int(skele.coords[1])
	z = int(skele.coords[2])

	print_coords = calcRotation((x, y, z))  # str(x) + " " + str(y) + " " + str(z)
	cv2.putText(video, str(print_coords[0]) + " " + str(print_coords[1]), uv_coords,
				cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)


def skele_unrecognized(skele):
	return (skele.name == "" or (skele.name == "Unknown" and skele.tries < 3)) and argDict["recognize_faces"]


# randomly picks an index of one of the present skeletons
def get_random_skele_index():
	present_skele_indeces = [i for i, skele in enumerate(skeletons_array.values) if skele.present]
	return random.choice(present_skele_indeces)


def video_handler_function(frame):
	video = np.empty((480, 640, 4), np.uint8)
	frame.image.copy_bits(video.ctypes.data)

	for index, skele in enumerate(skeletons_array.value):
		if skele.present:

			# if unrecognized skeleton, try to recognize
			if skele_unrecognized(skele):
				recognize_face(video, skeletons_array, index)
				skeletons_array.notify_observers()

			# if recognized skeleton, display coordinates on screen
			else:
				draw_skele_data(skele, video)

		# if named skeleton moves out of frame, remove them from array
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
	print("connecting to adafruit")
	fruit = Fruit("creds.txt")
	print("Initializing Kinect...")
	with nui.Runtime() as kinect:
		# initialize kinect functions
		kinect.skeleton_engine.set_enabled(True)
		kinect.skeleton_frame_ready += skeleton_frame_function  # skeleton async loop

		kinect.video_frame_ready += video_handler_function  # video async loop
		kinect.video_stream.open(nui.ImageStreamType.Video, 2, nui.ImageResolution.Resolution640x480,
								 nui.ImageType.Color)

		# open cv2 window of kinect video
		cv2.namedWindow('KINECT Video Stream', cv2.WINDOW_AUTOSIZE)

		print("Kinect Initialized")

		run = True
		while run:
			alexa_cmd = fruit.get_next()
			if alexa_cmd == "anyone":
				ks.cock_back()
				shoot_index = get_random_skele_index()  # pick a random present skeleton to shoot
				for index, skele in enumerate(skeletons_array.value):
					if skele.present:
						for i in range(25000):  # aim at each present skeleton
							pitch, yaw = calcRotation(skele.coords)
							ks.send_coords(pitch, yaw)
						if index == shoot_index:  # if chosen skeleton is being aimed at, shoot them
							print("shot someone")
							ks.shoot()
							break
			elif alexa_cmd == "unknown":
				print("shot unknown")
				for index, skele in enumerate(skeletons_array.value):
					if skele.present and skele.name != "unknown":
						pitch, yaw = calcRotation(skele.coords)
						ks.send_coords(pitch, yaw)
						ks.shoot()
						break
			elif alexa_cmd == "everyone":
				for index, skele in enumerate(skeletons_array.value):
					if skele.present:  # and skele.name != "":
						pitch, yaw = calcRotation(skele.coords)
						ks.send_coords(pitch, yaw)
						ks.shoot()
				print("shot everyone")
			else:
				if alexa_cmd in known_face_names:  # fuzzy search probably
					print("shot" + alexa_cmd)
					# do laterrrr

			# hot keys
			if cv2.waitKey(1) & 0xFF == ord('q'):  # q quit application
				run = False
			if cv2.waitKey(1) & 0xFF == ord(' '):  # space bar resets skeletons
				reset_skeletons_array()

		kinect.close()

		print("Exiting")


# initialize skeletons_array
skeletons_array = ObservableList()
reset_skeletons_array()
argDict = {
	"show_video": True,
	"recognize_faces": False,
}

if __name__ == "__main__":
	main_loop(argDict)
