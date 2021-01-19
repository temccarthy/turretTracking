# turretTracking

This a project that leverages facial recognition and the Kinect's skeleton tracking to track people in real time.

## Installing

Unfortunately, this project requires a lot of dependencies to run. Firstly, due to the nature of the Kinect SDK, this can only be run on a Windows machine with Python 2.7. 
Download the Kinect SDK, then install the pykinect module from pip.  

Next, for the face-recognition module you need to install CMake and Visual Studio for C++. These are for compiling dlib, which is a dependency of face-recognition. 
Once those are installed, you can pip install face-recognition.

Lastly, you need to install pywin32, numpy, and opencv. I had trouble with one of the latest opencv versions, so I used pip install opencv-python==4.2.0.32 which did the trick.

## Adding faces

To add faces to the encoding list, add them to their own folder in ./pics/. Your file structure should look like this:
```
project/
│   README.md
│   main.py
|   ...
└───pics/
    └───person_one/
    |   │   1.jpg
    |   │   2.jpg
    |   |   ...
    │   
    └───person_two/
        │   1.jpg
        │   2.jpg
        |   ...
```
File names are irrelevant, make sure the folders that contain the pictures are all of the same person