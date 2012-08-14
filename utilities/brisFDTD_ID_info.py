#!/usr/bin/env python3
"""
Converts between numID (01,02,67) and alphaID (df,jk,{l,etc)
"""

import sys
import math
import re

# TODO: This currently only handles frequency snapshot numbering. Time sanpshot numbering is different! Handle it as well.

def numID_to_alphaID(numID, snap_plane = 'x', probe_ident = '_id_', snap_time_number = 0):
  '''
  Converts numeric IDs to alpha IDs used by Bristol FDTD 2003
  function [ filename, alphaID, pair ] = numID_to_alphaID(numID, snap_plane, probe_ident, snap_time_number)
  examples:
  26 -> z
  26+27 -> a{
  MAXIMUM NUMBER OF SNAPSHOTS: 32767 (=(2^8)*(2^8)/2 -1)
  MAXIMUM NUMBER OF SNAPSHOTS BEFORE RETURN to aa: 6938 = 26+256*27
  MAXIMUM NUMBER OF SNAPSHOTS BEFORE DUPLICATE IDs: 4508 = 26+(6-(ord('a')-1)+256)*27+1 (6=character before non-printable bell character)
  MAXIMUM NUMBER OF SNAPSHOTS BEFORE ENTERING DANGER AREA (non-printable characters): 836 = 26+(126-(ord('a')-1))*27
  '''

  if numID<1 or numID>836:
    print('ERROR: numID must be between 1 and 836 or else you will suffer death by monkeys!!!', file=sys.stderr)
    sys.exit(-1)
  
  if snap_time_number<0 or snap_time_number>99:
    print('ERROR: snap_time_number must be between 0 and 99 or else you will suffer death by monkeys!!!', file=sys.stderr)
    sys.exit(-1)

  #snap_time_number = mod(snap_time_number,100);
  ilo = snap_time_number%10 # gets the 10^0 digit from snap_time_number
  ihi = snap_time_number//10 # gets the 10^1 digit from snap_time_number
  
  if numID<27:
    alphaID = chr(numID + ord('a')-1)
  else:
    alphaID = chr(numID//27 + ord('a')-1) + chr(numID%27 + ord('a'))

  filename = snap_plane + alphaID + probe_ident + chr(ihi + ord('0')) + chr(ilo + ord('0')) + '.prn'
  pair = str(numID) + ':' + alphaID
  
  return filename, alphaID, pair

def alphaID_to_numID(alphaID_or_filename):
  '''
  Converts alpha IDs used by Bristol FDTD 2003 to numeric IDs
  function [ numID, snap_plane, snap_time_number ] = alphaID_to_numID(alphaID, probe_ident)
  examples:
  z -> 26
  a{ -> 26+27
  MAXIMUM NUMBER OF SNAPSHOTS: 32767 (=(2^8)*(2^8)/2 -1)
  MAXIMUM NUMBER OF SNAPSHOTS BEFORE RETURN to aa: 6938 = 26+256*27
  MAXIMUM NUMBER OF SNAPSHOTS BEFORE DUPLICATE IDs: 4508 = 26+(6-(ord('a')-1)+256)*27+1 (6=character before non-printable bell character)
  MAXIMUM NUMBER OF SNAPSHOTS BEFORE ENTERING DANGER AREA (non-printable characters): 836 = 26+(126-(ord('a')-1))*27
  '''
  
  numID = None
  snap_plane = None
  probe_ident = None
  snap_time_number = None
  
  if not isinstance(alphaID_or_filename, str):
    print('ERROR: alphaID_or_filename should be a string.', file=sys.stderr)
    sys.exit(-1)
    
  pattern_alphaID = re.compile(r"^([a-z\{\|\}~][a-z\{]|[a-z])$")
  pattern_filename = re.compile(r"^([xyz])([a-z\{\|\}~][a-z\{]|[a-z])(.*)(\d\d)\.prn$")
  
  #print(alphaID_or_filename)
  m_alphaID = pattern_alphaID.match(alphaID_or_filename)
  #print(m_alphaID)
  m_filename = pattern_filename.match(alphaID_or_filename)
  #print(m_filename)
  
  if m_alphaID:
    alphaID = m_alphaID.group(1)
  elif m_filename:
    #print(m_filename.groups())
    snap_plane = m_filename.group(1)
    alphaID = m_filename.group(2)
    probe_ident = m_filename.group(3)
    snap_time_number = m_filename.group(4)
  else:
    print('Me thinks you made a little mistake in your alphaID_or_filename...', file=sys.stderr)
    sys.exit(-1)

  if len(alphaID) == 1:
    numID = ord(alphaID) - ord('a') + 1
  elif len(alphaID) == 2:
    numID = 27*(ord(alphaID[0]) - ord('a') + 1) + (ord(alphaID[1]) - ord('a'))
  else:
    print('Me thinks you made a little mistake in your alphaID...', file=sys.stderr)
    sys.exit(-1)

  #if len(alphaID)==1 | len(alphaID)==2:
    #[tokens, match] =  regexp(alphaID, alphaID_pattern, 'tokens', 'match', 'warnings')
    #if length(match)==1:
      #snap_plane = 'x'
      #just_alphaID = alphaID
      #snap_time_number = 0
    #else:
      #print('Match error. Invalid alphaID.', file = sys.stderr)
      #sys.exit(-1)
      
  #elif len(alphaID)>2:
    #[tokens, match] =  regexp(alphaID, ['([xyz])',alphaID_pattern,probe_ident,'(..)\.prn'], 'tokens', 'match', 'warnings')
    
    #if len(match)==1:
      #snap_plane = tokens{:}(1)
      #just_alphaID = tokens{:}{2}
      #snap_time_number = str2num(tokens{:}{3})

      #ilo = mod(snap_time_number,10)
      #ihi = div(snap_time_number,10)
    
      #if len(just_alphaID)==1:
        #numID = double(just_alphaID(1)) - double('a') + 1
      #else:
        #numID = 27*(double(just_alphaID(1)) - double('a') + 1) + (double(just_alphaID(2)) - double('a'))

    #else:
      #warning(['Match error. Invalid alphaID:',' alphaID=',alphaID,' probe_ident=',probe_ident])
      #numID = 1
      #snap_plane = 'a'
      #snap_time_number = -1
  #else:
    #print('Me thinks you made a little mistake in your alphaID...', file=sys.stderr)
    #sys.exit(-1)
    
  return numID, snap_plane, probe_ident, snap_time_number
  
def main():
  N = 26 + (126-(ord('a')-1))*27
  for i in range(N):
    numID_in = i+1
    
    print('numID_to_alphaID(numID_in) check')
    filename_in, alphaID, pair = numID_to_alphaID(numID_in)
    print((filename_in, alphaID, pair))
    
    print('alphaID_to_numID(alphaID) check')
    numID_out, snap_plane, probe_ident, snap_time_number = alphaID_to_numID(alphaID)
    print((numID_out, snap_plane, probe_ident, snap_time_number))
    if numID_out != numID_in:
      sys.exit(-1)

    print('alphaID_to_numID(filename_in) check')
    numID_out, snap_plane, probe_ident, snap_time_number = alphaID_to_numID(filename_in)
    print((numID_out, snap_plane, probe_ident, snap_time_number))
    if numID_out != numID_in:
      sys.exit(-1)
    
  return

if __name__ == "__main__":
  main()
