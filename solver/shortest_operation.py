"""

1. First convert radii to speed.
2. Virtual speed Table based on Train length L:
    for i in table rows:
     (1)if speed_i+1 <= speed_i:
            continue next row
        if speed_i+1 > speed_i:
            if l_path > L:
                duplicate row BEFORE current i (else loop fails?)
                assign speed_i   to the new row with distance step = L
                assign speed_i+1 to current row with distance step = l_path - L
                continue next row
            if l_path == L:
                assign speed_i to row
                continue next row
            if l_path < L:
                assign speed_i to row
                [[(recursion from (1), but with L=L-l_path, i+1)]]
                (1)if speed_i+1 <= speed_i:
                    continue next row
                if speed_i+1 > speed_i:
                    if l_path > L:
                        duplicate row BEFORE current i (else loop fails?)
                        assign speed_i   to the new row with distance step = L
                        assign speed_i+1 to current row with distance step = l_path - L
                        continue next row
                    if l_path == L:
                        assign speed_i to row
                        continue next row
                    if l_path < L:

    Virtual speed Table based on Train length L:
    L_train = constants['LOCO_LENGTH'] if constants['gb_locomotive'] else constants['TRAIN_LENGTH']
    def speed_from_length(row=0, array, length=L_train):
        distance_step=array[row,0]
        grade=array[row,2]
        speed=array[row,4]

        
        speed_from_length(i, l_path, L)
    


"""

from PyQt5 import QtWidgets as qtw
import numpy as np
import pandas as pd
import os
import sys
from numba import jit, njit
import matplotlib.pyplot as plt

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from solver.data_formatter import s_to_hhmmss, hhmm_to_s, effort_curve_to_arrays
# ! only wrap "basic" functions around njit

# import sys
# print("getrecursionlimit", sys.getrecursionlimit())
# sys.setrecursionlimit(90000)

from fn import recur


def ShortestOperationSolver(window, constants):
    # print(constants)
    # print(constants['LOCO_AXLES'])
    dataset_np = np.genfromtxt(
        "C:/Users/danic/MyPython/RailwaySim/Input_template - 300k rows.csv",  # constants['ProfileLoadFilename']
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
    # L_train = constants['LOCO_LENGTH'] if constants['gb_locomotive'] else constants['TRAIN_LENGTH']

    L_train = 200
    # copy array to track, assigning to it is useless since we edit the dataset
    dataset_np_original = np.copy(dataset_np)

    @recur.tco  # Tail-Call Optimization
    def speed_from_length(array, row=0, length=L_train, speed_to_check=0):
        """Calculates the speed which ensures that the last point in the train complies with
        the speed limit"""
        # TODO: remove redundancies
        total_rows, _ = array.shape
        if row >= total_rows - 1: return False, array  # last executed line
        if row < total_rows - 1:
            distance_step = array[row, 0]
            if not speed_to_check: speed = array[row, 3]
            else: speed = speed_to_check
            next_speed = array[row + 1, 3]
            next_distance_step = array[row + 1, 0]
            if distance_step == 0:  # ? This is a station
                # go to next step
                return True, (array, row + 1, L_train)
            else:
                if next_speed <= speed:
                    # braking will be handled later in code
                    # go to next step with L_train as offset
                    return True, (array, row + 1, L_train)
                else:  # ? next_speed > speed
                    if next_distance_step > length:
                        # array = np.insert(array, row+1, array[row+1], axis=0)
                        # duplicate the next row
                        array = np.concatenate(
                            (array[:row + 1], array[row + 1, None], array[row + 1:]), axis=0
                        )
                        array[row + 1, 3] = speed
                        array[row + 1, 0] = length
                        array[row + 2, 0] = next_distance_step - length
                        speed_to_check = array[row + 2, 3]
                        # skip the inserted row on the next check
                        return True, (array, row + 2, L_train, speed_to_check)
                    elif next_distance_step == length:
                        # replace speed
                        speed_to_check = next_speed
                        array[row + 1, 3] = speed
                        # check the next step but with the original speed from next row
                        return True, (array, row + 1, L_train, speed_to_check)
                    else:  # ? next_distance_step < length
                        # replace speed if
                        speed_to_check = next_speed
                        array[row + 1, 3] = speed
                        # check the next step, but using the remaining length
                        return True, (array, row + 1, length - next_distance_step)

    array = speed_from_length(dataset_np)
    dataset_np_original = dataset_np_original.T
    array = array.T

    dataset_np_original = np.vstack(
        (dataset_np_original, np.cumsum(dataset_np_original[0] / 1000, dtype=float))
    )
    array = np.vstack((array, np.cumsum(array[0] / 1000, dtype=float)))

    # ax = plt.subplot(111)
    # ax.set_title(L_train)
    # ax.step(dataset_np_original[9], dataset_np_original[3], label="old array", where="pre")
    # ax.step(array[9], array[3], color='red', label="new array", where="pre")
    # ax.legend()

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

    # plt.show()

    Diesel_T_speed, Diesel_T_effort = effort_curve_to_arrays(
        'C:/Users/danic/MyPython/RailwaySim/Input_BE.csv'
    )

    print(len(Diesel_T_speed))
    print(len(Diesel_T_effort))

    # #* Maximum effort based on speed (diesel)
    # if constants['gb_diesel_engine'] == True:
    #     try:
    #         Diesel_T_speed, Diesel_T_effort = effort_curve_to_arrays(constants['D_TELoadFilename'])
    #         Diesel_B_speed, Diesel_B_effort = effort_curve_to_arrays(constants['D_BELoadFilename'])
    #     except Exception as e:
    #         return qtw.QMessageBox.critical(
    #             window, "Error", "Could not load Diesel traction - speed curve data: " + str(e)
    #         )
    # #* Maximum effort based on speed (electric)
    # if constants['gb_electric_traction'] == True:
    #     try:
    #         Electric_T_speed, Electric_T_effort = effort_curve_to_arrays(
    #             constants['E_TELoadFilename']
    #         )
    #         Electric_B_speed, Electric_B_effort = effort_curve_to_arrays(
    #             constants['E_BELoadFilename']
    #         )
    #     except Exception as e:
    #         return qtw.QMessageBox.critical(
    #             window, "Error", "Could not load Electric traction - speed curve data: " + str(e)
    #         )
    # TODO: get current max effort from curve
    # np.interp(2.5, xp, fp)


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
#     'Grade [‰]',
#     'Profile [m]',
#     'Radius [m]',
#     'Speed restriction [km/h]',
#     'Speed [km/h]',
#     'Virtual speed limit [km/h]',
#     'Acceleration [m/s²]',
#     'Tractive Effort [kN]',
#     'Braking Effort [kN]',
#     'Resistance [kN]',
#     # 'Regeneration max power [kW]',
#     # 'AC line',
#     # 'DC line',
#     # 'Diesel mode',
#     # 'Battery mode',
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

ShortestOperationSolver(None, None)