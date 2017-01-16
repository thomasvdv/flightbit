'''
For each thermal location, extracts the grib weather data.

Example command:
wgrib2 ruc2_252_20080529_1900_000.grb.grb2 -irr_grid -120:45 1000 - | wgrib2 - -csv ~/RAP/CSV/test.csv

'''

import pandas as pd
from os.path import expanduser
import subprocess
import os.path
import pandas as pd
from datetime import datetime, timedelta
import urllib2
import Nomads as nm
import os
from functools import partial
from multiprocessing.dummy import Pool
from subprocess import call


home = expanduser("~")
time_format = "%Y-%m-%d %H:%M:%S"

processes = set()
max_processes = 5

def extractPoint(thermal):

    t_time = datetime.strptime(thermal.time, time_format)
    nomads = nm.Nomads(t_time)
    grib_file = home + '/RAP/GRIB/' + nomads.grib_file()

    # Point to the converted grb->grib2 file if needed
    if nomads.ext == "grb":
        grib_file += ".grb2"

    if os.path.isfile(grib_file):
        cmd = ["wgrib2", grib_file, "-irr_grid", str(thermal.longitude) + ":" + str(thermal.latitude), "1000", "-", "|", "wgrib2",
              "-", "-csv", home + "/RAP/CSV/" + thermal.thermal_id + ".csv"]
        cmd_str = ""
        for i in cmd:
            cmd_str += i+" "
        return cmd_str
    else:
        print "WARNING: GRIB file not found -", grib_file, "- for", thermal.thermal_id


if __name__ == '__main__':
    df = pd.read_csv(home + '/OLC/CSV/thermals.csv')
    cmds = set()
    for i, thermal in df.iterrows():
        if not os.path.isfile(home + "/RAP/CSV/" + thermal.thermal_id + ".csv"):
            cmds.add(extractPoint(thermal))
    print "Extracting", len(cmds), "points..."
    pool = Pool(8)  # 8 concurrent commands at a time
    for i, returncode in enumerate(pool.imap(partial(call, shell=True), cmds)):
        if returncode != 0:
            print("%d command failed: %d" % (i, returncode))