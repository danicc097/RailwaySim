import numpy as np
from numpy.core.records import array
import pandas as pd

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
distance = tuple([float(a) for a in dataset_np[3][1:] if a != ""])
grade = tuple([float(a) for a in dataset_np[4][1:] if a != ""])
radius = tuple([float(a) for a in dataset_np[5][1:] if a != ""])
speed_res = tuple([float(a) for a in dataset_np[6][1:] if a != ""])
station_names = tuple([str(a) for a in dataset_np[12][1:]])
print(distance[3])
print(grade[3])
print(radius[3])
print(speed_res[3])
print(station_names)

# ! Dump to CSV
# a = numpy.asarray([[2341.43243, 2, 3], [4, 5, 6], [7, 8, 9]])
# numpy.savetxt("foo.csv", a, delimiter=",", encoding='utf-8', fmt='%1.8f')
