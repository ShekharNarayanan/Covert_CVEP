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


STREAM = True # True  when actually testing
SCREEN = 2 # change for projection 
SCREEN_SIZE = (1536, 864)# # Mac: (1792, 1120), LabPC: (1920, 1080), HP: 1536, 864
SCREEN_WIDTH = 35.94  # Mac: (34,5), LabPC: 53.0, 35.94
SCREEN_DISTANCE = 60.0
SCREEN_COLOR = (0, 0, 0)
FR = 60  # screen frame rate
PR = 60  # codes presentation rate

STT_WIDTH = 2.2 # adjust later
STT_HEIGHT =2.2 # 3 when used in lab monitorq
TEXT_FIELD_HEIGHT = 3.0

KEY_WIDTH = 3.0
KEY_HEIGHT = 3.0

# Visual Angle Parameters 
deg_xpos = 4 # angle between the two stimuli on the screen
deg_ypos = 0 # angle from the fixation point

# key space and its corresponding visual angle in degrees(inner edge of left stimuli to inner edge of right stimuli)
# tan(theta/2) = (keyspace/2)/SCREEN_DISTANCE; therefore keyspace = 2*60* tan(theta/2); where theta is expected in radians 
   
KEY_SPACE = 120 * np.tan(np.radians(deg_xpos/2))

# Key colors and keys
KEY_COLORS = ["white", "blue"]
KEYS = ["Z", "L", "N", "T", "X"]

# Duration parameters
CUE_TIME = 1  #0.8
TRIAL_TIME = 15.5 # 10 for overt// dk for covert, 5 reps
FEEDBACK_TIME = 0#0.5 -->  feedback is blue; cue is green
ITI_TIME = 2#0.5

# chosen code
code = 'mgold_61_6521_mod'

# number of trials 
n_trials = 2


#---------------------------------------------------------------
# Setup
#---------------------------------------------------------------

# Initialize keyboard
keyboard = Keyboard(size=SCREEN_SIZE, width=SCREEN_WIDTH, distance=SCREEN_DISTANCE, screen=SCREEN, window_color=SCREEN_COLOR, stream=STREAM)
ppd = keyboard.get_pixels_per_degree()
    
# Add stimulus timing tracker (stt) at left top of the screen
x_pos = -SCREEN_SIZE[0] / 2 + STT_WIDTH / 2 * ppd
y_pos = SCREEN_SIZE[1] / 2 - STT_HEIGHT / 2 * ppd
images = ["images/black.png", "images/white.png"]
stt_image = keyboard.image_selector("stt", (STT_WIDTH * ppd, STT_HEIGHT * ppd), (x_pos, y_pos), images,draw = False) 
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
    images = [f"images/{KEYS[key_i]}_{color}.png" for color in KEY_COLORS]
            
    All_Images_Left[key] = keyboard.image_selector(key, (KEY_WIDTH * ppd, KEY_HEIGHT * ppd), (x_pos_left,y_pos_both), images,draw = False) 
    All_Images_Right[key] = keyboard.image_selector(key, (KEY_WIDTH * ppd, KEY_HEIGHT * ppd), (x_pos_right,y_pos_both), images,draw = False) 

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

# arrays with randomly chosen cue_sides ( runs-- user will participate in 3 blocks, each with n_trials -- each with an equal amount of cues from left and right)   
run_1 = np.random.permutation(np.arange(n_trials) % 2).astype("uint8")
run_2 = np.random.permutation(run_1)     
run_3 = np.random.permutation(run_2)

# concatenating all runs
runs = np.vstack((run_1,run_2,run_3))

#  loop through runs
for run in range(runs.shape[0]):       
    run_current = runs[run,:]
    run_accuracy_vec = []

    # Loop trials
    text = ""
    keyboard.set_field_text("text", "") 
    
    
    for i_trial in range(n_trials):
        
        # print("i trial is",i_trial)  
               
        # Specifying parameters for key sequence
        target_letter= 'X'
        letter_change_time_msec = 500 # The duration (msec) between the occurrance of two different letters
        total_frames = int(TRIAL_TIME*FR) # Total frames within a trial      
        change_letters = np.round(letter_change_time_msec/(16.67))  # The number of frames after which a new letter will appear on the screen
        target_dist_min = 5 # min target distance
        sequence_size = int(np.ceil(total_frames/change_letters)) # size of sequence
        max_targets = int(np.round(sequence_size/ (target_dist_min+1))) # maximum target occurrances possible in the trial
        targets_in_trial =5# random.randint(1,max_targets) # targets in the current trial
        print('max targets', max_targets)
        print('targets in this trial',targets_in_trial)
 
        
        Key_Sequence = keyboard.sequence_generator(letter_arr = KEYS, 
                                                   size_letter_arr = sequence_size, 
                                                   target_letter= target_letter, 
                                                   target_dist_min= target_dist_min, 
                                                   targets_in_trial = targets_in_trial)
        
        print(Key_Sequence['cued_sequence'])

        # Choosing which side will be attended 
        # if run_current[i_trial] == 0:   
        #     cued_side = 'LEFT'             
        #     cue_sym = '<'
        # else:
        cued_side = 'RIGHT'
        cue_sym = '>'
        # keyboard.set_field_text("text", "")
        print('SIDE',cued_side)
        # keyboard.add_text_field("text", "",((6 * ppd, 2 * ppd)),(0,0),(0, 0, 0), (-1, -1, -1), auto_draw = True)
        t1 = pylsl.local_clock()
        # keyboard.log("internal time before dict", print_time = True)
        log_dict_trial = dict()       
        
