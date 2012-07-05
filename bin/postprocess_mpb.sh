#!/bin/bash

# Converts .out files created by MPB to .dat files usable by plot_MPB.m
# TODO: Create plotting script able to read MPB output directly without any intermediate file (or MPB output reader returning directly usable variables)

set -eux

for IN in "$@"
do
  OUT="$IN.dat"
  grep freq "$IN" | awk --field-separator "," '{ for (x=2; x<=NF; x++) {  printf "%s ", $x } printf "\n" }' | sed 's/k index/k_index/' | sed 's/band \([0-9]*\)/band_\1/g' | sed 's/kmag\/2pi/kmag_over_2pi/' >"$OUT"
done
#for dir in "$@"
#do
#  grep freq $dir/data.out | awk --field-separator "," '{ for (x=2; x<=NF; x++) {  printf "%s ", $x } printf "\n" }' | sed 's/k index/k_index/' | sed 's/band \([0-9]*\)/band_\1/g' | sed 's/kmag\/2pi/kmag_over_2pi/' >$dir/band.dat
#done

