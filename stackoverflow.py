import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FixedFormatter
from matplotlib.widgets import CheckButtons
x_axis1 = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 5.5, 6.0, 10.5, 15.0, 15.5]
y_axis1 = [60.0, 80.0, 70.0, 60.0, 70.0, 50.0, 80.0, 100.0, 80.0, 60.0, 50.0]
x_axis2 = [0.0, 2.8, 10.4, 15.6]
y_axis2 = ['First Station', 'Second Station', 'Third Station', 'Last station']

fig, ax = plt.subplots()

ax.set_xlabel("Distance [km]")
ax.set_ylabel("Speed [km/h]")
l0, = ax.step(x_axis1, y_axis1, label="Speed", where="post")
ax2 = ax.twiny()
ax2.set_xlim(ax.get_xlim())
ax2.set_label('Stations')
ax2.tick_params(
    axis="x",
    which='major',
    direction="in",
    width=1.5,
    length=7,
    labelsize=10,
    color="red",
    rotation=60
)
x_locator = FixedLocator(x_axis2)
x_formatter = FixedFormatter(y_axis2)
ax2.xaxis.set_major_locator(
    x_locator
)  # it's best to first set the locator and only then the formatter
ax2.xaxis.set_major_formatter(x_formatter)
# ? optionally add vertical lines at each of the station positions
for x in x_axis2:
    ax2.axvline(x, color='red', ls=':', lw=1.5)

lines = [l0, ax2]
rax = plt.axes([0, 0, 0.12, 0.1])
labels = [str(line.get_label()) for line in lines]
visibility = [line.get_visible() for line in lines]
check = CheckButtons(rax, labels, visibility)


def func(label):
    index = labels.index(label)
    lines[index].set_visible(not lines[index].get_visible())
    plt.draw()


check.on_clicked(func)

fig.tight_layout()

plt.show()