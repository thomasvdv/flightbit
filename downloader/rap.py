import pandas as pd
from os.path import expanduser
import os.path
import pandas as pd
from datetime import datetime, timedelta
import urllib2

home = expanduser("~")
time_format = "%Y-%m-%d %H:%M:%S"
'''
The archive is a mess with missing files and different formats. Files represent end of time period.

https://nomads.ncdc.noaa.gov/data/rucanl/200612/20061231/ruc2_252_20061231_2300_000.grb
https://nomads.ncdc.noaa.gov/data/rucanl/200712/20071231/ruc2anl_130_20071231_2300_000.grb2
https://nomads.ncdc.noaa.gov/data/rucanl/200810/20081029/ruc2_252_20081029_2300_000.grb
https://nomads.ncdc.noaa.gov/data/rucanl/201106/20110620/ruc2anl_130_20110620_2300_000.grb2
https://nomads.ncdc.noaa.gov/data/rucanl/201610/20161001/rap_130_20161001_2300_000.grb2
https://nomads.ncdc.noaa.gov/data/ruc130/201701/20170113/rap_130_20170113_0000_000.grb2
'''

repos = [
    (datetime(2006, 12, 31), "rucanl", "ruc2_252", "grb"),
    (datetime(2007, 12, 31), "rucanl", "ruc2anl_130", "grb2"),
    (datetime(2008, 10, 29), "rucanl", "ruc2_252", "grb"),
    (datetime(2011, 6, 20), "rucanl", "ruc2anl_130", "grb2"),
    (datetime(2016, 10, 1), "rucanl", "rap_130", "grb2")
]

cache_200 = []
cache_404 = []

def processThermal(thermal):
    t_time = datetime.strptime(thermal.time, time_format)
    t_hour = t_time.hour

    # Round up to the next hour
    if t_time.minute > 30:
        t_hour = (t_time + timedelta(hours=1)).hour

    # Pick the right model based on date published
    dir = "ruc130"
    model = "rap_130"
    ext = "grb2"

    for repo in repos:
        if t_time <= repo[0]:
            dir = repo[1]
            model = repo[2]
            ext = repo[3]
            break

    grib_file = "%s_%s%s%s_%s00_000.%s" % (
    model, t_time.year, t_time.strftime('%m'), t_time.strftime('%d'), t_time.strftime('%H'), ext)
    grib_url = "https://nomads.ncdc.noaa.gov/data/%s/%s%s/%s%s%s/%s" % (dir,
    t_time.year, t_time.strftime('%m'), t_time.year, t_time.strftime('%m'), t_time.strftime('%d'), grib_file)

    is_found = False

    grib_local = "%s/RAP/GRIB/%s" % (home, grib_file)

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
    df['url'] = cache_200
    df_200.to_csv(home+'/grib_200.csv')
    df_404 = pd.DataFrame()
    df['url'] = cache_404
    df_404.to_csv(home + '/grib_404.csv')
