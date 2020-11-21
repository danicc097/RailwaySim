"""
TODO: use in 
1.effort curves, 
2.to find data from a given kpoint

x = array([ 0, 10, 15])
y = array([1, 3, 6])
x_new = array([ 1,  2,  9, 14, 15, 16])
i = np.searchsorted(x, x_new, side='right') - 1
y_new = y[i]
y_new
>>> array([1, 1, 1, 3, 6, 6])
"""
# Colored terminal:
from termcolor import colored

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

        # print(constants)
        # print(constants['LOCO_AXLES'])
        dataset_np = np.genfromtxt(
            constants['ProfileLoadFilename'],
            delimiter=',',
            dtype=float,
            encoding='utf-8-sig',
            autostrip=True,
            deletechars=""
        )
        dataset_np = dataset_np[1:, 3:-1]
        print(dataset_np.shape)
        myrow = 2
        distance_step = dataset_np[myrow, 0]
        grade = dataset_np[myrow, 1]
        speed = dataset_np[myrow, 3]
        next_speed = dataset_np[myrow + 1, 3]
        # print("distance_step: ", distance_step)
        # print("grade: ", grade)
        # print("speed: ", speed)
        # print("next_speed: ", next_speed)
        # dataset_np = np.insert(dataset_np, myrow, dataset_np[myrow], axis=0)
        print(dataset_np[myrow - 1])
        print(dataset_np[myrow])
        print(dataset_np[myrow + 1])
        L_TRAIN = 550

        def rolling_R(speed):
            """Returns the current Rolling resistance. Args: Speed [km/h], Static mass [t]"""
            return constants['ROLLING_R_A'] * MASS_STATIC * 9.81 + \
                constants['ROLLING_R_B'] * MASS_STATIC * 9.81 * speed + \
                constants['ROLLING_R_C'] * speed**2

        # TODO: use grade_equiv() instead of grade
        def grade_R(grade):
            """Returns the current Grade resistance. Args: Grade [‰]"""
            return MASS_STATIC * 9.81 + grade / 1000

        # TODO: use radii_equiv() instead of grade
        def curve_R(radius):
            """Returns the current Curve resistance. Args: Radius [m]"""
            return (0 if not radius else MASS_STATIC * 4.9 * constants['TRACK_GAUGE'] / abs(radius))

        # TODO: resistance based on current distance step and length of train
        def R_i(row):
            speed = row
            radius = row
            grade = row
            r_0 = constants['STARTING_R'] if speed == 0 else 0
            return r_0 + curve_R(radius) + grade_R(grade) + rolling_R(speed)

        #* Locomotive simulation
        if constants['gb_locomotive']:
            L_TRAIN = constants['LOCO_LENGTH']
            MASS_STATIC_LOCO = constants['LOCO_NUMBER'] * constants['LOCO_MASS']
            MASS_STATIC_WAG = constants['WAG_NUMBER'] * constants['WAG_MASS']
            MASS_STATIC = MASS_STATIC_WAG + MASS_STATIC_LOCO
            MASS_EQUIV = constants['MASS_STATIC_LOCO'] * (
                1 + constants['LOCO_ROT_MASS']
            ) + constants['MASS_STATIC_WAG'] * (1 + constants['WAG_ROT_MASS'])

        #* Passenger train simulation
        if constants['gb_passenger']:
            L_TRAIN = constants['TRAIN_LENGTH']
            MASS_STATIC = constants['TRAIN_MASS']
            MASS_EQUIV = constants['TRAIN_MASS'] * (1 + constants['TRAIN_ROT_MASS'])
        # copy array to track, assigning to it is useless since we edit the dataset
        dataset_np_original = np.copy(dataset_np)

        def d_same_or_higher_speed(array, row, max_step):
            """Returns the distance value (up to 'step' meters) during which speed is the same or higher."""
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

        def d_same_speed(array, row, max_step):
            """Returns the distance value (up to 'step' meters) ahead during which speed is constant"""
            distance = array[row, 0]
            if max_step > 0:
                total_rows, _ = array.shape
                while row < total_rows - 1:
                    if array[row + 1, 3] != array[row, 3]:
                        break
                    distance += array[row + 1, 0]
                    row += 1
            elif max_step < 0:
                while row > 0:
                    if array[row, 3] != array[row - 1, 3]:
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

        # TODO: refactor
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

        array = speed_from_length(dataset_np)
        dataset_np_original = dataset_np_original.T
        array = array.T

        dataset_np_original = np.vstack(
            (dataset_np_original, np.cumsum(dataset_np_original[0] / 1000, dtype=float))
        )
        kpoint = np.cumsum(array[0] / 1000, dtype=float)
        array = np.vstack((array, kpoint))  # appends to last column (along vertical axis)

        ax = plt.subplot(111)
        ax.set_title(f"Length of train: {L_TRAIN} m")
        ax.step(array[9], array[3], color='red', label="Revised speed", where="pre")
        ax.step(array[9], array[1], color='green', label="Revised grade", where="pre")
        ax.step(
            dataset_np_original[9],
            dataset_np_original[1],
            color='black',
            label="Original grade",
            where="pre"
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
        array = array.T

        # np to pd # TODO use os paths
        parentDirectory = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
        a = pd.DataFrame(data=array)
        a.to_csv(
            parentDirectory + '/Output_template_COPY.csv',
            encoding='utf-8-sig',
            float_format='%1.8f',
            index=False,
        )

        plt.show()

        #* Maximum effort based on speed (diesel)
        if constants['gb_diesel_engine'] == True:
            try:
                Diesel_T_speed, Diesel_T_effort = effort_curve_to_arrays(
                    constants['D_TELoadFilename']
                )
                Diesel_B_speed, Diesel_B_effort = effort_curve_to_arrays(
                    constants['D_BELoadFilename']
                )
            except Exception as e:
                return qtw.QMessageBox.critical(
                    window, "Error", "Could not load Diesel traction - speed curve data: " + str(e)
                )
        #* Maximum effort based on speed (electric)
        if constants['gb_electric_traction'] == True:
            try:
                Electric_T_speed, Electric_T_effort = effort_curve_to_arrays(
                    constants['E_TELoadFilename']
                )
                Electric_B_speed, Electric_B_effort = effort_curve_to_arrays(
                    constants['E_BELoadFilename']
                )
            except Exception as e:
                return qtw.QMessageBox.critical(
                    window, "Error",
                    "Could not load Electric traction - speed curve data: " + str(e)
                )

        def target_brake():
            """Determines where the braking algorithm should be called, 
            to avoid continuous execution.
            Returns a list containing kpoints and corresponding steps."""

        def grade_equiv(current_kpoint):
            """
            Backwards search to define the equivalent grade based on train length.
            current_kpoint: accumulated distance until front of train.
            row: current distance_step

            #* The current kpoint has to be retrieved from the output array based
            #* on the actual simulation accumulated distance.

            """
            """
            row=
            grade_steps = []
            accum_length = 0
            current_grade = array[row, 1]
            previous_kpoint = array[row, -1]
            distance_step = current_kpoint - previous_kpoint
            if L_TRAIN <= distance_step:
                return current_grade
            else:
                grade_steps.append(distance_step * current_grade)
            while accum_length < L_TRAIN:
                # update with previous row
                row -= 1
                distance_step = array[row, 0]
                if distance_step + accum_length <= L_TRAIN:
                    accum_length += distance_step

                current_grade = array[row, 1]
                previous_kpoint = array[row, -1]
                previous_distance_step = array[row - 1, 0]
                previous_grade = array[row - 1, 1]
                grade_steps.append(distance_step * current_grade)

            return sum(grade_steps) / L_TRAIN
            """

        def total_time():
            """"""

    # Initialize solution array
    # output_array = np.zeros()
    # Array to be hstacked after each iteration
    # array_to_stack = np.array[total_time(), ]

    # TODO:
    #* Check if dynamic inputs are needed first ! (R(u), T(u), B(u))

    # def traction_mode_is_electric(row):
    #     return True if

    # def traction_mode_is_diesel(row):

    # TODO: get current max effort from curve.
    # get tmode from current distance step where == 1
    # automatically return tractive or braking based on state
    # def max_effort(row, traction_mode=None):
    #     """Returns the maximum effort available at current speed."""
    #     if traction_modebasedonrow:
    #         max_effort = np.interp(speedbasedonrow, Electric_T_speed, Electric_T_effort)
    #     return max_effort


# dataset_np = dataset_np.T
# time_sec = np.array(
#     np.linspace(0, int(len(dataset_np[0][1:]) / 2), num=len(dataset_np[0][1:]))
# )
# time_hours = np.array([s_to_hhmmss(a) for a in time_sec])
# distance = np.array([float(a) for a in dataset_np[3][1:] if a != ""])
# kpoint = np.cumsum(distance / 1000, dtype=float)
# grade = np.array([float(a) for a in dataset_np[4][1:] if a != ""])
# radius = np.array([float(a) for a in dataset_np[5][1:] if a != ""])
# speed_res = np.array([float(a) for a in dataset_np[6][1:] if a != ""])
# station_names = np.array([str(a) for a in dataset_np[12][1:]])
# print(time_sec)
# print(distance)
# print(grade)
# print(radius[3])
# print(speed_res[3])
# print(station_names[-1])

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