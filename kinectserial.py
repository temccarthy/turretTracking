from serial import Serial
import time

arduino = Serial('/dev/cu.usbserial-1420', 115200, timeout=.1)
time.sleep(1)  # give the connection a second to settle


if __name__ == "__main__":
    while True:
        data = arduino.readline()
        if data:
            print data.rstrip('\n')  # strip out the new lines for now
            # (better to do .read() in the long run for this reason

        # x = input("Press a key to send message")
        #
        # if x == "A":
        #     arduino.write("p30y30\n")

