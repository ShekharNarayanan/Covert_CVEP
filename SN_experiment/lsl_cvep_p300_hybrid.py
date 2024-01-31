"""
@author: Jordy Thielen (jordy.thielen@donders.ru.nl), Shekhar Narayanan (shekharnarayanan833@gmail.com)

A hybrid P300 and code-modulated VEP speller for the covert CVEP project.
"""

import os, json
import numpy as np
from cvep_p300_speller import Keyboard
from psychopy import event, core
import random
import pylsl

# Screen Parameters
STREAM = True # True  when actually testing
SCREEN = 2 # change for projection 
SCREEN_SIZE = (1920, 1080)# # Mac: (1792, 1120), LabPC: (1920, 1080), HP: 1536, 864
SCREEN_WIDTH = 35.94  # Mac: (34,5), LabPC: 53.0, 35.94
SCREEN_DISTANCE = 60.0
SCREEN_COLOR = (0, 0, 0)
FR = 60  # screen frame rate
PR = 60  # codes presentation rate

# Key image Parameters
STT_WIDTH = 2.2 # adjust later
STT_HEIGHT =2.2 # 3 when used in lab monitorq
TEXT_FIELD_HEIGHT = 3.0

KEY_WIDTH = 3.0
KEY_HEIGHT = 3.0

# Visual Angle Parameters 
deg_xpos = 4.2 # angle between the two stimuli on the screen
deg_ypos = 0 # angle from the fixation point

# key space and its corresponding visual angle in degrees(inner edge of left stimuli to inner edge of right stimuli)
# tan(theta/2) = (keyspace/2)/SCREEN_DISTANCE; therefore keyspace = 2*60* tan(theta/2); where theta is expected in radians 
   
KEY_SPACE = deg_xpos 

# Key colors and keys
KEY_COLORS = ["black", "white"]
KEYS = ['s', 'c', 'i', 't', 'h'] # rectangle, circle, inv triangle, triangle, hourglass

# Duration parameters
CUE_TIME = 0#1  #0.8
TRIAL_TIME = 15.5 # 10 for overt// dk for covert, 5 reps
FEEDBACK_TIME = 0#0.5 -->  feedback is blue; cue is green
ITI_TIME = 0#2#0.5

# Sequence Parameters
# Sequence Parameters
target_letter= KEYS[-1]
letter_change_time_msec = 250 * 1e-3 # The duration (msec) between the occurrance of two different letters
total_frames = int(TRIAL_TIME*FR) # Total frames within a trial    
change_letters = np.round(letter_change_time_msec/(1/FR))  # The number of frames after which a new letter will appear on the screen
min_target_key_distance = 6*letter_change_time_msec # min target distance in TIME (duration of 6 letters)
sequence_size = int(np.ceil(total_frames /(change_letters))) # size of sequence
max_targets = int(TRIAL_TIME/ min_target_key_distance)

# chosen code
code = 'mgold_61_6521_mod'

# number of trials 
n_trials = 4


'start the lsl recorder click the tick option, where its saved on the right, other deets are obvious then press start'

'first start this script, press start on lsl, then start the task'

#---------------------------------------------------------------
# Setup
#---------------------------------------------------------------

# Initialize keyboard
keyboard = Keyboard(size=SCREEN_SIZE, width=SCREEN_WIDTH, distance=SCREEN_DISTANCE, screen=SCREEN, window_color=SCREEN_COLOR, stream=STREAM)
ppd = keyboard.get_pixels_per_degree()
    
# Add stimulus timing tracker (stt) at left top of the screen
x_pos = -SCREEN_SIZE[0] / 2 + STT_WIDTH / 2 * ppd
y_pos = SCREEN_SIZE[1] / 2 - STT_HEIGHT / 2 * ppd
images = ["images_BOTH_SIZE_INC/black.png", "images_BOTH_SIZE_INC/white.png"]

stt_image = keyboard.image_selector("stt", (STT_WIDTH * ppd, STT_HEIGHT * ppd), (x_pos, y_pos), images) 
# print(stt_image['stt'][1])

# # Add text field at the top of the screen
x_pos = STT_WIDTH * ppd
y_pos = SCREEN_SIZE[1] / 2 - TEXT_FIELD_HEIGHT * ppd / 2
keyboard.add_text_field("text", "", (SCREEN_SIZE[0] - STT_WIDTH * ppd, TEXT_FIELD_HEIGHT * ppd), (x_pos, y_pos), (0, 0, 0), (-1, -1, -1))

