#!/bin/bash
# copy files from source to destination, excluding any files generated by Bristol FDTD
set -eu
rsync -avz  --exclude-from=$(dirname $(readlink -f $0))/BFDTD_torque_output.list "$1" "$2"
