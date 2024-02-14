#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Jordy Thielen (jordy.thielen@donders.ru.nl)

Read LSL data
Modifications @ SN
1. Hardcoded the "conditions" vector for the codes used in the pilot
2. Added: A notch filter
3. Added: Option to view and remove bad epochs from data
4. Added: Option to remove bad channels 
5. Added: ICA for preprocessing and artefact removal

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
import easygui


# paths
data_path = r"C:\Users\s1081686\Desktop\RA_Project\Scripts\pynt_codes\SN_pilot_data"
codes_path = r"C:\Users\s1081686\Desktop\RA_Project\Scripts\pynt_codes\SN_experiment\codes_shifted"

subjects = ["pilot5"]
ses = "ses-S001"

skip_done = True

# presentation params 
fs = 120  # target EEG sampling frequency (multiple of stimulus presentation rate)
fr = 120
pr = 60  # stimulus presentation rate

# run params
overt_runs = 1
covert_runs = 4

# filtering params
cvep_l_freq = 1
cvep_h_freq = 40# originally 35 
notch = 50

# trial time 
trial_time = 20 # in seconds

# conditions
conditions = ['covert','overt']

for subject in subjects:
    print("*" * 15) # only one subject
          
    for i_condition in range(len(conditions)):
        
        print("starting data extraction for:",conditions[i_condition])
        labels_all=[] 
        eeg = []    
        
        if conditions[i_condition] == 'overt':
            i_run_range = overt_runs  
            
        else:
            i_run_range = covert_runs
        
        for i_run in range(i_run_range): # 
                        
            # Load xdf data into MNE
            fn = os.path.join(data_path, "raw", f"sub-{subject}", ses, "eeg", 
                f"sub-{subject}_{ses}_task-{conditions[i_condition]}_run-{1 + i_run:03d}_eeg.xdf")
            
            print("data_path is",fn)
            
            
            streams = pyxdf.resolve_streams(fn)
            names = [stream["name"] for stream in streams]

            stream_id = streams[names.index("BioSemi")]["stream_id"]
            raw = read_raw(fn, stream_ids=[stream_id])
           
            # Adjust marker channel data
            raw._data[0, :] -= np.min(raw._data[0, :])
            raw._data[0, raw._data[0, :] > 0] = 1
            raw._data[0, :] = np.logical_and(raw._data[0, :], np.roll(raw._data[0, :], -1)).astype(raw._data[0, :].dtype)
            events = mne.find_events(raw, stim_channel="Trig1")
            
            print("events found:", len(events))

            # Filtering
            raw = raw.filter(l_freq=cvep_l_freq, h_freq=cvep_h_freq, 
                picks=np.arange(1, 65), method="iir", 
                iir_params=dict(order=6, ftype='butter'))
                               
            # adding a notch filter
            raw.notch_filter(freqs=np.arange(notch,raw.info["sfreq"]/2,notch))
            
            
            'Plotting Raw Data (Optional but recommended)'
            '''Note- Only remove the epoch/trial if you see a huge/long fluctuation, 
            annotation ends up removing the whole trial even if only a small duration of it is bad'''
            
            #removing signal space projectors from raw file
            # ssp_projectors = raw.info["projs"]
            # raw.del_proj()           
                                    
            # print("raw data visualization, check for eye movement artefacts and huge movement artefacts")
            # eeg_chans = mne.pick_types(raw.info,eeg=True)
            # fig = raw.plot(duration=60,order = eeg_chans, n_channels = len(eeg_chans),remove_dc = False)# duration is the x second block with which you move in the plot
            # plt.title('Press A to begin',loc="center")
            # plt.show()
            # fig.fake_keypress("a")
            
            'Dropping bad channels (Optional)'
            # bad_chans = ['A24'] # found from the raw plots; A7 also looks strange for covert
            # raw.drop_channels(ch_names= bad_chans)

            # Eliminating bad channels based on the raw plots
            # print("bad channels", raw.info["bads"]) # checking for manually annotated bad channels during the recording
            
            
            'Powerline noise check after notch (Optional, recommended when running the script subjects from the same recording day)'
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
            # events = mne.find_events(raw, stim_channel="Trig1")
            
            # Extract labels and conditions from marker stream
            streams = pyxdf.load_xdf(fn)[0]
            names = [stream["info"]["name"][0] for stream in streams]
            marker_stream = streams[names.index("KeyboardMarkerStream")]
                             
            labels = [marker[3].lower().strip('""') == "right" 
            for marker in marker_stream["time_series"]
            if marker[2] == "cued_side"]

            
            'Setting up and fitting ICA'
            
            # picks_eeg = mne.pick_types(raw.info, meg = False, eeg = True, eog = False, stim = False, exclude = 'bads')            
            # ica_obj = mne.preprocessing.ICA(n_components = 64,   
            #                                 method =  'fastica',                                          
            #                                 max_iter = 'auto',
            #                                 random_state = 97 
            #                                 # fit_params = dict(extended = True)
            #                                 )
            
            # # Setting montage for biosemi (needed for topoplots)
            
            # # Read cap file
            # path_capfile = r"C:\Users\s1081686\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\site-packages\pyntbci\capfiles" 
            # capfile = os.path.join(path_capfile, "biosemi64.loc")
            # with open(capfile, "r") as fid:
            #     channels = []
            #     for line in fid.readlines():
            #         channels.append(line.split("\t")[-1].strip())
            
            # chan_names_old = raw.info.ch_names[1:63]
            
            # mapping = {}
            
            # for key, channel in zip(chan_names_old, channels):
            #     mapping[key] = channel
            
                
            # mne.rename_channels(raw.info,mapping = mapping)
            # # montage = mne.channels.make_standard_montage(kind = 'biosemi32')
            # montage = mne.channels.read_custom_montage(fname = capfile)
            # print(montage)
            # raw.set_montage(montage)
            
            # ica_obj.fit(raw, picks = picks_eeg)    # fitting the ica
            # ica =  ica_obj.get_sources(raw).get_data()
            # print("shape of ica matrix",ica.shape)
            
            # # plotting ICA results
            # ica_obj.plot_sources(raw)
            # ica_obj.plot_components(picks = None, show = True, inst = raw)# what does this actually show????0
            
            
            
            # # Applying ICA results to raw data and removing noisy components
            # exclude_vec_str = easygui.enterbox("Enter the component(s) you would like to exclude please (1 2 3 ..) ")
            # vector_list = [int(x) for x in exclude_vec_str.split()]
            # ica_obj.exclude = vector_list
            # ica_obj.apply(raw) # go back to EEG space????         

            # Slicing
            # N.B. Add baseline to capture filtering artefacts of 
            # downsampling (removed later)
            # N.B. Use largest trialtime (samples are cut away later)
            # baseline = 0.5
            epo = mne.Epochs(raw, events=events, tmin=-0.5, 
                tmax=trial_time, baseline= None, picks="eeg", 
                preload=True)           
            
            # Resampling
            # N.B. Downsampling is done after slicing to maintain accurate 
            # stimulus timing
            epo = epo.resample(sfreq=fs)
            
            # Collecting dropped epochs/trials
            # dropped_eps = [n for n, dl in enumerate(epo.drop_log) if len(dl)] 

            eeg.append(epo.get_data(tmin=0, tmax=trial_time))
            labels_all.append(labels)

            
            # Removing trials with bad data from labels                      
            # labels = [label for i, label in enumerate(labels) if i not in dropped_eps]            

        # Extract data 
        if i_run_range > 1:            
            X = np.squeeze(np.concatenate(eeg, axis=0)).astype("float32")  # trials channels samples
            y = np.concatenate(labels_all, axis=0).astype("uint8")
            
        else:
            X = np.squeeze(np.array(eeg)).astype("float32") 
            y = np.array(labels).astype("uint8")

        print("size of X and y ",[X.shape,y.shape])
        # Loop conditions-- hardcoding the value to the code used 
        code_used ='mgold_61_6521_mod'#
        
        # limiting the duration of data correctly
        X = X[:, :, :int(trial_time * fs)]
        
        # Load codes
        fn = os.path.join(codes_path, f"{code_used}.npz").replace('\\','/')
        
        V = np.load(fn)["codes"]
        
        V = np.repeat(V, int(fs / pr), axis=0).astype("uint8")
        
        print("Condition:", code_used)
        print("\tX:", X.shape)
        print("\ty:", y.shape)
        print("\tV:", V.shape)

        # Save data
        cvep = f"{subject}_cvep_{conditions[i_condition]}_{code_used}.npz"
        save_path = os.path.join(data_path, "derivatives", subject).replace('\\','/')
        if not os.path.isdir(save_path):
            os.makedirs(save_path)
        
        fn = os.path.join(save_path, cvep).replace('\\','/')
        np.savez(fn, X=X, y=y, V=V, fs=fs)
        
        print(f"data saved for {subject}")
        
    
            
    
            
 


