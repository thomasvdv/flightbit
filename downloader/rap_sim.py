from os.path import expanduser
import pandas as pd
from datetime import datetime, timedelta
import Nomads as nm

home = expanduser("~")
time_format = "%Y-%m-%d %H:%M:%S"

urls = set()

def processThermal(thermal):

    t_time = datetime.strptime(thermal.time, time_format)
    nomads = nm.Nomads(t_time)
    grib_url = nomads.grib_url()
    urls.add(grib_url)

if __name__ == '__main__':
    df = pd.read_csv(home + '/OLC/CSV/thermals.csv')
    for i, thermal in df.iterrows():
        processThermal(thermal)

    print "Number of thermals:", len(df.index)
    print "Number of GRIB files:", len(urls)