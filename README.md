# Covert_CVEP

# Main Idea
The goal of the project is to develop a novel gaze-independent brain-computer interface (BCI) based on code-modulated visual evoked potentials (C-VEP) for people living with late stage ALS. This repository contains code for the offline protocol of the said project.

# Contents
Contents: Different versions contain the various stages of the experimental paradigm and analyses scripts used for the project. 
1. **version 0**: preliminary experimental paradigm with parallel flashing with two classes. The stimuli displayed are the letters 'Y' and 'N'. 
2. **graz**: **This is the official folder for the submission made to the 2024 Graz BCI conference at TU Graz**. For a detailed overview of the experiment and analyses involved, refer to [arxiv](https://arxiv.org/pdf/2404.00031)
3. **version 2**: The most upto date script for the experiment will be found in version 2. The experiment consists of parallelly flashing stimuli containing 5 different shapes. The analysis folder now contains analyses for eye tracking data.

# Usage:
Each version (version_2 being the most up to date) contains an experiment and an analysis folder. 
## Experiment:
The scripts used to generate the stimuli, shape sequences and the overall experiment contents are located inside the experiment folder.
1. **lsl_eylink.py**: the script used for calibration and validation of eye tracking activity. It is used before the experiment begins.
2. **r_state.py**: the resting state script with only the fixation cross. Runs for 2 minutes. The experiment starts and ends with this script (2 minutes eyes open, 2 minutes eyes closed).
3. **lsl_cvep_p300_hybrid.py**: this script is used for presentation of the stimuli during the experiment. Parameters corresponding to monitor used, resolution, frame rate etc. from the config file are used here.
4. **cvep_p300_speller.py**: this script runs has the main keyboard class used in the lsl_cvep_p300_hybrid.py script.
5. **sequence_generation.ipynb**: this jupyter notebook shows the process and criteria for generating the shape sequences used in the experiment.

## Analysis:
Scripts used to analyze EEG and eyetracking data.
1. **read_and_preprocess_data.py**: loads the raw xdf files for the recorded EEG activity and preprocesss them. First step of the preliminary analysis.
2. **analyze_data.ipynb**: jupyter notebook for analyzing the preprocessed data. Performs classification using the rcca pipeline and stores the results. See this [paper]([https://arxiv.org/pdf/2404.00031](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0133797) for more details. Second step of the preliminary analysis.
3. **plot_results.ipynb**: jupyter notebook for visualizing the results from the analyzed data. Shows the variation of classification accuracy for different transient response lengths, over all classification accuracy along with the spatial filters and transient response curves. Last step of the preliminary analysis.
4. **eye_tracker_analysis.ipynb**: jupyter notebook for analzying eye tracking data from the experiment.
5. **plot_p300.ipynb**: jupyter notebook for visualizing the p300 response from the collected EEG activity.





