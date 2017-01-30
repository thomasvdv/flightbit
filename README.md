A place for lots of soaring coolness.

Parsing meteo data for a particular point:
grib_ls -m -l 47.683900,-120.935794,1 -p paramId,name,level,time rap_130_20120822_2100_000.grb2

RAP Archive:
https://www.ncdc.noaa.gov/data-access/model-data/model-datasets/rapid-refresh-rap

Thermal near Ephrata:
===
68de910c-ff55-4be7-b163-0d46e8a94c97	55584744	-119.56293333337	47.3514166666813	1425	1.94723618090453	775	2013-06-01 21:25:42


http://www.onlinecontest.org/olc-2.0/gliding/flightinfo.html?flightId=55584744

Mountain Thermal:
5efc712e-0656-4003-b981-88a2348f3756	537762561	-121.236050000037	48.4365833333483	2362	1.23099415204678	420	2015-05-03 23:22:58

Finding the GDAL package on Ubuntu:

sudo apt-cache search gdal

Then install libgdal-dev:

sudo apt-get install libgdal-dev

export CPLUS_INCLUDE_PATH=/usr/include/gdal

export C_INCLUDE_PATH=/usr/include/gdal

pip install GDAL

DEM Coordinates:

top left: 
	lat: 49
	lon: -125

lower right:
	lat: 43.5
	lon: -112

Download STRM TIFF here:

http://srtm.csi.cgiar.org/SELECTION/inputCoord.asp

SRTM 90m DEM version 4
srtm_12_03:

Latitude 
	min:	45 N
	max:	50 N
 	 
Longitude
	min:	125 W
	max:	120 W

srtm_13_03:

Latitude
	min:	45 N
	max:	50 N
 	 
Longitude
	min:	120 W
	max:	115 W


Notes
=
I started with leveraging GRIB_API but found it too slow for parsing data at a particular point. The tools do not appear to support multi-threading. I am switching to wgrib2 to generate CSV files, which should be easier to process.
 
Time bounds:

17Z through 3Z

Swiss Thermal Hot spots: http://thermal.kk7.ch/
XCSoar Custom Map: http://www.dotmana.com/weblog/2014/07/xcsoar-generate-custom-maps/

Mt Pilchuck:
48.058099
-121.796903