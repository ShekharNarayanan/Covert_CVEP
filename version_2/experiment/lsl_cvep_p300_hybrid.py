"""
@author: Shekhar Narayanan (shekharnarayanan833@gmail.com), Jordy Thielen* (jordy.thielen@donders.ru.nl)
*:corresponding author

Python script for displaying the stimulus paradigm for the covert CVEP project
"""

import os, json
import numpy as np
from cvep_p300_speller import Keyboard
from psychopy import event, core
import yaml
import pickle


#---------------------------------------------------------------
# Parameters
#---------------------------------------------------------------

# path to the project, shape sequences and the images used
project_path = r'D:\Users\bci\Covert_CVEP\experiment_v2'
images_path = os.path.join(project_path,'images')
codes_path = os.path.join(project_path,'codes') # codes are different than graz
sequence_path = os.path.join(project_path,'shape_sequences')

with open(os.path.join(project_path,'config.yml'), "r") as yaml_file:
    config_data = yaml.safe_load(yaml_file)
    
experiment_params = config_data['experimental_params']

STREAM = experiment_params['STREAM'] # stream LSL data
SCREEN = experiment_params['SCREEN'] # which screen to use, set to 0 for no projection

# change  'HOME' to 'LAB' to run script on different monitor specifications, see config file
SCREEN_SIZE = eval(experiment_params['SCREEN_SIZE_LAB_PC'])# resolution of the monitor 
SCREEN_WIDTH = experiment_params['SCREEN_WIDTH_LAB_PC']  # width of the monitor in cm
SCREEN_DISTANCE = experiment_params['SCREEN_DISTANCE'] # distance at which the participant is seated
SCREEN_COLOR = eval(experiment_params['SCREEN_COLOR']) # background color of the screen
FR = experiment_params['FR_LAB']  # screen frame rate
PR = experiment_params['PR']  # codes presentation rate

# height and width of the stimulus timing tracker (STT) on the top left of the screen
STT_WIDTH = experiment_params['STT_WIDTH'] 
STT_HEIGHT = experiment_params['STT_HEIGHT'] 

TEXT_FIELD_HEIGHT = experiment_params['TEXT_FIELD_HEIGHT'] # width of the text field

# dimensions of the circles 
CIRCLE_WIDTH = experiment_params['CIRCLE_WIDTH']
CIRCLE_HEIGHT =  experiment_params['CIRCLE_HEIGHT']

SPACING_X = experiment_params['SPACING_X'] # distance between the circles in visual degrees
ANGLE_FROM_FIXATION = experiment_params['ANGLE_FROM_FIXATION']# angle between the fixation cross and the circles (set to 0)

CIRCLE_COLORS = experiment_params['CIRCLE_COLORS'] # background color of the shapes, black or white
SHAPES = experiment_params['SHAPES']# initials of shapes ['r', 'c', 'i', 't', 'h'] # rectangle, circle, inv triangle, triangle, hourglass

# Duration parameters
CUE_TIME = experiment_params['CUE_TIME']#
TRIAL_TIME = experiment_params['TRIAL_TIME'] 
RESPONSE_TIME = experiment_params['RESPONSE_TIME'] 
FEEDBACK_TIME = experiment_params['FEEDBACK_TIME'] 
ITI_TIME = experiment_params['ITI_TIME'] # inter trial interval

# number of trials 
N_TRIALS = experiment_params['N_TRIALS']

# participant number
N_PARTICIPANT = experiment_params['N_PARTICIPANT']

# Sequence Parameters
target_shape= SHAPES[-1]
shape_change_time_sec = .250 # The duration (sec) between the occurrence of two different shapes
total_frames = int(TRIAL_TIME*FR) # Total frames within a trial    
change_shapes = int(shape_change_time_sec*FR)  # The number of frames after which a new shape will appear inside the circle
min_target_key_distance = 6*shape_change_time_sec # min inter-target distance in TIME (duration of 6 shapes)
sequence_size = int(np.ceil(total_frames /change_shapes)) # size of sequence


# load sequence and target info dictionaries (overt and covert)
with open(os.path.join(sequence_path,f'P{N_PARTICIPANT}_overt.json'), 'rb') as f:
    overt_data = json.load(f)    
    
