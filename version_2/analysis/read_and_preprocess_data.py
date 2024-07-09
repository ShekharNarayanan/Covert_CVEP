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
import easygui
import pyntbci

# paths
data_path = r'C:\Users\s1081686\Desktop\RA_Project\Scripts\pynt_codes\version_2\experiment_version_2\data_full_experiment' # path for raw data
codes_path = r'C:\Users\s1081686\Desktop\RA_Project\Scripts\pynt_codes\version_2\experiment_version_2\codes'


# subject and session
subjects = [f"VPpdi{letter}" for letter in 'abcdef'] # subject names
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
cvep_h_freq = 40# 40 high pass
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
                
            # apply ICA to channels
            picks_eeg = mne.pick_types(raw.info, meg = False, eeg = True, eog = False, stim = False)            
            ica_obj = mne.preprocessing.ICA(n_components = 64,   
                                            method =  'fastica',                                          
                                            max_iter = 'auto',
                                            random_state = 97 
                                            # fit_params = dict(extended = True)
                                            )
            
            # # Setting montage for biosemi (needed for topoplots)
            
            # Read cap file
            capfile = os.path.join(os.path.dirname(pyntbci.__file__), "capfiles", "biosemi64.loc") 
            with open(capfile, "r") as fid:
                channels = []
                for line in fid.readlines():
                    channels.append(line.split("\t")[-1].strip())
            
            chan_names_old = raw.info.ch_names[1:65]
            
            mapping = {}
            
            for key, channel in zip(chan_names_old, channels):
                mapping[key] = channel
            
  
            mne.rename_channels(raw.info,mapping = mapping)
            montage = mne.channels.read_custom_montage(fname = capfile)
            # print(montage)
            raw.set_montage(montage)
            
            ica_obj.fit(raw, picks = picks_eeg)    # fitting the ica
            ica =  ica_obj.get_sources(raw).get_data()
            print("shape of ica matrix",ica.shape)
            
            # plotting ICA results
            ica_obj.plot_sources(raw)
            ica_obj.plot_components(picks = None, show = True, inst = raw)# what does this actually show????
            
            # Applying ICA results to raw data and removing noisy components
            if i_run == 0: # check only the components for the first run per condition. For the rest of the runs, these components are automatically removed
                exclude_vec_str = easygui.enterbox("Enter the component(s) you would like to exclude with a space between them. For example: 1 2 3")
                vector_list =  [int(x) for x in exclude_vec_str.split()]
                
            ica_obj.exclude = vector_list
            ica_obj.apply(raw) 
 
            # Extract labels from marker stream
            streams = pyxdf.load_xdf(fn)[0]
            names = [stream["info"]["name"][0] for stream in streams]
            marker_stream = streams[names.index("KeyboardMarkerStream")]
                             
            labels = [marker[3].lower().strip('""') == "right" 
            for marker in marker_stream["time_series"]
            if marker[2] == "cued_side"]
            
            print("labels",len(labels))

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
        code ='mgold_61_6521'
        
        # limiting the duration of data to trial time
        X = X[:, :, :int(trial_time * fs)]
        
        # Load codes       
        V = np.load(os.path.join(codes_path,f'{code}.npz'))["codes"]
        
        V = np.repeat(V, int(fs / pr), axis=1).astype("uint8") # upsampling the code according to the downsampling freq and the presentation rate
        
        print("Condition:", code)
        print("\tX:", X.shape)
        print("\ty:", y.shape)
        print("\tV:", V.shape)

        # Save data
        cvep = f"{subject}_cvep_{condition}_{code}.npz"
        
        results_path = os.path.join(data_path, 'derivatives', subject)
        if not os.path.isdir(results_path):
            os.makedirs(results_path)
        fn = os.path.join(results_path, cvep)
        # np.savez(fn, X=X, y=y, V=V, fs=fs)
        
        print(f"data saved for subject {i_subject + 1}")