#Key Positions
y_pos_both =  (-KEY_SPACE/2 * ppd - TEXT_FIELD_HEIGHT * ppd)* np.tan(np.radians(deg_ypos))
x_pos_left = (-1)*(KEY_WIDTH + KEY_SPACE) * ppd
x_pos_right= (1)*(KEY_WIDTH + KEY_SPACE) * ppd


# All Key Images
All_Images_Left = {}
All_Images_Right = {}
for key_i in range(len(KEYS)):
    key = KEYS[key_i]      
    images = [f"images_BOTH_SIZE_INC/{KEYS[key_i]}_{color}.png" for color in KEY_COLORS]
            
    All_Images_Left[key] = keyboard.image_selector(key, (KEY_WIDTH * ppd, KEY_HEIGHT * ppd), (x_pos_left,y_pos_both), images) 
    All_Images_Right[key] = keyboard.image_selector(key, (KEY_WIDTH * ppd, KEY_HEIGHT * ppd), (x_pos_right,y_pos_both), images) 

All_Images = [stt_image,All_Images_Left,All_Images_Right]

# # Load sequences
if code != "onoff":
    # path for the code
    os.chdir(r"C:\Users\s1081686\Desktop\RA_Project\Scripts\pynt_codes\SN_experiment")
    tmp = np.load(f"codes_shifted\{code}.npz")["codes"]
    print(tmp.shape)
    
codes = dict()
SIDES = ['LEFT','RIGHT'] # code 0 is for the right, 1 is for the left
for i_side in range(len(SIDES)):
    if code == 'onoff':
        pass
    else:
        codes[SIDES[i_side]] = tmp[:,i_side].tolist()

if code == "onoff":
    codes["stt"] = [1, 0]
else:
    codes["stt"] = [1] + [0] * int((1 + TRIAL_TIME) * keyboard.get_framerate())

# # Set highlights
highlights = dict()
for side in SIDES:
            highlights[side] = [0]
highlights["stt"] = [0]
keyboard.log(["visual", "param", "codes", json.dumps(codes)])
print('codes logged')

#---------------------------------------------------------------
# Experiment
#---------------------------------------------------------------

# Wait for start    
keyboard.set_field_text("text", "")
keyboard.set_field_text("text", "Press button to start.")
print("Press button to start.")
event.waitKeys()

print("Starting.")
# Start experiment
keyboard.log(marker=["visual", "cmd", "start_experiment", ""])
print('start marker logged')

keyboard.set_field_text("text", "Starting...")

# arrays with randomly chosen cue_sides 
# (runs-- user will participate in 3 blocks, each with n_trials -- each with an equal amount of trials from left and right cued sides)   
run_1 = np.random.permutation(np.arange(n_trials) % 2).astype("uint8")
run_2 = np.random.permutation(run_1)     
run_3 = np.random.permutation(run_2)

# concatenating all runs (helps with indexing in the loop below)
runs = np.vstack((run_1,run_2,run_3))

# Specifying parameters for key sequence

dict_time_vec = []

