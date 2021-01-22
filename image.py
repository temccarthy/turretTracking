import cv2
import face_recognition
import math
import os
import numpy as np

# on import load faces in ./pics
print("Initializing facial recognition...")
known_face_encodings = []
known_face_names = []

for root, _, files in os.walk("./pics/"):
	for f in files:
		img = face_recognition.load_image_file(root + "/" + f)
		encoding = face_recognition.face_encodings(img)
		file_name_shortened = root[7:] + "/" + f
		print(file_name_shortened + " - " + str(len(encoding)) + " face(s) found")
		if len(encoding) == 0:
			print("no face found for " + file_name_shortened)
			continue
		known_face_encodings.append(encoding)
		name = (root[7:])  # remove ./pics/ from root to get name
		known_face_names.append(name)

print("Facial recognition initialized")


def recognize_face(frame, skeletons_array, skele_index):
	current_skeleton = skeletons_array.value[skele_index]

	small_frame = shrink_screen(frame, current_skeleton.coords)

	# Convert the image from BGR color (which OpenCV uses) to
	#  RGB color (which face_recognition uses)
	rgb_small_frame = small_frame[:, :, 2::-1]

	face_encodings = face_recognition.face_encodings(rgb_small_frame)

	#  should only be 1 face, not sure what else to do here
	for face_encoding in face_encodings:
		# See if the face is a match for the known face(s)
		matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=.07)  # compare faces
		valued_matches = map(lambda x: float((x == True).sum()) / 128, matches)  # map matches array to values

		# print(valued_matches)
		sorted_indeces = np.argsort(valued_matches)[::-1]
		name = "Unknown"
		for i, index in enumerate(sorted_indeces):
			if i == 0 and valued_matches[index] < .85:  # check that highest value is at least over threshold or else break
				break

			temp_name = known_face_names[index]
			if temp_name in map(lambda x: x.name, skeletons_array.value):  # check that temp_name hasn't been used yet or else check next index
				continue

			name = temp_name  # after finding the highest value with unused name, break
			break

		skeletons_array.value[skele_index].set_name(name)
		skeletons_array.notify_observers()
		print("found " + name)
		break


# Shrinks screen size so recognizer doesn't have to look at whole screen,
#  only has to look at where the skeleton head is
def shrink_screen(frame, current_skeleton_coords):
	x, y = uvMap(current_skeleton_coords)

	distance_factor = 100 / current_skeleton_coords[3]  # size factor of smaller screen
	head_width, head_height = 150 * distance_factor, 100 * distance_factor
	x_pixels = (max(0, int(x - head_width / 2)), min(int(x + head_width / 2), 640))
	y_pixels = (max(0, int(y - head_height / 2)) + 30, min(int(y + head_height / 2) + 30, 480))
	small_frame = frame[y_pixels[0]:y_pixels[1], x_pixels[0]:x_pixels[1]]

	if x_pixels[0] != x_pixels[1] and y_pixels[0] != y_pixels[1]:
		return small_frame
	else:
		return frame, (x, y)


def uvMap(coords):
	WIDTH, HEIGHT = 640, 480  # camera dimensions
	FOV_X, FOV_Y = math.radians(84.1), math.radians(53.8)  # camera FOVs

	if coords[2] != 0:
		pitch = math.atan(coords[0] / coords[2])
		yaw = math.atan(coords[1] / coords[2])

		x = WIDTH / 2 + (pitch * (WIDTH / FOV_X))
		y = HEIGHT / 2 - (yaw * (HEIGHT / FOV_Y))

		return int(x), int(y)
	else:
		return WIDTH, HEIGHT
