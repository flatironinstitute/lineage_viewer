
# required module __init__

# hack: add int to numpy
import numpy
try:
    test_int = numpy.int
except:
    numpy.int = int
    numpy.float = float