from operator import and_
from PyQt5 import QtWidgets as qtw
import numpy as np
from numpy.core.function_base import add_newdoc
import pandas as pd
import os
import sys
import matplotlib.pyplot as plt

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from solver.data_formatter import s_to_hhmmss, hhmm_to_s, effort_curve_to_arrays

# ! only wrap "basic" functions around njit
from numba import jit, njit

# import sys
# print("getrecursionlimit", sys.getrecursionlimit())
# sys.setrecursionlimit(90000)

from fn import recur


def ShortestOperationSolver(window, constants):
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
    # * Calculate virtual speed based on rolling stock length
    L_TRAIN = 290

    def rolling_R(speed):
        """Returns the current Rolling resistance. Args: Speed [km/h], Static mass [t]"""
        R = constants['ROLLING_R_A'] * MASS_STATIC * 9.81 + \
            constants['ROLLING_R_B'] * MASS_STATIC * 9.81 * speed + \
            constants['ROLLING_R_C'] * speed**2
        return R

    # TODO: use grade_equiv() instead of grade
    def grade_R(grade):
        """Returns the current Grade resistance. Args: Grade [‰]"""
        R = MASS_STATIC * 9.81 + grade / 1000
        return R

    def curve_R(radius):
        """Returns the current Curve resistance. Args: Radius [m]"""
        R = 0 if not radius else MASS_STATIC * 4.9 * constants['TRACK_GAUGE'] / abs(radius)
        return R

    # TODO: resistance based on current distance step
    def total_R(row):
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
        MASS_EQUIV = constants['MASS_STATIC_LOCO'] * (1 + constants['LOCO_ROT_MASS']) + constants[
            'MASS_STATIC_WAG'] * (1 + constants['WAG_ROT_MASS'])

    #* Passenger train simulation
    if constants['gb_passenger']:
        L_TRAIN = constants['TRAIN_LENGTH']
        MASS_STATIC = constants['TRAIN_MASS']
        MASS_EQUIV = constants['TRAIN_MASS'] * (1 + constants['TRAIN_ROT_MASS'])
    # copy array to track, assigning to it is useless since we edit the dataset
    dataset_np_original = np.copy(dataset_np)

    def speed_grabber(array, row, step):
        """Returns a list of speeds contained in [kpoint(row), kpoint(row)+step] meters.
        Used to determine the minimum speed when step=L_TRAIN"""
        kpoint = np.cumsum(array[row, 0] / 1000, dtype=float)
        limit = kpoint + step
        speed_set = set()
        speed_set.add(array[row, 3])
        total_rows, _ = array.shape
        if step > 0:
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
        else:
            return array[row, 3]
        return speed_set

    @recur.tco  # Tail-Call Optimization
    def speed_from_length(array, row=0, length=L_TRAIN, speed_accum=None, distance_accum=None):
        """Calculates the speed which ensures that the last point in the train complies with
        the speed limit"""
        # TODO: remove redundancies
        total_rows, _ = array.shape
        if row >= total_rows - 1: return False, array  # last executed line
        if row < total_rows - 1:
            distance_step = array[row, 0]
            speed = array[row, 3]
            next_speed = array[row + 1, 3]
            next_distance_step = array[row + 1, 0]

            if distance_step == 0:  # ? This is a station
                # go to next step
                return True, (array, row + 1, L_TRAIN)
            else:
                if next_speed <= speed:
                    # braking will be handled later in code
                    # go to next step with L_TRAIN as offset
                    return True, (array, row + 1, L_TRAIN)
                else:  # ? next_speed > speed
                    if next_distance_step >= length:
                        # array = np.insert(array, row+1, array[row+1], axis=0)
                        # duplicate the next row
                        array = np.concatenate(
                            (array[:row + 1], array[row + 1, None], array[row + 1:]), axis=0
                        )
                        # speed_accum = array[row, 3]
                        min_speed = min(speed, *speed_grabber(array, row, length))
                        array[row + 1, 3] = min_speed
                        array[row + 1, 0] = length
                        array[row + 2, 0] = next_distance_step - length
                        # There is accumulated length and next step is larger
                        if distance_accum and distance_accum < array[row + 2, 0]:
                            array = np.concatenate(
                                (array[:row + 2], array[row + 2, None], array[row + 2:]), axis=0
                            )
                            array[row + 2, 3] = speed_accum
                            array[row + 2, 0] = distance_accum
                            array[row + 3, 0] -= distance_accum
                            # skip the 2 inserted rows
                            return True, (array, row + 3, L_TRAIN, speed_accum)
                        # skip the inserted row
                        return True, (array, row + 2, L_TRAIN, speed_accum)
                    else:  # ? next_distance_step < length
                        min_speed = min(speed_grabber(array, row, length))
                        if not speed_accum or speed_accum is None:
                            speed_accum = np.copy(array)[row + 1, 3]  # keep ref to previous speed
                        distance_accum = next_distance_step
                        # Assign the minimum speed
                        array[row + 1, 3] = min_speed
                        # check the next step, but using the remaining length
                        return True, (
                            array, row + 1, length - distance_accum, speed_accum, distance_accum
                        )

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
            Diesel_T_speed, Diesel_T_effort = effort_curve_to_arrays(constants['D_TELoadFilename'])
            Diesel_B_speed, Diesel_B_effort = effort_curve_to_arrays(constants['D_BELoadFilename'])
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
                window, "Error", "Could not load Electric traction - speed curve data: " + str(e)
            )

    def grade_equiv(current_kpoint, row):
        """
        Backwards search to define the equivalent grade based on train length.
        current_kpoint: accumulated distance until front of train.
        row: current distance_step

        #* The current kpoint has to be retrieved from the output array based
        #* on the actual simulation accumulated distance.

        #* In order to use this function to calculate max previous speed 
        #* based on braking ability, use current_kpoint = array[row,-1] in args
        #* ensuring kpoint is vstacked before to the array 
        """
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

    # TODO:
    #* Check if dynamic inputs are needed first ! (R(u), T(u), B(u))
    # def speed_from_brake():
    #     """
    #     Defines maximum speed based on braking capability.
    #     """

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


# constants = dict(
#     [('ProfileLoadFilename', "C:/Users/danic/MyPython/RailwaySim/Input_template - Long.csv")]
# )
# print(ShortestOperationSolver(None, constants))

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

# # column names, (1,...,n by default)
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
#     'Speed restriction [km/h]',
#     'Virtual speed limit [km/h]',
#     'Tractive Effort [kN]',
#     'Braking Effort [kN]',
#     'Resistance [kN]',
#     'Regeneration max power [kW]',
#     'AC line',
#     'DC line',
#     'Diesel mode',
#     'Battery mode',
# ]

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