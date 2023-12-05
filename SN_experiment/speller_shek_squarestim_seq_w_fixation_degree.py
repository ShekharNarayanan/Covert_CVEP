#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Jordy Thielen (jordy.thielen@donders.ru.nl)

Python implementation of a keyboard for the noise-tagging project.
"""
'''Modifications @ SN:
- Removed: The matrix keyboard is reduced to two classes: Y and N
- Added: "+" is placed in between the two classes
- Added: Function to highlight the cued key during trial
- Added: Sequential format for showing the stimuli- starts with only N flashing, then Y and then both.
- Added: Option to change the visual angle between the two classes.
- Added: Option for changing the placement of stimuli relative to the fixation cross.

'''

import os, json
import numpy as np
import psychopy
from psychopy import visual, event, monitors, misc, prefs
from psychopy import core
import math
import time
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
        self.window = visual.Window(monitor=self.monitor, screen=screen, units="pix", size=size, color=window_color, fullscr=True, waitBlanking=False, allowGUI=False)
        self.window.setMouseVisible(False)

        # Initialize keys and fields
        self.keys = dict()
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

    def add_key(self, name, size, pos, images=["black.png", "white.png"]):
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
        self.keys[name] = []
    
        
        for i in range(len(images)):
           
            image = images[i] 
            
            self.keys[name].append(visual.ImageStim(win=self.window, image=image,
            units="pix", pos=pos, size=size, autoLog=False))

        # Set autoDraw to True for first default key to keep app visible
        self.keys[name][0].setAutoDraw(True)
        
    def add_highlighter(self,name,color,lineWidth,size_str = 'same'):
        """
        Add a rectangular highlighter window around the cued option

        Args:
            name (str):
                The name of the key
            color (array):
                color of the window (set to red during trial otherwise same as background)
            lineWidth (int):
                Specify the thickness of the border
            size_str (str):
                Area of the highlighter (default is same as the key area)
            
        """
        assert name in self.keys, "Key does not exist!"
        key = self.keys[name][0]  # Get the first image associated with the key
        
        if size_str == 'same':
            highlighter = visual.Rect(win=self.window,
                                  width=key.size[0]+0.05, height=key.size[1]+0.05, 
                                  units="pix", lineWidth = lineWidth,lineColor=color, pos=key.pos, 
                                  fillColor=None, opacity= 1)
        else:
            
            highlighter = visual.Rect(win=self.window,
                                  width=2*key.size[0]+0.05, height=2*key.size[1]+0.05, 
                                  units="pix", lineWidth = lineWidth,lineColor=color, pos=key.pos, 
                                  fillColor=None, opacity= 1)
            
            
    
        
  
        
        highlighter.setAutoDraw(True)
        
            
        
        

    def add_text_field(self, name, text, size, pos, field_color=(0, 0, 0), text_color=(-1, -1, -1)):
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
        assert name not in self.fields, "Trying to add a text field with a name that already extists!"
        self.fields[name] = self.fields[name] = visual.TextBox2(win=self.window, text=text, font='Courier', 
            units="pix", pos=pos, size=size, letterHeight=0.5*size[1], 
            color=text_color, fillColor=field_color, alignment="left", 
            autoDraw=True, autoLog=False)
        
        

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
    
    def run(self, codes, duration=None, start_marker=None, stop_marker=None, flashing_letter = None):
        """
        Present a trial with concurrent flashing of each of the symbols.

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
        # Set number of frames
        if duration is None:
            n_frames = len(codes[list(codes.keys())[0]])
        else:
            n_frames = int(duration * self.get_framerate())

        # Set autoDraw to False for full control
        for key in self.keys.values():
            key[0].setAutoDraw(False)
            

        # Send start marker
        self.log(start_marker, on_flip=True)

        # Loop frame flips
        for i in range(n_frames):

            # Check quiting
            if i % 60 == 0:
                if self.is_quit():
                    self.quit()

            # Draw keys with color depending on code state
            for name, code in codes.items():
                
                if flashing_letter == 'both':
                    self.keys[name][code[i % len(code)]].draw()
                    
                elif name == flashing_letter or name == 'stt':
                                        
                    self.keys[name][code[i % len(code)]].draw()   # drawning the chosen key and stt, only the chosen key flashes now             
                                        
                else:
                    self.keys[name][0].draw() # drawing the key but keeping it constantly as black
               
            self.window.flip()        
   
           
            
        # Send stop markers
        self.log(stop_marker)

        # Set autoDraw to True to keep app visible
        for key in self.keys.values():
            key[0].setAutoDraw(True)
        self.window.flip()

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


