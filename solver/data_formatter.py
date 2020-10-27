"""
Bisection:
>>> def grade(score, breakpoints=[60, 70, 80, 90], grades='FDCBA'):
...     i = bisect(breakpoints, score)
...     return grades[i]
...
>>> [grade(score) for score in [33, 99, 77, 70, 89, 90, 100]]
['F', 'A', 'C', 'C', 'B', 'A', 'A']
"""


def hhmm_to_s(time):
    """Convert hh:mm to seconds"""
    h, m = time.split(':')
    return int(h) * 3600 + int(m) * 60


def s_to_hhmmss(seconds):
    """Convert seconds to hh:mm:ss."""
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    return "%d:%02d:%02d" % (hour, minutes, seconds)
