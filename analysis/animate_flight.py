import xcsoar
import simplekml
import csv
from os import listdir
from os.path import isfile, join


def processIGCs(in_dir, out_dir):
    my_igcs = [f for f in listdir(in_dir) if isfile(join(in_dir, f))]

    anim_kml = simplekml.Kml()

    for my_igc in my_igcs:
        processIGC(join(in_dir, my_igc), out_dir, anim_kml)

    anim_kml.save('{}/Animation.kml'.format(out_dir))


def processIGC(my_igc, out_dir, anim_kml):
    flight_id = my_igc.split('/')[-1].split('.')[0]

    print("Processing flight {}...".format(flight_id))

    flight = xcsoar.Flight(my_igc)

    times = flight.times()

    for dtime in times:
        takeoff = dtime['takeoff']
        landing = dtime['landing']

    fixes = flight.path(takeoff['time'], landing['time'])



if __name__ == '__main__':
    processIGCs("test", "/media/sf_thomasvdv/Desktop/KML")
