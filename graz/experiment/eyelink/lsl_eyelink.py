'''
Created on Jul 10, 2012
Updated Aug 17, 2016
@author: SCCN
'''


from pylink import *
import pylsl,socket, time
import msvcrt
import os
from psychopy import visual, core, event, monitors, gui
from EyeLinkCoreGraphicsPsychoPy import EyeLinkCoreGraphicsPsychoPy

def calibrateEye():
    # Optional tracking parameters
    # Sample rate, 250, 500, 1000, or 2000, check your tracker specification
    # if eyelink_ver > 2:
    #     el_tracker.sendCommand("sample_rate 1000")
    # Choose a calibration type, H3, HV3, HV5, HV13 (HV = horizontal/vertical),
    tracker.sendCommand("calibration_type = HV9")
    # Set a gamepad button to accept calibration/drift check target
    # You need a supported gamepad/button box that is connected to the Host PC
    tracker.sendCommand("button_function 5 'accept_target_fixation'")

    # Step 4: set up a graphics environment for calibration
    #
    # Open a window, be sure to specify monitor parameters
    mon = monitors.Monitor('myMonitor', width=60.0, distance=60.0)
    win = visual.Window(fullscr=True,
                        monitor=mon,
                        winType='pyglet',
                        units='pix')
    # get the native screen resolution used by PsychoPy
    scn_width, scn_height = win.size
    # Pass the display pixel coordinates (left, top, right, bottom) to the tracker
    # see the EyeLink Installation Guide, "Customizing Screen Settings"
    el_coords = "screen_pixel_coords = 0 0 %d %d" % (scn_width - 1, scn_height - 1)
    tracker.sendCommand(el_coords)

    # Write a DISPLAY_COORDS message to the EDF file
    # Data Viewer needs this piece of info for proper visualization, see Data
    # Viewer User Manual, "Protocol for EyeLink Data to Viewer Integration"
    dv_coords = "DISPLAY_COORDS  0 0 %d %d" % (scn_width - 1, scn_height - 1)
    tracker.sendMessage(dv_coords)

    # Configure a graphics environment (genv) for tracker calibration
    genv = EyeLinkCoreGraphicsPsychoPy(tracker, win)
    print(genv)  # print out the version number of the CoreGraphics library

    # Set background and foreground colors for the calibration target
    # in PsychoPy, (-1, -1, -1)=black, (1, 1, 1)=white, (0, 0, 0)=mid-gray
    foreground_color = (-1, -1, -1)
    background_color = win.color
    genv.setCalibrationColors(foreground_color, background_color)

    # get the native screen resolution used by PsychoPy
    scn_width, scn_height = win.size

    # Set up the calibration target
    #
    # The target could be a "circle" (default), a "picture", a "movie" clip,
    # or a rotating "spiral". To configure the type of calibration target, set
    # genv.setTargetType to "circle", "picture", "movie", or "spiral", e.g.,
    # genv.setTargetType('picture')
    #
    # Use gen.setPictureTarget() to set a "picture" target
    # genv.setPictureTarget(os.path.join('images', 'fixTarget.bmp'))
    #
    # Use genv.setMovieTarget() to set a "movie" target
    # genv.setMovieTarget(os.path.join('videos', 'calibVid.mov'))

    # Use a picture as the calibration target
    genv.setTargetType('picture')
    genv.setPictureTarget(os.path.join('images', 'fixTarget.bmp'))

    # Configure the size of the calibration target (in pixels)
    # this option applies only to "circle" and "spiral" targets
    # genv.setTargetSize(24)

    # Beeps to play during calibration, validation and drift correction
    # parameters: target, good, error
    #     target -- sound to play when target moves
    #     good -- sound to play on successful operation
    #     error -- sound to play on failure or interruption
    # Each parameter could be ''--default sound, 'off'--no sound, or a wav file
    genv.setCalibrationSounds('', '', '')

    # Request Pylink to use the PsychoPy window we opened above for calibration
    openGraphicsEx(genv)
    # Calibrate the tracker
    tracker.doTrackerSetup()
    tracker.exitCalibration()
    #closeGraphics()
    win.close()


