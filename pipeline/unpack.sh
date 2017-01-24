#!/bin/bash

for i in ./*.grb2
do
  wgrib2ms 8 $i -set_grib_type c3 -grib_out $i.c3
done

