#!/usr/bin/env python

import serial
import signal
import threading

from OpenGL.GL import *
from OpenGL.GLU import *

import pygame
from pygame.locals import *

SERIAL_PORT = 'COM7'

exit_event = threading.Event()

ax = ay = az = 0.0
yaw_mode = True

GL_EXIT = False

def init():
    glShadeModel(GL_SMOOTH)
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

def resize(width, height):
    if height==0:
        height=1
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1.0*width/height, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def drawText(position, textString):     
    font = pygame.font.SysFont ("Courier", 18, True)
    textSurface = font.render(textString, True, (255,255,255,255), (0,0,0,255))     
    textData = pygame.image.tostring(textSurface, "RGBA", True)     
    glRasterPos3d(*position)     
    glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, textData)

def draw():
    global rquad
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);	
    
    glLoadIdentity()
    glTranslatef(0,0.0,-7.0)

    osd_text = "pitch: " + str("{0:.2f}".format(ay)) + ", roll: " + str("{0:.2f}".format(-ax))

    if yaw_mode:
        osd_line = osd_text + ", yaw: " + str("{0:.2f}".format(az))
    else:
        osd_line = osd_text

    drawText((-2,-2, 2), osd_line)

    # The way I'm holding the IMU board, X and Y axis are switched 
    # with respect to the OpenGL coordinate system
    if yaw_mode:                            # experimental
        glRotatef(az, 0.0, 1.0, 0.0)        # Yaw,   rotate around y-axis
    else:
        glRotatef(0.0, 0.0, 1.0, 0.0)

    glRotatef(-1*ax, 1.0, 0.0, 0.0)        # Roll,  rotate around x-axis
    glRotatef(ay, 0.0, 0.0, 1.0)           # Pitch, rotate around z-axis

    glBegin(GL_QUADS)	
    glColor3f(0.0,1.0,0.0)
    glVertex3f( 1.0, 0.2,-1.0)
    glVertex3f(-1.0, 0.2,-1.0)		
    glVertex3f(-1.0, 0.2, 1.0)		
    glVertex3f( 1.0, 0.2, 1.0)		

    glColor3f(1.0,0.5,0.0)	
    glVertex3f( 1.0,-0.2, 1.0)
    glVertex3f(-1.0,-0.2, 1.0)		
    glVertex3f(-1.0,-0.2,-1.0)		
    glVertex3f( 1.0,-0.2,-1.0)		

    glColor3f(1.0,0.0,0.0)		
    glVertex3f( 1.0, 0.2, 1.0)
    glVertex3f(-1.0, 0.2, 1.0)		
    glVertex3f(-1.0,-0.2, 1.0)		
    glVertex3f( 1.0,-0.2, 1.0)		

    glColor3f(1.0,1.0,0.0)	
    glVertex3f( 1.0,-0.2,-1.0)
    glVertex3f(-1.0,-0.2,-1.0)
    glVertex3f(-1.0, 0.2,-1.0)		
    glVertex3f( 1.0, 0.2,-1.0)		

    glColor3f(0.0,0.0,1.0)	
    glVertex3f(-1.0, 0.2, 1.0)
    glVertex3f(-1.0, 0.2,-1.0)		
    glVertex3f(-1.0,-0.2,-1.0)		
    glVertex3f(-1.0,-0.2, 1.0)		

    glColor3f(1.0,0.0,1.0)	
    glVertex3f( 1.0, 0.2,-1.0)
    glVertex3f( 1.0, 0.2, 1.0)
    glVertex3f( 1.0,-0.2, 1.0)		
    glVertex3f( 1.0,-0.2,-1.0)		
    glEnd()	

def worker_serial():
    global ax, ay, az
    ser = serial.Serial(SERIAL_PORT, 115200, timeout=1)

    # Complementary filter data
    roll = pitch = yaw = 0.0

    while True:
        try:
            line = ser.readline()
            data = line.split(b" ")

            # Raw data

            # ax = float(data[0])
            # ay = float(data[1])
            # az = float(data[2])

            # x = float(data[3])
            # y = float(data[4])
            # z = float(data[5])

            # Complementary filter data
            roll = float(data[6])
            pitch = float(data[7])
            yaw = float(data[8])

            # print("Acc: %f %f %f Gyr: %f %f %f Pos %f %f %f" % (ax, ay, az, x, y, z, roll, pitch, yaw))

            ax = roll
            ay = pitch
            az = yaw

        except Exception as e:
            print(e)
            pass

        if exit_event.is_set() or GL_EXIT:
            ser.close()
            return

def signal_handler(signum, frame):
    exit_event.set()

if __name__ == '__main__':

    t1 = threading.Thread(target=worker_serial, daemon=True)
    t1.start()
   
    signal.signal(signal.SIGINT, signal_handler)

    video_flags = OPENGL|DOUBLEBUF

    pygame.init()

    screen = pygame.display.set_mode((1920,1080), video_flags)
    pygame.display.set_caption("Press Esc to quit, z toggles yaw mode")

    resize(1920, 1080)
    init()

    try:
        while True:
            event = pygame.event.poll()

            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                # Quit pygame properly
                pygame.quit()  

                GL_EXIT = True

                break      

            draw()
            pygame.display.flip()

    except KeyboardInterrupt:
        t1.join()

    print('Exiting main thread.')