with open(os.path.join(sequence_path,f'P{N_PARTICIPANT}_covert.json'), 'r') as f:
    covert_data = json.load(f)

# load specific information about sequences and target info for both conditions

# overt 
overt_left_seq = np.array(overt_data['sequence_info']['left_sequences'])
overt_right_seq = np.array(overt_data['sequence_info']['right_sequences'])
overt_left_target_counts = np.array(overt_data['target_count_info']['left_target_counts'])
overt_right_target_counts = np.array(overt_data['target_count_info']['right_target_counts'])

# covert 
covert_left_seq = np.array(overt_data['sequence_info']['left_sequences'])
covert_right_seq = np.array(overt_data['sequence_info']['right_sequences'])
covert_left_target_counts = np.array(overt_data['target_count_info']['left_target_counts'])
covert_right_target_counts = np.array(overt_data['target_count_info']['right_target_counts'])

# chosen code
code = 'mgold_61_6521'

#---------------------------------------------------------------
# Setup
#---------------------------------------------------------------

# # Initialize keyboard
keyboard = Keyboard(size=SCREEN_SIZE, width=SCREEN_WIDTH, distance=SCREEN_DISTANCE, screen=SCREEN, window_color=SCREEN_COLOR, stream=STREAM)
ppd = keyboard.get_pixels_per_degree()
    
# Add stimulus timing tracker (stt) at left top of the screen
x_pos = -SCREEN_SIZE[0] / 2 + STT_WIDTH / 2 * ppd
y_pos = SCREEN_SIZE[1] / 2 - STT_HEIGHT / 2 * ppd

# get black and white images for stt
images_stt = [os.path.join(images_path,'black.png'),os.path.join(images_path,'white.png') ]

# place stt image on top left
stt_image = keyboard.image_selector("stt", (STT_WIDTH * ppd, STT_HEIGHT * ppd), (x_pos, y_pos), images_stt, auto_draw = True)  


# Add text field at the top of the screen
x_pos = STT_WIDTH * ppd
y_pos = SCREEN_SIZE[1] / 2 - TEXT_FIELD_HEIGHT * ppd / 2
keyboard.add_text_field("text", "", (SCREEN_SIZE[0] - STT_WIDTH * ppd, TEXT_FIELD_HEIGHT * ppd), (x_pos, y_pos), (0, 0, 0), (-1, -1, -1))

# Add fixation/cue text field
keyboard.add_text_field("fix", "", ((3 * ppd, 3 * ppd)), (0,0), (0, 0, 0), (-1, -1, -1), auto_draw=True)
keyboard.set_field_text("fix", "+")

#Circle Positions
y_pos_both =  (-SPACING_X/2 * ppd - TEXT_FIELD_HEIGHT * ppd)* np.tan(np.radians(ANGLE_FROM_FIXATION))
x_pos_left = (-1)*(CIRCLE_WIDTH + SPACING_X) * ppd
x_pos_right= (1)*(CIRCLE_WIDTH + SPACING_X) * ppd


# All shape Images
All_Images_Left = {}
All_Images_Right = {}

for shape in SHAPES:     
    images = [os.path.join(images_path,f'{shape}_{color}.png') for color in CIRCLE_COLORS]
    
    if shape == 'r': # rectangle is drawn by default on the left
        All_Images_Left[shape] = keyboard.image_selector(shape, (CIRCLE_WIDTH * ppd, CIRCLE_HEIGHT * ppd), (x_pos_left,y_pos_both), images, auto_draw = True) 
        All_Images_Right[shape] = keyboard.image_selector(shape, (CIRCLE_WIDTH * ppd, CIRCLE_HEIGHT * ppd), (x_pos_right,y_pos_both), images)
         
    elif shape == 'i': # triangle is drawn by default on the right
        All_Images_Left[shape] = keyboard.image_selector(shape, (CIRCLE_WIDTH * ppd, CIRCLE_HEIGHT * ppd), (x_pos_left,y_pos_both), images) 
        All_Images_Right[shape] = keyboard.image_selector(shape, (CIRCLE_WIDTH * ppd, CIRCLE_HEIGHT * ppd), (x_pos_right,y_pos_both), images, auto_draw = True)
    else:
    
        All_Images_Left[shape] = keyboard.image_selector(shape, (CIRCLE_WIDTH * ppd, CIRCLE_HEIGHT * ppd), (x_pos_left,y_pos_both), images) 
        All_Images_Right[shape] = keyboard.image_selector(shape, (CIRCLE_WIDTH * ppd, CIRCLE_HEIGHT * ppd), (x_pos_right,y_pos_both), images)

