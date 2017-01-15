'''
For each thermal location, extracts the grib weather data.

Example command:
wgrib2 ruc2_252_20080529_1900_000.grb.grb2 -irr_grid -120:45 1000 - | wgrib2 - -csv ~/RAP/CSV/test.csv

'''

import pandas as pd
from os.path import expanduser
from subprocess import call
import os.path
import pandas as pd
from datetime import datetime, timedelta
import urllib2
import Nomads as nm
import os
home = expanduser("~")
time_format = "%Y-%m-%d %H:%M:%S"


def extractPoint(thermal):
    t_time = datetime.strptime(thermal.time, time_format)
    nomads = nm.Nomads(t_time)
    grib_file = home + '/RAP/GRIB/' + nomads.grib_file()

    # Point to the converted grb->grib2 file if needed
    if nomads.ext == "grb":
        grib_file += ".grb2"

    if os.path.isfile(grib_file):
        print "Extracting", thermal.longitude, thermal.latitude, "from", grib_file
        cmd = ["wgrib2", grib_file, "-irr_grid", str(thermal.longitude) + ":" + str(thermal.latitude), "1000", "-", "|", "wgrib2",
              "-", "-csv", home + "/RAP/CSV/" + thermal.thermal_id + ".csv"]
        cmd_str = ""
        for i in cmd:
            cmd_str += i+" "
        print cmd_str
        #call(cmd_str, shell=True)
        os.system(cmd_str)
    else:
        print "WARNING: GRIB file not found -", grib_file, "- for", thermal.thermal_id


if __name__ == '__main__':
    df = pd.read_csv(home + '/OLC/CSV/thermals.csv')
    print df.head()
    for i, thermal in df.iterrows():
        extractPoint(thermal)
