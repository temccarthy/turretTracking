import cv2
import face_recognition
import math
import os
import numpy as np

# on import load faces in ./pics
print("Initializing facial recognition...")
known_face_encodings = []
known_face_names = []

for _, _, files in os.walk("./pics"):
    for f in files:
        img = face_recognition.load_image_file("./pics/"+f)
        encoding = face_recognition.face_encodings(img)
        print(f + " - " + str(len(encoding)) + " face(s) found")
        if len(encoding) == 0:
            print("no face found for " + f)
            continue
        known_face_encodings.append(encoding)
        known_face_names.append(f[:f.find('.')])

print("Facial recognition initialized")


def recognize_face(frame, skeletons_array, index):
    current_skeleton = skeletons_array[index]

    small_frame = shrink_screen(frame, current_skeleton.coords)

    # Convert the image from BGR color (which OpenCV uses) to
    #  RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, 2::-1]

    face_encodings = face_recognition.face_encodings(rgb_small_frame)

    #  should only be 1 face, not sure what else to do here
    for face_encoding in face_encodings:
        # See if the face is a match for the known face(s)
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=.1)  # compare faces
        valued_matches = map(lambda x: float((x == True).sum()) / 128, matches)  # map matches array to values

        print(valued_matches)
        name = "Unknown"
        for idx, x in enumerate(valued_matches):
            if x > .95:
                print(idx)
                name = known_face_names[idx]
                break
        skeletons_array[index].name = name
        print("found " + name)
        break


# Shrinks screen size so recognizer doesn't have to look at whole screen,
#  only has to look at where the skeleton head is
def shrink_screen(frame, current_skeleton_coords):
    x,y = uvMap(current_skeleton_coords)

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
    # FOV_X, FOV_Y = math.radians(84.1), math.radians(53.8)  # camera FOVs
    FOV_X, FOV_Y = math.radians(90), math.radians(53.8)  # camera FOVs

    pitch = math.atan(coords[0] / coords[2])
    yaw = math.atan(coords[1] / coords[2])

    x = WIDTH / 2 + (pitch * (WIDTH / FOV_X))
    y = HEIGHT / 2 - (yaw * (HEIGHT / FOV_Y))

    return int(x), int(y)
