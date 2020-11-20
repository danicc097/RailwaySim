import numpy as np
import matplotlib.pyplot as plt
from termcolor import colored


def effort_curve_to_arrays(path):
    """Returns speed and effort as separate arrays from a given path."""
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
    for index, (y, x) in reversed(list(enumerate(a))):
        local_text_positions = [
            i for i in a
            if i[0] > (y - txt_height) and (abs(i[1] - x) < txt_width * 2) and i != (y, x)
        ]
        if local_text_positions:
            sorted_ltp = sorted(local_text_positions)
            if abs(sorted_ltp[0][0] - y) < txt_height:  #True == collision
                differ = np.diff(sorted_ltp, axis=0)

                a[index] = (sorted_ltp[-1][0] + txt_height, a[index][1])
                text_positions[index] = sorted_ltp[-1][0] + txt_height * 2
                for k, (j, m) in enumerate(differ):
                    #j is the vertical distance between words
                    if j > txt_height * 2:  #if True then room to fit a word in
                        a[index] = (sorted_ltp[k][0] + txt_height, a[index][1])
                        text_positions[index] = sorted_ltp[k][0] + txt_height
                        break

    return text_positions


def text_plotter(
    x_data,
    y_data,
    y_heigth,
    text_positions,
    axis,
    txt_width,
    txt_height,
    labelsize=12,
    darkMode=False,
):
    """Changes label text location and adds arrow if there's a collision."""
    for x, y, h, t in list(zip(x_data, y_data, y_heigth, text_positions)):
        axis.text(
            x - txt_width,
            1.01 * t,
            str(y),
            rotation=20,
            color='black' if not darkMode else 'white',
            clip_on=False,
            fontsize=labelsize
        )
        if h != t:
            axis.arrow(
                x,
                t,
                0,
                (h - t),
                color='black' if not darkMode else 'white',
                alpha=0.1,
                width=txt_width * 0.1,
                head_width=txt_width / 2,
                head_length=txt_height * 0.2,
                zorder=0,
                length_includes_head=True,
                clip_on=False,
            )