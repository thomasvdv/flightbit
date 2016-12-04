import xcsoar
import simplekml
import csv
from os import listdir
from os.path import isfile, join


def processIGCs(in_dir, out_dir):

    my_igcs = [f for f in listdir(in_dir) if isfile(join(in_dir, f))]

    try:
        f = open('{}/thermals.csv'.format(out_dir), 'wt')
        writer = csv.writer(f)
        writer.writerow(('longitude', 'latitude', 'heigth', 'vario', 'alt_diff', 'time'))

        ef = open('{}/errors.csv'.format(out_dir), 'wt')
        ef_writer = csv.writer(ef)

        for my_igc in my_igcs:
            processIGC(join(in_dir, my_igc), out_dir, writer, ef_writer)

    finally:
        f.close()
        ef.close()


def processIGC(my_igc, out_dir, writer, ef_writer):
    flight_id = my_igc.split('/')[-1].split('.')[0]

    print("Processing flight {}...".format(flight_id))

    flight = xcsoar.Flight(my_igc)

    times = flight.times()

    if len(times) == 0:
        print("Skipping file {}!".format(flight_id))
        ef_writer.writerow((str(flight_id)))
        return

    for dtime in times:
        takeoff = dtime['takeoff']
        try:
            release = dtime['release']
        except KeyError:
            print("No release detected!")
            release = dtime['takeoff']
        landing = dtime['landing']

    analysis = flight.analyse(takeoff=takeoff['time'],
                              scoring_start=release['time'],
                              scoring_end=landing['time'],
                              landing=landing['time'])

    fixes = flight.path(release['time'], landing['time'])

    for phase in analysis['phases']:
        bottom_lon = 0
        bottom_lat = 0
        bottom_heigth = 0
        for fix in fixes:
            if fix[0] == phase['start_time']:
                bottom_fix = fix[2]
                bottom_lon = bottom_fix['longitude']
                bottom_lat = bottom_fix['latitude']
                bottom_heigth = fix[4]
            if fix[0] == phase['end_time']:
                top_fix = fix[2]
                top_lon = top_fix['longitude']
                top_lat = top_fix['latitude']
                top_heigth = fix[4]
                if bottom_lat < 49 and top_lat < 49:
                    if phase['type'] == 'circling':
                        writer.writerow((bottom_lon, bottom_lat, bottom_heigth, phase['vario'], phase['alt_diff'],
                                         phase['start_time'].isoformat(' ')))

if __name__ == '__main__':
    processIGCs("/home/thomasvdv/OLC/IGC", "/home/thomasvdv/OLC/CSV")
