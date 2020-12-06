#%% #!###################
import numpy as np

array = np.array(([1, 2, 3, 4, 5], [0, 0, 0, 0, 0]))
array2 = np.array(([9, 8, 7, 6], [0, 0, 0, 0]))
array[0, 2:4] = array2[0, 0:2]
print(array)
#%% #!###################
import numpy as np
import matplotlib.pyplot as plt
x = np.linspace(-2, 2, 81)
y = np.exp(-0.5 * x**2) * np.cos(np.pi * x)
print(x.dtype)
print(y.dtype)
plt.plot(x, y)
plt.show()
#%% #!###################
import numpy as np
import pandas as pd
import csv

with open('input_template.csv', mode='r', encoding='utf-8-sig') as f:
    dataset = list(csv.reader(f))
# header, values = dataset[0], dataset[1:]
data_np = np.asarray(dataset).T
print(data_np)

#%% #!###################
from matplotlib.pyplot import xticks
import numpy as np
locs, labels = xticks()  # Get the current locations and labels.
xticks(np.arange(0, 1, step=0.2))  # Set label locations.
xticks(np.arange(3), ['Tom', 'Dick', 'Sue'])  # Set text labels.
#xticks([0, 1, 2], ['January', 'February', 'March'], rotation=20)  # Set text labels and properties.
# xticks([])  # Disable xticks.
# %%
import matplotlib.pyplot as plt

x = np.linspace(0, 10, 100)
y = np.sin(x)

fig, ax = plt.subplots(
    nrows=1, ncols=1
)  # This is saying you'll have 1 row and 1 column of subplots (so just 1 plot)

ax.scatter(x, y, c='red', s=10)
ax.set_xlabel('X Values')
ax.set_ylabel('Y Values')
ax.set_ylim(bottom=-0.75, top=0.75)

plt.show()
# %%
fig, axes = plt.subplots(nrows=3, ncols=2)
fig.set_size_inches(12, 12)

x = np.linspace(0, 10, 100)
y = np.sin(x)

colors = ['red', 'black', 'blue', 'green', 'yellow', 'purple']

for index, ax in enumerate(axes.flatten()):
    ax.scatter(x, y, c=colors[index])

axes[2, 1].set_title('Title')
axes[0, 1].set_xlabel('X Label')
plt.show()
# %%
fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2)

ax1.scatter(x, y, c='blue')
ax2.hist(y)

plt.show()

# %%
# def selectionSort(array: list):
#     array_length = len(array)  # this just stores the length of the given list
#     _index = 0  # this takes care of dynamically changing the index in which a minimum value is to be found

#     for i in array:
#         min_value = min(array[_index:array_length])
#         print("min: ", min_value)
#         print("i:", i)
#         print(array)
#         if i == min_value:  # if i is the minimum value then do nothing, however update _index
#             print("i is min")
#         else:  # if i is not the minimum value....
#             array[array.index(min_value)], array[_index] = i, min_value
#         _index += 1  # don'f forget to update _index
#     return array

# selectionSort([5, 2, 3, 9, 8, 7])
# %%
