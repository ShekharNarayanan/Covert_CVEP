"""
@author: Jordy Thielen (jordy.thielen@donders.ru.nl), Shekhar Narayanan (SN) (shekharnarayanan833@gmail.com)

Python implementation of a keyboard for the noise-tagging project.
"""
'''Modifications @ SN
- Modified: The keyboard is replaced with just the Y and N keys.
- Modified: The add_key function (now Image_Selector) is modified to add images on the fly when the code is running.
- Modified: The run function can now flash CVEP codes for each key individually 
- Added: Option to change the angle between the two classes (x-axis) and from the fixation point (y-axis).
- Added: P300 paradigm works in conjunction with the previous CVEP only setup.
- Added: Sequence generator function that generates sequences of letters that are flashed on the screen

'''

import os, json
import numpy as np
import psychopy
from psychopy import visual, event, monitors, misc, prefs
from psychopy import core
from PIL import Image, ImageDraw
import random

# change directory to your experiment folder
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
        self.window = visual.Window(monitor=self.monitor, screen=screen, units="pix", size=size, color=window_color, fullscr=False, waitBlanking=False, allowGUI=False,allowStencil=True)
        self.window.setMouseVisible(False)

        # Initialize keys and fields
        self.keys = dict()
        self.images_out = dict()
        self.fields = dict()

        # Setup LSL stream
        self.stream = stream
        if self.stream:
            
            from pylsl import StreamInfo, StreamOutlet, StreamInlet, local_clock
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
 

    def image_selector(self, name, size, pos , images=["white.png", "blue.png"]):
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
            
        if name == 'stt':
            images_out[name][0].setAutoDraw(True)
            
            # self.window.flip()
               
            
    
        return images_out
        # Set autoDraw to True for first default key to keep app visible
        # self.keys[name][0].setAutoDraw(True)
        
       

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

    def log(self, marker, on_flip=False, print_time =  False):
        import pylsl

        if self.stream and not marker is None:
            if not isinstance(marker, list):
                marker = [marker]
            if on_flip:
                self.window.callOnFlip(self.outlet.push_sample, marker)
            else:

                self.outlet.push_sample(marker)  
        return pylsl.local_clock()
    


    
    def run(self, FR, Keys = None, All_Images = None, codes = None, letter_change_time_msec=250, duration=None, start_marker=None, stop_marker=None, cued_side = None): # flashing letter can be replaced by flashing side
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
        key_dict = {'c': 'circle' , 'h' :'hour_glass', 'i': 'inverted_triangle', 't': 'triangle', 'r':'rectangle'}
        if Keys != None:
           cued_sequence = Keys['cued_sequence']
           non_cued_sequence = Keys['non_cued_sequence']

           
            
        if All_Images != None:
            stt_image = All_Images[0]
            Dict_Images_left = All_Images[1]
            Dict_Images_right = All_Images[2]
        
        #(1/60 hz is 16.67 ms, dividing letter change time/refresh rate tells us after how many frames the letter should be changed)
        # In case of CVEP, code presentation rate is the same as refresh rate, i.e 1 bit = 1 frame.
        # After a certain number of frames, the letter flashing on the screen will change
        
       
        frame_change_time_msec  = (1/FR) 
        
        change_frames = int(np.round((letter_change_time_msec/ frame_change_time_msec)))
        print('change frame before loop',change_frames)
   
        # Set number of frames
        if duration is None:
        
            n_frames = len(codes[list(codes.keys())[0]])
            
        else:
            
            n_frames = int(duration * 60)#self.get_framerate())
            

        # Send start marker
        self.log(start_marker, on_flip=True)
        
        # Accessing all the codes
        code_left = codes['LEFT']
        code_right = codes['RIGHT']
        
        for i in range(len(All_Images)):
            if i==0:
                stt_image  = All_Images[0]
                stt_image['stt'][0].setAutoDraw(False)
                
                
                
            # .setAutoDraw(False)
        # Loop frame flips
        for i in range(n_frames): 
            print('change frame is', change_frames)

            
            # Check quiting
            if i % 60 == 0:
                if self.is_quit():
                    self.quit()                                        

        
            # Draw keys with color depending on code state
            for name, code in codes.items(): 

                if name == 'stt':
                    'set autodraw false here'
                    # stt_image["stt"].setAutoDraw(True)
                    stt_image["stt"][code[i % len(code)]].draw()#[code_stt[i % len(code)]].draw()
    
            if cued_side == 'LEFT' :            
                'possible: nothing happens on the non attending side'
                if (i % (2*change_frames)) < change_frames: 
                    rem1 = i % (2*change_frames)
                    # print(int((i-rem1)/change_frames))
                    
                    
                    lkey_chosen = cued_sequence[int((i-rem1)/change_frames)]  # left side will have the cued letter sequence
                    rkey_chosen = non_cued_sequence[int((i-rem1)/change_frames)]
                    # print('lkey',lkey_chosen)
                    
                    # both sides flash
                    # Dict_Images_left[lkey_chosen][lkey_chosen][code_left[i % len(code_left)]].draw()
                    # Dict_Images_right[rkey_chosen][rkey_chosen][code_right[i % len(code_right)]].draw()
                    
                    # other side does not flash option
                    # send keys to the log here 
                    self.log(["Left_and_Right_symbols", "","", ""], [key_dict[lkey_chosen], key_dict[rkey_chosen]])
                    
                    Dict_Images_left[lkey_chosen][lkey_chosen][code_left[i % len(code_left)]].draw()                 
                    Dict_Images_right[rkey_chosen][rkey_chosen][0].draw()

                else:
                    rem2 = i%change_frames
                    lkey_chosen = cued_sequence[int((i  - rem2)/change_frames)] # left side will have the cued letter sequence
                    rkey_chosen = non_cued_sequence[int((i  - rem2)/change_frames)]
                    
                    # both sides flash
                    # Dict_Images_left[lkey_chosen][lkey_chosen][code_left[i % len(code_left)]].draw()
                    # Dict_Images_right[rkey_chosen][rkey_chosen][code_right[i % len(code_right)]].draw()
                    
                    # send keys to the log here 
                    self.log(["Left_and_Right_symbols", "","", ""], [key_dict[lkey_chosen], key_dict[rkey_chosen]])
                    # other side does not flash option       
                    Dict_Images_left[lkey_chosen][lkey_chosen][code_left[i % len(code_left)]].draw()                 
                    Dict_Images_right[rkey_chosen][rkey_chosen][0].draw()
    
            elif cued_side == 'RIGHT' : 
                
                if (i % (2*change_frames)) < change_frames: 
                    rem1 = i % (2*change_frames)
                    lkey_chosen = non_cued_sequence[int((i-rem1)/change_frames)]
                    rkey_chosen = cued_sequence[int((i-rem1)/change_frames)] # right side will have the cued letter sequence
                    
                    # send keys to the log here 
                    self.log(["Left_and_Right_symbols", "","", ""], [key_dict[lkey_chosen], key_dict[rkey_chosen]])
                    # other side does not flash option                        
                    Dict_Images_right[rkey_chosen][rkey_chosen][code_right[i % len(code_right)]].draw()
                    Dict_Images_left[lkey_chosen][lkey_chosen][0].draw() 
                    
                    # both sides flash option     
                    # Dict_Images_left[lkey_chosen][lkey_chosen][code_left[i % len(code_left)]].draw()                  
                    # Dict_Images_right[rkey_chosen][rkey_chosen][code_right[i % len(code_right)]].draw()   
                
                else:
                    rem2 = i%change_frames
                    lkey_chosen = non_cued_sequence[int((i  - rem2)/change_frames)]
                    rkey_chosen = cued_sequence[int((i  - rem2)/change_frames)]  # right side will have the cued letter sequence
                    
                    # send keys to the log here 
                    self.log(["Left_and_Right_symbols", "","", ""], [key_dict[lkey_chosen], key_dict[rkey_chosen]])
                     # other side does not flash option                        
                    Dict_Images_right[rkey_chosen][rkey_chosen][code_right[i % len(code_right)]].draw()
                    Dict_Images_left[lkey_chosen][lkey_chosen][0].draw() 
                    
                    # both sides flash option     
                    # Dict_Images_left[lkey_chosen][lkey_chosen][code_left[i % len(code_left)]].draw()                  
                    # Dict_Images_right[rkey_chosen][rkey_chosen][code_right[i % len(code_right)]].draw() 
    
            self.window.flip()  
            
        # self.add_text_field(None, "",((3 * ppd, 3 * ppd)),(0,0),(0, 0, 0), (-1, -1, -1), auto_draw = True)

        # Send stop markers
        self.log(stop_marker)

        # # Set autoDraw to True to keep app visible
        for i in range(len(All_Images)):
            if i==0:
                stt_image  = All_Images[0]
                stt_image['stt'][0].setAutoDraw(True)
        self.window.flip()
        
    def sequence_generator(self, letter_arr = None, size_letter_arr = None, target_letter= None, targets_in_trial_cued = None, targets_in_trial_non_cued = None, min_target_key_distance = 5):
        
        # Defining an array with letters without the target letter  (size = len(letter_arr) - 1)  
        letter_arr_non_target = [letter for letter in letter_arr if letter != target_letter] # does not contain the target letter, see use later in adjacency rule  

        # Defining the array for the cued side
        cued_array = np.array(random.choices(letter_arr_non_target, k = size_letter_arr)) # target letters will be placed in this array later    
        # non_cued_array  =  np.array(random.choices(letter_arr_non_target, k = size_letter_arr)) 

        cued_array_length = len(cued_array)

        # strategy for cued arr: 
        # 1. Design an array with no two identical letters placed adjacently (adjacency rule).
        # 2. Place the target letter in the said array at random distances with minimum distance = min_target_key_distance (target distancing rule)

        # for noncued arr: 
        # 1. Same rules are followed

        # CUED ARRAY: making sure no identical letters are placed next to each other 
        for i in range(len(cued_array) - 1):
            if cued_array[i] == cued_array[i + 1]:
            # Find a different letter to replace the adjacent duplicate
                for letter in letter_arr_non_target: #replacing with any other letter other than the target letter
                    if letter != cued_array[i] and (i == 0 or letter != cued_array[i - 1]):
                        cued_array[i + 1] = letter
                        break
                    
        # mapping: each letter in the cued array is mapped to another one in letter_arr_non_target
        mapping = {letter: letter_arr_non_target[(index + len(letter_arr_non_target)//2) % len(letter_arr_non_target)]
            for index, letter in enumerate(letter_arr_non_target)}

        # NON_CUED ARRAY: each letter in the cued array is mapped to another one in letter_arr, hence the cued and noncued side will never show the same letter at the same time
        non_cued_array = np.array([mapping[letter] for letter in cued_array])


        # targets in the current trial
        target_count_trial_cued = targets_in_trial_cued


        # Calculate the default target distance given the fixed number of target letters in a trial
        tar_dist = np.round(cued_array_length/(target_count_trial_cued)) 
        print("tar_dist cued",tar_dist)


        # Initializing loop variables
        current_index = 0
        target_count = 0

        while target_count != target_count_trial_cued and current_index < cued_array_length:

            deviation = np.random.randint(0,5) # this varies the distance at which the targets are presented
            
            if (tar_dist - deviation) <= min_target_key_distance: # deviation in distance can not be less than the minimum value
                tar_dist_new =  tar_dist # no changes made
                    
            else:
                tar_dist_new = tar_dist - deviation # new target distance used

            
            if  current_index == 0: # the first letter should not be a target
                cued_array[current_index+1] = target_letter 
                target_count +=1
                current_index += int(tar_dist_new)+1 
                
            else:
                cued_array[current_index] = target_letter
                target_count +=1
                current_index += int(tar_dist_new) 
                
        'non cued side'
        current_index = 0
        target_count = 0

        target_count_trial_non_cued = targets_in_trial_non_cued

        # targets in the non_cued_seq will always be less than max_targets, 
        # so tar_dist here is always > min_target_key_distance
        tar_dist = np.round(cued_array_length/(target_count_trial_non_cued)) 


        while target_count != target_count_trial_non_cued and current_index < cued_array_length:

            deviation = np.random.randint(0,min_target_key_distance) # this varies the distance at which the targets are presented
            
            if (tar_dist - deviation) <= min_target_key_distance: # deviation in distance can not be less than the minimum value
                tar_dist_new =  tar_dist # no changes made
                    
            else:
                tar_dist_new = tar_dist - deviation # new target distance used
                # print('deviation in tar_dist by',deviation)
            
            if  current_index == 0: # the first letter should not be a target
                non_cued_array[current_index+2] = target_letter # the third letter is the target letter 
                target_count +=1
                current_index += int(tar_dist_new)+1 
                
            else:
                non_cued_array[current_index] = target_letter
                target_count +=1
                current_index += int(tar_dist_new)

        
        return cued_array, non_cued_array
    
    def targets_in_trial(self,n_trials,max_targets):
        
            size_of_arr = int(np.ceil(n_trials / 2))

            while True:
                array1 = np.random.randint(1, max_targets, size=size_of_arr)
                array2 = np.random.randint(1, max_targets, size=size_of_arr)
            # The sum of targets within a run on left and right sides should be the equal. 
            # This is done to make sure the number of p300 responses are balanced
                if np.sum(array1)== np.sum(array2):
                    break

            return array1.tolist(), array2.tolist()
    
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
