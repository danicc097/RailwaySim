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

L_TRAIN = 100


def grade_equiv(current_kpoint, row):
    """
    Backwards search to define the equivalent grade based on train length.
    :parameters:
    current_kpoint: accumulated distance until front of train.
    row: current distance_step
    """
    grade_steps = []
    accum_length = 0

    while accum_length < L_TRAIN:
        distance_step = 40
        grade = 10
        # The current kpoint has to be retrieved from the output array based
        # on the actual simulation accumulated distance.
        # In order to use this function to calculate max previous speed
        # based on braking ability, use current_kpoint = previous_kpoint in args
        current_kpoint = 12050
        # with kpoint vstacked before to original array
        previous_kpoint = 12000
        previous_distance_step = 300
        previous_grade = 30
        if L_TRAIN < previous_distance_step and L_TRAIN - accum_length > 0:
            accum_length = L_TRAIN
        else:
            accum_length += previous_distance_step
            row -= 1
        grade_steps.append(accum_length * previous_grade)
    return sum(grade_steps) / L_TRAIN


print(grade_equiv(None, 5))
