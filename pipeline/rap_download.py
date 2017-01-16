import pandas as pd
from os.path import expanduser
import os.path
import pandas as pd
from datetime import datetime, timedelta
import urllib2
import Nomads as nm

home = expanduser("~")
time_format = "%Y-%m-%d %H:%M:%S"

cache_200 = []
cache_404 = []

def processThermal(thermal):

    t_time = datetime.strptime(thermal.time, time_format)
    nomads = nm.Nomads(t_time)
    grib_url = nomads.grib_url()

    is_found = False

    grib_local = "%s/RAP/GRIB/%s" % (home, nomads.grib_file())

    if os.path.isfile(grib_local):
        is_found = True
    elif cache_404.count(grib_url) == 0:
        # Check if the file exist
        try:
            r = urllib2.urlopen(grib_url)
            data = r.read()
            with open(grib_local, "wb") as grib:
                grib.write(data)
        except urllib2.URLError as e:
            r = e
        if r.code in (200, 401):
            cache_200.append(grib_url)
            is_found = True
        elif r.code == 404:
            cache_404.append(grib_url)

    if is_found:
        print '[{}]: '.format(grib_url), "Found!"
    else:
        print '[{}]: '.format(grib_url), "Not Found!"


if __name__ == '__main__':
    df = pd.read_csv(home + '/OLC/CSV/thermals.csv')
    print df.head()
    for i, thermal in df.iterrows():
        processThermal(thermal)

    # Write the results
    df_200 = pd.DataFrame()
    df_200['url'] = cache_200
    df_200.to_csv(home+'/RAP/CSV/grib_200.csv')
    df_404 = pd.DataFrame()
    df_404['url'] = cache_404
    df_404.to_csv(home + '/RAP/CSV/grib_404.csv')