def test(n_trials, vis_angle, deg_ypos, code="onoff"):# modulated gold codes used
    """
    Example experiment with initial setup and highlighting and presenting a few trials.
    """

    STREAM = False # True during the actual experiment
    SCREEN = 2 # change for projection (0 during the actual experiment)
    SCREEN_SIZE = (1536, 864)# # Mac: (1792, 1120), LabPC: (1920, 1080), HP: 1536, 864
    SCREEN_WIDTH = 35.94  # in cm Mac: (34,5), LabPC: 53.0, 35.94
    SCREEN_DISTANCE = 60.0
    SCREEN_COLOR = (0, 0, 0)
    FR = 60  # screen frame rate
    PR = 60  # codes presentation rate
    
    STT_WIDTH = 2.2 # adjust later
    STT_HEIGHT =2.2 # 3 when used in lab monitor during the experiment

    TEXT_FIELD_HEIGHT = 3.0

    KEY_WIDTH = 3.0
    KEY_HEIGHT = 3.0
    
    # key space and its corresponding visual angle in degrees(inner edge of left stimuli to inner edge of right stimuli)
    # tan(theta/2) = (keyspace/2)/SCREEN_DISTANCE; therefore keyspace = 2*60* tan(theta/2); where theta is expected in radians    
    KEY_SPACE = 120 * np.tan(np.radians(vis_angle/2))
    
    KEY_COLORS = ["black", "white", "green", "blue"]
    KEYS = ["N", 
            "Y"]
    

    CUE_TIME = 1  #0.8
    TRIAL_TIME = 10.5 # 10 for overt// dk for covert, 5 reps
    FEEDBACK_TIME = 0#0.5 -->  feedback is blue; cue is green
    ITI_TIME = 0#0.5

    # Initialize keyboard
    keyboard = Keyboard(size=SCREEN_SIZE, width=SCREEN_WIDTH, distance=SCREEN_DISTANCE, screen=SCREEN, window_color=SCREEN_COLOR, stream=STREAM)
    ppd = keyboard.get_pixels_per_degree()
   
    
    # Add stimulus timing tracker at left top of the screen
    x_pos = -SCREEN_SIZE[0] / 2 + STT_WIDTH / 2 * ppd
    y_pos = SCREEN_SIZE[1] / 2 - STT_HEIGHT / 2 * ppd
    images = ["images/black.png", "images/white.png"]
    keyboard.add_key("stt", (STT_WIDTH * ppd, STT_HEIGHT * ppd), (x_pos, y_pos), images)
    
    print("add text key first line is ",TEXT_FIELD_HEIGHT * ppd)
    

    # # Add text field at the top of the screen
    x_pos = STT_WIDTH * ppd
    y_pos = SCREEN_SIZE[1] / 2 - TEXT_FIELD_HEIGHT * ppd / 2
    keyboard.add_text_field("text", "", (SCREEN_SIZE[0] - STT_WIDTH * ppd, TEXT_FIELD_HEIGHT * ppd), (x_pos, y_pos), (0, 0, 0), (-1, -1, -1))
    
    # Add '+' between the two classes
    keyboard.add_text_field(None, "+",((STT_WIDTH * ppd, STT_HEIGHT * ppd)),(0,0),(0, 0, 0), (-1, -1, -1) )

    
    for key_i in range(len(KEYS)):
        
        # placing the keys either at the 'same' level as the fixation cross or 'below' it
        # if key_ypos== 'below': # default 
        #     y_pos = -(0.5)* ppd - TEXT_FIELD_HEIGHT * ppd
        # else:
        #     y_pos = 0
        y_pos =  -KEY_SPACE/2* np.tan(np.radians(deg_ypos)) * ppd - TEXT_FIELD_HEIGHT * ppd
        print('ypos is',y_pos)
        if key_i==0:
            # x_pos = (-1)*(KEY_WIDTH + KEY_SPACE) * ppd 
            x_pos = (1)*(KEY_WIDTH + KEY_SPACE) * ppd

        else:
            x_pos = (-1)*(KEY_WIDTH + KEY_SPACE) * ppd
            # x_pos = (1)*(KEY_WIDTH + KEY_SPACE) * ppd
        images = [f"images/{KEYS[key_i]}_{color}.png" for color in KEY_COLORS]
        keyboard.add_key(KEYS[key_i], (KEY_WIDTH * ppd, KEY_HEIGHT * ppd), (x_pos, y_pos), images)
        
 

    # Load sequences
    if code != "onoff":
        os.chdir(r"C:\Users\s1081686\Desktop\RA_Project\Scripts\pynt_codes\SN_experiment")
        tmp = np.load(f"codes\{code}.npz")["codes"]
    codes = dict()
    i = 0
    for key in KEYS:
        
        if code == "onoff":
            codes[key] = [1, 0]
        else:
               
            codes[key] = tmp[:, i].tolist()

        i += 1

    if code == "onoff":
        codes["stt"] = [1, 0]
    else:
        codes["stt"] = [1] + [0] * int((1 + TRIAL_TIME) * keyboard.get_framerate())

    # Set highlights
    highlights = dict()
    for row in KEYS:
        for key in row:
            highlights[key] = [0]
    highlights["stt"] = [0]
    

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
    
    keyboard.run(highlights, 5.0)
    keyboard.set_field_text("text", "")
    
    # run matrices with 1's and 0's   
    run_1 = np.random.permutation(np.arange(n_trials) % 2).astype("uint8")
    run_2 = np.random.permutation(run_1)     
    run_3 = np.random.permutation(run_2)
    
    #concatenating all runs
    runs = np.vstack((run_1,run_2,run_3))
    # choices for chosen_keys
    keys = ['N','Y']
    
    #  loop blocks
    for run in range(runs.shape[0]):       
        run_current = runs[run,:]
    

        # Loop trials
        text = ""
        keyboard.set_field_text("text", "")
        for i_trial in range(n_trials):
            print("i trial is",i_trial)
            target = int(run_current[i_trial])
            target_key = KEYS[target]
                        
            # Choose which key will flash (for the third run, both keys are flashing)
            if run == 0 or run == 1:                
                flashing_letter = keys[target]
            else:
                flashing_letter = 'both'           
            
            print(f"{1 + i_trial:03d}/{n_trials}\t{target_key}\t{target}")
            
            keyboard.log(["visual", "param", "target", json.dumps(target)])
            keyboard.log(["visual", "param", "key", json.dumps(target_key)])            
            
            
            # Cue
            highlights[target_key] = [-2]
            keyboard.run(highlights, CUE_TIME, 
                start_marker=["visual", "cmd", "start_cue", json.dumps(1+i_trial)], 
                stop_marker=["visual", "cmd", "stop_cue", json.dumps(1+i_trial)])
            highlights[target_key] = [0]

            # Trial                     
            keyboard.add_highlighter(target_key,color="yellow",lineWidth=5, size_str = 'same')#red is [1,-1,-1]
            keyboard.run(codes, TRIAL_TIME, 
                start_marker=["visual", "cmd", "start_trial", json.dumps(1+i_trial)], 
                stop_marker=["visual", "cmd", "stop_trial", json.dumps(1+i_trial)],flashing_letter = flashing_letter)
            keyboard.add_highlighter(target_key,color = [0,0,0],lineWidth=6, size_str = 'same')          
                        
            
        
            # text += target_key
            # keyboard.set_field_text("text", text)

            # # Feedback
            # highlights[target_key] = [-1]
            # keyboard.run(highlights, FEEDBACK_TIME, 
            #     start_marker=["visual", "cmd", "start_feedback", json.dumps(1+i_trial)], 
            #     stop_marker=["visual", "cmd", "stop_feedback", json.dumps(1+i_trial)])
            # highlights[target_key] = [0]

            # Inter-trial time
            keyboard.run(highlights, ITI_TIME, 
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
    keyboard.run(highlights, 5.0)
    keyboard.set_field_text("text", "")
    keyboard.quit()
    print("Finished.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Test keyboard.py")
    parser.add_argument("-n", "--ntrials", type=int, help="number of trials", default=1)
    parser.add_argument("-c", "--code", type=str, help="code set to use", default="mgold_61_6521")
    parser.add_argument("-vs_ang","--vis_angle", type = float, default = 7.5)
    parser.add_argument('-kyps',"--deg_ypos",type= float,help = 'degrees from the fixation cross', default = 7.5)
    
    args = parser.parse_args()

    test(n_trials=args.ntrials, vis_angle= args.vis_angle, deg_ypos = args.deg_ypos,code=args.code)