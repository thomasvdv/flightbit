'''
Generates sounding file and thermal statistics
'''
from os.path import expanduser
import os
import pandas as pd
import numpy as np
from skewt import SkewT


home = expanduser("~")
time_format = "%Y-%m-%d %H:%M:%S"

snd_cols = ['LEVEL', 'HGT', 'TMP', 'RH', 'UGRD', 'VGRD', 'VVEL']

def valueFromGrib(df_grib, field, level):
    try:
        return df_grib[(df_grib.FIELD == field) & (df_grib.LEVEL == level)].iloc[0]['VALUE']
    except IndexError:
        print field, "at", level, "not found."

def dew_point(df_snd):
    df_snd.DPT_A = df_snd.TMP_C.apply(lambda x: 17.368 if x > 0 else 17.966)
    df_snd.DPT_B = df_snd.TMP_C.apply(lambda x: 238.88 if x > 0 else 247.15)

    pa = df_snd.RH / 100. * np.exp(df_snd.DPT_A * df_snd.TMP_C / (df_snd.DPT_B + df_snd.TMP_C))
    df_snd['DPT_C'] = df_snd.DPT_B * np.log(pa) / (df_snd.DPT_A - np.log(pa))


def processSounding(df_grib, df_thermal, idx):

    df_snd = pd.DataFrame()

    # Core vertical profile
    snd_series = []
    for col in snd_cols[1:]:
        snd_series.append(df_grib.loc[df_grib['FIELD'] == col][['LEVEL', 'VALUE']].rename(columns={'VALUE': col}))

    df_snd = reduce(lambda left, right: pd.merge(left, right, on='LEVEL'), snd_series)

    # Convert the level to a numeric
    df_snd['LEVEL'] = df_snd['LEVEL'].map(lambda x: x.rstrip(' mb'))
    df_snd['LEVEL'] = pd.to_numeric(df_snd['LEVEL'])

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

    # Surface heigth
    sfc_hgt = valueFromGrib(df_grib, 'HGT', 'surface')

    # Surface pressure
    sfc_pres = valueFromGrib(df_grib, 'PRES', 'surface')/100

    # DALR
    df_snd['DALR'] = sfc_tmp - ((df_snd.HGT - sfc_hgt) / 1000) * 9.8

    # Virtual Temperature
    df_snd.VIRTT = (df_snd.TMP) / (
    1 - 0.379 * (6.11 * np.power(((7.5 * df_snd.DPT_C) / (237.7 + df_snd.DPT_C)), 10)) / df_snd.LEVEL) - 273.15

    # Thermal Index
    df_snd['TI'] = df_snd.TMP_C - df_snd.DALR
    df_snd['TI_ROUND'] = df_snd.TI.round()

    # Top of lift
    lift_top = np.NAN
    df_lift = df_snd.loc[df_snd['TI'] < -2]
    if len(df_lift.index > 0) :
        lift_top = df_lift.iloc[-1]['HGT']

    df_thermal.set_value(idx, 'top_lift', lift_top)

    # Cloud base
    hgt_cb = valueFromGrib(df_grib, 'HGT', 'cloud base')
    df_thermal.set_value(idx, 'cloud_base', hgt_cb)

    # Parcel to raise
    parcel = (sfc_pres, sfc_tmp, sfc_dpt, 'interp')
    print parcel

    # Plot the Skew-T
    hght = df_snd[['HGT']].as_matrix().flatten()
    pres = df_snd[['LEVEL']].as_matrix().flatten()
    temp = df_snd[['TMP_C']].as_matrix().flatten()
    dwpt = df_snd[['DPT_C']].as_matrix().flatten()
    sknt = df_snd[['W_DIR']].as_matrix().flatten()
    drct = df_snd[['W_SPD_KTS']].as_matrix().flatten()

    mydata = dict(zip(('hght', 'pres', 'temp', 'dwpt', 'sknt', 'drct'), (hght, pres, temp, dwpt, sknt, drct)))
    S = SkewT.Sounding(soundingdata=mydata)
    S.make_skewt_axes();
    S.add_profile();
    S.lift_parcel(*parcel)
    Plcl, Plfc, P_el, CAPE, CIN = S.get_cape(*parcel)
    # S.plot_skewt(title="Thermal Plot")

    # Add parcel stats
    df_thermal.set_value(idx, 'Plcl', Plcl)
    df_thermal.set_value(idx, 'Plfc', Plfc)
    df_thermal.set_value(idx, 'P_el', P_el)
    df_thermal.set_value(idx, 'CAPE', CAPE)
    df_thermal.set_value(idx, 'CIN', CIN)

    # Add the stats we got from the GRIB


    return df_snd




if __name__ == '__main__':

    df_thermal = pd.read_csv(home + '/OLC/CSV/thermals.csv')

    for idx, thermal in df_thermal.iterrows():
        grib_csv = home + "/RAP/CSV/" + thermal.thermal_id + ".csv"
        if os.path.isfile(grib_csv):
            df_grib = pd.read_csv(home + "/RAP/CSV/" + thermal.thermal_id + ".csv",
                                  names=['START', 'END', 'FIELD', 'LEVEL', 'LON', 'LAT', 'VALUE'])
            df_snd = processSounding(df_grib, df_thermal, idx)
            df_snd.to_csv(home+"/RAP/SND/" +thermal.thermal_id+".snd.csv")

    df_thermal.to_csv(home + '/OLC/CSV/thermal_stats.csv')
