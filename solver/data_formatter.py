import numpy as np
import matplotlib.pyplot as plt


def effort_curve_to_arrays(path):
    """Returns speed, effort as ndarrays from a given path."""
    if path == "" or path is None:
        return (None, None)

    curve = np.genfromtxt(
        path,
        delimiter=',',
        dtype=str,
        encoding='utf-8-sig',
        autostrip=True,
        deletechars="",
    )
    curve = curve.T
    speed = np.array(curve[0][1:], dtype=float)
    effort = np.array(curve[1][1:], dtype=float)
    return (speed, effort)


def hhmm_to_s(time):
    """Convert hh:mm to seconds"""
    h, m = time.split(':')
    return int(h) * 3600 + int(m) * 60


def hhmmss_to_s(time):
    """Convert hh:mm:ss to seconds"""
    h, m, s = time.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)


def s_to_hhmmss(seconds):
    """Convert seconds to hh:mm:ss."""
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    return "%d:%02d:%02d" % (hour, minutes, seconds)


def get_text_positions(x_data, y_data, txt_width, txt_height):
    """Get plot tick labels to check for collision."""
    a = list(zip(y_data, x_data))
    text_positions = y_data.copy()
    for index, (y, x) in enumerate(a):
        local_text_positions = [
            i for i in a
            if i[0] > (y - txt_height) and (abs(i[1] - x) < txt_width * 2) and i != (y, x)
        ]
        if local_text_positions:
            sorted_ltp = sorted(local_text_positions)
            if abs(sorted_ltp[0][0] - y) < txt_height:  #True == collision
                differ = np.diff(sorted_ltp, axis=0)
                a[index] = (sorted_ltp[-1][0] + txt_height, a[index][1])
                text_positions[index] = sorted_ltp[-1][0] + txt_height
                for k, (j, m) in enumerate(differ):
                    #j is the vertical distance between words
                    if j > txt_height * 2:  #if True then room to fit a word in
                        a[index] = (sorted_ltp[k][0] + txt_height, a[index][1])
                        text_positions[index] = sorted_ltp[k][0] + txt_height
                        break
    return text_positions


def text_plotter(x_data, y_data, text_positions, axis, txt_width, txt_height):
    """Changes label text location and adds arrow if there's a collision."""
    for x, y, t in list(zip(x_data, y_data, text_positions)):
        axis.text(x - txt_width, 1.01 * t, '%d' % int(y), rotation=0, color='blue')
        if y != t:
            axis.arrow(
                x,
                t,
                0,
                y - t,
                color='red',
                alpha=0.3,
                width=txt_width * 0.1,
                head_width=txt_width,
                head_length=txt_height * 0.5,
                zorder=0,
                length_includes_head=True
            )


# import matplotlib.pyplot as plt
# from matplotlib.ticker import FixedLocator, FixedFormatter
# from matplotlib.widgets import CheckButtons
# x_axis1 = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 5.5, 6.0, 10.5, 15.0, 15.5]
# y_axis1 = [60.0, 80.0, 70.0, 60.0, 70.0, 50.0, 80.0, 100.0, 80.0, 60.0, 50.0]
# x_axis2 = [0.0, 0.3, 0.6, 0.9]
# y_axis2 = [" " * 10 + 'First Station', ' ' * 5 + 'Second Station', 'Third Station', 'Last station']
# fig, ax = plt.subplots()

# ax.set_xlabel("Distance [km]")
# ax.set_ylabel("Speed [km/h]")
# l0, = ax.step(x_axis1, y_axis1, label="Speed", where="post")

# #* Twin axis y 2
# ax2 = ax.twiny()
# ax2.set_xlim(ax.get_xlim())
# ax2.set_label('Stations')

# # See https://matplotlib.org/3.3.3/api/text_api.html#matplotlib.text.Text
# ax2.tick_params(
#     axis="x",
#     which='major',
#     direction="in",
#     width=1.5,
#     length=7,
#     labelsize=10,
#     color="red",
#     rotation=60,
#     # linespacing=2.4,
# )

# x_locator = FixedLocator(x_axis2)
# x_formatter = FixedFormatter(y_axis2)
# ax2.xaxis.set_major_locator(
#     x_locator
# )  # it's best to first set the locator and only then the formatter
# ax2.xaxis.set_major_formatter(x_formatter)
# # ? optionally add vertical lines at each of the station positions
# for x in x_axis2:
#     ax2.axvline(x, color='red', ls=':', lw=1.5)

# #set the bbox for the text. Increase txt_width for wider text.
# txt_height = 0.04 * (plt.ylim()[1] - plt.ylim()[0])
# txt_width = 0.02 * (plt.xlim()[1] - plt.xlim()[0])
# #Get the corrected text positions, then write the text.
# y_axis2 = [max(ax.get_ylim()) for i in y_axis2]
# # text_positions = get_text_positions(x_axis2, y_axis2, txt_width, txt_height)
# # text_plotter(x_axis2, y_axis2, text_positions, ax, txt_width, txt_height)

# # plt.ylim(0, max(text_positions) + 2 * txt_height)
# # plt.xlim(-0.1, 1.1)

# locs, labels = plt.xticks()
# print(locs)
# print(labels)

# # * Edit lines for each new axis
# lines = [l0]
# rax = plt.axes([0, 0, 0.12, 0.1])
# labels = [str(line.get_label()) for line in lines]
# visibility = [line.get_visible() for line in lines]
# check = CheckButtons(rax, labels, visibility)

# def func(label):
#     index = labels.index(label)
#     lines[index].set_visible(not lines[index].get_visible())
#     plt.draw()

# check.on_clicked(func)

# fig.tight_layout()

# plt.show()

# #----------------------------------------------------------------
# #----------------------------------------------------------------
# #----------------------------------------------------------------

# #random test data:
# x_data = np.random.random_sample(100)
# y_data = np.random.random_integers(10, 50, (100))

# #GOOD PLOT:
# fig2 = plt.figure()
# ax2 = fig2.add_subplot(111)
# ax2.bar(x_data, y_data, width=0.00001)
# #set the bbox for the text. Increase txt_width for wider text.
# txt_height = 0.04 * (plt.ylim()[1] - plt.ylim()[0])
# txt_width = 0.02 * (plt.xlim()[1] - plt.xlim()[0])
# #Get the corrected text positions, then write the text.
# text_positions = get_text_positions(x_data, y_data, txt_width, txt_height)
# text_plotter(x_data, y_data, text_positions, ax2, txt_width, txt_height)

# plt.ylim(0, max(text_positions) + 2 * txt_height)
# plt.xlim(-0.1, 1.1)

# #BAD PLOT:
# fig = plt.figure()
# ax = fig.add_subplot(111)
# ax.bar(x_data, y_data, width=0.0001)
# #write the text:
# for x, y in list(zip(x_data, y_data)):
#     ax.text(x - txt_width, 1.01 * y, '%d' % int(y), rotation=0)
# plt.ylim(0, max(text_positions) + 2 * txt_height)
# plt.xlim(-0.1, 1.1)

# plt.show()