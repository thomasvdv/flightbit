HRRR Data Pipeline:

1) Download grib2 with desired field
2) gdal_translate hrrr.t00z.wrfsfcf03.grib2 dpt.tif
3) gdalwarp -t_srs EPSG:3857 -r BILINEAR dpt.tif mercator_dpt.tif
4) gdaldem color-relief mercator_dpt.tif color.txt color_dpt.tif

Color Map (Temperature):

0       191     191     191
2       191     127     255
4       127     0       255
6       102     153     255
8       0       0       255
10      127     255     255
12      0       255     255
14      0       255     0
16      127     255     0
18      255     255     0
20      255     127     0
22      255     0       0
24      255     127     255
26      255     255     255

Create your own here: 
