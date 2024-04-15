"""
@author: Shekhar Narayanan (SN) (shekharnarayanan833@gmail.com), Jordy Thielen (jordy.thielen@donders.ru.nl)

Python implementation for the stimulus paradigm made for the covert c-VEP project.
"""

import json
import numpy as np
from psychopy import visual, event, monitors, misc
from psychopy import core
from PIL import Image, ImageDraw

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
        self.window = visual.Window(monitor=self.monitor, screen=screen, units="pix", size=size, color=window_color, fullscr=False, waitBlanking=False, allowGUI=False,allowStencil=True)
        self.window.setMouseVisible(False)

        # Initialize keys and fields
        self.keys = dict()
        self.images_out = dict()
        self.fields = dict()

        # Setup LSL stream
        self.stream = stream
        if self.stream:
            
            from pylsl import StreamInfo, StreamOutlet, StreamInlet
            self.outlet = StreamOutlet(StreamInfo(name='KeyboardMarkerStream', type='Markers', channel_count=4, nominal_srate=0, channel_format='string', source_id='KeyboardMarkerStream'))
            self.inlet = StreamInlet(StreamInfo(name='KeyboardMarkerStream', type='Markers', channel_count=4, nominal_srate=0, channel_format='string', source_id='KeyboardMarkerStream'))
            

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
    
    
    def image_selector(self, name: str, size: tuple, pos, images=["white.png", "blue.png"], auto_draw = False):
        """
        Add circular spaces/ stimulus timing tracker (STT) to the stimulus paradigm

        Args:
            name (str):
                The name of the shape/image
            size (array-like):
                The (width, height) of the circle in pixels
            pos (array-like):
                The (x, y) coordinate of the center of the circle, relative to the center of the window
            images (array-like):
                The images of the shapes. Indices will correspond to the 
                values of the codes. Default: ["black.png", "white.png"]
        """
        assert name not in self.keys, "Trying to add a box with a name that already extists!"
        images_out = dict()
        images_out[name] = []
    
        
        for image in images:  
                        
            image_stim = visual.ImageStim(win=self.window,image=image,units="pix",pos=pos,size=size,autoLog=False)
            images_out[name].append(image_stim)
            
        if auto_draw:
            images_out[name][0].setAutoDraw(True)

        return images_out

        
       

    def add_text_field(self, name, text, size, pos, field_color=(0, 0, 0), text_color=(-1, -1, -1), auto_draw = True, font = 'Courier New'):
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
        self.fields[name] =  visual.TextBox2(win=self.window, text=text, font=font, 
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

    def run(self, FR, cued_sequence, non_cued_sequence, All_Images, codes, duration, cued_side, shape_change_time_sec,start_marker=None, stop_marker=None):
        """
        Present a trial with concurrent flashing for either of the circles.
        
        Args:
            FR (int):
                The frame rate of the monitor
            cued_sequence (dict):
                Shape sequence for the cued side
            non_cued_sequence (np.array):
                Shape sequence for the non_cued_side
            All_Images (dict):
                A dictionary of ImageStim objects of all images required for the stimulus paradigm
            codes (dict): 
                A dictionary with keys being the symbols to flash and the value a list (the code 
                sequence) of integer states (images) for each frame
            duration (float):
                The duration of the trial in seconds. If the duration is longer than the code
                sequence, it is repeated. If no duration is given, the full length of the first 
                code is used. Default: None
            cued_side (str): 
                This argument decides side will have flashing stimuli. Options : 'left, 'right'.
            shape_change_time_sec (float):
                duration (in seconds) after which shapes change during the trial
            start/ stop_marker (str):
                Information used for logging
            
        """
        initials_to_shapes = {'c': 'circle' , 'h' :'hour_glass', 'i': 'inverted_triangle', 't': 'triangle', 'r':'rectangle'}
    

        # get images
        stt_image = All_Images[0]
        Dict_Images_left = All_Images[1]
        Dict_Images_right = All_Images[2]
        
        # get the codes
        code_left = codes['LEFT']
        code_right = codes['RIGHT']
        code_stt = codes["stt"]

        change_frames = int(shape_change_time_sec * FR) # the number of frames after which the shapes will change during the trial
        
   
        # Set number of frames
        if duration is None:        
            n_frames = len(codes[list(codes.keys())[0]])            
        else:            
            n_frames = int(duration * FR)

        # disabling autodraw during code presentation
        stt_image['stt'][0].setAutoDraw(False)
                
        # Send start marker
        self.log(start_marker, on_flip=True)

        # Loop frame flips
        for i in range(n_frames): 

            # Check quiting
            if i % 60 == 0:
                if self.is_quit():
                    self.quit()                                        

        
            # Draw keys with color depending on code state
            for name, _ in codes.items(): 

                if name == 'stt':
                    stt_image["stt"][code_stt[i % len(code_stt)]].draw()

            # left side has the cued shape sequence
            if cued_side == 'LEFT' :            

                if (i % (2*change_frames)) < change_frames: # logic for changing the shapes
                    
                    rem1 = i % (2*change_frames)

                    shape_left_side = cued_sequence[int((i-rem1)/change_frames)]  
                    shape_right_side = non_cued_sequence[int((i-rem1)/change_frames)]

                    self.log(["Left_and_Right_symbols", "","", json.dumps([initials_to_shapes[shape_left_side], initials_to_shapes[shape_right_side]])])
                    
                    Dict_Images_left[shape_left_side][shape_left_side][code_left[i % len(code_left)]].draw()                 
                    Dict_Images_right[shape_right_side][shape_right_side][code_right[i % len(code_right)]].draw()
                    
                else:
                    rem2 = i%change_frames
                    shape_left_side = cued_sequence[int((i  - rem2)/change_frames)]
                    shape_right_side = non_cued_sequence[int((i  - rem2)/change_frames)]
                      
                    self.log(["Left_and_Right_symbols", "","", json.dumps([initials_to_shapes[shape_left_side], initials_to_shapes[shape_right_side]])])
                    Dict_Images_left[shape_left_side][shape_left_side][code_left[i % len(code_left)]].draw()                 
                    Dict_Images_right[shape_right_side][shape_right_side][code_right[i % len(code_right)]].draw()

            # right side has the cued shape sequence
            elif cued_side == 'RIGHT' : 
                
                if (i % (2*change_frames)) < change_frames: 
                
                    rem1 = i%change_frames
                    shape_left_side = non_cued_sequence[int((i-rem1)/change_frames)]
                    shape_right_side = cued_sequence[int((i-rem1)/change_frames)] 

                    self.log(["Left_and_Right_symbols", "","", json.dumps([initials_to_shapes[shape_left_side], initials_to_shapes[shape_right_side]])])                                           
                    Dict_Images_right[shape_right_side][shape_right_side][code_right[i % len(code_right)]].draw()
                    Dict_Images_left[shape_left_side][shape_left_side][code_left[i % len(code_left)]].draw() 

                else:
                    rem2 = i%change_frames
                    shape_left_side = non_cued_sequence[int((i  - rem2)/change_frames)]
                    shape_right_side = cued_sequence[int((i  - rem2)/change_frames)]
                    
                    self.log(["Left_and_Right_symbols", "","", json.dumps([initials_to_shapes[shape_left_side], initials_to_shapes[shape_right_side]])])                        
                    Dict_Images_right[shape_right_side][shape_right_side][code_right[i % len(code_right)]].draw()
                    Dict_Images_left[shape_left_side][shape_left_side][code_left[i % len(code_left)]].draw() 
                    

    
            self.window.flip()  

        # Send stop markers
        self.log(stop_marker)
        

        # set autodraw to true to keep stt visible
        stt_image['stt'][0].setAutoDraw(True)
        
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
