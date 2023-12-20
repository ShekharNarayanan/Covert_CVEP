#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Jordy Thielen (jordy.thielen@donders.ru.nl)

Python implementation of a keyboard for the noise-tagging project.
"""
'''Modifications @ SN
- Modified: The keyboard is replaced with just the Y and N keys.
- Added: "+" is placed in between the two classes.
- Added: Sequential format for showing the stimuli- starts with only N flashing, then Y, and then both.
- Added: Option to change the visual angle between the two classes.
- Added: Option for changing the placement of stimuli relative to the fixation cross.
- Added: Option to use the p300 paradigm along with the current setup.

'''

import os, json
import numpy as np
import psychopy
from psychopy import visual, event, monitors, misc, prefs
from psychopy import core
import math
from PIL import Image, ImageDraw
from matplotlib import pyplot as plt
from itertools import permutations
import random

os.chdir(r"C:/Users/s1081686/Desktop/RA_Project/Scripts/pynt_codes/SN_experiment")
class Keyboard(object):
    """
    A keyboard with keys and text fields.
    """

    def __init__(self, size, width, distance, screen=0, window_color=(0, 0, 0), stream=True):
        """
        Create a keyboard.

        Args:
            size (array-like): 
                The (width, height) of the window in pixels, i.e., resolution
            width (float):
                The width of the screen in centimeters
            distance (float):
                The distance of the user to the screen in centimeters
            screen (int):
                The screen number that is used, default: 0
            window_color (array-like):
                The background color of the window, default: (0, 0, 0)
            stream (bool):
                Whether or not to log events/markers in an LSL stream. Default: True
        """
        # Set up monitor (sets pixels per degree)
        self.monitor = monitors.Monitor("testMonitor", width=width, distance=distance)
        self.monitor.setSizePix(size)

        # Set up window
        self.window = visual.Window(monitor=self.monitor, screen=screen, units="pix", size=size, color=window_color, fullscr=True, waitBlanking=False, allowGUI=False,allowStencil=True)
        self.window.setMouseVisible(False)

        # Initialize keys and fields
        self.keys = dict()
        self.images_out = dict()
        self.fields = dict()

        # Setup LSL stream
        self.stream = stream
        if self.stream:
            from pylsl import StreamInfo, StreamOutlet
            self.outlet = StreamOutlet(StreamInfo(name='KeyboardMarkerStream', type='Markers', channel_count=4, nominal_srate=0, channel_format='string', source_id='KeyboardMarkerStream'))
        

    
    def get_size(self):
        """
        Get the size of the window in pixels, i.e., resolution.

        Returns:
            (array-like): 
                The (width, height) of the window in pixels, i.e., resolution
        """
        return self.window.size

    def get_pixels_per_degree(self):
        """
        Get the pixels per degree of visual angle of the window.

        Returns:
            (float): 
                The pixels per degree of visual angle
        """
        return misc.deg2pix(1.0, self.monitor)

    def get_framerate(self):
        """
        Get the framerate in Hz of the window.

        Returns:
            (float): 
                The framerate in Hz
        """
        return int(np.round(self.window.getActualFrameRate()))
    
    def circular_cropping(self,image_path):
        """
            Crop the square key images into a circle with a diameter length equal to the length of a side
            
            Args:
                image_path(str):
                   The path to the image file                        
               
        """ 
        img = Image.open(image_path)
        width, height = img.size
        
        # Create an alpha mask (circular shape)
        mask = Image.new('L', (width, height), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, width, height), fill=200,outline=0)

        # Apply the mask to the image
        img.putalpha(mask)
    
               
        return img
 

    def image_selector(self, name, size, pos , images=["black.png", "white.png"],draw= False):
        """
        Add a key to the keyboard.

        Args:
            name (str):
                The name of the key, if none then text is used
            size (array-like):
                The (width, height) of the key in pixels
            pos (array-like):
                The (x, y) coordinate of the center of the key, relative to the center of the window
            images (array-like):
                The images of the key. The first image is the default key. Indices will correspond to the 
                values of the codes. Default: ["black.png", "white.png"]
        """
        assert name not in self.keys, "Trying to add a box with a name that already extists!"
        images_out = dict()
        images_out[name] = []
    
        
        for i in range(len(images)):           
                       
            image = images[i]  
            
            if name == 'stt': # opto tracker image should still be a square 
                image_stim = visual.ImageStim(win=self.window,image=image,units="pix",pos=pos,size=size,autoLog=False) 
                
                 
            else:
                prep_image = self.circular_cropping(image)  
                image_stim = visual.ImageStim(win=self.window,image=prep_image,units="pix",pos=pos,size=size,autoLog=False)

            images_out[name].append(image_stim)
            
        if draw == True:
            images_out[name][0].setAutoDraw(True)
               
            
    
        return images_out
        # # Set autoDraw to True for first default key to keep app visible
        # self.keys[name][0].setAutoDraw(True)
        
       

    def add_text_field(self, name, text, size, pos, field_color=(0, 0, 0), text_color=(-1, -1, -1), auto_draw = True):
        """
        Add a text field to the keyboard.

        Args:
            name (str):
                The name of the text field, if none then text is used
            text (str):
                The text on the text field
            size (array-like):
                The (width, height) of the text field in pixels
            pos (array-like):
                The (x, y) coordinate of the center of the text field, relative to the center of the window
            field_color (array-like):
                The color of the background of the text field, default: (0, 0, 0)
            text_color (array-like):
                The color of the text on the text field, default: (-1, -1, -1)
        """
        # assert name not in self.fields, "Trying to add a text field with a name that already extists!"
        self.fields[name] =  visual.TextBox2(win=self.window, text=text, font='Courier', 
            units="pix", pos=pos, size=size, letterHeight=0.5*size[1], 
            color=text_color, fillColor=field_color, alignment="left", 
            autoDraw=auto_draw, autoLog=False)
        
        return self.fields[name]
        

    def set_field_text(self, name, text):
        """
        Set the text of a text field.

        Args:
            name (str):
                The name of the key
            text (str):
                The text
        """
        self.fields[name].setText(text)
        self.window.flip()

    def log(self, marker, on_flip=False):
        if self.stream and not marker is None:
            if not isinstance(marker, list):
                marker = [marker]
            if on_flip:
                self.window.callOnFlip(self.outlet.push_sample, marker)
            else:
                self.outlet.push_sample(marker)    
    
    def run(self, Keys = None,All_Images = None, codes = None, letter_change_time_msec=1000, target_letter = None, duration=None, target_dist = None, start_marker=None, stop_marker=None, cued_side = None): # flashing letter can be replaced by flashing side
        """
        Present a trial with concurrent flashing of each of the symbols.
        flashing letter can be replaced by flashing side
        Args:
            codes (dict): 
                A dictionary with keys being the symbols to flash and the value a list (the code 
                sequence) of integer states (images) for each frame
            duration (float):
                The duration of the trial in seconds. If the duration is longer than the code
                sequence, it is repeated. If no duration is given, the full length of the first 
                code is used. Default: None
            flashing_letter (str): 
                This argument decides which stimuli will be flashing. Options : 'Y', 'N' and 'both'. This is used to make a sequential paradigm
        """
       
       
       
        if Keys != None:
           cued_sequence = Keys['cued_sequence']
           non_cued_sequence = Keys['non_cued_sequence']

        # deciding the cue parameter specifications (will inform the participant to focus covertly on the left or the right)
        ppd = self.get_pixels_per_degree()
        
        if cued_side!= None:
            print('shape cued/non cued seq', cued_sequence.shape)
            if cued_side == 'LEFT':    
                self.add_text_field(None, "<",((3 * ppd, 3 * ppd)),(0,0),(0, 0, 0), (-1, -1, -1), auto_draw = True)
            else:
                self.add_text_field(None, ">",((3 * ppd, 3 * ppd)),(0,0),(0, 0, 0), (-1, -1, -1), auto_draw = True)
            
            
        if All_Images != None:
            stt_image = All_Images[0]
            Dict_Images_left = All_Images[1]
            Dict_Images_right = All_Images[2]
        
        #(1/60 hz is 16.67, dividing time/refresh rate tells us after how many frames the letter should be changed)
        # In case of CVEP, code presentation rate is the same as refresh rate, i.e 1 bit = 1 frame.
        # After a certain number of frames, the letter flashing on the screen will change
        change_frames = int(np.round(letter_change_time_msec/16.67)) 
   
        # Set number of frames
        if duration is None:
            print('i went to none condition')
            n_frames = len(codes[list(codes.keys())[0]])
        else:
            print('i went to else condition')
            n_frames = int(duration * self.get_framerate())

        # Send start marker
        self.log(start_marker, on_flip=True)
  
        # Loop frame flips
        for i in range(n_frames): 
                 
            
            # appending keys to key history every key 
            'key distance between targets missing'
            'do not repeat the same key feature missing'
            
            # Check quiting
            if i % 60 == 0:
                if self.is_quit():
                    self.quit()                                        
            
            # Draw keys with color depending on code state
            for name, code in codes.items(): 
                code_left = codes['LEFT']
                code_right = codes['RIGHT']
                
                if name == 'stt':
                    stt_image['stt'][code[i % len(code)]].draw()
    
                elif cued_side == 'LEFT' :                    
                    # print(name)
                    if (i % (2*change_frames)) < change_frames: #keys chosen = [0, 2x change_frames, 4xchangebits, 6 x changebits]
                        'i rem/change_frames logic works- good luck!'
                        
                        rem1 = i % (2*change_frames)
                        lkey_chosen = cued_sequence[int((i-rem1)/change_frames)]  # left side will have the cued letter sequence
                        rkey_chosen = non_cued_sequence[int((i-rem1)/change_frames)]
                        Dict_Images_left[lkey_chosen][lkey_chosen][code_left[i % len(code_left)]].draw()                        
                        Dict_Images_right[rkey_chosen][rkey_chosen][code_right[i % len(code_right)]].draw()   
                       
                        
                    else:
                        rem2 = i%change_frames
                        lkey_chosen = cued_sequence[int((i  - rem2)/change_frames)] # left side will have the cued letter sequence
                        rkey_chosen = non_cued_sequence[int((i  - rem2)/change_frames)]
                        Dict_Images_left[lkey_chosen][lkey_chosen][code_left[i % len(code_left)]].draw()                        
                        Dict_Images_right[rkey_chosen][rkey_chosen][code_right[i % len(code_right)]].draw()
        
                elif cued_side == 'RIGHT':
                    
                    if (i % (2*change_frames)) < change_frames: 
                        rem1 = i % (2*change_frames)
                        lkey_chosen = non_cued_sequence[int((i-rem1)/change_frames)]
                        rkey_chosen = cued_sequence[int((i-rem1)/change_frames)] # right side will have the cued letter sequence
                        Dict_Images_left[lkey_chosen][lkey_chosen][code_left[i % len(code_left)]].draw()                        
                        Dict_Images_right[rkey_chosen][rkey_chosen][code_right[i % len(code_right)]].draw()   
                    
                    
                    else:
                        rem2 = i%change_frames
                        lkey_chosen = cued_sequence[int((i  - rem2)/change_frames)]
                        rkey_chosen = non_cued_sequence[int((i  - rem2)/change_frames)]  # right side will have the cued letter sequence
                        Dict_Images_left[lkey_chosen][lkey_chosen][code_left[i % len(code_left)]].draw()                        
                        Dict_Images_right[rkey_chosen][rkey_chosen][code_right[i % len(code_right)]].draw() 
    
            self.window.flip()  
            
        self.add_text_field(None, "",((3 * ppd, 3 * ppd)),(0,0),(0, 0, 0), (-1, -1, -1), auto_draw = True)

        # Send stop markers
        self.log(stop_marker)

        # Set autoDraw to True to keep app visible
        for key in self.keys.values():
            key[0].setAutoDraw(True)
        self.window.flip()
        
    def sequence_generator(self,letter_arr = None, letter_change_time_msec = None, trial_time_sec= None, frame_rate= None, target_letter= None, target_dist= None):
        
        # Initializing output
        Output_Sequence = dict()
        
        total_frames = int(np.round(trial_time_sec*frame_rate))        
        change_letters = int(np.round(letter_change_time_msec/(16.67)))         
        target_count = int(np.ceil(total_frames/(change_letters*(target_dist + 1))))
        
        print(f'total frames(refresh rate x trial_time) i.e.,{frame_rate}x{trial_time_sec}=',total_frames)
        print('letters will change every :letter_change_time_msec/(16.67 ms)', change_letters,'frames')
        print(f'total letters needed in array (total_frames/ letter_change) = {total_frames}/{change_letters}=',np.ceil(total_frames/change_letters))
        print('target should appear every',target_dist,'letters or in', target_dist * change_letters, 'ms')
        print(f'total target letters (rounded up)needed are therfore total:{total_frames}/({change_letters}*{target_dist+1})=', target_count)
        
        
        output_size = int(np.ceil(total_frames/change_letters)) 
               
        letter_arr_non_target = [letter for letter in letter_arr if letter!= target_letter] # does not contain the target letter, see usage later in adjacency check
        
        cued_array = np.array(random.choices(letter_arr_non_target, k= output_size)) # target letters will be placed at an interval of target_dist+1 in this array later       
        
        # strategy for cued arratr: design an array with no two identical letters are placed adjacently and then place the target letter at target dist + 1
        # for noncued- target distancing will not be followed, only the adjacency rule will be checked
        
        # CUED ARRAY: making sure no identical letters are placed next to each other 
        for i in range(len(cued_array) - 1):
            if cued_array[i] == cued_array[i + 1]:
            # Find a different letter to replace the adjacent duplicate
                for letter in letter_arr_non_target: #replacing with any other letter other than the target letter
                    if letter != cued_array[i] and (i == 0 or letter != cued_array[i - 1]):
                        cued_array[i + 1] = letter
                        break
        
        # placing the target letter at target distances, range starts from 1 as first letter should not be the target
        for i in range(1, len(cued_array), target_dist + 1): # target_dist+1 allows exactly target_dist number of keys between two targets
            cued_array[i] = target_letter
        
        cued_array = np.array([char for char in cued_array])
      
        # non_cued_array: Creating a map that replaces every letter in the cued array with its conjugate,this is done such that:
        # 1. No two identical letters are flashing on the screen at the same time 
        # 2. There is a difference in the number of targets in the cued and non_cued array. This is how we will know if the participant paid attention to the correct side.
        
        # creating a mapping dictionary 
        mapping = {letter: letter_arr[(index + len(letter_arr)//2) % len(letter_arr)]
           for index, letter in enumerate(letter_arr)}
        
        non_cued_array = np.array([mapping[letter] for letter in cued_array])
        
        # storing both arrays
        Output_Sequence['cued_sequence'] = cued_array
        Output_Sequence['non_cued_sequence'] = non_cued_array
        
        return Output_Sequence
    
    def is_quit(self):
        """
        Test if a quit is forced by the user by a key-press.

        Returns:
            (bool): 
                True is quit forced, otherwise False
        """
        # If quit keys pressed, return True
        if len(event.getKeys(keyList=["q", "escape"])) > 0:
            return True
        return False

    def quit(self):
        """
        Quit the keyboard.
        """
        self.window.setMouseVisible(True)
        self.window.close()
        core.quit()

def test(n_trials, vis_angle, deg_ypos, code="onoff"):# modul gold codes 
    """
    Example experiment with initial setup and highlighting and presenting a few trials.
    """

    STREAM = False # True  when actually testing
    SCREEN = 2 # change for projection 
    SCREEN_SIZE = (1536, 864)# # Mac: (1792, 1120), LabPC: (1920, 1080), HP: 1536, 864
    SCREEN_WIDTH = 35.94  # Mac: (34,5), LabPC: 53.0, 35.94
    SCREEN_DISTANCE = 60.0
    SCREEN_COLOR = (0, 0, 0)
    FR = 60  # screen frame rate
    PR = 60  # codes presentation rate
    
    STT_WIDTH = 2.2 # adjust later
    STT_HEIGHT =2.2 # 3 when used in lab monitor

    TEXT_FIELD_HEIGHT = 3.0

    KEY_WIDTH = 3.0
    KEY_HEIGHT = 3.0
    
    # key space and its corresponding visual angle in degrees(inner edge of left stimuli to inner edge of right stimuli)
    # tan(theta/2) = (keyspace/2)/SCREEN_DISTANCE; therefore keyspace = 2*60* tan(theta/2); where theta is expected in radians    
    KEY_SPACE = 120 * np.tan(np.radians(vis_angle/2))
    
    KEY_COLORS = ["black", "white"]
    KEYS = ["N", "Y", "B","D"]
    

    CUE_TIME = 1  #0.8
    TRIAL_TIME = 10.5 # 10 for overt// dk for covert, 5 reps
    FEEDBACK_TIME = 0#0.5 -->  feedback is blue; cue is green
    ITI_TIME = 2#0.5
 
    # Initialize keyboard
    keyboard = Keyboard(size=SCREEN_SIZE, width=SCREEN_WIDTH, distance=SCREEN_DISTANCE, screen=SCREEN, window_color=SCREEN_COLOR, stream=STREAM)
    ppd = keyboard.get_pixels_per_degree()
       
    # Add stimulus timing tracker (stt) at left top of the screen
    x_pos = -SCREEN_SIZE[0] / 2 + STT_WIDTH / 2 * ppd
    y_pos = SCREEN_SIZE[1] / 2 - STT_HEIGHT / 2 * ppd
    images = ["images/black.png", "images/white.png"]
    stt_image = keyboard.image_selector("stt", (STT_WIDTH * ppd, STT_HEIGHT * ppd), (x_pos, y_pos), images,draw = True) 

    # # Add text field at the top of the screen
    x_pos = STT_WIDTH * ppd
    y_pos = SCREEN_SIZE[1] / 2 - TEXT_FIELD_HEIGHT * ppd / 2
    keyboard.add_text_field("text", "", (SCREEN_SIZE[0] - STT_WIDTH * ppd, TEXT_FIELD_HEIGHT * ppd), (x_pos, y_pos), (0, 0, 0), (-1, -1, -1))
    
    #Key Positions
    y_pos_both =  (-KEY_SPACE/2 * ppd - TEXT_FIELD_HEIGHT * ppd)* np.tan(np.radians(deg_ypos))
    x_pos_left = (-1)*(KEY_WIDTH + KEY_SPACE) * ppd
    x_pos_right= (1)*(KEY_WIDTH + KEY_SPACE) * ppd
    
    # KEYS USED
    KEYS = ["N", "Y", "B","D"]
    
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
        os.chdir(r"C:\Users\s1081686\Desktop\RA_Project\Scripts\pynt_codes\SN_experiment")
        tmp = np.load(f"codes_shifted\{code}_mod.npz")["codes"]
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
    
    # print('code dict looks like',codes.items())
    
    keyboard.log(["visual", "param", "codes", json.dumps(codes)])
    
    # Wait for start    
    keyboard.set_field_text("text", "")
    keyboard.set_field_text("text", "Press button to start.")
    print("Press button to start.")
    event.waitKeys()
   
    print("Starting.")
    # Start experiment
    keyboard.log(marker=["visual", "cmd", "start_experiment", ""])
    keyboard.set_field_text("text", "Starting...")

    # keyboard.run(highlights, 5.0)
    # keyboard.set_field_text("text", "")
    
    # arrays with randomly chosen cue_sides ( runs-- user will participate in 3 blocks, each with n_trials -- each with an equal amount of cues from left and right)   
    run_1 = np.random.permutation(np.arange(n_trials) % 2).astype("uint8")
    run_2 = np.random.permutation(run_1)     
    run_3 = np.random.permutation(run_2)
    
    # concatenating all runs
    runs = np.vstack((run_1,run_2,run_3))

    #  loop through runs
    for run in range(runs.shape[0]):       
        run_current = runs[run,:]
        
        # Choosing the target letter, target distance and letter change time -- could be changed for different runs
        target_dist = 5
        letter_change_time_msec = 500
        target_letter= 'D'

        Key_Sequence  = keyboard.sequence_generator(letter_arr = KEYS, letter_change_time_msec = letter_change_time_msec , trial_time_sec= TRIAL_TIME, 
                                        frame_rate= 60,
                                        target_letter= target_letter, 
                                        target_dist= target_dist)
        print('key sequence checks', Key_Sequence.items())
    

        # Loop trials
        text = ""
        keyboard.set_field_text("text", "")
        for i_trial in range(n_trials):
            log_dict_trial = dict()
            
            print("i trial is",i_trial)
 
                        
            # Choose which key will flash (for the third run, both keys are flashing)
            if run_current[i_trial] == 0:                
                cued_side = 'LEFT'
            else:
                cued_side = 'RIGHT'           
            
    #         print(f"{1 + i_trial:03d}/{n_trials}\t{target_key}\t{target}")
            log_dict_trial['cued_sequence'] = Key_Sequence['cued_sequence'].tolist()
            log_dict_trial['non_cued_sequence'] = Key_Sequence['non_cued_sequence'].tolist()
            log_dict_trial['target_letter'] = target_letter
            log_dict_trial['cued_side'] = cued_side
            log_dict_trial['target_distance'] =  target_dist
            log_dict_trial['letter_change_time_msec'] = letter_change_time_msec
            
            keyboard.log(["visual", "param", "target and sequence info",json.dumps(log_dict_trial)])
            print(keyboard.log(["visual", "param", "target and sequence info",json.dumps(log_dict_trial)]))
    #         keyboard.log(["visual", "param", "key", json.dumps(target_key)])            
            
            
    #         # Cue
    #         highlights[target_key] = [-2]
    #         keyboard.run(highlights, CUE_TIME, 
    #             start_marker=["visual", "cmd", "start_cue", json.dumps(1+i_trial)], 
    #             stop_marker=["visual", "cmd", "stop_cue", json.dumps(1+i_trial)])
    #         highlights[target_key] = [0]

            # Trial                     
            
            keyboard.run(Keys = Key_Sequence, 
                         All_Images=  All_Images, codes = codes, 
                         letter_change_time_msec =  letter_change_time_msec, 
                         target_letter = target_letter, 
                         duration = TRIAL_TIME, 
                         target_dist = target_dist, 
                         start_marker=["visual", "cmd", "start_trial", json.dumps(1+i_trial)], 
                         stop_marker=["visual", "cmd", "stop_trial", json.dumps(1+i_trial)],cued_side = cued_side)
          
    #         # text += target_key
    #         # keyboard.set_field_text("text", text)

    #         # # Feedback
    #         # highlights[target_key] = [-1]
    #         # keyboard.run(highlights, FEEDBACK_TIME, 
    #         #     start_marker=["visual", "cmd", "start_feedback", json.dumps(1+i_trial)], 
    #         #     stop_marker=["visual", "cmd", "stop_feedback", json.dumps(1+i_trial)])
    #         # highlights[target_key] = [0]

            # Inter-trial time
            keyboard.run(All_Images = All_Images, codes = highlights, duration =ITI_TIME, 
                start_marker=["visual", "cmd", "start_intertrial", json.dumps(1+i_trial)], 
                stop_marker=["visual", "cmd", "stop_intertrial", json.dumps(1+i_trial)])
            
        if run != 2:            
            keyboard.set_field_text("text", "Press any key to start the next block :)")  
            event.waitKeys()
            keyboard.set_field_text("text", "") 
        

    # Stop experiment
    keyboard.log(marker=["visual", "cmd", "stop_experiment", ""])
    keyboard.set_field_text("text", "Stopping...")
    print("Stopping.")
    # keyboard.run(highlights, 5.0)
    keyboard.set_field_text("text", "")
    keyboard.quit()
    print("Finished.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Test keyboard.py")
    parser.add_argument("-n", "--ntrials", type=int, help="number of trials", default=2)
    parser.add_argument("-c", "--code", type=str, help="code set to use", default="mgold_61_6521")
    parser.add_argument("-vs_ang","--vis_angle", type = float,help = 'visual angle between stimuli', default = 4)# degree x rename 
    parser.add_argument('-kyps',"--deg_ypos",type= float,help = 'degrees from the fixation cross', default = 0)
    
    args = parser.parse_args()

    test(n_trials=args.ntrials, vis_angle= args.vis_angle, deg_ypos = args.deg_ypos,code=args.code)