#  loop through runs
for run_i in range(runs.shape[0]):       
    run_current = runs[run_i,:]
    run_accuracy_vec = [] # % of correctly counted target occurrences in a run

    # Loading number of cued targets for both sides in the current run
    targs_left, targs_right = keyboard.targets_in_trial(n_trials=n_trials, max_targets=max_targets)

    keyboard.set_field_text("text", "") 
    
    
    for i_trial in range(n_trials):

        # Choosing which side will be attended 
        if run_current[i_trial] == 0:   
            cued_side = 'LEFT'             
            cue_sym = '<'
            targets_in_trial_cued = int(targs_left.pop())
            
            
        else:
            cued_side = 'RIGHT'
            cue_sym = '>'
            targets_in_trial_cued = int(targs_right.pop())
            
        # targets in non_cued_side
        targets_in_trial_non_cued =  random.randint(1, max_targets)
        
        while targets_in_trial_non_cued == targets_in_trial_cued: # targets on cued and non_cued sides within a trial should be unequal
            targets_in_trial_non_cued = random.randint(1, max_targets)
            
        print('targets in this trial',targets_in_trial_cued)
        print('SIDE',cued_side)

        # Generating the key sequence used
        Key_Sequence = {}
        
        cued_sq, non_cued_sq = keyboard.sequence_generator(letter_arr = KEYS,
                                                           size_letter_arr = sequence_size, 
                                                           target_letter= target_letter,
                                                           targets_in_trial_cued = targets_in_trial_cued, 
                                                           targets_in_trial_non_cued = targets_in_trial_non_cued)
        
        Key_Sequence['cued_sequence'] = cued_sq
        Key_Sequence['non_cued_sequence'] = non_cued_sq
        
        
        # Cue
        keyboard.add_text_field(None, cue_sym,((3 * ppd, 3 * ppd)),(0,0),(0, 0, 0), (-1, -1, -1), auto_draw = True)
        keyboard.window.flip()
        core.wait(1, hogCPUperiod= 0.2)
        keyboard.add_text_field(None, "+",((3 * ppd, 3 * ppd)),(0,0),(0, 0, 0), (-1, -1, -1), auto_draw = True)
        
        
        # Trial                 
        keyboard.run(Keys = Key_Sequence, 
                     All_Images = All_Images, 
                     codes = codes, 
                     letter_change_time_msec=letter_change_time_msec, 
                     PR = PR,
                     duration=TRIAL_TIME, 
                     start_marker=["visual", "cmd", "start_trial", json.dumps(1+i_trial)], 
                     stop_marker=["visual", "cmd", "stop_trial", json.dumps(1+i_trial)], 
                     cued_side = cued_side)

        # Target Count Confirmation
        keyboard.add_text_field(None,"?",((3 * ppd, 3 * ppd)),(0,0),(0, 0, 0), (-1, -1, -1), auto_draw = True)
        keyboard.window.flip()  
            
        key_pressed = event.waitKeys(maxWait= 3) # wait time of 3 seconds
        if key_pressed is None:
            key_pressed = '-'
        tick_symbol = u'\u2713'  # Unicode for tick mark (✓)
        cross_symbol = u'\u274C'  # Unicode for cross mark (❌) 
        
        if key_pressed[0]== str(targets_in_trial_cued):
            keyboard.add_text_field(None, tick_symbol,((3 * ppd, 3 * ppd)),(0,0),(0, 0, 0), (0,1,0), auto_draw = True, font ='Arial Unicode MS' )
            run_accuracy_vec.append(1)
        else:
            keyboard.add_text_field(None, 'X',((3 * ppd, 3 * ppd)),(0,0),(0, 0, 0), (1, 0, 0), font ='Arial Unicode MS')
            run_accuracy_vec.append(0)
            
        keyboard.set_field_text("text", "")
        
        t1 = keyboard.log(['init dict', "", "",""], print_time=True)
        log_dict_trial = dict()       
        # 'make the keys conventional-- similar format' 
        log_dict_trial['run_and_trial'] = [run_i, i_trial]
        log_dict_trial['cued_sequence'] = Key_Sequence['cued_sequence'].tolist()
        log_dict_trial['non_cued_sequence'] = Key_Sequence['non_cued_sequence'].tolist()
        log_dict_trial['cued_side'] = cued_side
        log_dict_trial['target_count'] = targets_in_trial_cued
        log_dict_trial['key_pressed'] = key_pressed
        
        t2 = keyboard.log(["target and sequence info","","",""],json.dumps(log_dict_trial), print_time=True)
        dict_time_vec.append((t2 - t1)*1000)
        # t2 = pylsl.local_clock()
        print('time difference between dict entries', (t2 - t1)* 1000, 'ms')


        # Inter-trial time
        keyboard.run(FR = FR, Keys=Key_Sequence, All_Images = All_Images, codes = highlights, duration =ITI_TIME, 
            start_marker=["visual", "cmd", "start_intertrial", json.dumps(1+i_trial)], 
            stop_marker=["visual", "cmd", "stop_intertrial", json.dumps(1+i_trial)])



    run_acc_perc = (np.array(run_accuracy_vec).sum()/len(run_accuracy_vec))*100 
    keyboard.log(["run accuracy %", "", "", ""],json.dumps(run_acc_perc))
    
    if run_acc_perc<=50:
        color = (1, 0, 0)
    elif run_acc_perc>50 and run_acc_perc<75:
        color = (1.0, 0.647, 0.0)
    else:
        color = (0, 1, 0)
        
    keyboard.add_text_field(None, f'{run_acc_perc:.0f}%',((3 * ppd, 2 * ppd)),(0,0),(0, 0, 0), color, auto_draw = True) 
      
    if run_i != (runs.shape[0]-1):            
        keyboard.set_field_text("text", "Press any key to start the next block :)")  
        event.waitKeys()
        keyboard.add_text_field(None, ' ',((5 * ppd, 3 * ppd)),(0,0),(0, 0, 0), (-1, -1, -1), auto_draw = True)  
        keyboard.set_field_text("text", "") 

 # Stop experiment
 keyboard.log(marker=["visual", "cmd", "stop_experiment", ""])
 keyboard.set_field_text("text", "Stopping...")
 print("Stopping.")
 keyboard.run(highlights, 5.0)
 keyboard.set_field_text("text", "")
 keyboard.quit()
 print("Finished.")
     


