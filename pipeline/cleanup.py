'''
Removes files that could not be processed.
'''
import csv
from os.path import expanduser
import os

home = expanduser("~")

with open(home+'/OLC/CSV/errors.csv', 'rb') as f:
    reader = csv.reader(f)
    for row in reader:
        print row[0]
        os.remove(home+'/OLC/IGC/'+row[0]+'.igc')