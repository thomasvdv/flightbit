import pygrib as pg
import numpy as np


def all_and(data):
    """Logical and for a list of arrays.

    Required arguments:
        - data -- list of Numpy boolean arrays

    Return:
        - result -- Logical and of all given arrays
    """
    result = data.pop()
    for d in data:
        result = np.logical_and(result, d)

    return result


grib = pg.open("hrrr.t00z.wrfprsf01.grib2")

for g in grib:
    print g

lat0=48.162474
lon0=-122.161616

area = (lat0+1.5, lon0-1.5, lat0-0.5, lon0+1.5)


grib.seek(0)
u_msgs = grib.select(name='U component of wind')
v_msgs = grib.select(name='V component of wind')
g_msgs = grib.select(name='Geopotential Height')
t_msgs = grib.select(name='Temperature')
d_msgs = grib.select(name='Dew point temperature')
d2m_msgs = grib.select(name='2 metre dewpoint temperature')

lats, lons = u_msgs[0].latlons()



tlat, llat, blat, rlat = area

# Find closest pixel location
locs = all_and([lats <= tlat, lats >= blat,
                       lons <= rlat, lons >= llat])
row_idx, col_idx = np.where(locs)
lats = lats[row_idx, col_idx]
lons = lons[row_idx, col_idx]

# Collect U component of wind data
u_wind = {}
for msg in u_msgs:
    if msg.typeOfLevel == 'isobaricInhPa':
        u_wind[msg.level] = msg.values[row_idx, col_idx]

# Collect V component of wind data
v_wind = {}
for msg in v_msgs:
    if msg.typeOfLevel == 'isobaricInhPa':
        v_wind[msg.level] = msg.values[row_idx, col_idx]

# Collect temperatures
temperature = {}
for msg in t_msgs:
    if msg.typeOfLevel == 'isobaricInhPa':
        temperature[msg.level] = msg.values[row_idx, col_idx]
    # Add msg.typeOfLevel == 'surface', save to another variable for
    # later use
    if msg.typeOfLevel == 'surface':
        t_surface = msg.values[row_idx, col_idx]

# Collect dewpoints
dewpoint = {}
for msg in d_msgs:
    if msg.typeOfLevel == 'isobaricInhPa':
        dewpoint[msg.level] = msg.values[row_idx, col_idx]

# Collect dewpoint at 2m
dewpoint2m = {}
for msg in d2m_msgs:
    if msg.typeOfLevel == 'heightAboveGround':
        dewpoint2m[msg.level] = msg.values[row_idx, col_idx]

# Collect Geopotential heights
altitude = {}
for msg in g_msgs:
    if msg.typeOfLevel == 'isobaricInhPa':
        altitude[msg.level] = msg.values[row_idx, col_idx]

# Collect data to correct altitude order. Set "surface" values
# before real data.
u_winds = [np.zeros(lats.shape)]
v_winds = [np.zeros(lats.shape)]
# Use given surface temperature if available, otherwise use the
# model value
temperatures = [t_surface]
dewpoints = [dewpoint2m]

altitudes = [0.0*np.ones(lats.shape)]
pressures = u_wind.keys()
pressures.append(max(pressures))

# Put pressures in altitude order and use them as keys
pressures.sort()
pressures.reverse()
i = 0
for key in pressures:
    if i == 0:
        i = 1
    else:
        uwnd, vwnd, temp, dewp, alt = [], [], [], [], []
        uwnd.append(u_wind[key])
        vwnd.append(v_wind[key])
        temp.append(temperature[key])
        dewp.append(dewpoint[key])
        alt.append(altitude[key])
        u_winds.append(np.hstack(uwnd))
        v_winds.append(np.hstack(vwnd))
        temperatures.append(np.hstack(temp))
        dewpoints.append(np.hstack(dewp))
        altitudes.append(np.hstack(alt))

# Convert data in lists to Numpy arrays and add them to a
# dictionary that is returned
data = {}
data['lats'] = np.array(lats)
data['lons'] = np.array(lons)
data['u_winds'] = np.array(u_winds)
data['v_winds'] = np.array(v_winds)
data['temperatures'] = np.array(temperatures)
data['dewpoints'] = np.array(dewpoints)
data['altitudes'] = np.array(altitudes)
all_pressures = []
for dat in data['lats']:
    all_pressures.append(100*np.array(pressures)) # Convert hPa to Pa
data['pressures'] = np.array(all_pressures).transpose()

print len(data['u_winds'][0])
print len(data['u_winds'])
print len(data['altitudes'])
print len(data['lats'])
print len(data['dewpoints'])