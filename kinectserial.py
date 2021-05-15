from serial import Serial
import time

# arduino = Serial('COM6', 500000, timeout=.1)
time.sleep(1)  # give the connection a second to settle


def send_coords(pitch, yaw):
    arduino.write("p" + str(pitch) + "y" + str(yaw) + "\n")


def cock_back():
    arduino.write("cockback")  # idk


def shoot():
    arduino.write("s\n")  # idk


def reload_mag():
    arduino.write("r\n")


def finish_reload():
    arduino.write("f\n")


def retract():
    arduino.write("x\n")


# serial tests
if __name__ == "__main__":
    flip = True
    x = "p0y0"
    yaw = 65;
    print("starting")
    while True:
        x = raw_input("Press a key to send message")
        if x == "u":
            yaw+=1
        elif x == "d":
            yaw-=1
        x = "p0y" + str(yaw)
        arduino.write(x + "\n")
