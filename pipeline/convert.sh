#!/bin/bash

for i in ./*.grb
do
  grb1to2.pl $i
done

