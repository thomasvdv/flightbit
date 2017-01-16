import pandas as pd

'''
1) Download grib files. GFS, nam4k, and HRRR for current day.
2) Retrieve the soundings
3) Compute L2
4) Upload data to plotly

GFS 0.25 degrees File format:
gfs.tCCz.pgrb2.0p25.fFFF
CC is the model cycle runtime (i.e. 00, 06, 12, 18)
FFF is the forecast hour of product from 000 - 384
YYYYMMDD is the Year, Month and Day
'''

df = pd.read_csv("three_fingers.csv", names=['start', 'end', 'param', 'level', 'lon', 'lat', 'value'])
snd = pd.DataFrame(columns=['LEVEL', 'HGT', 'TMP', 'RH', 'UGRD', 'VGRD', 'VVEL'])

snd['LEVEL'] = df.loc[df['param'] == 'HGT']['level']
for column in ['HGT', 'TMP', 'RH', 'UGRD', 'VGRD', 'VVEL']:
    snd[column] = df.loc[df['param'] == column]['value'].

print snd