#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from bfdtd.bfdtd_parser import *

import sys

# gaussian excitation template object which creates a 2D gaussian surface with a central maximum point
class ExcitationGaussian1:
  def __init__(self,amplitude = 1, beam_centre_x = 0, beam_centre_y = 0, sigma_x = 1, sigma_y = 1):
    self.amplitude = amplitude
    self.beam_centre_x = beam_centre_x
    self.beam_centre_y = beam_centre_y
    self.sigma_x = sigma_x
    self.sigma_y = sigma_y

  def writeDatFile(self,fileName,x_list,y_list,out_col_name,column_titles):
    '''Generate template .dat file for a plane excitation'''
    x_col = []
    y_col = []
    out_col = []
    
    for x in x_list:
      for y in y_list:
        x_col.append(x)
        y_col.append(y)
        X = x-self.beam_centre_x
        Y = y-self.beam_centre_y
        R = abs(sqrt( pow((X),2) + pow((Y),2) ))
        #out = self.amplitude * exp( -pow((R-c),2) / (2*pow(sigma,2)) )
        out = self.amplitude * exp( -( pow(X,2)/(2*pow(self.sigma_x,2)) + pow(Y,2)/(2*pow(self.sigma_y,2)) ) )
        out_col.append(out)
    
    # write file
    with open(fileName, 'w') as FILE:
      for idx_col in range(len(column_titles)):
        if idx_col>0:
          FILE.write('\t')
        FILE.write(column_titles[idx_col])
      FILE.write('\n')
      for idx_row in range(len(out_col)):
        #print(x_col[idx_row])
        FILE.write("%15.6E\t%15.6E" % (x_col[idx_row], y_col[idx_row]))
        for idx_col in range(len(column_titles)-2):
          if column_titles[idx_col+2] == out_col_name:
            FILE.write("\t%15.6E" % out_col[idx_row])
          else:
            FILE.write("\t%15.6E" % 0)
        FILE.write('\n')

    return

# gaussian excitation template object which creates a 2D gaussian surface with a circular maximum of radius c
class ExcitationGaussian2:
  def __init__(self,amplitude = 1, beam_centre_x = 0, beam_centre_y = 0, c = 1, sigma = 2):
    self.amplitude = amplitude
    self.beam_centre_x = beam_centre_x
    self.beam_centre_y = beam_centre_y
    self.c = c
    self.sigma = sigma

  def writeDatFile(self,fileName,x_list,y_list,out_col_name,column_titles):
    '''Generate template .dat file for a plane excitation'''
    x_col = []
    y_col = []
    out_col = []
    
    for x in x_list:
      for y in y_list:
        x_col.append(x)
        y_col.append(y)
        X = x-self.beam_centre_x
        Y = y-self.beam_centre_y
        R = abs(sqrt( pow((X),2) + pow((Y),2) ))
        out = self.amplitude * exp( -pow((R-self.c),2) / (2*pow(self.sigma,2)) )
        #out = self.amplitude * exp( -( pow(X,2)/(2*pow(sigma_x,2)) + pow(Y,2)/(2*pow(sigma_y,2)) ) )
        out_col.append(out)
    
    # write file
    with open(fileName, 'w') as FILE:
      for idx_col in range(len(column_titles)):
        if idx_col>0:
          FILE.write('\t')
        FILE.write(column_titles[idx_col])
      FILE.write('\n')
      for idx_row in range(len(out_col)):
        #print(x_col[idx_row])
        FILE.write("%15.6E\t%15.6E" % (x_col[idx_row], y_col[idx_row]))
        for idx_col in range(len(column_titles)-2):
          if column_titles[idx_col+2] == out_col_name:
            FILE.write("\t%15.6E" % out_col[idx_row])
          else:
            FILE.write("\t%15.6E" % 0)
        FILE.write('\n')

    return

#beam_centre_x = 2.1732
#beam_centre_y = 2.00
#c = 0
#sigma = 0.5
#sigma_x = 0.1
#sigma_y = 0.9

#x_min = 0.0
#x_max = 4.00
#y_min = 0.0
#y_max = 4.00
#step_x = 2.00e-2
#step_y = 2.00e-1
#x_list = arange(x_min,x_max,step_x)
#y_list = arange(y_min,y_max,step_y)

#print(len(x_list))
#print(len(y_list))

#x_col = []
#y_col = []
#out_col = []

#for x in x_list:
  #for y in y_list:
    #x_col.append(x)
    #y_col.append(y)
    #X = x-beam_centre_x
    #Y = y-beam_centre_y
    #R = abs(sqrt( pow((X),2) + pow((Y),2) ))
    ##out = exp( -pow((R-c),2) / (2*pow(sigma,2)) )
    #out = exp( -( pow(X,2)/(2*pow(sigma_x,2)) + pow(Y,2)/(2*pow(sigma_y,2)) ) )
    #out_col.append(out)

#fileName = sys.argv[1]
#E = [1,1,1]
#H = [1,1,1]
#out_col_name = 'Exre'

#column_titles = ['x','z','Exre','Exim','Eyre','Eyim','Ezre','Ezim','Hxre','Hxim','Hyre','Hyim','Hzre','Hzim']
#with open(fileName, 'w') as FILE:
  #for idx_col in range(len(column_titles)):
    #if idx_col>0:
      #FILE.write('\t')
    #FILE.write(column_titles[idx_col])
  #FILE.write('\n')
  #for idx_row in range(len(out_col)):
    ##print(x_col[idx_row])
    #FILE.write("%15.6E\t%15.6E" % (x_col[idx_row], y_col[idx_row]))
    #for idx_col in range(len(column_titles)-2):
      #if column_titles[idx_col+2] == out_col_name:
        #FILE.write("\t%15.6E" % out_col[idx_row])
      #else:
        #FILE.write("\t%15.6E" % 0)
    #FILE.write('\n')
