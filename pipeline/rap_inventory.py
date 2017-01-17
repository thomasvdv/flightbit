'''
Builds an inventory of the available model data.
'''
from os.path import expanduser
import os
import pandas as pd
from datetime import datetime, timedelta
import Nomads as nm

home = expanduser("~")
time_format = "%Y-%m-%d %H:%M:%S"

if __name__ == '__main__':

    inventory = []
    df = pd.read_csv(home + '/OLC/CSV/thermals.csv')

    for i, thermal in df.iterrows():
        t_time = datetime.strptime(thermal.time, time_format)
        nomads = nm.Nomads(t_time)
        # Check if we have data on the thermal
        has_grib = os.path.isfile(home+"/RAP/GRIB/"+nomads.grib_file())
        has_sounding = os.path.isfile(home+"/RAP/CSV/"+thermal.thermal_id+".csv")
        inventory.append((thermal.thermal_id, nomads.model, has_grib, has_sounding))

    df_idx = pd.DataFrame(inventory, columns=['thermal_id', 'model', 'has_grib', 'has_sounding'])

    print df_idx