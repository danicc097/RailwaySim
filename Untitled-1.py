from solver.data_formatter import hhmm_to_s
import numpy as np

row = 0
array = np.array(([1, 2, 3], [4, 5, 6], [7, 8, 9]))
# array = np.insert(array, row, array[row], axis=0)
# array = np.concatenate((array[:row], array[row, None], array[row:]), axis=0)

array = np.concatenate((array[:row + 1], array[row + 1, None], array[row + 1:]), axis=0)
print(array)
