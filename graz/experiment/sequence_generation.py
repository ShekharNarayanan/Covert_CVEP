"""
author: Shekhar Narayanan (shekharnarayanan833@gmail.com)

Python script to generate shape sequences used in the stimulus paradigm
"""

import numpy as np
import random


def sequence_generator(all_shapes, sequence_size, target_shape, targets_in_trial_cued, targets_in_trial_non_cued, min_target_key_distance = 5):
    """
    Generate shape sequence for the stimulus paradigm

    Args:
        all_shapes (list): 
            The list containing the str initials of all shapes (r,i,t,c,h for rectange, inverted triangle, triangle, circle and hourglass)
        sequence_size (int): 
            The length of the sequence
        target_shape (str): 
            Target shape (hourglass)
        targets_in_trial_cued (int): 
            Number of targets on the cued side
        targets_in_trial_non_cued (int): 
            Number of targets on the cued side
        min_target_key_distance (int, optional): 
            Number of shapes between two target shapes. Defaults to 5.

    Returns:
        np.array: 
            The cued and non_cued sequences
    """
    # Defining an array with letters without the target shape  (size = len(all_shapes) - 1)  
    shapes_without_target = [shape for shape in all_shapes if shape != target_shape] # does not contain the target shape, see use later in adjacency rule  

    # Defining the array for the cued side
    cued_array = np.array(random.choices(shapes_without_target, k = sequence_size)) # target letters will be placed in this array later    
    cued_array_length = len(cued_array)

    # strategy for cued arr (same rules for the non_cued array): 
    # 1. Design an array with no two identical letters placed adjacently (adjacency rule).
    # 2. Place the target shape in the said array at random distances with minimum distance = min_target_key_distance (target distancing rule)

    # CUED ARRAY: making sure no identical letters are placed next to each other 
    for i in range(len(cued_array) - 1):
        if cued_array[i] == cued_array[i + 1]:
        # Find a different shape to replace the adjacent duplicate
            for shape in shapes_without_target: #replacing with any other shape other than the target shape
                if shape != cued_array[i] and (i == 0 or shape != cued_array[i - 1]):
                    cued_array[i + 1] = shape
                    break
                
    # mapping: each shape in the cued array is mapped to another one in shapes_without_target
    mapping = {shape: shapes_without_target[(index + len(shapes_without_target)//2) % len(shapes_without_target)]
        for index, shape in enumerate(shapes_without_target)}

    # NON_CUED ARRAY: each shape in the cued array is mapped to another one in all_shapes, 
    # hence the cued and noncued side will never show the same shape at the same time
    non_cued_array = np.array([mapping[shape] for shape in cued_array])

    # targets in the current trial
    target_count_trial_cued = targets_in_trial_cued


    # Calculate the default target distance given the fixed number of target letters in a trial
    tar_dist = np.round(cued_array_length/(target_count_trial_cued)) 

    # Initializing loop variables
    current_index = 0
    target_count = 0

    while target_count != target_count_trial_cued and current_index < cued_array_length:

        deviation = np.random.randint(0,5) # this varies the distance at which the targets are presented
        
        if (tar_dist - deviation) <= min_target_key_distance: # deviation in distance can not be less than the minimum value
            tar_dist_new =  tar_dist # no changes made
                
        else:
            tar_dist_new = tar_dist - deviation # new target distance used

        
        if  current_index == 0: # the first shape should not be a target
            cued_array[current_index+1] = target_shape 
            target_count +=1
            current_index += int(tar_dist_new)+1 
            
        else:
            cued_array[current_index] = target_shape
            target_count +=1
            current_index += int(tar_dist_new) 
            
    # Creating sequence for the non_cued side
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
        
        if  current_index == 0: # the first shape should not be a target
            non_cued_array[current_index+2] = target_shape # the third shape is the target shape 
            target_count +=1
            current_index += int(tar_dist_new)+1 
            
        else:
            non_cued_array[current_index] = target_shape
            target_count +=1
            current_index += int(tar_dist_new)

    
    return cued_array, non_cued_array

def targets_in_trial(n_trials: int, min_targets: int, max_targets: int):
    """
        Computes the number of targets for cued and non_cued sides 

    Args:
        n_trials (int): 
            Total trials in a run
        min_targets (int): 
            Criterion for minimum number of targets
        max_targets (int): 
            Criterion for maximum number of targets

    Returns:
        list: 
            Two lists containing the number of targets for the cued and non_cued sides respectively
    """
    
    size_of_arr = int(np.ceil(n_trials / 2))

    while True:
        array1 = np.random.randint(min_targets, max_targets, size=size_of_arr)
        array2 = np.random.randint(min_targets, max_targets, size=size_of_arr)
        
    # The sum of targets within a run on left and right sides should be the equal
        if np.sum(array1)== np.sum(array2):
            break

    return array1.tolist(), array2.tolist()