# video packages
import picamera

# general packages
import socket
import uuid
import os
from datetime import datetime as dt
import time
import shutil

# detection packages
import RPi.GPIO as GPIO


# video setup
qual=22 # level of image quality between 1 (highest quality, largest size) and 40 (lowest quality, sm$
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

# general settings
start_cam = True           # start the camera
movement = False           # initial movement supposed false
file_number = 0            # number of file produced (buffer)
movement_number = 0        # number of movement detected
video_duration = 6         # duration of buffer videos in seconds
timer = video_duration
list_recorded_file = []    # list of the file recorded
record_file = False        # variable to record files when needed
time_before_movement = 2.5   # seconds recorded before movement detection


# remove previous files
# check if there are files
filenames_records = next(os.walk('records'), (None, None, []))[2]  # [] if no file
filenames_saved = next(os.walk('records/saved'), (None, None, []))[2]  # [] if no file
# ask and delete
if len(filenames_records) > 0 or len(filenames_saved) > 0:
    delete_files = input("Voulez-vous supprimer les fichiers existants ? (Y/N)")
    if delete_files == "Y":
        os.remove('records/' + filenames_records)
        os.remove('records/saved' + filenames_saved)


while True:
    # detect movement
    i=GPIO.input(11)
    if i==0: #When output from motion sensor is LOW
        movement = False
    else:
        if movement == False:
            motion_start_time = time.time()
            movement_number += 1
            print('Movement detected at ' + str(motion_start_time))
            print('Last file recording at ' + str(file_start_time))


            if motion_start_time - file_start_time  < time_before_movement:
                print('save 2 files')
                save_multiple_files = True
                # much more complex compare to length of previous file
                time_to_cut = round(motion_start_time - file_start_time - time_before_movement, 2)
                print('Movement starts' + str(time_to_cut) + ' seconds before the end of the other file')
            else:
                save_multiple_files = False
                print('save 1 file')
                time_to_cut = round(motion_start_time - file_start_time - time_before_movement, 2)
                print('Movement starts at ' + str(time_to_cut) + ' seconds in the file')

        movement = True
        record_file = True

    # buffer control
    if start_cam:
        file_number += 1
        print "start_cam " + str(file_number)
        camera.start_recording('records/recorded' + str(file_number) + '.h264')
        file_start_time = time.time()
        start_time = file_start_time
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
            print "copy movement file"
            # change to move
            file_to_copy = 'records/recorded' + str(file_number) + '.h264'
            if save_multiple_files:
                copied_file = 'records/saved/movement_' + str(movement_number) + '_buffer_' + str(file_number) + '_nocut' + '.h264'
            else:
                copied_file = 'records/saved/movement_' + str(movement_number) + '_buffer_' + str(file_number) + '_cut_' + str(time_to_cut) + '.h264'
            shutil.copyfile(file_to_copy, copied_file)
            list_recorded_file.append(file_number)
            record_file = False
            if save_multiple_files:
                file_to_copy = 'records/recorded' + str(file_number) + '.h264'
                copied_file = 'records/saved/movement_' + str(movement_number) + '_buffer_' + str(file_number - 1) + '_cut_' + str(time_to_cut) + '.h264'
                shutil.copyfile(file_to_copy, copied_file)
                list_recorded_file.append(file_number)

            print 'file ' + copied_file + ' recorded'
#        if file_number - 1 > 0 and file_number - 1 not in list_recorded_file:
#             os.remove('records/recorded' + str(file_number - 1) + '.h264')
    # else:
       #  print "go on because movement"
