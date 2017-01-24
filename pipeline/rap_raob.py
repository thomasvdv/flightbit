'''
Generates sounding file and thermal statistics
'''
from os.path import expanduser
import os
import StringIO
import csv
import pandas as pd
import collections

home = expanduser("~")
time_format = "%Y-%m-%d %H:%M:%S"


def generateRAOB(df_snd, thermal):

    df_snd['RH'] = df_snd['RH'].astype(int)

    m = collections.OrderedDict()
    m['LEVEL'] = 'PRES'
    m['TMP'] = 'TEMP'
    m['RH'] = 'RH'
    m['UGRD'] = 'UU'
    m['VGRD'] = 'VV'
    m['HGT'] = 'GPM'
    m['VVEL'] = 'WSPEED'

    df_raob = pd.DataFrame(columns=m.values())
    for key, value in m.iteritems():
        df_raob[value] = df_snd[key].copy()

    raob_file = home + "/RAP/RAOB/" + thermal.thermal_id + ".raob.csv"
    df_raob.to_csv(raob_file, index=False)

    headers = [["RAOB/CSV"], ["DTG", thermal.time], ["LAT", thermal.latitude, "N"],
               ["LON", abs(thermal.longitude), "W"], ["ELEV", int(thermal.ELEV), "M"], ["TEMPERATURE", "K"],
               ["MOISTURE", "RH"], ["WIND", "kts", "U/V"], ["RAOB/DATA"]]

    header = StringIO.StringIO()
    writer = csv.writer(header, lineterminator=os.linesep)
    for h in headers:
        writer.writerow(h)

    with file(raob_file, 'r') as original:
        data = original.read()
    with file(raob_file, 'w') as modified:
        modified.write(header.getvalue() + data)


if __name__ == '__main__':

    df_thermal = pd.read_csv(home + '/OLC/CSV/thermal_stats.csv')

    for idx, thermal in df_thermal.iterrows():
        snd_file = home + "/RAP/SND/" + thermal.thermal_id + ".snd.csv"
        if os.path.isfile(snd_file):
            print "Processing", thermal.thermal_id
            df_snd = pd.read_csv(snd_file)
            generateRAOB(df_snd, thermal)
