import numpy
from numpy.core.records import array
import pandas as pd
# ! Dump to CSV
a = numpy.asarray([[2341.43243, 2, 3], [4, 5, 6], [7, 8, 9]])
numpy.savetxt("foo.csv", a, delimiter=",", encoding='utf-8', fmt='%1.8f')
