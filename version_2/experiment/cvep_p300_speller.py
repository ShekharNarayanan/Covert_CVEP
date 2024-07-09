import json
import numpy as np
from psychopy import visual, event, monitors, misc, core



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
                        
            image_stim = visual.ImageStim(win=self.window,image=image,units="pix",pos=pos,size=size,autoLog=False, interpolate=True)
            images_out[name].append(image_stim)
            
        if auto_draw:
            images_out[name][0].setAutoDraw(True)

        return images_out

        
       

    def add_text_field(self, name, text, size, pos, field_color=(0, 0, 0), text_color=(-1, -1, -1), auto_draw = True, font = 'Courier New',alignment="left"):
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
            color=text_color, fillColor=field_color, alignment=alignment, 
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

    
    def run(self, FR, left_sequence, right_sequence, All_Images, codes, duration, cued_side, shape_change_time_sec,start_marker=None, stop_marker=None,sequence=True):
        """
        Present a trial with concurrent flashing for either of the circles.
        
        Args:
            FR (int):
                The frame rate of the monitor
            left_sequence (dict):
                Shape sequence for the left side
            right_sequence (np.array):
                Shape sequence for the right side
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
        if sequence:
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
            Dict_Images_left['r']['r'][0].setAutoDraw(False)
            Dict_Images_right['i']['i'][0].setAutoDraw(False)
                    
            # Send start marker
            self.log(start_marker, on_flip=True)
            
            # using shape history of one of the circles to decide when to log them both (only one is needed because shapes on both sides change simultaneously)
            prev_shape_left = ''
            prev_shape_right  = ''
            c_l = 0
            c_r = 0
            
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
                    
                if (i % (2*change_frames)) < change_frames: # logic for changing the shapes
                
                    rem1 = i % (2*change_frames)

                    shape_left_side = left_sequence[int((i-rem1)/change_frames)]  
                    shape_right_side = right_sequence[int((i-rem1)/change_frames)]

                    # logic for logging the shapes on the screen
                    if (shape_left_side != prev_shape_left):
                        
                        if cued_side == 'LEFT' and initials_to_shapes[shape_left_side] == 'hour_glass':
                            target = 1
                        else:
                            target = 0
                        self.log(["visual","cmd","left_shape_stim",json.dumps(f'shape={initials_to_shapes[shape_left_side]};target={target}')])
                        prev_shape_left = shape_left_side
                        c_l += 1
                        print(f"log left {initials_to_shapes[shape_left_side]}")
                        print(f"shape num left{c_l}")
                    
                    else:
                        pass
                        
                    if (shape_right_side != prev_shape_right):
                        if cued_side == 'RIGHT' and initials_to_shapes[shape_right_side] == 'hour_glass':
                            target = 1
                            
                        else:
                            target = 0
                            
                        self.log(["visual","cmd","right_shape_stim",json.dumps(f'shape={initials_to_shapes[shape_right_side]};target={target}')])
                        prev_shape_right = shape_right_side
                        # c_r += 1
                        # print(f"log right {initials_to_shapes[shape_right_side]}")
                        # print(f"shape num right{c_r}")
                        
                    else:
                        pass
                    
                    Dict_Images_left[shape_left_side][shape_left_side][code_left[i % len(code_left)]].draw()                 
                    Dict_Images_right[shape_right_side][shape_right_side][code_right[i % len(code_right)]].draw()
                    
                else:
                
                    rem2 = i%change_frames
                    
                    shape_left_side = left_sequence[int((i  - rem2)/change_frames)]
                    shape_right_side = right_sequence[int((i  - rem2)/change_frames)]                     
                    
                    if (shape_left_side != prev_shape_left):
                        
                        if cued_side == 'LEFT' and initials_to_shapes[shape_left_side] == 'hour_glass':
                            target = 1
                        else:
                            target = 0
                        self.log(["visual","cmd","left_shape_stim",json.dumps(f'shape={initials_to_shapes[shape_left_side]};target={target}')])
                        prev_shape_left = shape_left_side
                        # c_l += 1
                        # print(f"log left {initials_to_shapes[shape_left_side]}")
                        # print(f"shape num left{c_l}")
                    
                    else:
                        pass
                        
                    if (shape_right_side != prev_shape_right):
                        if cued_side == 'RIGHT' and initials_to_shapes[shape_right_side] == 'hour_glass':
                            target = 1
                            
                        else:
                            target = 0
                            
                        self.log(["visual","cmd","right_shape_stim",json.dumps(f'shape={initials_to_shapes[shape_right_side]};target={target}')])
                        prev_shape_right = shape_right_side
                        # c_r += 1
                        # print(f"log right {initials_to_shapes[shape_right_side]}")
                        # print(f"shape num right{c_r}")
                        
                    else:
                        pass
                    
                    Dict_Images_left[shape_left_side][shape_left_side][code_left[i % len(code_left)]].draw()                 
                    Dict_Images_right[shape_right_side][shape_right_side][code_right[i % len(code_right)]].draw()

                self.window.flip()  

            # Send stop markers
            self.log(stop_marker)
            

            # set autodraw to true to keep stt visible
            stt_image['stt'][0].setAutoDraw(True)
            Dict_Images_left['r']['r'][0].setAutoDraw(True)
            Dict_Images_right['i']['i'][0].setAutoDraw(True)
            
            self.window.flip()
            
        else:
            # a simpler version of the run function for running the resting state script
            stt_image_top = All_Images[0]
            shape_im = All_Images[1]

            
            # set auto draw to false 
            stt_image_top['stt_top'][0].setAutoDraw(False)
            shape_im['shape'][0].setAutoDraw(False)
            
            if duration is None:        
                n_frames = len(codes[list(codes.keys())[0]])            
            else:            
                n_frames = int(duration * FR)
            # Send start marker
            self.log(start_marker, on_flip=True)
            
            for i in range(n_frames):
                # Check quiting
                if i % 60 == 0:
                    if self.is_quit():
                        self.quit()

        #     # Draw keys with color depending on code state
            
                for name, code in codes.items():
                    if name == 'stt_top':
                        stt_image_top[name][code[i % len(code)]].draw()
                    else:
                        shape_im[name][code[i % len(code)]].draw()
                self.window.flip()       
                    
            # stt_image_bottom['stt_bottom'][0].setAutoDraw(True)
            stt_image_top['stt_top'][0].setAutoDraw(True)
            shape_im['shape'][0].setAutoDraw(True)
                    
            

        # Send stop markers
        self.log(stop_marker)
            
        
    
    
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
