#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Jordy Thielen (jordy.thielen@donders.ru.nl)

Python implementation of a keyboard for the noise-tagging project.
"""
'''Notes:
- Press Q to quit
- Keyboard is replaced with just the Y and N keys
- "+" is placed in between the two classes
'''

import os, json
import numpy as np
import psychopy
from psychopy import visual, event, monitors, misc, prefs
from psychopy import core
import math

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
        
    def add_highlighter(self,name,color,lineWidth):
        """
        Add a rectangular highlighter window around the cued option

        Args:
            name (str):
                The name of the key
            color (array):
                color of the window (set to red during trial otherwise same as background)
            
        """
        assert name in self.keys, "Key does not exist!"
        key = self.keys[name][0]  # Get the first image associated with the key
    
        highlighter = visual.Rect(win=self.window,
                                  width=key.size[0]+0.05, height=key.size[1]+0.05, 
                                  units="pix", lineWidth = lineWidth,lineColor=color, pos=key.pos, 
                                  fillColor=None, opacity= 1)
        # self.highlighters[name] = highlighter
        
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
    
    def run(self, codes, duration=None, start_marker=None, stop_marker=None):
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
                self.keys[name][code[i % len(code)]].draw()
                # self.add_highlighter(name)
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

# change n to 15
def test(n_trials, code="onoff"):# modul gold codes 
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
    KEY_SPACE = 12
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
    
    keyboard.add_text_field(None, "+",((STT_WIDTH * ppd, STT_HEIGHT * ppd)),(0,0),(0, 0, 0), (-1, -1, -1) )

    
    for key_i in range(len(KEYS)):
        
        # key_2_add = KEYS[key_i]
        y_pos = -(0.5)* ppd - TEXT_FIELD_HEIGHT * ppd
        
        if key_i==1:
            x_pos = (-1)*(KEY_WIDTH + KEY_SPACE) * ppd 
            # print("x pos1 is", x_pos) 
            # print("x pos1 difference from cross is",abs(x_pos)-SCREEN_WIDTH/2)
        else:
            x_pos = (1)*(KEY_WIDTH + KEY_SPACE) * ppd 
            # print("xpos 2 is",x_pos)
            # print("x pos2 difference from cross is",abs(x_pos)-SCREEN_WIDTH/2)
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
    
  
    trial_vec = np.random.permutation(np.arange(n_trials) % 2).astype("uint8")
    
    # Loop trials
    text = ""
    for i_trial in range(n_trials):
        print("i trial is",i_trial)
        # Set target
       
        target = int(trial_vec[i_trial]) # we need
        

        # target_key = KEYS[int(target) // len(KEYS[0])][int(target) % len(KEYS[0])]
        
        target_key = KEYS[target]

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
        keyboard.add_highlighter(target_key,color="yellow",lineWidth=5)#red is [1,-1,-1]
        keyboard.run(codes, TRIAL_TIME, 
            start_marker=["visual", "cmd", "start_trial", json.dumps(1+i_trial)], 
            stop_marker=["visual", "cmd", "stop_trial", json.dumps(1+i_trial)])
        keyboard.add_highlighter(target_key,color = [0,0,0],lineWidth=6)
        
        
        
        
       
        # text += target_key
        # keyboard.set_field_text("text", text)

        # # Feedback
        # highlights[target_key] = [-1]
        # keyboard.run(highlights, FEEDBACK_TIME, 
        #     start_marker=["visual", "cmd", "start_feedback", json.dumps(1+i_trial)], 
        #     stop_marker=["visual", "cmd", "stop_feedback", json.dumps(1+i_trial)])
        # highlights[target_key] = [0]

        # # Inter-trial time
        # keyboard.run(highlights, ITI_TIME, 
        #     start_marker=["visual", "cmd", "start_intertrial", json.dumps(1+i_trial)], 
        #     stop_marker=["visual", "cmd", "stop_intertrial", json.dumps(1+i_trial)])

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
    parser.add_argument("-n", "--ntrials", type=int, help="number of trials", default=20)
    parser.add_argument("-c", "--code", type=str, help="code set to use", default="mgold_61_6521")
    args = parser.parse_args()

    test(n_trials=args.ntrials, code=args.code)
