'''
System-wide utilities and constants. (TODO: Make these environment settings.)
'''
from os.path import expanduser

home = expanduser("~")

class Flightbit():

    OLC_DIR = home + "/OLC"
    OLC_CSV = OLC_DIR + "/CSV"
    OLC_THERMALS = OLC_CSV + "/thermals.csv"

    RAP_DIR = home + "/RAP"
    RAP_GRIB = RAP_DIR + "/GRIB"