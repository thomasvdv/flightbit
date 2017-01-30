'''
Generates sounding file and thermal statistics
'''
from os.path import expanduser
import os
import StringIO
import csv
import pandas as pd
import numpy as np
import sys
from skewt import SkewT

home = expanduser("~")
time_format = "%Y-%m-%d %H:%M:%S"

snd_cols = ['LEVEL', 'HGT', 'TMP', 'RH', 'UGRD', 'VGRD', 'VVEL']


def valueFromGrib(df_grib, field, level):
    try:
        return df_grib[(df_grib.FIELD == field) & (df_grib.LEVEL == level)].iloc[0]['VALUE']
    except IndexError:
        print field, "at", level, "not found."
        return None


def dew_point(df_snd):
    df_snd.DPT_A = df_snd.TMP_C.apply(lambda x: 17.368 if x > 0 else 17.966)
    df_snd.DPT_B = df_snd.TMP_C.apply(lambda x: 238.88 if x > 0 else 247.15)

    pa = df_snd.RH / 100. * np.exp(df_snd.DPT_A * df_snd.TMP_C / (df_snd.DPT_B + df_snd.TMP_C))
    df_snd['DPT_C'] = df_snd.DPT_B * np.log(pa) / (df_snd.DPT_A - np.log(pa))


def generateSounding(df_grib, df_thermal, idx):
    df_snd = pd.DataFrame()

    # Core vertical profile
    snd_series = []
    for col in snd_cols[1:]:
        snd_series.append(df_grib.loc[df_grib['FIELD'] == col][['LEVEL', 'VALUE']].rename(columns={'VALUE': col}))

    df_snd = reduce(lambda left, right: pd.merge(left, right, on='LEVEL'), snd_series)

    # Convert the level to a numeric
    df_snd['LEVEL'] = df_snd['LEVEL'].map(lambda x: x.rstrip(' mb'))
    df_snd['LEVEL'] = pd.to_numeric(df_snd['LEVEL'])

    # Interpolate on height.
    df_snd['HGT'] = df_snd['HGT'].astype(int)
    print "Height range:", df_snd.HGT.min(), df_snd.HGT.max()
    new_index = pd.Index(range(df_snd.HGT.min(), df_snd.HGT.max(), 1), name='HGT')
    df_snd = df_snd.set_index('HGT').reindex(new_index).reset_index()
    df_snd = df_snd.interpolate()

    # Surface heigth
    sfc_hgt = valueFromGrib(df_grib, 'HGT', 'surface')

    # Strip the sounding to terrain
    df_snd = df_snd.loc[df_snd['HGT'] >= sfc_hgt].reset_index(drop=True)

    # Heigth in feet
    df_snd['HGT_FT'] = df_snd.HGT * 3.28084

    # Wind Speed
    df_snd['W_SPD_MS'] = (df_snd.UGRD ** 2 + df_snd.VGRD ** 2) ** (0.5)
    df_snd['W_SPD_KTS'] = df_snd.W_SPD_MS * 1.94384

    # Wind Direction
    df_snd['W_DIR'] = np.arctan2(df_snd.UGRD, df_snd.VGRD) * (180. / np.pi)

    # Temperature in Celcius
    df_snd['TMP_C'] = df_snd.TMP - 273.15

    # Add the dewpoint temperature in celcius
    dew_point(df_snd)

    # Surface temperature
    sfc_tmp = valueFromGrib(df_grib, 'TMP', '2 m above ground') - 273.15

    # Surface dewpoint
    sfc_dpt = valueFromGrib(df_grib, 'DPT', '2 m above ground') - 273.15

    # Surface pressure
    sfc_pres = valueFromGrib(df_grib, 'PRES', 'surface') / 100

    # DALR
    df_snd['DALR'] = sfc_tmp - ((df_snd.HGT - sfc_hgt) * 0.0098)

    # Virtual Temperature
    df_snd['VIRTT'] = (df_snd.TMP) / (
        1 - 0.379 * (6.11 * np.power(((7.5 * df_snd.DPT_C) / (237.7 + df_snd.DPT_C)), 10)) / df_snd.LEVEL) - 273.15

    # Thermal Index
    df_snd['TI'] = df_snd.VIRTT - df_snd.DALR
    df_snd['TI_ROUND'] = df_snd.TI.round(1)

    # Cloud base
    hgt_cb = valueFromGrib(df_grib, 'HGT', 'cloud base')
    df_thermal.set_value(idx, 'cloud_base', hgt_cb)

    # Set terrain elevation
    df_thermal.set_value(idx, 'ELEV', sfc_hgt)
    df_thermal.set_value(idx, 'ELEV_FT', sfc_hgt * 3.28084)

    # Top of lift in feet
    lift_top = np.NAN
    df_lift = df_snd.loc[df_snd['TI'].abs().argsort()]
    if len(df_lift.index > 0):
        lift_top = df_lift.iloc[0]['HGT']

    df_thermal.set_value(idx, 'TI_0_M', lift_top)

    # Thermal heigth in feet
    df_thermal.set_value(idx, 'THERMAL_HGT_FT', thermal.heigth * 3.28084)

    # Russell Pearson Thermal Heigth
    lift_RPe = (133.72 + 1.03 * (lift_top * 3.28084)) * 0.3048
    df_thermal.set_value(idx, 'THERMAL_RPe_M', lift_RPe)
    print "Set THERMAL_RPe_M at to", lift_RPe

    # Mario Piccagli Thermal Heigth
    lift_MPi = (1580 + (0.57 * lift_top)) * 0.3048
    df_thermal.set_value(idx, 'THERMAL_MPi_M', lift_RPe)

    # Surface Temp, Surface wind direction and speed, Terrain height,
    df_thermal.set_value(idx, 'SFC_TMP', sfc_tmp)
    df_thermal.set_value(idx, 'SFC_PRES', sfc_pres)
    df_thermal.set_value(idx, 'SFC_DPT', sfc_dpt)

    # Generate the output
    # df_snd.to_csv(home + "/RAP/SND/" + thermal.thermal_id + ".snd.csv", index=False)
    return df_snd


if __name__ == '__main__':

    df_thermal = pd.read_csv(home + '/OLC/CSV/thermals.csv')

    f = open(home+'/OLC/CSV/thermal_errors.txt', 'w')

    for idx, thermal in df_thermal.iterrows():
        grib_csv = home + "/RAP/CSV/" + thermal.thermal_id + ".csv"
        if os.path.isfile(grib_csv):
            print "Processing", thermal.thermal_id
            df_grib = pd.read_csv(home + "/RAP/CSV/" + thermal.thermal_id + ".csv",
                                  names=['START', 'END', 'FIELD', 'LEVEL', 'LON', 'LAT', 'VALUE'])
            try:
                generateSounding(df_grib, df_thermal, idx)
            except:
                f.write(thermal.thermal_id+'\n')
                f.write(str(sys.exc_info()[0])+'\n\n')
                continue

    df_thermal.to_csv(home + '/OLC/CSV/thermal_stats.csv')
    f.close()