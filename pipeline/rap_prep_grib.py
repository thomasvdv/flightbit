'''
Prepares the GRIB for processing by fixing errors and reducing the size to the area of interest.
'''
from os import listdir
import os
import subprocess
from os.path import expanduser

home = expanduser("~")
grib_dir = "/media/thomasvdv/DATA/RAP/"


def removeRecord(grib, skip):
    grib_file = grib_dir + grib
    print "Fixing:", grib

    p1 = subprocess.Popen(['wgrib2', grib_file,
                           '-pdt'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p2 = subprocess.Popen(['egrep', '-v', '^{}:'.format(skip)], stdin=p1.stdout, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)
    p3 = subprocess.Popen(['wgrib2', '-i', grib_file, '-grib', grib_file + '.fixed'], stdin=p2.stdout,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    out, err = p3.communicate()
    if len(err) == 0:
        subprocess.Popen(['mv', grib_file + '.fixed', grib_file])
    else:
        print err


def checkGrib(grib):
    p = subprocess.Popen(["wgrib2", grib_dir + grib], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if err.strip().startswith("***"):
        lines = out.splitlines()
        skip = lines[-1].split(':')[0]
        removeRecord(grib, skip)


if __name__ == '__main__':
    gribs = [f for f in listdir(grib_dir) if f.endswith(".grb2")]
    print len(gribs)
    for grib in gribs:
        checkGrib(grib)
