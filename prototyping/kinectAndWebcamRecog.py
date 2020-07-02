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


def recognize_face(frame):
    global safetyTimer, safeTime, curr_unknowns, shoot_boolean, max_unknowns
    # Resize frame of video to 1/4 size for faster face recognition processing
    # small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    if frame is None:
        return

    rgb_small_frame = frame[:, :, ::-1]
    # rgb_small_frame = frame[:, :, 2::-1]
    # Only process every other frame of video to save time
    # if process_this_frame:

    # Find all the faces and face encodings in the current frame of video
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    face_names = []

    for face_encoding in face_encodings:
        # See if the face is a match for the known face(s)
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"

        # # If a match was found in known_face_encodings, just use the first one.
        if True in matches:
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


def video_handler_function(frame):
    t = time.time()
    video = np.empty((480, 640, 4), np.uint8)
    frame.image.copy_bits(video.ctypes.data)
    recognize_face(video)
    print("Frame time: " + str(time.time()-t))
    print("---------")
    cv2.imshow('KINECT Video Stream', video)

def video_handler_function2(frame):
    t = time.time()
    #video = np.empty((480, 640, 4), np.uint8)
    #frame.image.copy_bits(video.ctypes.data)
    recognize_face(frame)
    print("Frame time: " + str(time.time() - t))
    print("---------")
    cv2.imshow('WEBCAM Video Stream', frame)


def skeleton_frame_function(frame):
    global curr_head, skeleton_frames, max_skeleton_frames
    for skeleton in frame.SkeletonData:
        if skeleton.eTrackingState == nui.SkeletonTrackingState.TRACKED:
            head = skeleton.SkeletonPositions[JointId.Head]
            head_data = re.findall("-?\d+.\d+", str(head))[:3]
            head_data = tuple(float(h)*38.39 for h in head_data)
            curr_head = head_data
            skeleton_frames = 0
            distance = math.sqrt(head_data[0]**2 + head_data[1]**2 + head_data[2]**2)
            #print("head at: " + str(head_data) + ", distance: " + str(distance))
        else:
            skeleton_frames+=1
    if skeleton_frames >= max_skeleton_frames:
        #print("- set curr head to none")
        curr_head = None
        skeleton_frames = 0


def resetSafeBool():
    print("safe zone no longer active")


print("Initializing facial recognition...")
tim_image = face_recognition.load_image_file("pics/Tim.jpg")
tim_face_encoding = face_recognition.face_encodings(tim_image)[0]

known_face_encodings = [
    tim_face_encoding
]
known_face_names = [
    "Tim"
]
print("Facial recognition initialized")

safeTime = 7.0
safetyTimer = threading.Timer(safeTime, resetSafeBool)
shoot_boolean = False
curr_unknowns = 0
max_unknowns = 2
curr_head = None
skeleton_frames = 0
max_skeleton_frames = 10

if __name__ == "__main__":
    print("Initializing Kinect and Webcam...")
    # subprocess.call([r"E:\\Documents\Programming\\facialRecog\\Skeleton\\Debug\\KinectTutorial4.exe"])
    with nui.Runtime() as kinect:
        kinect.skeleton_engine.set_enabled(True)

        # kinect.video_frame_ready += video_handler_function
        # kinect.video_stream.open(nui.ImageStreamType.Video, 2, nui.ImageResolution.Resolution640x480,
        #                          nui.ImageType.Color)

        kinect.skeleton_frame_ready += skeleton_frame_function

        video_capture = cv2.VideoCapture(0)

        cv2.namedWindow('WEBCAM Video Stream', cv2.WINDOW_AUTOSIZE)

        print("Kinect and Webcam Initialized")
        while True:
            # print("safe: " + str(safetyTimer.is_alive()))
            ret, frame = video_capture.read()
            video_handler_function2(frame)

            if shoot_boolean:
                if curr_head is not None:
                    # print("BANG\nBANG\nBANG")
                    print("---head shot at " + str(curr_head))
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
