import serial
import signal

import numpy as np
import matplotlib.pyplot as plt

ser = serial.Serial("COM7", 115200)

import threading
import queue

acc = queue.Queue()
gyr = queue.Queue()
pos = queue.Queue()

exit_event = threading.Event()

ACC_MAX = 2 ** 16 / 2

def worker_serial():
    x = y = z = 0.0
    ax = ay = az = 0.0
    roll = pitch = yaw = 0.0

    while True:
        try:
            line = ser.readline()
            data = line.split(b" ")

            ax = float(data[0])
            ay = float(data[1])
            az = float(data[2])

            x = float(data[3])
            y = float(data[4])
            z = float(data[5])

            roll = float(data[6])
            pitch = float(data[7])
            yaw = float(data[8])

            # print("Acc: %f %f %f Gyr: %f %f %f Pos %f %f %f" % (ax, ay, az, x, y, z, roll, pitch, yaw))

            acc.put([ax, ay, az])
            gyr.put([x, y, z])
            pos.put([roll, pitch, yaw])

            if acc.qsize() > 50:
                acc.get()
            if gyr.qsize() > 50:
                gyr.get()
            if pos.qsize() > 50:
                pos.get()
        except Exception as e:
            print(e)
            pass

        if exit_event.is_set():
            ser.close()
            return

def signal_handler(signum, frame):
    exit_event.set()

if __name__ == "__main__":
    t1 = threading.Thread(target=worker_serial, daemon=True)
    t1.start()
   
    signal.signal(signal.SIGINT, signal_handler)

    fig = plt.figure()
    try:
        while True:
            if len(acc.queue) > 0 and len(gyr.queue) > 0 and len(pos.queue) > 0:
                plt.clf()
                ax1 = plt.subplot(3, 1, 1)
                ax1.set_title("Accelerometer")
                plt.plot(np.array(acc.queue)[:, 0], label="ax")
                plt.plot(np.array(acc.queue)[:, 1], label="ay")
                plt.plot(np.array(acc.queue)[:, 2], label="az")
                ax1.legend(loc="upper right")

                ax2 = plt.subplot(3, 1, 2)
                ax2.set_title("Gyroscope")
                plt.plot(np.array(gyr.queue)[:, 0], label="wx")
                plt.plot(np.array(gyr.queue)[:, 1], label="wy")
                plt.plot(np.array(gyr.queue)[:, 2], label="wz")
                ax2.legend(loc="upper right")

                ax3 = plt.subplot(3, 1, 3)
                ax3.set_title("Position")
                plt.plot(np.array(pos.queue)[:, 0], label="roll")
                plt.plot(np.array(pos.queue)[:, 1], label="pitch")
                plt.plot(np.array(pos.queue)[:, 2], label="yaw")
                ax3.legend(loc="upper right")

                plt.pause(0.0001)

            if exit_event.is_set():
                plt.close('all')
                break

    except KeyboardInterrupt:
        t1.join()

    print('Exiting main thread.')
