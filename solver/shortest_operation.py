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
        distance_step=array[row,3]

        
        speed_from_length(i, l_path, L)
    
dataset
[['0'   '0' '0' ... '0' '0' 'Station 1'],
 ['400' '0' '0' ... '0' '0'          ''],
 ...]





"""
from PyQt5 import QtWidgets as qtw
import numpy as np
import pandas as pd
import os
import sys
from numba import jit, njit
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from solver.data_formatter import s_to_hhmmss, hhmm_to_s, effort_curve_to_arrays
from save_restore import grab_GC

# ! only wrap "basic" functions around njit


def ShortestOperationSolver(window, constants):
    # print(constants)
    # print(constants['LOCO_AXLES'])
    dataset_np = np.genfromtxt(
        constants['ProfileLoadFilename'],
        delimiter=',',
        dtype=float and str,
        encoding='utf-8-sig',
        autostrip=True,
        deletechars=""
    )
    dataset_np = dataset_np[1:, 3:]
    print(dataset_np)
    print(type(constants['gb_locomotive']))
    L_train = constants['LOCO_LENGTH'] if constants['gb_locomotive'] else constants['TRAIN_LENGTH']
    print(L_train)
    if constants['gb_diesel_engine'] == True:
        try:
            #* Maximum effort based on speed (diesel)
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

# # column names
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
