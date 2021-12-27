# video packages
import picamera
import socket
import uuid
import os
from datetime import datetime as dt

# detection packages
import RPi.GPIO as GPIO
import time

# video setup
qual=22 # level of image quality between 1 (highest quality, largest size) and 40 (lowest quality, sm$
video_duration = 6 # video buffer duration in seconds
UID = uuid.uuid4().hex[:4].upper()+'_'+dt.now().strftime('%Y-%m-%d_%H-%M') # generate random unique I$
HostName=socket.gethostname()

camera = picamera.PiCamera()
camera.resolution = (1296, 972) # max fps is 42 at 1296x972
camera.framerate = 15 # recomended are 12, 15, 24, 30
camera.annotate_frame_num = True
camera.annotate_text_size = int(round(camera.resolution[0]/64))
camera.annotate_background = picamera.Color('black') # text background  colour
camera.annotate_foreground = picamera.Color('white') # text colour

# detection setup
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.IN)         #Read output from PIR motion sensor

start_cam = True
file_number = 0
timer = video_duration
list_recorded_file = []
record_file = False

while True:
    time.sleep(0.1)

    # detect movement
    i=GPIO.input(11)
    if i==0: #When output from motion sensor is LOW
        movement = False
    else:
        if movement == False:
            motion_start_time = time.time()
            print(motion_start_time)
            print(motion_start_time + 2)

        movement = True
        record_file = True

    # buffer control
    if start_cam:
        file_number += 1
        print "start_cam " + str(file_number)
        camera.start_recording('records/recorded' + str(file_number) + '.h264')
        start_time = time.time()
        start_cam = False
    elif timer > 0:
        current_time = time.time()
        if current_time - start_time > 1:
            timer -= 1
            start_time = current_time
    elif not movement:
        start_cam = True
        timer = video_duration
        print "write file"
        camera.stop_recording()
        if record_file:
            print "rename"
            # change to move
            os.rename('records/recorded' + str(file_number) + '.h264', 'records/movement_' + str(file_number) + '.h264')
            list_recorded_file.append(file_number)
            record_file = False
            print list_recorded_file
        if file_number - 1 > 0 and file_number - 1 not in list_recorded_file:
            os.remove('records/recorded' + str(file_number - 1) + '.h264')
    # else:
       #  print "go on because movement"
