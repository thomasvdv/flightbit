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

snd_cols = ['LEVEL', 'HGT', 'TMP', 'RH', 'UGRD', 'VGRD', 'VVEL']


def processSounding(df_grib):
    df_snd = pd.DataFrame()

    snd_series = []
    for col in snd_cols[1:]:
        snd_series.append(df_grib.loc[df_grib['FIELD'] == col][['LEVEL', 'VALUE']].rename(columns={'VALUE': col}))

    df_snd = reduce(lambda left, right: pd.merge(left, right, on='LEVEL'), snd_series)

    return df_snd


if __name__ == '__main__':

    df = pd.read_csv(home + '/OLC/CSV/thermals.csv')

    for i, thermal in df.iterrows():
        grib_csv = home + "/RAP/CSV/" + thermal.thermal_id + ".csv"
        if os.path.isfile(grib_csv):
            df_grib = pd.read_csv(home + "/RAP/CSV/" + thermal.thermal_id + ".csv",
                                  names=['START', 'END', 'FIELD', 'LEVEL', 'LON', 'LAT', 'VALUE'])
            df_snd = processSounding(df_grib)
            df_snd.to_csv(home+"/RAP/SND/" +thermal.thermal_id+".snd.csv")

