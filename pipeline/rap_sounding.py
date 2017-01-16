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
                          names=['START', 'END', 'FIELD', 'LEVEL', 'LON', 'LAT', 'VALUE'])

    snd_cols = ['LEVEL', 'HGT', 'TMP', 'RH', 'UGRD', 'VGRD']
    df_snd = pd.DataFrame()

    snd_series = []
    for col in snd_cols[1:]:
        snd_series.append(df_grib.loc[df_grib['FIELD'] == col][['LEVEL', 'VALUE']].rename(columns={'VALUE': col}))

    df_snd = reduce(lambda left, right: pd.merge(left, right, on='LEVEL'), snd_series)

    print df_snd
