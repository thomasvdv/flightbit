import xcsoar
import simplekml

flight = xcsoar.Flight('/home/vagrant/OLC/IGC/941526393.igc')
kml = simplekml.Kml()

times = flight.times()

for dtime in times:
    takeoff = dtime['takeoff']
    release = dtime['release']
    landing = dtime['landing']

analysis = flight.analyse(takeoff=takeoff['time'],
                          scoring_start=release['time'],
                          scoring_end=landing['time'],
                          landing=landing['time'])

fixes = flight.path(release['time'], landing['time'])

for phase in analysis['phases']:
    if phase['type'] == 'circling':
        for fix in fixes:
            if fix[0] == phase['start_time']:
                t_fix = fix[2]
                print(fix)
                print(phase)
                kml.newpoint(name="Kirstenbosch", coords=[(t_fix['latitude'],t_fix['longitude'])])

kml.save('/home/vagrant/OLC/KML/941526393.kml')

