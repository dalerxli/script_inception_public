#!/bin/bash

set -eux

BLENDERSCRIPTDIR="$HOME/Application Data/Blender Foundation/Blender/.blender/scripts"
SCRIPTS="\
bfdtd_parser.py \
bfdtd_import.py \
bfdtd_export.py \
meep_parser.py \
meep_import.py \
meep_export.py \
bfdtd_meep_export.py"
    
function BlenderScriptDir_to_repo()
{
    echo "BlenderScriptDir->repo"
    for f in $SCRIPTS
    do
        cp -iv "$BLENDERSCRIPTDIR/$f" ".";
    done
}

function repo_to_BlenderScriptDir()
{
    echo "repo->BlenderScriptDir";
    for f in $SCRIPTS
    do
        cp -iv "$f" "$BLENDERSCRIPTDIR";
    done
}

echo "0=BlenderScriptDir->repo / 1=repo->BlenderScriptDir"
read ans
case $ans in
  0) BlenderScriptDir_to_repo;;
  1) repo_to_BlenderScriptDir;;
  *) echo "Unknown option";;
esac
