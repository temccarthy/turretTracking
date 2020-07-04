import math
import face_recognition
import cv2
import numpy as np
from pykinect import nui
from pykinect.nui import JointId
import subprocess
import re
import time
import threading
import os


def recognize_face(frame):
    global safetyTimer, safeTime, curr_unknowns, shoot_boolean, max_unknowns
    # Resize frame of video to 1/4 size for faster face recognition processing
    # small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    # rgb_small_frame = small_frame[:, :, ::-1]
    rgb_small_frame = frame[:, :, 2::-1]
    if curr_head is not None:
        WIDTH, HEIGHT = 640, 480
        FOV_X, FOV_Y = math.radians(84.1), math.radians(53.8) # from internet

        pitch = math.atan(curr_head[0]/curr_head[2])
        yaw = math.atan(curr_head[1]/curr_head[2])

        x = WIDTH / 2 + (pitch * (WIDTH / FOV_X))
        y = HEIGHT / 2 - (yaw * (HEIGHT / FOV_Y))

        distance_factor = 100/curr_head[3]
        head_width, head_height = 150*distance_factor, 100*distance_factor
        x_pixels = (max(0, int(x - head_width / 2)), min(int(x + head_width / 2), 640))
        y_pixels = (max(0, int(y - head_height / 2))+30, min(int(y + head_height / 2)+30, 480))
        small_frame = rgb_small_frame[y_pixels[0]:y_pixels[1], x_pixels[0]:x_pixels[1]]

        if x_pixels[0] != x_pixels[1] and y_pixels[0] != y_pixels[1]:
            rgb_small_frame = small_frame

    # Find all the faces and face encodings in the current frame of video
    # face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame)

    face_names = []

    for face_encoding in face_encodings:
        # See if the face is a match for the known face(s)
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"
        print(matches)

        # # If a match was found in known_face_encodings, just use the first one.
        if matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]
            curr_unknowns = 0

            if safetyTimer.is_alive():
                safetyTimer.cancel()
            safetyTimer = threading.Timer(safeTime, resetSafeBool)
            safetyTimer.start()
        else:
            curr_unknowns += 1

        # Or instead, use the known face with the smallest distance to the new face
        # face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        # best_match_index = np.argmin(face_distances)
        # if matches[best_match_index]:
        #     name = known_face_names[best_match_index]

        face_names.append(name)

    for name in face_names:
        print("FOUND NAME: " + name)

    if curr_unknowns >= max_unknowns:
        shoot_boolean = True
    return rgb_small_frame


def video_handler_function(frame):
    global curr_head, prev_head, skeleton_frames, max_skeleton_frames, stop
    t = time.time()
    video = np.empty((480, 640, 4), np.uint8)
    frame.image.copy_bits(video.ctypes.data)
    vid = recognize_face(video)

    if curr_head is not None:
        if curr_head == prev_head:
            skeleton_frames += 1
        else:
            prev_head = curr_head
    else:
        prev_head = curr_head

    if skeleton_frames >= max_skeleton_frames:
        print("- set curr head to none")
        curr_head = None
        skeleton_frames = 0
        stop = True

    print("Frame time: " + str(time.time()-t))
    print("---------")
    try:
        cv2.imshow('KINECT Video Stream', vid[:, :, ::-1])
    except cv2.error:
        pass

    # cv2.imshow('KINECT Video Stream', video)


def skeleton_frame_function(frame):
    global curr_head, skeleton_frames
    for skeleton in frame.SkeletonData:
        if skeleton.eTrackingState == nui.SkeletonTrackingState.TRACKED:
            head = skeleton.SkeletonPositions[JointId.Head]
            head_data = re.findall("-?\d+.\d+", str(head))[:3]
            head_data = tuple(float(h)*38.39 for h in head_data)
            head_data_with_dist = head_data + (math.sqrt(head_data[0]**2 + head_data[1]**2 + head_data[2]**2),)
            curr_head = head_data_with_dist
            skeleton_frames = 0
            distance = math.sqrt(head_data[0]**2 + head_data[1]**2 + head_data[2]**2)
            # print("head at: " + str(head_data) + ", distance: " + str(distance))


def resetSafeBool():
    print("safe zone no longer active")


print("Initializing facial recognition...")

known_face_encodings = []
known_face_names = []

for _, _, files in os.walk("../pics"):
    for f in files:
        img = face_recognition.load_image_file("../pics/"+f)
        encoding = face_recognition.face_encodings(img)
        print(f + " - " + str(len(encoding)) + " face(s) found")
        if len(encoding) == 0:
            print("no face found for " + f)
            continue
        known_face_encodings.append(encoding)
        known_face_names.append(f[:f.find('.')])

# tim_image = face_recognition.load_image_file("Tim.jpg")
# gabe_img = face_recognition.load_image_file("Gabe.jpg")
# tim_face_encoding = face_recognition.face_encodings(tim_image)[0]
# gabe_face_encoding = face_recognition.face_encodings(gabe_img)[0]
#
# known_face_encodings = [
#     tim_face_encoding,
#     gabe_face_encoding
# ]
# known_face_names = [
#     "Tim",
#     "Gabe"
# ]


print("Facial recognition initialized")

safeTime = 7.0
safetyTimer = threading.Timer(safeTime, resetSafeBool)
shoot_boolean = False
curr_unknowns = 0
max_unknowns = 2
curr_head = None
prev_head = None
skeleton_frames = 0
max_skeleton_frames = 20
stop = False

if __name__ == "__main__":
    print("Initializing Kinect...")
    # subprocess.call([r"E:\\Documents\Programming\\facialRecog\\Skeleton\\Debug\\KinectTutorial4.exe"])
    with nui.Runtime() as kinect:
        kinect.skeleton_engine.set_enabled(True)

        kinect.video_frame_ready += video_handler_function
        kinect.video_stream.open(nui.ImageStreamType.Video, 2, nui.ImageResolution.Resolution640x480,
                                 nui.ImageType.Color)

        kinect.skeleton_frame_ready += skeleton_frame_function

        cv2.namedWindow('KINECT Video Stream', cv2.WINDOW_AUTOSIZE)

        print("Kinect Initialized")
        start = time.time()
        thing = False
        while True:
            # print("safe: " + str(safetyTimer.is_alive()))
            if shoot_boolean:
                if curr_head is not None:
                    # print("BANG\nBANG\nBANG")
                    print("---head shot at " + str(curr_head))


                    # move gun
                    # shoot
                    # return back to normal


                else:
                    print("---idk where to shoot")
                shoot_boolean = False
                curr_unknowns = 0
                skeleton_frames = 0



            # Hit 'q' on the keyboard to quit!
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        kinect.close()
        cv2.destroyAllWindows()
