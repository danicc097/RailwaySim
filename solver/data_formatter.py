import numpy as np


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
