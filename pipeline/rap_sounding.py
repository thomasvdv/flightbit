'''
Generates sounding file and thermal statistics
'''
from os.path import expanduser
import os
import pandas as pd
from datetime import datetime, timedelta
import Nomads as nm

home = expanduser("~")
time_format = "%Y-%m-%d %H:%M:%S"

if __name__ == '__main__':
    df_grib = pd.read_csv(home + "/RAP/CSV/" + "d5ea0989-96c1-4351-9fd8-aae68dfd26a4.csv",
                          names=['start', 'end', 'field', 'level', 'lon', 'lat', 'value'])
    print df_grib.field == 'HGT'
