"""
author(s): Shekhar Narayanan (shekharnarayanan833@gmail.com), Jordy Thielen (jordy.thielen@donders.ru.nl)*
*: corresponding author

Read and preprocess raw eeg data
"""
import os
import pyxdf
import numpy as np
import mne
from mnelab.io import read_raw

# paths
data_path = r'C:\Users\s1081686\Desktop\RA_Project\graz_conference\data' # path for raw data
codes_path = r'C:\Users\s1081686\Desktop\RA_Project\graz_conference\experiment\codes'

# subject and session
subjects = [f"pilot{ind}" for ind in range(3,8)] # 5 subjects
ses = "ses-S001"

# presentation params 
fs = 120  # target EEG (down)sampling frequency 
fr = 120  # frame rate of the PC used for stimulus presentation rate
pr = 60  # stimulus presentation rate

# experimental params
overt_runs = 1
covert_runs = 4

# filtering params
cvep_l_freq = 1 # low pass
cvep_h_freq = 40# high pass
notch = 50

# trial time 
trial_time = 20 # in seconds

# conditions
conditions =['overt', 'covert']

for i_subject, subject in enumerate(subjects):
    print(f"starting preprocessing for subject {i_subject}") # only one subject
          
    for i_condition, condition in enumerate(conditions):
        
        print("condition:",condition)
        
        eeg = []  # eeg data for a subject
        labels_all=[] # labels for a subject
        
        if condition == 'overt':
            i_run_range = overt_runs  
            
        else:
            i_run_range = covert_runs
        
        for i_run in range(i_run_range): # 
            
            # Load xdf data into MNE
            fn = os.path.join(data_path, "raw", f"sub-{subject}", ses, "eeg", 
                f"sub-{subject}_{ses}_task-{condition}_run-{1 + i_run:03d}_eeg.xdf")
                       
            # read data from BioSemi stream
            streams = pyxdf.resolve_streams(fn)
            names = [stream["name"] for stream in streams]

            stream_id = streams[names.index("BioSemi")]["stream_id"]
            raw = read_raw(fn, stream_ids=[stream_id])
           
            # Adjust marker channel data
            raw._data[0, :] = (raw._data[0, :] - np.median(raw._data[0, :])) > 0
            raw._data[0, :] = np.logical_and(raw._data[0, :], np.roll(raw._data[0, :], -1)).astype(raw._data[0, :].dtype)
            events = mne.find_events(raw, stim_channel="Trig1")
                           
            print("events found:", len(events))

            # Filtering
            raw = raw.filter(l_freq=cvep_l_freq, h_freq=cvep_h_freq, 
                picks=np.arange(1, 65), method="iir", 
                iir_params=dict(order=6, ftype='butter'))
                               
            # adding a notch filter
            raw.notch_filter(freqs=np.arange(notch,raw.info["sfreq"]/2,notch))
                       
            # Extract labels from marker stream
            streams = pyxdf.load_xdf(fn)[0]
            names = [stream["info"]["name"][0] for stream in streams]
            marker_stream = streams[names.index("KeyboardMarkerStream")]
                             
            labels = [marker[3].lower().strip('""') == "right" 
            for marker in marker_stream["time_series"]
            if marker[2] == "cued_side"]
            
            print("i_run",i_run)
            # for pilot 6, the last two event onset times were incorrect.
            # the onsets are corrected using data from both the lsl and the stimulus timing tracker (stt) stream
            if (i_run ==2) and (subject == 'pilot6'): 

                offset = marker_stream["time_stamps"][0] # the time the PC was turned on
                # all onset times are found without the offset
                start_trial_seconds_lsl = np.array([time_stamp - offset for marker, time_stamp in zip(marker_stream["time_series"], marker_stream["time_stamps"]) if marker[2] == 'start_trial'])

                # stt timestamps
                start_trial_seconds_stt = events[:,0]/raw.info["sfreq"]
                
                # comparing the latency between two time streams
                time_comparison_matrix = start_trial_seconds_stt - start_trial_seconds_lsl[0:start_trial_seconds_stt.shape[0]] 
                mean_latency = np.mean(time_comparison_matrix[:-1])
                
                #correct event matrix (the 19th and 20th values were not correct in stt)
                events_corrected_first_col = np.zeros((20,))
                events_corrected_cols_remaining = np.vstack((np.zeros(20,),np.ones(20,))).T
                
                #first 18 values
                events_corrected_first_col[:18] = start_trial_seconds_stt[:18]  
                #last 2 values
                events_corrected_first_col[18:] = np.array([(ind + mean_latency) for ind in start_trial_seconds_lsl[len(start_trial_seconds_lsl)-2:len(start_trial_seconds_lsl)]]) 

                #concatenating data
                events_corrected_all_cols = np.hstack((events_corrected_first_col.reshape(-1,1)*raw.info['sfreq'],events_corrected_cols_remaining)).astype(np.int64)
                
                events  = events_corrected_all_cols

            # epoch the data with the trial duration 
            epo = mne.Epochs(raw, events=events, tmin=-0.5, 
                tmax=trial_time, baseline= None, picks="eeg", 
                preload=True)           
            
            # Resampling
            # N.B. Downsampling is done after slicing to maintain accurate 
            # stimulus timing
            epo = epo.resample(sfreq=fs)
            
            # appending data for the subject
            eeg.append(epo.get_data(tmin=0, tmax=trial_time))
            labels_all.append(labels)
           

        # Extract data 
        if condition == 'covert':  # concatenate all four covert runs          
            X = np.squeeze(np.concatenate(eeg, axis=0)).astype("float32")  # trials channels samples
            y = np.concatenate(labels_all, axis=0).astype("uint8")
            
        else:
            X = np.squeeze(np.array(eeg)).astype("float32") 
            y = np.array(labels).astype("uint8")
        
        # name of the code used
        code ='mgold_61_6521_mod'
        
        # limiting the duration of data to trial time
        X = X[:, :, :int(trial_time * fs)]
        
        # Load codes       
        V = np.load(os.path.join(codes_path,f'{code}.npz'))["codes"]
        
        V = np.repeat(V, int(fs / pr), axis=0).astype("uint8") # upsampling the code according to the downsampling freq and the presentation rate
        
        print("Condition:", code)
        print("\tX:", X.shape)
        print("\ty:", y.shape)
        print("\tV:", V.shape)

        # Save data
        cvep = f"{subject}_cvep_{condition}_{code}.npz"
        save_path = os.path.join(data_path, 'derivatives', subject)
        if not os.path.isdir(save_path):
            os.makedirs(save_path)
        
        fn = os.path.join(save_path, cvep)
        np.savez(fn, X=X, y=y, V=V, fs=fs)
        
        print(f"data saved for subject {i_subject + 1}")
