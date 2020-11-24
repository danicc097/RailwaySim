"""
TODO: use in 
1.effort curves, 
2.to find data from a given kpoint

kpoint_new = np.array([0, 2, 2.523, 4, 5, 6, 7, 8])
kpoint = np.array([0, 3, 6])
speed = np.array([0, 120, 200])
i = np.searchsorted(kpoint, kpoint_new, side='right') - 1
speed_new = speed[i]
print(speed_new)
# [  0   0   0 120 120 200 200 200]

"""
# Colored terminal:
from numpy.core.numeric import roll
from termcolor import colored
import copy
from PyQt5 import QtWidgets as qtw
import numpy as np
import pandas as pd
import os
import sys
import matplotlib.pyplot as plt

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from solver.data_formatter import s_to_hhmmss, hhmm_to_s, effort_curve_to_arrays


# TODO: Refactor inner functions for readability
class ShortestOperationSolver():
    def __init__(self, window, constants):
        C = constants
        dataset_np = np.genfromtxt(
            C['ProfileLoadFilename'],
            delimiter=',',
            dtype=float,
            encoding='utf-8-sig',
            autostrip=True,
            deletechars=""
        )
        dataset_np = dataset_np[1:, 3:-1]

        #* Locomotive simulation
        if C['gb_locomotive']:
            L_TRAIN = C['LOCO_LENGTH']
            MASS_STATIC_LOCO = C['LOCO_NUMBER'] * C['LOCO_MASS']
            MASS_STATIC_WAG = C['WAG_NUMBER'] * C['WAG_MASS']
            MASS_STATIC = MASS_STATIC_WAG + MASS_STATIC_LOCO
            MASS_EQUIV = MASS_STATIC_LOCO * (1 + C['LOCO_ROT_MASS']
                                             ) + MASS_STATIC_WAG * (1 + C['WAG_ROT_MASS'])
            MAX_SPEED = C['LOCO_MAX_SPEED']
        #* Passenger train simulation
        elif C['gb_passenger']:
            L_TRAIN = C['TRAIN_LENGTH']
            MASS_STATIC = C['TRAIN_MASS']
            MASS_EQUIV = C['TRAIN_MASS'] * (1 + C['TRAIN_ROT_MASS'])
            MAX_SPEED = C['TRAIN_MAX_SPEED']
        else:
            return qtw.QMessageBox.critical(window, "Error", "Select a type of rolling stock.")

        def R_i(lookup_array, current_kpoint, current_speed):
            """Compute current rolling resistance."""
            lookup_kpoint = lookup_array[:, -1]
            lookup_index = np.searchsorted(lookup_kpoint, current_kpoint, side='right')
            radius = lookup_array[lookup_index, 2]
            curve_R = 0 if not radius else MASS_STATIC * 4.9 * C['TRACK_GAUGE'] / abs(radius)
            grade = grade_equiv(grade_array, current_kpoint)
            grade_R = MASS_STATIC * 9.81 + grade / 1000
            r_0 = C['STARTING_R'] if current_speed == 0 else 0
            rolling_R = C['ROLLING_R_A'] * MASS_STATIC * 9.81 + \
                        C['ROLLING_R_B'] * MASS_STATIC * 9.81 * current_speed + \
                        C['ROLLING_R_C'] * current_speed**2
            return r_0 + curve_R + grade_R + rolling_R

        # copy array to track changes, assigning to it is useless since we edit the dataset
        dataset_np_original = np.copy(dataset_np)

        def d_same_or_higher_speed(array, row, max_step):
            """Returns the distance (up to 'step' meters) during which speed is the same or higher."""
            distance = array[row, 0]
            if max_step > 0:
                total_rows, _ = array.shape
                while row < total_rows - 1:
                    if array[row + 1, 3] < array[row, 3]:
                        break
                    distance += array[row + 1, 0]
                    row += 1
            elif max_step < 0:
                while row > 0:
                    if array[row, 3] < array[row - 1, 3]:
                        break
                    distance += array[row - 1, 0]
                    row -= 1
            return distance

        def speed_grabber(array, row, step):
            """Returns a list of speeds contained in [kpoint(row), kpoint(row)+step] meters.
            Used to determine the minimum speed when step=L_TRAIN"""
            kpoint = np.cumsum(array[row, 0] / 1000, dtype=float)
            limit = kpoint + step
            speed_set = {array[row, 3]}
            if step > 0:
                total_rows, _ = array.shape
                while (kpoint < limit) and (row < total_rows - 1):
                    if array[row + 1, 3] < array[row, 3]: break  # braking applies
                    if array[row, 3] != 0: speed_set.add(array[row, 3])
                    kpoint += array[row, 0]
                    row += 1
            elif step < 0:
                while (kpoint > limit) and (row > 0):
                    if array[row, 3] != 0: speed_set.add(array[row, 3])
                    kpoint -= array[row, 0]
                    row -= 1
            return speed_set if speed_set is not None else 99999

        def split_row(array, row, distance=None, speed=None):
            """Splits a row and assigns a given distance and speed to the first part."""
            array = np.concatenate((array[:row], array[row, None], array[row:]), axis=0)
            if distance and speed:
                array[row, 3] = speed
                array[row, 0] = distance
            return array

        def speed_from_length(array, row=0):
            """Calculates the speed which ensures that the last point in the train complies with
            the speed limit. Returns a modified array."""
            stacked_steps = list()
            total_rows, _ = array.shape
            speed_to_check = 0
            while row < total_rows - 1:
                total_rows, _ = array.shape
                speed = np.copy(array)[row, 3]
                next_distance = np.copy(array)[row + 1, 3]
                next_speed = array[row + 1, 3]
                distance_same_or_higher_speed = d_same_or_higher_speed(array, row + 1, L_TRAIN)
                if array[row, 0] == 0 or next_speed <= speed or next_speed == speed_to_check:
                    row += 1
                    stacked_steps.clear()
                    speed_to_check = 0
                else:
                    #* If there's an equal or higher speed for more than L_TRAIN,
                    #* override speed and split last row
                    if distance_same_or_higher_speed >= L_TRAIN:
                        # ? Refactor into separate function.
                        if len(stacked_steps) > 0:
                            array, row = _apply_offset_array(stacked_steps, array, row, L_TRAIN)
                        else:
                            #* Loop and replace speed in all rows until accumulated length = L_TRAIN, but
                            #* saving original (distance, speed) pairs, to be applied after the L_TRAIN offset
                            array, row, speed_to_check = _create_offset_array(
                                array, row, speed, next_speed, stacked_steps
                            )

                    #* Once L_TRAIN has been offset, override the following rows with
                    #* the original values, saved in stacked_steps
                    else:
                        #* Check if there's accumulated (distance,speed) pairs,
                        #* i.e. an offset was applied
                        if len(stacked_steps) > 0:
                            array, row = _apply_offset_array(
                                stacked_steps, array, row, next_distance
                            )
                        #* If the following distance (with equal or higher speed) has no
                        #* accumulated offset, speed is simply replaced
                        #* and there's no need to accumulate this change creating an offset array
                        #* since there's a smaller speed ahead and everything gets reset
                        else:
                            array[row + 1, 3] = array[row, 3]
                            row += 1
            return array

        def _create_offset_array(array, row, speed, next_speed, stacked_steps):
            """Offsets an array based on train length and stores the original array slices."""
            accum_steps = 0
            remaining_length = 9999
            speed_to_check = 0
            while accum_steps < L_TRAIN and remaining_length > 0:
                remaining_length = L_TRAIN - accum_steps
                #* When the next step is larger than the remaining length to be overridden,
                #* split this next row and assign the previous speed to the first slice
                if array[row + 1, 0] > remaining_length:
                    array = split_row(array, row + 1, remaining_length, speed)
                    array[row + 2, 0] -= remaining_length
                    accum_steps = L_TRAIN + 9999  # break out of inner loop
                    row += 1  # skip the newly created row as well
                    speed_to_check = next_speed  # the next loop will check the original speed
                #* If the next step is smaller or equal, assign previous speed and accumulate distance
                else:
                    stacked_steps.append([np.copy(array)[row + 1, 0], np.copy(array)[row + 1, 3]])
                    array[row + 1, 3] = speed
                    accum_steps += array[row + 1, 0]
                    row += 1
            return array, row, speed_to_check

        def _apply_offset_array(stacked_steps, array, row, stop_cond):
            """Applies the stacked steps and corresponding speed until the stop
            distance is reached or the steps have been completely offset."""
            i = 0
            accum_offset = 0
            while i < len(stacked_steps) and accum_offset < stop_cond:
                stacked_distance, stacked_speed = stacked_steps.pop(i)
                if array[row + 1, 0] > stacked_distance:
                    array = split_row(array, row + 1, stacked_distance, stacked_speed)
                    array[row + 2, 0] -= stacked_distance
                    row += 1  # skip the newly created row as well
                else:
                    array[row + 1, 3] = stacked_speed
                    accum_offset += array[row + 1, 0]
                    updated_step = [stacked_distance - array[row + 1, 0], stacked_speed]
                    stacked_steps.insert(i + 1, updated_step)
                i += 1
            row += 1
            stacked_steps.clear()
            return array, row

        def d_same_value(lookup_array, current_kpoint, lookup_column, direction='forward'):
            """Returns the distance in meters from the `current_kpoint` during 
            which the values of the specified ``lookup_column`` (e.g. speed, grade or radius)
            are constant in `lookup_array`.\n
            ``direction``: 'forward', 'backward'\n
            Examples:
            ---------
            Grade equivalent: d_same_value(lookup_array, current_kpoint, 1, direction='backward')
            """

            lookup_kpoint = lookup_array[:, -1]
            lookup_index = np.searchsorted(lookup_kpoint, current_kpoint, side='right')
            distance = 0
            value = 0
            skip_blank_counter = 0
            initial_index = copy.deepcopy(lookup_index)
            if direction == 'forward':
                distance = (lookup_kpoint[lookup_index] - current_kpoint) * 1000
                total_rows, _ = lookup_array.shape
                while lookup_index < total_rows - 1:
                    if lookup_array[lookup_index + 1, lookup_column] != \
                    lookup_array[lookup_index, lookup_column]:
                        break
                    distance += lookup_array[lookup_index + 1, 0]
                    lookup_index += 1
                value = lookup_array[lookup_index, lookup_column]
            elif direction == 'backward':
                distance = (current_kpoint - lookup_kpoint[lookup_index - 1]) * 1000
                while lookup_index > 0:

                    if lookup_array[lookup_index, lookup_column] != \
                        lookup_array[lookup_index - 1,lookup_column]:
                        break
                    distance += lookup_array[lookup_index - 1, 0]
                    lookup_index -= 1
                    if lookup_array[lookup_index - 1, 0] == 0:
                        skip_blank_counter += 1
                value = lookup_array[initial_index - skip_blank_counter, lookup_column]
            return distance, value

        #* Maximum effort based on speed (diesel)
        if C['gb_diesel_engine'] == True:
            try:
                Diesel_T_speed, Diesel_T_effort = effort_curve_to_arrays(C['D_TECurveLoadFilename'])
                Diesel_B_speed, Diesel_B_effort = effort_curve_to_arrays(C['D_BECurveLoadFilename'])
            except Exception as e:
                return qtw.QMessageBox.critical(
                    window, "Error", "Could not load Diesel traction - speed curve data: " + str(e)
                )
        #* Maximum effort based on speed (electric)
        if C['gb_electric_traction'] == True:
            try:
                Electric_T_speed, Electric_T_effort = effort_curve_to_arrays(
                    C['E_TECurveLoadFilename']
                )
                Electric_B_speed, Electric_B_effort = effort_curve_to_arrays(
                    C['E_BECurveLoadFilename']
                )
            except Exception as e:
                return qtw.QMessageBox.critical(
                    window, "Error",
                    "Could not load Electric traction - speed curve data: " + str(e)
                )

        ########## Virtual speed based on length #############
        ##########    Equivalent grade array     #############
        ######################################################
        kpoint = np.cumsum(dataset_np_original[:, 0] / 1000, dtype=float)
        dataset_np_original = np.hstack((dataset_np_original, kpoint.reshape(kpoint.size, 1)))
        a = speed_from_length(dataset_np)
        kpoint = np.cumsum(a[:, 0] / 1000, dtype=float)
        a = np.hstack((a, kpoint.reshape(kpoint.size, 1)))
        virtual_speed_array = np.copy(a)

        #* Array to calculate average grade, without 0 m steps
        b = dataset_np
        b = b[~(b == 0).all(1)]
        kpoint = np.cumsum(b[:, 0] / 1000, dtype=float)
        b = np.hstack((b, kpoint.reshape(kpoint.size, 1)))
        # assume previous route conditions as the station's
        grade_array = np.concatenate((b[0, None], b[0:]), axis=0)
        grade_array[0, 0] = L_TRAIN

        ######################################################

        def grade_equiv(lookup_grade_array, current_kpoint):
            """Backward search to define the equivalent grade based on train length.\n
            ``current_kpoint``: simulation point on the front of the train.
            """
            lookup_kpoint = lookup_grade_array[:, -1]
            row = np.searchsorted(lookup_kpoint, current_kpoint, side="right")
            grade_steps = []
            accum_length = (current_kpoint - lookup_kpoint[row - 1]) * 1000
            grade_steps.append(accum_length * lookup_grade_array[row, 1])
            row -= 1
            while accum_length < L_TRAIN:
                d_same_grade, grade = lookup_grade_array[row, 0], lookup_grade_array[row, 1]
                if d_same_grade > (L_TRAIN - accum_length):
                    # Last remaining section
                    grade_steps.append((L_TRAIN - accum_length) * grade)
                    break
                else:
                    grade_steps.append(d_same_grade * grade)
                    accum_length += d_same_grade
                    row -= 1
            return sum(grade_steps) / L_TRAIN

        def max_effort(current_speed, mode=1):
            """Returns the maximum effort available at current speed.
            Parameters:
            -----------
            `mode`: ``1`` (powering/cruising), ``2`` (braking)"""
            max_effort = 0
            if mode == 1:
                if current_speed > MAX_SPEED:
                    current_speed = MAX_SPEED
                max_effort = np.interp(current_speed, Electric_T_speed, Electric_T_effort)
            elif mode == 2:
                if current_speed > MAX_SPEED:
                    current_speed = MAX_SPEED
                max_effort = np.interp(current_speed, Electric_B_speed, Electric_B_effort)
            return max_effort

        # * R_i(lookup_array, current_kpoint, current_speed)

        def main_simulation(lookup_array, grade_lookup_array):
            """
            append row with step=Ltrain to LOOKUP_ARRAY, to calculate equiv grade
            3 arrays: LOOKUP_ARRAY constant, braking_table and output_array.
            braking_table contains an array for every target brake row with d_step = LOOKUP_ARRAY[d_step] 

            FORWARD CALC (main_calculations()):
            initialize np.zeros 
            while kpoint_(i) < ROUTE_LENGTH
                k = 0
                # check against the upcoming "k" brake array
                if kpoint_(i) < braking_table[k][0,0]: # still not a target for braking
                    get_max_effort(speed_(i))
                    if speed_(i) < speed_limit(i):
                        power_mode()
                    if speed_(i) >= speed_limit(i):
                        replace speed_(i) with speed_limit(i)
                        cruising_mode() calculate effort result with u=speed_limit
                else: # inside brake target array limits
                    if kpoint_(i) > braking_table[k][0,-1]: # we passed the last kpoint in the current brake array
                        k+=1
                        continue
            """
            array = np.zeros(8, dtype=float)
            print(grade_equiv(grade_lookup_array, 3.98))
            return array

        main_simulation(virtual_speed_array, grade_array)

        #* Plotting and saving
        dataset_np_original = dataset_np_original.T
        virtual_speed_array = virtual_speed_array.T

        ax = plt.subplot(111)
        ax.set_title(f"Length of train: {L_TRAIN} m")
        ax.step(
            virtual_speed_array[9],
            virtual_speed_array[3],
            color='red',
            label="Revised speed",
            where="pre",
        )
        ax.step(
            virtual_speed_array[9],
            virtual_speed_array[1],
            color='green',
            label="Revised grade",
            where="pre",
        )
        ax.step(
            dataset_np_original[9],
            dataset_np_original[1],
            color='black',
            label="Original grade",
            where="pre",
        )
        ax.step(
            dataset_np_original[9],
            dataset_np_original[3],
            label="Original speed",
            where="pre",
        )
        ax.set_xlabel('Distance [km]')
        ax.set_ylabel('Speed [km/h]')
        ax.legend()

        dataset_np_original = dataset_np_original.T
        virtual_speed_array = virtual_speed_array.T

        # np to pd # TODO use os paths
        parentDirectory = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
        a = pd.DataFrame(data=virtual_speed_array)
        a.to_csv(
            parentDirectory + '/Output_template_COPY.csv',
            encoding='utf-8-sig',
            float_format='%1.8f',
            index=False,
        )

        # plt.show()

        def target_brake():
            """Determines where the braking algorithm should be called, 
            to avoid continuous execution.
            Returns a list containing kpoints and corresponding steps."""

    # Initialize solution array
    # output_array = np.zeros()
    # Array to be hstacked after each iteration
    # array_to_stack = np.array[total_time(), ]

    # TODO:
    #* Check if dynamic inputs are needed first ! (R(u), T(u), B(u))

    def current_traction_mode(lookup_array, current_kpoint):
        traction_mode_is_electric_AC = 0
        traction_mode_is_electric_DC = 0
        traction_mode_is_diesel = 0
        traction_mode_is_battery = 0


