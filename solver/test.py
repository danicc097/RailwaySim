# import numpy as np

# ini_array = np.array([['a', 'b', 'c'], ['d', 'e', 'f'], ['g', 'h', 'i']])

# print("initial_array : ", ini_array)

# # Array to be added as column
# column_to_be_added = np.array([1, 2, 3])

# # Adding column to numpy array
# result = np.hstack((ini_array, np.atleast_2d(column_to_be_added).T))

# # Adding row to numpy array
# result2 = np.stack((ini_array, (column_to_be_added).T))

# print("resultant array hstack", result)
# print("resultant array vstack", result2)

# def namelist(names):
#     output = ""

#     for i in range(len(names)):
#         if i == 0:
#             output += names[i]['name']
#         elif i == len(names) - 1:
#             output += " & " + names[i]['name']
#         else:
#             output += ", " + names[i]['name']

#     return output

# namelist1 = [{'name': 'Bart'}, {'name': 'Lisa'}, {'name': 'Maggie'}]
# print(namelist(namelist1))