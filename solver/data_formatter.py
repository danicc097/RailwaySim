import numpy as np
from numpy.core.arrayprint import dtype_is_implied
from numpy.core.records import array

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
print(dataset_np)
print('*' * 90)
# listcomp removes empty last row
x_axis1 = tuple([float(a) for a in dataset_np[8][1:] if a != ""])  # Speed limitation
y_axis1 = tuple([float(a) for a in dataset_np[9][1:] if a != ""])
x_axis2 = tuple([float(a) for a in dataset_np[0][1:] if a != ""])  # Stations
y_axis2 = tuple([str(a) for a in dataset_np[1][1:] if a != ""])
x_axis3 = tuple([float(a) for a in dataset_np[4][1:] if a != ""])  # Grade
y_axis3 = tuple([float(a) for a in dataset_np[5][1:] if a != ""])
x_axis4 = tuple([float(a) for a in dataset_np[6][1:] if a != ""])  # Radius
y_axis4 = tuple([float(a) for a in dataset_np[7][1:] if a != ""])

#Grade = set(x_axis3)
#print(Grade)
# Grade = set(x_axis3)
# print(Grade)
#print(x_axis3)
isol_paths = np.array(x_axis2, dtype=None)
isol_paths2 = np.array(y_axis2, dtype=None)

isol_paths = np.insert(isol_paths, isol_paths2, axis=1)
print(isol_paths)
idx = isol_paths.searchsorted(x_axis3, side='right')
print(idx)
isol_paths = np.insert(isol_paths, idx, x_axis3, axis=0)
print(isol_paths)
#*1 Create new array

#*2 Create new array
"""
Bisection:
>>> def grade(score, breakpoints=[60, 70, 80, 90], grades='FDCBA'):
...     i = bisect(breakpoints, score)
...     return grades[i]
...
>>> [grade(score) for score in [33, 99, 77, 70, 89, 90, 100]]
['F', 'A', 'C', 'C', 'B', 'A', 'A']
"""