if __name__ == '__main__':

    outlet = None 
    SR = 1000
    edfFileName = "TRIAL.edf"
    try:
        #info = pylsl.stream_info("EyeLink","Gaze",9,500,pylsl.cf_float32,"eyelink-" + socket.gethostname());
        #info = pylsl.stream_info("EyeLink","Gaze",10,SR,pylsl.cf_double64,"eyelink-" + socket.gethostname());
        info = pylsl.stream_info("EyeLink","Gaze",6,SR,pylsl.cf_double64,"eyelink-" + socket.gethostname());
        channels = info.desc().append_child("channels")

        channels.append_child("channel") \
            .append_child_value("label", "leftEyeX") \
            .append_child_value("type", "eyetracking")
        channels.append_child("channel") \
            .append_child_value("label", "leftEyeY") \
            .append_child_value("type", "eyetracking")
        channels.append_child("channel") \
            .append_child_value("label", "rightEyeX") \
            .append_child_value("type", "eyetracking")
        channels.append_child("channel") \
            .append_child_value("label", "rightEyeY") \
            .append_child_value("type", "eyetracking")
        channels.append_child("channel") \
            .append_child_value("label", "leftPupilArea") \
            .append_child_value("type", "eyetracking")
        channels.append_child("channel") \
            .append_child_value("label", "rightPupilArea") \
            .append_child_value("type", "eyetracking")
        """
        channels.append_child("channel") \
            .append_child_value("label", "pixelsPerDegreeX") \
            .append_child_value("type", "eyetracking")
        channels.append_child("channel") \
            .append_child_value("label", "pixelsPerDegreeY") \
            .append_child_value("type", "eyetracking")
        channels.append_child("channel") \
            .append_child_value("label", "eyelink_timestamp") \
            .append_child_value("type", "eyetracking")
        channels.append_child("channel") \
            .append_child_value("label", "LSL_timestamp") \
            .append_child_value("type", "eyetracking")
        """


            
        outlet = pylsl.stream_outlet(info)
        print("Established LSL outlet.")
    except:
        print("Could not create LSL outlet.")
    

    quit = 0
    isVerbose = 0 
    while quit != 1 :
        print("Trying to connect to EyeLink tracker...")
        try:
            tracker = EyeLink("255.255.255.255")
            print("Established a passive connection with the eye tracker.")
        except:
            tracker = EyeLink("100.1.1.1")
            print("Established a primary connection with the eye tracker.")
        # uncomment if you want to get pupil size in diameter, otherwise it is the area
        # tracker.setPupilSizeDiameter(YES)  
        # tracker.setVelocityThreshold(22)
        beginRealTimeMode(100)
        getEYELINK().openDataFile(edfFileName)	
        getEYELINK().startRecording(1, 1, 1, 1)                
        print("Now reading samples...")
        print("\nPress \'c\' to callibrate\nPress \'Esc\' to exit callibration\nPress \'q\' to exit lsl")

        while quit != 1: 
            sample = getEYELINK().getNewestSample()
            quit = getEYELINK().escapePressed();
            if sample is not None:
                now = pylsl.local_clock()
                ppd = sample.getPPD()
                #values = [0,0, 0,0, 0, 0, sample.getTargetX(),sample.getTargetY(),sample.getTargetDistance(), ppd[0],ppd[1]]
                values = [0,0, 0,0, 0, 0, ppd[0],ppd[1], sample.getTime(), now]
                if (sample.isLeftSample()) or (sample.isBinocular()):
                    values[0:2] = sample.getLeftEye().getGaze()
                    values[4] = sample.getLeftEye().getPupilSize() 
                if (sample.isRightSample()) or (sample.isBinocular()):
                    values[2:4] = sample.getRightEye().getGaze()
                    values[5] = sample.getRightEye().getPupilSize()
  
                outlet.push_sample(pylsl.vectord(values[0:6]), now, True)
                time.sleep(1.0/SR)

            if msvcrt.kbhit():  
                pressedKey = msvcrt.getch().decode()
                print(pressedKey)   
                if pressedKey == 'q':
                    # getch acquires the character encoded in binary ASCII
                    # check if quit
                    #if msvcrt.getch() == chr(27):
                    print("escape lsl stream")
                    quit = 1
                elif pressedKey == 'c':  #c = calibrate
                    print("calibration")
                    calibrateEye()
                    print("exit calibration")
                    getEYELINK().startRecording(1, 1, 1, 1)
                    
                if quit==1 :
                    getEYELINK().setOfflineMode()                         
                    msecDelay(500);                 

                    # Close the file and transfer it to Display PC
                    getEYELINK().closeDataFile()
                    getEYELINK().receiveDataFile(edfFileName, edfFileName)
                    getEYELINK().close();    
    
    