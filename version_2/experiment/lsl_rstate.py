#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Jordy Thielen (jordy.thielen@donders.ru.nl)

Python implementation of a flash-VEP block for the noise-tagging project.
"""


import os, json
import numpy as np
from cvep_p300_speller import Keyboard
from psychopy import event

from psychopy import event, core
import yaml


#---------------------------------------------------------------
# Parameters
#---------------------------------------------------------------

# path to the project, shape sequences and the images used
project_path = r'C:\Users\s1081686\Desktop\RA_Project\Scripts\pynt_codes\version_2'
images_path = os.path.join(project_path,'experiment_version_2','images')

with open(os.path.join(project_path,'config.yml'), "r") as yaml_file:
    config_data = yaml.safe_load(yaml_file)
    
experiment_params = config_data['experimental_params']

STREAM = experiment_params['STREAM'] # stream LSL data
SCREEN = experiment_params['SCREEN'] # which screen to use, set to 0 for no projection

# change  HOME to LAB to run script on different monitor specifications, see config file
SCREEN_SIZE = eval(experiment_params['SCREEN_SIZE_LAB_PC'])# resolution of the monitor 
SCREEN_WIDTH = experiment_params['SCREEN_WIDTH_LAB_PC']  # width of the monitor in cm
SCREEN_DISTANCE = experiment_params['SCREEN_DISTANCE'] # distance at which the participant is seated
SCREEN_COLOR = eval(experiment_params['SCREEN_COLOR']) # background color of the screen
FR = experiment_params['FR']  # screen frame rate
PR = experiment_params['PR']  # codes presentation rate

# height and width of the stimulus timing tracker (STT) on the top left of the screen -- remove the bottom
STT_TOP_WIDTH = 3
STT_TOP_HEIGHT = 3

TEXT_FIELD_HEIGHT = experiment_params['TEXT_FIELD_HEIGHT'] # width of the text field

# dimensions of the circles 
CIRCLE_WIDTH = experiment_params['CIRCLE_WIDTH']
CIRCLE_HEIGHT =  experiment_params['CIRCLE_HEIGHT']

SPACING_X = experiment_params['SPACING_X'] # distance between the circles in visual degrees
ANGLE_FROM_FIXATION = experiment_params['ANGLE_FROM_FIXATION']# angle between the fixation cross and the circles (set to 0)

CIRCLE_COLORS = experiment_params['CIRCLE_COLORS'] # background color of the shapes, black or white
SHAPES = experiment_params['SHAPES']# initials of shapes ['r', 'c', 'i', 't', 'h'] # rectangle, circle, inv triangle, triangle, hourglass

TRIAL_TIME = 2 * 60


#---------------------------------------------------------------
# Setup
#---------------------------------------------------------------


# Initialize keyboard
keyboard = Keyboard(size=SCREEN_SIZE, width=SCREEN_WIDTH, distance=SCREEN_DISTANCE, screen=SCREEN, window_color=SCREEN_COLOR, stream=STREAM)
ppd = keyboard.get_pixels_per_degree()

# images for stt
stt_images = [os.path.join(images_path,f'{color}.png') for color in ['black','white']]

# Add stimulus timing tracker at left top of the screen
x_pos = -SCREEN_SIZE[0] / 2 + STT_TOP_WIDTH / 2 * ppd
y_pos = SCREEN_SIZE[1] / 2 - STT_TOP_HEIGHT / 2 * ppd
stt_top_image = keyboard.image_selector("stt_top", (STT_TOP_WIDTH * ppd, STT_TOP_HEIGHT * ppd), (x_pos,y_pos), stt_images, auto_draw = True)


# Add text field at the top of the screen
x_pos = STT_TOP_WIDTH * ppd
y_pos = SCREEN_SIZE[1] / 2 - TEXT_FIELD_HEIGHT / 2 * ppd
keyboard.add_text_field("text", "", (SCREEN_SIZE[0] - STT_TOP_WIDTH * ppd, TEXT_FIELD_HEIGHT * ppd), (x_pos, y_pos), (0, 0, 0), (-1, -1, -1))

# Add one key
x_pos = 0
y_pos = 0
image_shapes= [os.path.join(images_path,'plus_black.png'),os.path.join(images_path,'plus_white.png')]
shape_im = keyboard.image_selector("shape", (CIRCLE_WIDTH * ppd, CIRCLE_HEIGHT * ppd), (x_pos,y_pos), image_shapes, auto_draw = True)

# Set codes
codes = dict()
codes["shape"] = [1]
codes["stt_top"] = [1] + [0] * int(FR * (TRIAL_TIME + 1))



#---------------------------------------------------------------
# Experiment
#---------------------------------------------------------------


# Wait for start
keyboard.set_field_text("text", "Waiting for researcher to start")
print("Waiting for researcher to start")
event.waitKeys()

# Start experiment
keyboard.log(marker=["visual", "cmd", "start_run", ""])
keyboard.set_field_text("text", "Starting")
print("Starting")
core.wait(5)


# Trial
All_Images = [stt_top_image,shape_im]
print("Started")
keyboard.run(FR = FR, 
                     left_sequence= None, 
                     right_sequence= None,
                     All_Images= All_Images, 
                     codes= codes, 
                     duration= TRIAL_TIME, 
                     cued_side= None, 
                     shape_change_time_sec= None,
                     start_marker= ["visual", "cmd", "start_trial", ""],
                     stop_marker= ["visual", "cmd", "stop_trial", ""],
                     sequence=False)

print("Stopped")

# Wait for stop
core.wait(5)
keyboard.log(marker=["visual", "cmd", "stop_run", ""])
keyboard.set_field_text("text", "Waiting for researcher to stop")
print("Waiting for researcher to stop")
event.waitKeys()
print("Stopped")
keyboard.quit()

# naming condition 
# task-rstate_open run-001
# task-rstate_closed run-001
# task-practice run-001
# task-covert run-001
# task-covert run-002
# task-covert run-003
# task-covert run-004
# task-overt run-001
# task-rstate_open run-002
# task-rstate_closed run-002
