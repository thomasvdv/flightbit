'''
Generates sounding file and thermal statistics
'''
from os.path import expanduser
import os
import StringIO
import csv
import pandas as pd
import collections

snd_cols = ['LEVEL', 'HGT', 'TMP', 'RH', 'UGRD', 'VGRD', 'VVEL']

def valueFromGrib(df_grib, field, level):
    try:
        return df_grib[(df_grib.FIELD == field) & (df_grib.LEVEL == level)].iloc[0]['VALUE']
    except IndexError:
        print field, "at", level, "not found."
        return None

def generateRAOB(df_grib, snd_file):

    snd_time = df_grib.iloc[0]['START']
    snd_lon = df_grib.iloc[0]['LON']
    snd_lat = df_grib.iloc[0]['LAT']

    # Surface heigth
    snd_hgt = valueFromGrib(df_grib, 'HGT', 'surface')

    snd_series = []
    for col in snd_cols[1:]:
        snd_series.append(df_grib.loc[df_grib['FIELD'] == col][['LEVEL', 'VALUE']].rename(columns={'VALUE': col}))

    df_snd = reduce(lambda left, right: pd.merge(left, right, on='LEVEL'), snd_series)

    # Convert the level to a numeric
    df_snd['LEVEL'] = df_snd['LEVEL'].map(lambda x: x.rstrip(' mb'))
    df_snd['LEVEL'] = pd.to_numeric(df_snd['LEVEL'])

    df_snd = df_snd[(df_snd['HGT'] >= snd_hgt) & (df_snd['LEVEL'] >= 100)].reset_index(drop=True)

    # Sort by level
    df_snd = df_snd.sort_values(['LEVEL'], ascending=[0])

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

    raob_file = snd_file + ".raob"
    df_raob.to_csv(raob_file, index=False)

    headers = [["RAOB/CSV"], ["DTG", snd_time], ["LAT", snd_lat, "N"],
               ["LON", abs(snd_lon), "W"], ["ELEV", int(snd_hgt), "M"], ["TEMPERATURE", "K"],
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
    snd_file = raw_input("File to convert: ")
    if os.path.isfile(snd_file):
        df_grib = pd.read_csv(snd_file,
                              names=['START', 'END', 'FIELD', 'LEVEL', 'LON', 'LAT', 'VALUE'])
        generateRAOB(df_grib, snd_file)
    else:
        print "Not a valid file!"
