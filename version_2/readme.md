# Usage:
Each version (version_2 being the most up to date) contains an experiment and an analysis folder. For usage of specific versions, please refer to their respective readme.md file.
## Experiment:
The scripts used to generate the stimuli, shape sequences and the overall experiment contents are located inside the experiment folder.
1. **\eyelink\lsl_eylink.py**: the script used for calibration and validation of eye tracking activity. It is used before the experiment begins.
2. **r_state.py**: the resting state script with only the fixation cross. Runs for 2 minutes. The experiment starts and ends with this script (2 minutes eyes open, 2 minutes eyes closed).
3. **lsl_cvep_p300_hybrid.py**: this script is used for presentation of the stimuli during the experiment. Parameters corresponding to monitor used, resolution, frame rate etc. from the config file are used here.
4. **cvep_p300_speller.py**: this script runs has the main keyboard class used in the lsl_cvep_p300_hybrid.py script.
5. **sequence_generation.ipynb**: this jupyter notebook shows the process and criteria for generating the shape sequences used in the experiment.

## Analysis:
Scripts used to analyze EEG and eyetracking data.
1. **read_and_preprocess_data.py**: loads the raw xdf files for the recorded EEG activity and preprocesss them. First step of the preliminary analysis.
2. **analyze_data.ipynb**: jupyter notebook for analyzing the preprocessed data. Performs classification using the rcca pipeline and stores the results. See this [paper](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0133797) for more details. Second step of the preliminary analysis.
3. **plot_results.ipynb**: jupyter notebook for visualizing the results from the analyzed data. Shows the variation of classification accuracy for different transient response lengths, over all classification accuracy along with the spatial filters and transient response curves. Last step of the preliminary analysis.
4. **eye_tracker_analysis.ipynb**: jupyter notebook for analzying eye tracking data from the experiment.
5. **plot_p300.ipynb**: jupyter notebook for visualizing the p300 response from the collected EEG activity.
