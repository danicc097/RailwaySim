import numpy as np
import pandas as pd
import os
import sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from solver.data_formatter import s_to_hhmmss, hhmm_to_s


def run(settings):

    with open('RailwaySim/Input_template.csv', mode='r', encoding='utf-8-sig') as f:
        dataset_np = np.genfromtxt(
            'RailwaySim/Input_template.csv',
            delimiter=',',
            dtype=float and str,
            encoding='utf-8-sig',
            autostrip=True,
            deletechars=""
        )

    dataset_np = dataset_np.T
    time_sec = np.array(np.linspace(0, int(len(dataset_np[0][1:]) / 2), num=len(dataset_np[0][1:])))
    time_hours = np.array([s_to_hhmmss(a) for a in time_sec])
    distance = np.array([float(a) for a in dataset_np[3][1:] if a != ""])
    kpoint = np.cumsum(distance / 1000, dtype=float)
    grade = np.array([float(a) for a in dataset_np[4][1:] if a != ""])
    radius = np.array([float(a) for a in dataset_np[5][1:] if a != ""])
    speed_res = np.array([float(a) for a in dataset_np[6][1:] if a != ""])
    station_names = np.array([str(a) for a in dataset_np[12][1:]])
    print(time_sec)
    print(distance)
    print(grade)
    print(radius[3])
    print(speed_res[3])
    print(station_names[-1])

    # creating the Numpy array
    myarray = np.empty((0, 7), dtype=float)
    #myarray = np.array([time_sec, time_hours, distance, kpoint, grade, radius, speed_res]).T
    myarray = np.vstack((myarray, [1, 2, 3, 4, 5, 6, 7]))
    print(myarray[0, 2])
    myarray = np.vstack((myarray, [1, myarray[0, 1] * 5, 3, 4, 5, 6, 7]))

    #index_values = ['first', 'second'] # index names ("row headers")

    # column names
    column_values = [
        'Time [s]',
        'Time [hh:mm:ss]',
        'Distance step [m]',
        'KP [km]',
        'Grade [‰]',
        'Profile [m]',
        'Radius [m]',
        'Speed restriction [km/h]',
        'Speed [km/h]',
        'Virtual speed limit [km/h]',
        'Acceleration [m/s²]',
        'Tractive Effort [kN]',
        'Braking Effort [kN]',
        'Resistance [kN]',
        # 'Regeneration max power [kW]',
        # 'AC line',
        # 'DC line',
        # 'Diesel mode',
        # 'Battery mode',
    ]

    # np to pd # TODO use os paths

    parentDirectory = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    a = pd.DataFrame(data=myarray, columns=column_values[:7])
    a.to_csv(
        parentDirectory + '/Output_template_COPY.csv',
        encoding='utf-8-sig',
        float_format='%1.8f',
        index=False,
    )

    # # ! Copy template and dump to CSV
    # def copy_csv(filename):
    #     df = pd.read_csv(filename, encoding='utf-8-sig')
    #     df.to_csv('RailwaySim/Output_template_COPY.csv', encoding='utf-8-sig')
    #     pd.DataFrame(a).to_csv(
    #         'RailwaySim/Output_template_COPY.csv',
    #         mode='a',
    #         sep=",",
    #         header=False,
    #         encoding='utf-8-sig',
    #         float_format='%1.8f',
    #         index=False,
    #     )
    # copy_csv('RailwaySim/Output_template.csv')

    print('Simulation ended successfully.')