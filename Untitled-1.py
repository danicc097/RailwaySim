from solver.data_formatter import hhmm_to_s
import numpy as np
from numba import njit, jit, jitclass

# @jitclass
# class compute(object):
#     def __init__(self):
#         self.ROUTE_INPUT_DF = np.genfromtxt(
#             "C:/Users/danic/MyPython/RailwaySim/Input_template - Long.csv",
#             delimiter=',',
#             dtype=str,
#             encoding='utf-8-sig',
#             autostrip=True,
#             deletechars="",
#         )

#         self.ROUTE_INPUT_DF = self.ROUTE_INPUT_DF.T

#         # try:
#         self.numba_compute()
#         # self.plot_route()

#     @jit(nopython=True)
#     def numba_compute(self):
#         self.distance = np.array(self.ROUTE_INPUT_DF[3][1:], dtype=float)
#         self.kpoint = np.cumsum(self.distance / 1000, dtype=float)
#         self.grade = np.array(self.ROUTE_INPUT_DF[4][1:], dtype=float)
#         self.radii = np.array(self.ROUTE_INPUT_DF[5][1:], dtype=float)
#         self.speed_res = np.array(self.ROUTE_INPUT_DF[6][1:], dtype=float)
#         self.station_names = np.array(self.ROUTE_INPUT_DF[12][1:], dtype=str)

#         #* Initialize profile array
#         self.profile = np.zeros(len(self.distance), dtype=float)

#         #* Calculate profile height from distance steps and grade
#         for index, distance_step in enumerate(self.distance):

#             if index < 1:
#                 self.profile[index] = 0
#             else:
#                 self.profile[
#                     index] = distance_step * self.grade[index] / 1000 + \
#                         self.profile[index-1]
#         # * Timetable
#         self.timetable_stations = np.array([str(a) for a in self.ROUTE_INPUT_DF[0][1:] if a != ""])
#         # * Find station kilometric points (0 m travelled paths)
#         self.timetable_stations_kpoint = np.array(
#             [self.kpoint[index] for index, a in enumerate(self.distance) if a == 0]
#         )
#         # * Optional timetable
#         try:
#             self.timetable_dwell_time = np.array(
#                 [int(a) for a in self.ROUTE_INPUT_DF[1][1:] if a != ""]
#             )
#         except:
#             self.timetable_dwell_time = None
#         # * Optional timetable
#         try:
#             self.timetable_arrival_time = np.array(
#                 [hhmm_to_s(a) for a in self.ROUTE_INPUT_DF[2][1:] if a != ""]
#             )
#         except:
#             self.timetable_arrival_time = None

# @jitclass(float)
# class compute(object):
#     @jit(nopython=True)
#     def __init__(self):

#         self.test = [x * y for x in range(10) for y in range(10)]

# a = compute()
# print(a.test1)

# import random

# @jit(nopython=True)
# def spherical_to_cartesian(r, theta, phi):
#     '''Convert spherical coordinates (physics convention) to cartesian coordinates'''
#     sin_theta = np.sin(theta)
#     x = r * sin_theta * np.cos(phi)
#     y = r * sin_theta * np.sin(phi)
#     z = r * np.cos(theta)

#     return x, y, z  # return a tuple

# @jit(nopython=True)
# def random_directions(n, r):
#     '''Return ``n`` 3-vectors in random directions with radius ``r``'''
#     out = np.empty(shape=(n, 3), dtype=np.float64)

#     for i in range(n):
#         # Pick directions randomly in solid angle
#         phi = random.uniform(0, 2 * np.pi)
#         theta = np.arccos(random.uniform(-1, 1))
#         # unpack a tuple
#         x, y, z = spherical_to_cartesian(r, theta, phi)
#         out[i] = x, y, z

#     return out

# print(random_directions(10, 1.0))
row = 0
array = np.array(([1, 2, 3], [4, 5, 6], [7, 8, 9]))
# array = np.insert(array, row, array[row], axis=0)
# array = np.concatenate((array[:row], array[row, None], array[row:]), axis=0)

array = np.concatenate((array[:row + 1], array[row + 1, None], array[row + 1:]), axis=0)
print(array)
