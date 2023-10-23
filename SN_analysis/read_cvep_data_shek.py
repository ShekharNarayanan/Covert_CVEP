#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Jordy Thielen (jordy.thielen@donders.ru.nl)

Read LSL data

Modifications @ SN
1. Hardcoded the "conditions" vector for the codes used in the pilot
2. Added a notch filter
3. Option to view and remove bad epochs from data
4. Option to remove bad channels 
"""


import os
import json
import pyxdf
import numpy as np
import pandas as pd
import mne
from mnelab.io import read_raw
from mne.io import Raw 
from mne.preprocessing import ICA
from matplotlib  import pyplot as plt
from copy import deepcopy



path = r"C:\Users\s1081686\Desktop\RA_Project\Scripts\pynt_codes\analysis\pilot_shek_dat"
repo = r"C:\Users\s1081686\Desktop\RA_Project\Scripts\pynt_codes\experiment\codes"

subjects = ["pilot"]
ses = "ses-S001"

skip_done = True

## IMPORTANT PARAMETERS TO CHANGE
fs = 240  # target EEG sampling frequency (multiple of stimulus presentation rate)
fr = 60  # monitor refresh rate
pr = 60  # stimulus presentation rate


# cvep_n_runs = 4 (irrelevant for shek pilot)
cvep_l_freq = 2
cvep_h_freq = 35# originally 35 

# how to change this for mgold_61?
cvep_trial_time_1 = 63 / pr * 4  # 126 / pr * 2 (m-sequence, Gold)
cvep_trial_time_2 = 64 / pr * 4  # 128 / pr * 2 (de Bruijn, Golay)

# for shek_pilot
key_words = ['covert','overt']

for subject in subjects:
    print("*" * 15) # only one subject
          
    for i_word in range(len(key_words)):
        
        print("starting data extraction for:",key_words[i_word])
        labels=[] 
        eeg =[]        
        
        for i_run in range(2): # for shek_pilot you have 2 covert runs and 2 overt runs, hence the range is set to 2
                        
            # Load xdf data into MNE
            fn = os.path.join(path, "raw", f"sub-{subject}", ses, "eeg", 
                f"sub-{subject}_{ses}_task-{key_words[i_word]}_run-{1 + i_run:03d}_eeg.xdf")
            
            streams = pyxdf.resolve_streams(fn)
            names = [stream["name"] for stream in streams]

            stream_id = streams[names.index("BioSemi")]["stream_id"]
            raw = read_raw(fn, stream_ids=[stream_id])
           
            # Adjust marker channel data
            raw._data[0, :] -= np.min(raw._data[0, :])
            raw._data[0, raw._data[0, :] > 0] = 1

            # Filtering
            raw = raw.filter(l_freq=cvep_l_freq, h_freq=cvep_h_freq, 
                picks=np.arange(1, 65), method="iir", 
                iir_params=dict(order=6, ftype='butter'))
                               
            # adding a notch filter
            notch = 50
            print("no new errors ")
            raw.notch_filter(freqs=np.arange(notch,raw.info["sfreq"]/2,notch))
            
            
            'Plotting Raw Data (Optional but recommended)'
            '''Note- Only remove the epoch/trial if you see a huge/long fluctuation, 
            annotation ends up removing the whole trial even if only a small duration of it is bad'''
            
            #removing signal space projectors from raw file
            ssp_projectors = raw.info["projs"]
            raw.del_proj()           
                                    
            print("raw data visualization, check for eye movement artefacts and huge movement artefacts")
            eeg_chans = mne.pick_types(raw.info,eeg=True)
            fig = raw.plot(duration=60,order = eeg_chans, n_channels = len(eeg_chans),remove_dc = False)# duration is the x second block with which you move in the plot
            plt.title('Press A to begin',loc="center")
            plt.show()
            fig.fake_keypress("a")
            
            'Dropping bad channels (Optional)'
            # bad_chans = ['A24'] # found from the raw plots; A7 also looks strange for covert
            # raw.drop_channels(ch_names= bad_chans)

            # Eliminating bad channels based on the raw plots
            # print("bad channels", raw.info["bads"]) # checking for manually annotated bad channels during the recording
            
            
            'Powerline noise check after notch (Optional, recommended when running the script subjects from the same day)'
            # fig = raw.compute_psd(tmax=np.inf, fmax=250).plot(average=True, picks="eeg", exclude="bads")
            # # add some arrows at 60 Hz and its harmonics:
            # for ax in fig.axes[1:]:
            #     freqs = ax.lines[-1].get_xdata()
            #     psds = ax.lines[-1].get_ydata()
            #     for freq in (60, 120, 180, 240):
            #         idx = np.searchsorted(freqs, freq)
            #         ax.arrow(
            #             x=freqs[idx],
            #             y=psds[idx] + 18,
            #             dx=0,
            #             dy=-12,
            #             color="red",
            #             width=0.1,
            #             head_width=3,
            #             length_includes_head=True,
            #         )
            # plt.show()                          

            # Read events
            events = mne.find_events(raw, stim_channel="Trig1")            

            # Slicing
            # N.B. Add baseline to capture filtering artefacts of 
            # downsampling (removed later)
            # N.B. Use largest trialtime (samples are cut away later)
            baseline = 0.5
            epo = mne.Epochs(raw, events=events, tmin=-baseline, 
                tmax=cvep_trial_time_2, baseline= None, picks="eeg", 
                preload=True, reject_by_annotation= True)

            # Resampling
            # N.B. Downsampling is done after slicing to maintain accurate 
            # stimulus timing
            epo = epo.resample(sfreq=fs)
            
            # Collecting dropped epochs/trials
            dropped_eps = [n for n, dl in enumerate(epo.drop_log) if len(dl)] 

            # Add to database (trials channels samples)            
            baseline_idx = int(baseline * epo.info["sfreq"])           
            eeg.append(epo.get_data()[:, :, baseline_idx:])

            # Extract labels and conditions from marker stream
            streams = pyxdf.load_xdf(fn)[0]
            names = [stream["info"]["name"][0] for stream in streams]

            marker_stream = streams[names.index("KeyboardMarkerStream")]
                        
            labels.extend([int(marker[3]) 
                for marker in marker_stream["time_series"] 
                if marker[2] == "target"])
            
            # Removing trials with bad data from labels                      
            labels = [label for i, label in enumerate(labels) if i not in dropped_eps]            

        # Extract data (Data should be extracted per condition)
        X = np.concatenate(eeg, axis=0).astype("float32")  # trials channels samples
        y = np.array(labels).astype("uint8")
        
        print("size of X and y after epoch removal",[X.shape,y.shape])
        

       # Loop conditions-- hardcoding the value to the code used 
        conditions = ['mgold_61_6521'] * X.shape[0]         

        for condition in set(conditions):
            
            #Select trials
            idx = np.array([x == condition for x in conditions]).astype("bool_")
            _X = X[idx, :, :].astype("float32")
            _y = y[idx].astype("uint8")

            # Set correct trial length
            if "mseq" in condition or "gold" in condition:
                _X = _X[:, :, :int(cvep_trial_time_1 * fs)]
                
            # Load codes
            fn = os.path.join(repo, f"{condition}.npz").replace('\\','/')
            
            V = np.load(fn)["codes"]
            
            V = np.repeat(V, int(fs / pr), axis=0).astype("uint8")
            
            print("Condition:", condition)
            print("\tX:", _X.shape)
            print("\ty:", _y.shape)
            print("\tV:", V.shape)

            # Save data
            cvep = f"{subject}_cvep_{key_words[i_word]}_{condition}.npz"
            fn = os.path.join(path, "derivatives", subject, cvep)
            np.savez(fn, X=_X, y=_y, V=V, fs=fs)
            
    
            
 


