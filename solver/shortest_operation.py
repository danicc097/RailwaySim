from numpy.lib.scimath import sqrt
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

C = {
    'AUX_EFF': 0.0,
    'BATT_CAPACITY': 0,
    'BATT_CHARG_RATE': 0.0,
    'BATT_DISCHARG_RATE': 0.0,
    'BATT_NUMBER': 0,
    'BOGIES': 4,
    'BRAKE_DELAY': 0,
    'D_AUX_CONS': 0,
    'D_BECurveLoadFilename': '',
    'D_MAX_RATE': 0,
    'D_TECurveLoadFilename': '',
    'E_AUX_CONS': 0,
    'E_BECurveLoadFilename': 'C:/Users/danic/MyPython/RailwaySim/Input_TE.csv',
    'E_MAX_RATE': 0,
    'E_TECurveLoadFilename': 'C:/Users/danic/MyPython/RailwaySim/Input_TE.csv',
    'INV_EFF': 0.0,
    'LOCO_AREA': 6.0,
    'LOCO_AXLES': 2,
    'LOCO_LENGTH': 550.0,
    'LOCO_MASS': 120.0,
    'LOCO_MAX_A': 1.5,
    'LOCO_MAX_SPEED': 200,
    'LOCO_NUMBER': 1,
    'LOCO_ROT_MASS': 5.0,
    'MOTOR_BOGIES': 4,
    'MOTOR_EFF': 0.0,
    'ProfileLoadFilename': 'C:/Users/danic/MyPython/RailwaySim/Input_template - Long.csv',
    'RECT_EFF': 0.0,
    'ROLLING_R_A': 1.919,
    'ROLLING_R_B': 0.03611,
    'ROLLING_R_C': 0.00049,
    'STARTING_R': 30.0,
    'TIME_STEP': 1.5,
    'TRACK_GAUGE': 1.668,
    'TRAFO_EFF': 0.0,
    'TRAIN_AREA': 0.0,
    'TRAIN_LENGTH': 88.0,
    'TRAIN_MASS': 194.0,
    'TRAIN_MAX_A': 1.5,
    'TRAIN_MAX_SPEED': 200,
    'TRAIN_ROT_MASS': 5.84,
    'WAG_AXLES': 4,
    'WAG_MASS': 35.0,
    'WAG_NUMBER': 10,
    'WAG_ROT_MASS': 4.0,
    'cb_InvertRoute': False,
    'cb_r_grade': True,
    'cb_r_legend': True,
    'cb_r_profile': False,
    'cb_r_radii': False,
    'cb_r_speedres': True,
    'cb_r_stations': True,
    'gb_diesel_engine': False,
    'gb_eff': False,
    'gb_electric_traction': True,
    'gb_locomotive': False,
    'gb_onboard_storage': False,
    'gb_passenger': True,
    'groupBox': False,
    'groupBox_13': False,
    'groupBox_14': False,
    'groupBox_15': False,
    'groupBox_17': False,
    'groupBox_2': False,
    'groupBox_3': False,
    'groupBox_4': False,
    'groupBox_5': False,
    'groupBox_6': False,
    'groupBox_7': False,
    'spinBox_2': 0
}


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
        if C['cb_InvertRoute']: dataset_np = np.flip(dataset_np, axis=0)
        # copy array to track changes, assigning to it is useless since we edit the dataset
        dataset_np_original = np.copy(dataset_np)

        #* Locomotive simulation
        if C['gb_locomotive']:
            L_TRAIN = C['LOCO_LENGTH']
            MASS_STATIC_LOCO = C['LOCO_NUMBER'] * C['LOCO_MASS']
            MASS_STATIC_WAG = C['WAG_NUMBER'] * C['WAG_MASS']
            MASS_STATIC = MASS_STATIC_WAG + MASS_STATIC_LOCO
            MASS_EQUIV = MASS_STATIC_LOCO * (1 + C['LOCO_ROT_MASS'] /
                                             100) + MASS_STATIC_WAG * (1 + C['WAG_ROT_MASS'] / 100)
            MAX_SPEED = C['LOCO_MAX_SPEED']
            MAX_ACCEL = C['LOCO_MAX_A']
        #* Passenger train simulation
        elif C['gb_passenger']:
            L_TRAIN = C['TRAIN_LENGTH']
            MASS_STATIC = C['TRAIN_MASS']
            MASS_EQUIV = C['TRAIN_MASS'] * (1 + C['TRAIN_ROT_MASS'] / 100)
            MAX_SPEED = C['TRAIN_MAX_SPEED']
            MAX_ACCEL = C['TRAIN_MAX_A']
        else:
            return qtw.QMessageBox.critical(window, "Error", "Select a type of rolling stock.")

        def d_same_speed(array, row, max_step):
            """Returns the distance during which speed is the same or higher.
            If `max_step` < `0` it will search backwards."""
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
                if array[row, 3] > MAX_SPEED:
                    array[row, 3] = MAX_SPEED
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

        def d_same_value(lookup_array, kpoint, lookup_column, direction='forward'):
            """Returns the distance in meters from the `kpoint` during 
            which the values of the specified ``lookup_column`` (e.g. speed, grade or radius)
            are constant in `lookup_array`.\n
            ``direction``: 'forward', 'backward'\n
            Examples:
            ---------
            Grade equivalent: d_same_value(lookup_array, kpoint, 1, direction='backward')
            """

            lookup_kpoint = lookup_array[:, -1]
            lookup_index = np.searchsorted(lookup_kpoint, kpoint, side='left')
            distance = 0
            value = 0
            skip_blank_counter = 0
            initial_index = copy.deepcopy(lookup_index)
            if direction == 'forward':
                distance = (lookup_kpoint[lookup_index] - kpoint) * 1000
                total_rows, _ = lookup_array.shape
                while lookup_index < total_rows - 1:
                    if lookup_array[lookup_index + 1, lookup_column] != \
                    lookup_array[lookup_index, lookup_column]:
                        break
                    distance += lookup_array[lookup_index + 1, 0]
                    lookup_index += 1
                value = lookup_array[lookup_index, lookup_column]
            elif direction == 'backward':
                distance = (kpoint - lookup_kpoint[lookup_index - 1]) * 1000
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
        ##########              &                #############
        ##########    Equivalent grade array     #############
        ######################################################
        #* Array to calculate average grade,
        #* Removes 0 m steps and accounts for train length
        b = dataset_np
        # b = b[~(b == 0).all(1)]
        b = b[b[:, 0] > 0]
        kpoint = np.cumsum(b[0:, 0] / 1000, dtype=float)
        b = np.hstack((b, kpoint.reshape(kpoint.size, 1)))
        grade_array = np.concatenate((b[0, None], b[0:]), axis=0)
        grade_array[0, 0] = L_TRAIN
        grade_array[0, 1:] = 0

        kpoint = np.cumsum(dataset_np_original[:, 0] / 1000, dtype=float)
        dataset_np_original = np.hstack((dataset_np_original, kpoint.reshape(kpoint.size, 1)))
        a = speed_from_length(dataset_np)
        kpoint = np.cumsum(a[:, 0] / 1000, dtype=float)
        a = np.hstack((a, kpoint.reshape(kpoint.size, 1)))
        virtual_speed_array = np.copy(a)

        ######################################################

        # def original_grade(lookup_grade_array, kpoint):
        #     """Backward search to define the equivalent grade based on train length.\n
        #     ``kpoint``: simulation point on the front of the train.
        #     """
        #     lookup_kpoint = lookup_grade_array[:, -1]
        #     row = np.searchsorted(lookup_kpoint, kpoint, side="left")  # left for backwards
        #     return lookup_grade_array[row, 1]

        def radius(lookup_grade_array, kpoint):
            """Backward search to retrieve the current radius.\n
            ``kpoint``: simulation point on the front of the train.
            """
            lookup_kpoint = lookup_grade_array[:, -1]
            row = np.searchsorted(lookup_kpoint, kpoint, side="left")  # left for backwards
            return lookup_grade_array[row, 2]

        #!TODO: SAME LOGIC TO FIND CURRENT RADIUS, ELECTRIFICATION, ETC
        def grade_equiv(lookup_grade_array, kpoint, side=None):
            """Backward search to define the equivalent grade based on train length.\n
            ``kpoint``: simulation point on the front of the train.
            """
            lookup_kpoint = lookup_grade_array[:, -1]
            row = np.searchsorted(lookup_kpoint, kpoint, side=side)
            grade_steps = []
            accum_length = (kpoint - lookup_kpoint[row - 1]) * 1000
            if accum_length > L_TRAIN:
                return lookup_grade_array[row, 1]
            grade_steps.append(accum_length * lookup_grade_array[row, 1])
            row -= 1
            if row < 0: return lookup_grade_array[0, 1]
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

        def max_effort(speed, speed_limit, mode=1):
            """Returns the maximum effort available at current speed.\n
            Parameters:
            -----------
            `mode`: `1` (powering/cruising), `2` (braking)"""
            max_effort = 0
            if mode == 1:
                if speed > speed_limit:
                    speed = speed_limit
                max_effort = np.interp(speed, Electric_T_speed, Electric_T_effort)
            elif mode == 2:
                if speed > speed_limit:
                    speed = speed_limit
                max_effort = abs(np.interp(speed, Electric_B_speed, Electric_B_effort))
            return max_effort

        # * Validated
        def R_i(speed, grade, radius, braking=None):
            """Compute instantaneous rolling resistance.
            Parameters:
            -----------
            `braking`: `None` or `1`"""
            curve_R = 0 if radius == 0 \
                else MASS_STATIC * 4.9 * C['TRACK_GAUGE'] / abs(radius)
            grade_R = MASS_STATIC * 9.81 * grade / 1000
            rolling_R = C['ROLLING_R_A'] + \
                        C['ROLLING_R_B'] * speed/3.6 + \
                        C['ROLLING_R_C'] * (speed/3.6)**2
            #* Don't include starting resistance when computing brake steps
            if not braking:
                starting_R = C['STARTING_R'] if speed == 0 else 0
            else:
                starting_R = 0
            return starting_R + curve_R + grade_R + rolling_R

        def accel_i(speed, speed_limit, resistance, mode=1):
            """Determine instantaneous acceleration.\n
            Parameters:
            -----------
            `mode`: `1` (powering), `2` (braking), `3` (cruising)"""
            # * Ensure it goes down when not enough power!!
            if mode == 1:
                tractive_effort = max_effort(speed, speed_limit, mode=1)
                accel = (tractive_effort - resistance) / MASS_EQUIV
                if accel > MAX_ACCEL: accel = MAX_ACCEL
                return accel
            elif mode == 2:
                #* Max regenerative braking without losses
                reg_effort = max_effort(speed, speed_limit, mode=2)
                accel = -MAX_ACCEL
                total_braking_effort = resistance + MASS_EQUIV * abs(accel)
                return accel, total_braking_effort
            elif mode == 3:  # cruising
                accel = 0
                output_effort = resistance
                maximum_effort = max_effort(speed, speed_limit, mode=1)
                if (maximum_effort - resistance) / MASS_EQUIV < 0:
                    accel = (maximum_effort - resistance) / MASS_EQUIV
                    output_effort = maximum_effort
                return accel, output_effort

        def some_cool_braking_function(lookup_array, lookup_grade_array):
            """Computes a list of arrays to append braking curves
            the main forward calculations."""
            #* Initialize table (last station):
            k = 0
            dx = 5  # braking distance step accuracy #TODO: user-defined
            braking = [np.zeros((2, 11), dtype=float)]
            braking[k][1, 0] = kpoint = lookup_array[-1, -1]
            lookup_kpoint = lookup_array[:, -1]
            u_lim_not_reached = False  # Override initial braking speed with the simulated one if the speed limit wasn't reached
            speed_accum = 0
            min_d = dx / 1000 * 3
            while kpoint > min_d:
                print(colored(kpoint, "green"))
                row = np.searchsorted(lookup_kpoint, kpoint, side="left")
                if row < 2: break
                speed_limit = lookup_array[row, 3]
                previous_speed_limit = lookup_array[row + 1, 3]
                r, _ = braking[0].shape
                if r == 2:  #* Initialize new array list element
                    braking[k][1, 0] = kpoint
                    braking[k][1, 3] = previous_speed_limit
                if u_lim_not_reached:  #* Safe speed below limit → Override
                    braking[k][1, 3] = speed_accum
                if speed_limit > previous_speed_limit or u_lim_not_reached:  #* Target to calculate array
                    u_lim_not_reached = False
                    target_distance = d_same_speed(lookup_array, row, -1)
                    end_of_target = kpoint - target_distance / 1000
                    run_loop = True
                    while run_loop:  # and kpoint > end_of_target
                        kpoint, u_lim_not_reached, run_loop, speed_accum, k = _compute_braking_curve(
                            braking, k, dx, lookup_grade_array, speed_limit, kpoint, end_of_target,
                            lookup_kpoint, lookup_array
                        )
                else:
                    #* Not a possible target → Skip
                    u_lim_not_reached = False
                    row -= 1
                    kpoint = lookup_array[row, -1]

            return _clean_braking(braking, dx)

        def _compute_braking_curve(
            braking, k, dx, lookup_grade_array, speed_limit, kpoint, end_of_target, lookup_kpoint,
            lookup_array
        ):
            """Inserts an array of a single braking curve to `braking`."""
            kpoint = _new_brake_step(braking, k, dx, lookup_grade_array, speed_limit, kpoint)
            u_lim_not_reached = False
            run_loop = True
            speed_accum = 0
            if kpoint < end_of_target:
                previous_row = np.searchsorted(lookup_kpoint, kpoint, side="left") + 1
                #* if the end_of_target isn't a station, override the next speed limit
                if lookup_array[previous_row, 3] != 0:
                    u_lim_not_reached = True
                    speed_accum = braking[k][0, 3]
                #* don't use kpoint value as loop condition,
                #* else it breaks as soon as kpoint > end_of_target
                run_loop = False
            if braking[k][0, 3] < speed_limit:  #* Continue braking
                braking[k] = np.insert(braking[k], 0, np.zeros((1, 11)), axis=0)
            else:
                #* Jump to end of target and continue searching
                braking[k][0, 3] = speed_limit
                a = np.zeros((2, 11), dtype=float)
                braking.insert(0, a)
                k += 1
                kpoint = end_of_target
                run_loop = False
            return kpoint, u_lim_not_reached, run_loop, speed_accum, k

        #TODO: SAME LOGIC TO APPEND CURVE slice TO FORWARD CALC
        def _clean_braking(braking, dx):
            """Remove unnecessary empty rows and singularities 
            from the braking list of arrays."""
            braking = np.concatenate(braking, axis=0)
            braking = braking[braking[:, 0] > 0]
            accum_brake_steps = 0
            total_rows, _ = braking.shape
            for row in range(total_rows - 2):
                next_kpoint = braking[row + 1, 0]
                kpoint = braking[row, 0]
                next_speed = braking[row + 1, 3]
                speed = braking[row, 3]
                if (
                    next_kpoint - kpoint
                ) * 1000 < dx * 2 and next_speed - speed < 0:  # it's a braking curve
                    accum_brake_steps += 1
                else:
                    if accum_brake_steps < 2:
                        braking = np.delete(braking, row, axis=0)
                    accum_brake_steps = 0
            return braking

        def _new_brake_step(braking, k, dx, lookup_grade_array, speed_limit, kpoint):
            """Simulates one braking step of `dx` meters based on previous state."""
            braking[k][0, 0] = kpoint = braking[k][1, 0] - dx / 1000
            braking[k][0, 1] = dx
            braking[k][0, 5] = grade_equiv(lookup_grade_array, kpoint, 'left')
            braking[k][0, 6] = radius(lookup_grade_array, kpoint)
            braking[k][0, 7] = speed_limit
            braking[k][0, 10] = R_i(braking[k][1, 3], braking[k][0, 5], braking[k][0, 6])
            braking[k][0, 4], braking[k][
                0, 9] = accel_i(braking[k][1, 3], MAX_SPEED, braking[k][0, 10], mode=2)
            braking[k][0, 3] = sqrt((braking[k][1, 3] / 3.6)**2 - 2 * braking[k][0, 4] * dx) * 3.6
            braking[k][0, 2] = dx / ((braking[k][0, 3] + braking[k][1, 3]) / 3.6 / 2)
            return kpoint

        def new_powering_step(output, k, dx, lookup_grade_array, speed_limit, kpoint):
            """Simulates one powering step of `dx` meters based on previous state."""
            output[k][1, 0] = kpoint = output[k][0, 0] + dx / 1000
            output[k][1, 1] = dx
            output[k][1, 5] = grade_equiv(lookup_grade_array, kpoint, 'left')
            output[k][1, 6] = radius(lookup_grade_array, kpoint)
            output[k][1, 7] = speed_limit
            output[k][1, 8] = max_effort(output[k][0, 3], MAX_SPEED, mode=1)
            output[k][1, 10] = R_i(output[k][0, 3], output[k][1, 5], output[k][1, 6])
            output[k][1, 4] = accel_i(output[k][0, 3], MAX_SPEED, output[k][1, 10], mode=1)
            output[k][1, 3] = sqrt((output[k][0, 3] / 3.6)**2 - 2 * output[k][1, 4] * dx) * 3.6
            output[k][1, 2] = dx / ((output[k][1, 3] + output[k][0, 3]) / 3.6 / 2)
            return kpoint

        # TODO:
        def new_cruising_step(output, k, dx, lookup_grade_array, speed_limit, kpoint):
            """Simulates one cruising step of `dx` meters based on previous state."""
            output[k][1, 0] = kpoint = output[k][0, 0] + dx / 1000
            output[k][1, 1] = dx
            output[k][1, 5] = grade_equiv(lookup_grade_array, kpoint, 'left')
            output[k][1, 6] = radius(lookup_grade_array, kpoint)
            output[k][1, 7] = speed_limit
            output[k][1, 10] = R_i(output[k][0, 3], output[k][1, 5], output[k][1, 6])
            output[k][1, 4], output[k][
                1, 8] = accel_i(output[k][0, 3], MAX_SPEED, output[k][1, 10], mode=3)
            output[k][1, 3] = speed_limit
            output[k][1, 2] = dx / ((output[k][1, 3] + output[k][0, 3]) / 3.6 / 2)
            return kpoint

        def main_simulation(lookup_array, lookup_grade_array):
            """
            """
            # braking table calculation
            braking = some_cool_braking_function(lookup_array, lookup_grade_array)
            if braking is not None:
                print(braking)
                return braking
            output = np.zeros((2, 11), dtype=float)
            ROUTE_LENGTH = lookup_array[-1, -1]
            #* Initialize train start up:
            output[0, 0] = kpoint = 0
            output[0, 1] = distance_step = 0
            output[0, 2] = total_time = 0
            output[0, 3] = speed = 0
            output[0, 10] = resistance = R_i(speed, output[0, 6], output[0, 8])
            output[0, 4] = accel_i(speed, MAX_SPEED, resistance, mode=1)
            output[0, 5] = grade_equiv(lookup_grade_array, kpoint, 'right')
            output[0, 6] = radius(lookup_grade_array, kpoint)
            output[0, 7] = speed_limit = lookup_array[1, 3]
            output[0, 8] = max_effort(speed, speed_limit, mode=1)
            print(output)
            k = 0  # check against the upcoming "k" brake array
            print("output : ", output)
            lookup_kpoint = lookup_grade_array[:, -1]
            print("lookup_kpoint: ", lookup_kpoint)
            while kpoint < ROUTE_LENGTH:
                kpoint = output[-1, 0]
                print("kpoint: ", kpoint)
                row = np.searchsorted(lookup_kpoint, kpoint, side="right")
                print("row: ", row)
                # use array without stations to get speed limit
                speed_limit = lookup_grade_array[row, 3]
                #* Every brake array has the same format as output !!
                if kpoint < braking[k][0, 0]:  # still not a target for braking
                    powering_or_cruising(output, speed, speed_limit, row)
                else:  # inside brake target array limits
                    if kpoint > braking[k][0, -1]:
                        # passed the last kpoint in the current brake array
                        if speed < braking[k][0, 3]:
                            continue
                        else:
                            #! slice at searchsorted row
                            #! append the slice
                            #! recalculate previous accel so that speed = brtable speed

                            k += 1

                # 'KP [km]', 0
                # 'Distance step [m]', 1
                # 'Time [s]', 2
                # 'Speed [km/h]', 3
                # 'Acceleration [m/s²]', 4
                # 'Equivalent grade [‰]', 5
                # 'Radius [m]', 6
                # 'Speed restriction [km/h]', 7
                # 'Tractive Effort [kN]', 8
                # 'Braking Effort [kN]', 9
                # 'Resistance [kN]', 10

            return output

        def plot_virtual_speed(output):
            """Show computed virtual max speed profile against the original speed limit."""
            nonlocal dataset_np_original, virtual_speed_array
            dataset_np_original = dataset_np_original.T
            virtual_speed_array = virtual_speed_array.T
            output = output.T

            ax = plt.subplot(111)
            ax.set_title(f"Length of train: {L_TRAIN} m")
            ax.step(
                virtual_speed_array[9],
                virtual_speed_array[3],
                color='black',
                label="Revised speed",
                where="pre",
            )
            ax.scatter(
                output[0],
                output[3],
                color='red',
                s=3,
                label="Braking speed",
            )
            # ax.step(
            #     virtual_speed_array[9],
            #     virtual_speed_array[1],
            #     color='green',
            #     label="Revised grade",
            #     where="pre",
            # )
            # ax.step(
            #     dataset_np_original[9],
            #     dataset_np_original[1],
            #     color='black',
            #     label="Original grade",
            #     where="pre",
            # )
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
            output = output.T

            plt.show()

        # np to pd # TODO use os paths
        parentDirectory = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
        a = pd.DataFrame(data=virtual_speed_array)
        a.to_csv(
            parentDirectory + '/Output_template_COPY_virtual_speed.csv',
            encoding='utf-8-sig',
            float_format='%1.8f',
            index=False,
        )

        column_values = [
            'KP [km]',
            'Distance step [m]',  # computed
            'Time [s]',
            'Speed [km/h]',
            'Acceleration [m/s²]',
            'Equivalent grade [‰]',
            'Radius [m]',
            'Speed restriction [km/h]',
            'Tractive Effort [kN]',
            'Braking Effort [kN]',
            'Resistance [kN]',
        ]

        output = main_simulation(virtual_speed_array, grade_array)
        # *if we were to change braking to a 3d array instead of list of 2d arrays
        # output = np.reshape(output, (output.shape[0] * output.shape[1], output.shape[2]))
        output = np.vstack(output)
        plot_virtual_speed(output)

        def export_output(output):
            b = pd.DataFrame(data=output, columns=column_values)
            b.to_csv(
                parentDirectory + '/Output_template_COPY_output.csv',
                encoding='utf-8-sig',
                float_format='%1.8f',
                index=False,
            )

        export_output(output)

        def target_brake():
            """Determines where the braking algorithm should be called, 
            to avoid continuous execution.
            Returns a list containing kpoints and corresponding steps."""

        # Initialize solution array
        # output = np.zeros()
        # Array to be hstacked after each iteration
        # array_to_stack = np.array[total_time(), ]

        def traction_mode(lookup_array, kpoint):
            traction_mode_is_electric_AC = 0
            traction_mode_is_electric_DC = 0
            traction_mode_is_diesel = 0
            traction_mode_is_battery = 0


##########     ndarray to dataframe      #############
######################################################

# # TODO: REPLACE WITH output
# myarray = np.empty((0, len(column_values)), dtype=float)
# myarray = np.vstack((myarray, np.linspace(0, 40, len(column_values))))
# myarray = np.vstack((myarray, 2 * myarray))

# parentDirectory = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
# a = pd.DataFrame(data=myarray, columns=column_values)
# a.to_csv(
#     parentDirectory + '/Output_template_COPY_pandas.csv',
#     encoding='utf-8-sig',
#     float_format='%1.8f',
#     index=False,
# )
ShortestOperationSolver(None, C)
