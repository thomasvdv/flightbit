'''
Generates sounding file and thermal statistics
'''
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn; seaborn.set()

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

    # Heigth in feet
    df_snd['HGT_FT'] = df_snd.HGT * 3.28084

    # Round the relative humidity
    df_snd['RH'] = df_snd['RH'].astype(int)

    # Wind Speed
    df_snd['W_SPD_MS'] = (df_snd.UGRD ** 2 + df_snd.VGRD ** 2) ** (0.5)

    # Wind Direction
    df_snd['W_DIR'] = np.arctan2(df_snd.UGRD, df_snd.VGRD) * (180. / np.pi)

    # Temperature in Celcius
    df_snd['TMP_C'] = df_snd.TMP - 273.15

    # Scorer Parameter
    Ys = []
    for i, row in df_snd.iterrows():
        if (i < len(df_snd.index) - 1):
            Ys.append((df_snd.TMP_C.iloc[i + 1] - df_snd.TMP_C.iloc[i]) / (df_snd.HGT.iloc[i] - df_snd.HGT.iloc[i + 1]))
    df_snd['Y'] = pd.Series(Ys)

    df_snd['Y2'] = (((0.00986 - df_snd.Y) / df_snd.TMP) * (9.81 / df_snd.W_SPD_MS ** 2) - (1 / 4) * (
        (9.81 / 287 - df_snd.Y) / df_snd.TMP) ** 2) * 100000

    wave_file = snd_file + ".wave"
    df_snd.to_csv(wave_file, index=False)

    # Plot the Scorer Parameter
    ax = df_snd.plot(x='Y2', y='HGT_FT', xlim=(0,0.3), ylim=(0,18000), title="Scorer Parameter", legend=False)
    ax.axhline(y=13600,  c="blue", linewidth=2.0, zorder=0)
    fig = ax.get_figure()
    fig.savefig(snd_file + '.png')


if __name__ == '__main__':
    snd_file = raw_input("File to convert: ")
    if os.path.isfile(snd_file):
        df_grib = pd.read_csv(snd_file,
                              names=['START', 'END', 'FIELD', 'LEVEL', 'LON', 'LAT', 'VALUE'])
        generateRAOB(df_grib, snd_file)
    else:
        print "Not a valid file!"