All_Images = [stt_image,All_Images_Left,All_Images_Right]


# Load sequences
if code != "onoff":

    tmp = np.load(os.path.join(project_path,'codes',f'{code}.npz'))["codes"].T

tmp = tmp.repeat(int(FR / PR), axis=0) # upsample the codes based on frame rate and presentation rate
  
codes = dict()
SIDES = ['LEFT','RIGHT'] 
for i_side in range(len(SIDES)):
    if code == 'onoff':
        pass
    else:
        codes[SIDES[i_side]] = tmp[:,i_side].tolist()

if code == "onoff":
    codes["stt"] = [1, 0]
else:
    codes["stt"] = [1] + [0] * int((1 + TRIAL_TIME) * FR)

# logging codes
keyboard.log(marker = ["visual","param","codes",json.dumps(codes)])

# #---------------------------------------------------------------
# # Experiment
# #---------------------------------------------------------------

# Wait for start    
keyboard.set_field_text("text", "")
keyboard.set_field_text("text", "Press button to start.")
print("Press button to start.")
event.waitKeys(keyList=["c"])

print("Starting.")
# Start experiment
keyboard.log(marker=["visual", "cmd", "start_experiment", ""])

# # arrays with randomly chosen cue_sides ( runs-- user will participate in 3 blocks, each with N_TRIALS -- 
# each with an equal amount of cues from left and right) 
  
run_1 = np.random.permutation(np.arange(N_TRIALS) % 2).astype("uint8")
run_2 = np.random.permutation(run_1)   
run_3 = np.random.permutation(run_2)
run_4 = np.random.permutation(run_3)
run_5 = np.random.permutation(run_4)

# concatenating all runs (helps with indexing in the loop below)
runs = np.vstack((run_1,run_2,run_3, run_4,run_5))