#         print(f"{1 + i_trial:03d}/{n_trials}\t{target_key}\t{target}")
        'make the keys conventional-- similar format' 
        log_dict_trial['run_and_trial'] = [run, i_trial]
        log_dict_trial['cued_sequence'] = Key_Sequence['cued_sequence'].tolist()
        log_dict_trial['non_cued_sequence'] = Key_Sequence['non_cued_sequence'].tolist()
        log_dict_trial['cued_side'] = cued_side
        log_dict_trial['target_count'] = targets_in_trial
        # log_dict_trial['letter_change_time_msec'] = letter_change_time_msec # not needed for each trial 

        keyboard.log(["visual", "param", "target and sequence info",json.dumps(log_dict_trial)])
        
        t2 = pylsl.local_clock()
        print('time difference between dict entries', (t2 - t1)* 1000, 'ms')
        # keyboard.log("internal time before dict", print_time = True)
 
  
        
        'introduce a cue time'
        'make the dictionary content more efficient-- all has to be done within a frame 16.67 ms'
        'be careful of the time in the log, histogram of the time the response is logged'
        'especially relevent because of the neural responses associated to short and long flashes might be shifted'
        
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
                     duration=TRIAL_TIME, 
                     start_marker=["visual", "cmd", "start_trial", json.dumps(1+i_trial)], 
                     stop_marker=["visual", "cmd", "stop_trial", json.dumps(1+i_trial)], 
                     cued_side = cued_side)

        # Target Count Confirmation
        keyboard.add_text_field(None,"?",((3 * ppd, 3 * ppd)),(0,0),(0, 0, 0), (-1, -1, -1), auto_draw = True)
        keyboard.window.flip()  
            
        keys_pressed = event.waitKeys(maxWait= 4)
        if keys_pressed is None:
            keys_pressed = '-'
        tick_symbol = u'\u2713'  # Unicode for tick mark (✓)
        cross_symbol = u'\u274C'  # Unicode for cross mark (❌) 
        
        if keys_pressed[0]== str(targets_in_trial):
            keyboard.add_text_field(None, tick_symbol,((3 * ppd, 3 * ppd)),(0,0),(0, 0, 0), (0,1,0), auto_draw = True, font ='Arial Unicode MS' )
            run_accuracy_vec.append(1)
        else:
            keyboard.add_text_field(None, 'X',((3 * ppd, 3 * ppd)),(0,0),(0, 0, 0), (1, 0, 0), font ='Arial Unicode MS')
            run_accuracy_vec.append(0)
            
        keyboard.set_field_text("text", "")
   
#         # text += target_key
#         # keyboard.set_field_text("text", text)

#         # # Feedback
#         # highlights[target_key] = [-1]
#         # keyboard.run(highlights, FEEDBACK_TIME, 
#         #     start_marker=["visual", "cmd", "start_feedback", json.dumps(1+i_trial)], 
#         #     stop_marker=["visual", "cmd", "stop_feedback", json.dumps(1+i_trial)])
#         # highlights[target_key] = [0]

        # Inter-trial time
        keyboard.run(Keys=Key_Sequence, All_Images = All_Images, codes = highlights, duration =ITI_TIME, 
            start_marker=["visual", "cmd", "start_intertrial", json.dumps(1+i_trial)], 
            stop_marker=["visual", "cmd", "stop_intertrial", json.dumps(1+i_trial)])


        # keyboard.set_field_text("text", "")  
    run_acc_perc = (np.array(run_accuracy_vec).sum()/len(run_accuracy_vec))*100 
    if run_acc_perc<=50:
        color = (1, 0, 0)
    elif run_acc_perc>50 and run_acc_perc<75:
        color = (1.0, 0.647, 0.0)
    else:
        color = (0, 1, 0)
        
    keyboard.add_text_field(None, f'{run_acc_perc:.0f}%',((3 * ppd, 2 * ppd)),(0,0),(0, 0, 0), color, auto_draw = True)   
    if run != (runs.shape[0]-1):            
        keyboard.set_field_text("text", "Press any key to start the next block :)")  
        event.waitKeys()
        keyboard.add_text_field(None, ' ',((5 * ppd, 3 * ppd)),(0,0),(0, 0, 0), (-1, -1, -1), auto_draw = True)  
        keyboard.set_field_text("text", "") 
    # else:
        
        
    

# Stop experiment
keyboard.log(marker=["visual", "cmd", "stop_experiment", ""])
keyboard.set_field_text("text", "Stopping...")
print("Stopping.")
# keyboard.run(highlights, 5.0)
keyboard.set_field_text("text", "")
keyboard.quit()
print("Finished.")