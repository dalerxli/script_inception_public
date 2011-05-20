#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import getopt
import fnmatch
import os
import string
from optparse import OptionParser
import glob
import re
#from sets import Set
from subprocess import call

class Foo:
  def __init__(self, filename):
    self.Filename = filename
    pattern = re.compile("([xyz]).+id..\.E.mod\.max_1\.lambda\(nm\)_([\d.]+)\.freq\(Mhz\)_([\d.]+).pos\(mum\)_([\d.]+)\.png")
    m = pattern.match(self.Filename)
    #print m
    if m:
      #print m.groups()
      self.Plane = m.group(1)
      self.Lambda = float(m.group(2))
      self.Freq = float(m.group(3))
      self.Pos = float(m.group(4))
    else:
      print 'ERROR: NO MATCH : ', filename
      sys.exit(-1)

      #Xpos_set.add(pos)
      #freq_set.add(freq)
      #lambda_set.add(Lambda)

    #self.r = realpart
    #self.i = imagpart

os.chdir(sys.argv[1])

plane_filenames = glob.glob('[xyz]*.png')
plane_list=[]

Xpos_set=set([])
Ypos_set=set([])
Zpos_set=set([])
freq_set=set([])
lambda_set=set([])

for filename in plane_filenames:
  p = Foo(filename)
  plane_list.append(p)
  if p.Plane=='x':
    Xpos_set.add(p.Pos)
  elif p.Plane=='y':
    Ypos_set.add(p.Pos)
  else:
    Zpos_set.add(p.Pos)
  freq_set.add(p.Freq)
  lambda_set.add(p.Lambda)

Xpos_set=sorted(list(Xpos_set))
Ypos_set=sorted(list(Ypos_set))
Zpos_set=sorted(list(Zpos_set))
lambda_set=sorted(list(lambda_set))

print Xpos_set
print Ypos_set
print Zpos_set
print lambda_set

if len(Xpos_set)!=3:
  print 'len(Xpos_set)=',len(Xpos_set)
  sys.exit(-1)

if len(Ypos_set)!=3:
  print 'len(Ypos_set)=',len(Ypos_set)
  sys.exit(-1)

if len(Zpos_set)!=3:
  print 'len(Zpos_set)=',len(Zpos_set)
  sys.exit(-1)
    
print '=== To merge: ==='
for Lambda in lambda_set:
  for p in plane_list:
    if p.Plane=='x' and p.Pos==Xpos_set[1] and p.Lambda==Lambda:
      #print 'BIP 1'
      p1=p
    if p.Plane=='y' and p.Pos==Ypos_set[1] and p.Lambda==Lambda:
      #print 'BIP 2'
      p2=p
    if p.Plane=='z' and p.Pos==Zpos_set[1] and p.Lambda==Lambda:
      #print 'BIP 3'
      p3=p
  print p1.Filename+' + '+p2.Filename+' + '+p3.Filename+' -> '+str(Lambda)+'.png'
  cmd=['convert', p1.Filename, '(', p2.Filename, p3.Filename, '-append', ')', '-gravity', 'center', '+append', str(Lambda)+'.png']
  print cmd
  call(cmd)

print '=== To delete: ==='
for p in plane_list:
  print p.Filename
  os.remove(p.Filename)
  #if p.Plane=='x' and p.Pos==Xpos_set[0] or p.Pos==Xpos_set[2]:
    #print p.Filename
    #os.remove(p.Filename)
  
sys.exit(0)