# #  loop through runs
for run_i in range(runs.shape[0]): 
    
    #start of run
    keyboard.log(marker = ["visual","cmd","start_run",json.dumps(1+run_i)])
    keyboard.set_field_text("text", "Starting...")
    core.wait(1, hogCPUperiod= 0.2)
    keyboard.set_field_text("text", "")
    
    # current run and trial range   
    run_current = runs[run_i,:]
    trial_range = range(run_i*N_TRIALS, (run_i+1)*N_TRIALS)
    
    run_accuracy_vec = np.zeros((N_TRIALS)) # accuracy vector storing the responses of the subject

    for i_trial in range(N_TRIALS):

        # start_trial
        keyboard.log(marker = ["visual","cmd","start_trial",json.dumps(1+i_trial)])
        
        if run_i==4: # the last run is always set to be overt 
            left_sequence = overt_left_seq[i_trial]
            right_sequence = overt_right_seq[i_trial]
            targets_left = overt_left_target_counts[i_trial]
            targets_right = overt_right_target_counts[i_trial]
            
        else: # the first four 4 runs are covert
            left_sequence = covert_left_seq[i_trial]
            right_sequence = covert_right_seq[i_trial]
            targets_left = covert_left_target_counts[i_trial]
            targets_right = covert_right_target_counts[i_trial]
        
        if run_current[i_trial] == 0:   
            cued_side = 'LEFT'             
            cue_sym = '<'           
  
        else:
            cued_side = 'RIGHT'
            cue_sym = '>'

        # log cued side to define labels for the experiment
        keyboard.log(["visual","param","cued_side",json.dumps(cued_side)])   
        
        # details for sequences and num_targets for the left side
        keyboard.log(["visual","param","left_sequence",json.dumps(left_sequence.tolist())]) 
        keyboard.log(["visual","param","left_num_targets",json.dumps(targets_left)])
        
        # details for sequences and num_targets for the right side
        keyboard.log(["visual","param","right_sequence",json.dumps(right_sequence.tolist())]) 
        keyboard.log(["visual","param","right_num_targets",json.dumps(targets_right)])

        # Cue 
        #cue start
        keyboard.log(marker = ["visual","cmd","start_cue", json.dumps(cue_sym)])
        
        keyboard.set_field_text("fix", cue_sym)
        keyboard.window.flip()
        core.wait(CUE_TIME, hogCPUperiod= 0.2)
        
        #cue stop
        keyboard.log(marker = ["visual","cmd","stop_cue",""])
        
        # Fixation
        keyboard.set_field_text("fix", "+")
    
        # Trial      
        keyboard.run(FR = FR, 
                     left_sequence= left_sequence, 
                     right_sequence= right_sequence,
                     All_Images= All_Images, 
                     codes= codes, 
                     duration= TRIAL_TIME, 
                     cued_side= cued_side, 
                     shape_change_time_sec= shape_change_time_sec,
                     start_marker= ["visual", "cmd", "start_stimulus", json.dumps(1+i_trial)],
                     stop_marker= ["visual", "cmd", "stop_stimulus", json.dumps(1+i_trial)])
        
        # Target Count Confirmation
        keyboard.set_field_text("fix", "?")
        keyboard.window.flip() 
        
        # Wait response
        response = ''
        timer = core.CountdownTimer(RESPONSE_TIME)
        response = ''
        #log response start
        keyboard.log(marker = ["visual","cmd","start_response",""]) 
        while timer.getTime() > 0:                       
            key = event.getKeys(keyList=["return", "backspace", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "num_1", "num_2", "num_3", "num_4", "num_5", "num_6", "num_7", "num_8", "num_9", "num_0"])
            
            if len(key) > 0:
                if 'return' in key:
                    break
                elif 'backspace' in key:
                    response = response[:-1]
                elif "num_" in key[-1]:
                    response += key[-1][-1]
                else:
                    response += key[-1]
                    
                # Show response
                keyboard.set_field_text("fix", response)

        
        print("response is:", response)
        keyboard.log(marker = ["visual","cmd","stop_response",json.dumps(response)])
        if response != '':
            response = float(response)
        
        # Present feedback
        if (cued_side == 'LEFT') and (response == targets_left):
            keyboard.set_field_text("fix", "+++")
            run_accuracy_vec[i_trial] = 1
            
        elif (cued_side == 'RIGHT') and (response == targets_right):
            keyboard.set_field_text("fix", "+++")
            run_accuracy_vec[i_trial] = 1 
                       
        else:
            keyboard.set_field_text("fix", "---")
            run_accuracy_vec[i_trial] = 0
        
        #feedback start
        keyboard.log(marker = ["visual","cmd","start_feedback",""])
        core.wait(FEEDBACK_TIME, hogCPUperiod= 0.2)
        keyboard.log(marker = ["visual","cmd","stop_feedback",""])

        # Inter-trial time
        keyboard.set_field_text("fix", "+")
        
        #start ITI
        keyboard.log(marker = ["visual","cmd","start_iti",""])        
        core.wait(ITI_TIME, hogCPUperiod= 0.2)
        
        #stop ITI
        keyboard.log(marker = ["visual","cmd","stop_iti",""])
            
        keyboard.log(marker = ["visual","cmd","stop_trial",json.dumps(1+i_trial)])
    keyboard.log(marker = ["visual","cmd","stop_run",json.dumps(1+run_i)])

    # Present performance
    run_acc_perc = (run_accuracy_vec).sum()/len(run_accuracy_vec)*100 
    keyboard.log(["visual", "param", "run_accuracy", json.dumps(run_acc_perc)])       
    keyboard.set_field_text("fix", f'{run_acc_perc:.0f}%') 
    keyboard.set_field_text("text", "Press any key to start the next run")  
    event.waitKeys(keyList=["c"])
    keyboard.set_field_text("fix", "+") 
    keyboard.set_field_text("text", "") 
    

# Stop experiment
keyboard.log(marker=["visual", "cmd", "stop_experiment", ""])
keyboard.set_field_text("text", "Stopping...")
print("Stopping.")
# keyboard.run(highlights, 5.0)
keyboard.set_field_text("text", "")
keyboard.quit()
print("Finished.")