# # creating the Numpy array
# myarray = np.empty((0, 7), dtype=float)
# #myarray = np.array([time_sec, time_hours, distance, kpoint, grade, radius, speed_res]).T
# myarray = np.vstack((myarray, [1, 2, 3, 4, 5, 6, 7]))
# print(myarray[0, 2])
# myarray = np.vstack((myarray, [1, myarray[0, 1] * 5, 3, 4, 5, 6, 7]))

# #index_values = ['first', 'second'] # index names ("row headers")

# # Change column names (1,...,n by default)
# column_values = [
#     'Time [s]',
#     'Time [hh:mm:ss]',
#     'Distance step [m]',
#     'KP [km]',
#     'Speed [km/h]',
#     'Acceleration [m/s²]',
#     'Grade [‰]',
#     'Profile [m]',
#     'Radius [m]',
#     'Speed restriction [km/h]', # from original dataset (write based on kpoint)
#     'Tractive Effort [kN]',
#     'Braking Effort [kN]',
#     'Resistance [kN]',
# ]
#     'Regeneration max power [kW]',
#     'AC line',
#     'DC line',
#     'Diesel mode',
#     'Battery mode',

# # np to pd # TODO use os paths

# parentDirectory = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
# a = pd.DataFrame(data=myarray, columns=column_values[:7])
# a.to_csv(
#     parentDirectory + '/Output_template_COPY.csv',
#     encoding='utf-8-sig',
#     float_format='%1.8f',
#     index=False,
# )

# # # ! Copy template and dump to CSV
# # def copy_csv(filename):
# #     df = pd.read_csv(filename, encoding='utf-8-sig')
# #     df.to_csv('RailwaySim/Output_template_COPY.csv', encoding='utf-8-sig')
# #     pd.DataFrame(a).to_csv(
# #         'RailwaySim/Output_template_COPY.csv',
# #         mode='a',
# #         sep=",",
# #         header=False,
# #         encoding='utf-8-sig',
# #         float_format='%1.8f',
# #         index=False,
# #     )
# # copy_csv('RailwaySim/Output_template.csv')

# print('Simulation ended successfully.')

# ShortestOperationSolver(None, None)