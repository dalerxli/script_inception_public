#!/bin/bash
# remove files generated by bristol FDTD
#TODO: Try replacing find string with variable, use flags, etc. Pythonify and argparse?

function findBFDTDoutput
{
  find . -type f \( -name "*.prn" -o -name "*.out" -o -name "geom.geo" -o -name "namiki.txt" -o -name "*.int" -o -name "heat.txt" -o -name "lumped.log" -o -name "time*.txt" -o -name "e*.txt" -o -name "*.sh.e*" -o -name "*.sh.o*" \) $*
}

#alias findBFDTDoutput='find . -type f \( -name "*.prn" -o -name "*.out" -o -name "geom.geo" -o -name "namiki.txt" -o -name "*.int" -o -name "heat.txt" -o -name "lumped.log" -o -name "time*.txt" -o -name "e*.txt" \)'

findBFDTDoutput | less

echo "Remove those object files? (y=directly, i=interactively, *=exit)"
read ans
case $ans in
  y|Y|yes) findBFDTDoutput -exec rm -v {} \; ;;
  i|I)     findBFDTDoutput -exec rm -iv {} \; ;;
  *)       exit 1;;
esac
