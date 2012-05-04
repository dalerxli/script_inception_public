#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import getopt
import numpy
import math

class Usage(Exception):
  def __init__(self, msg):
    self.msg = msg

def fixLowerUpper(L,U):
  real_L = [0,0,0]
  real_U = [0,0,0]
  for i in range(3):
    real_L[i] = min(L[i],U[i])
    real_U[i] = max(L[i],U[i])
  return real_L, real_U

def LimitsToThickness(limits):
  return [ limits[i+1]-limits[i] for i in range(len(limits)-1) ]

#def getUnitaryDirection()
#E = subtract(excitation.P2,excitation.P1)
#E = list(E/linalg.norm(E))

def Unit(vec):
  ''' return unit vector parallel to vec. '''
  tot = numpy.linalg.norm(vec)
  if tot > 0.0:
    return vec/tot
  else:
    return vec

  #tot = Mag2(vec)
  #if tot > 0.0:
    #return vec*(1.0/math.sqrt(tot))
  #else:
    #return vec

def Mag2(vec):
  return vec[0]*vec[0] + vec[1]*vec[1] + vec[2]*vec[2]

def Mag(vec):
  ''' return the magnitude (rho in spherical coordinate system) '''
  return math.sqrt(Mag2(vec))

def getProbeColumnFromExcitation(excitation):
  print(('excitation = ',excitation))
  probe_col = 0
  if excitation == [1,0,0]:
    probe_col = 2
  elif excitation == [0,1,0]:
    probe_col = 3
  elif excitation == [0,0,1]:
    probe_col = 4
  else:
    print('ERROR in getProbeColumnFromExcitation: Unknown Excitation type')
    sys.exit(-1)
  print(('probe_col', probe_col))
  return probe_col

def symmetrifyEven(vec):
  ''' [1, 2, 3]->[1, 2, 3, 3, 2, 1] '''
  sym = vec[:]; sym.reverse()
  return vec + sym

def symmetrifyOdd(vec):
  ''' [1, 2, 3]->[1, 2, 3, 2, 1] '''
  sym = vec[:]; sym.reverse()
  return vec + sym[1:]

def symmetrifyAndSubtractOdd(vec,max):
  ''' [1, 2, 3]->[1, 2, 3, 8, 9] for max = 10
      [0, 1, 2, 3]->[0, 1, 2, 3, 4, 5, 6] for max = 6 '''
  sym = vec[:]; sym.reverse()
  sym_cut = [max-x for x in sym[1:]]
  return vec + sym_cut

def float_array(A):
    ''' convert string array to float array '''
    for i in range(len(A)):
        A[i]=float(A[i])
    return(A)
  
def int_array(A):
    ''' convert string array to int array '''
    for i in range(len(A)):
        A[i]=int(float(A[i]))
    return(A)


def is_number(s):
    ''' returns true if s can be converted to a float, otherwise false '''
    try:
        float(s)
        return True
    except ValueError:
        return False

def addExtension(filename, default_extension):
    ''' add default_extension if the file does not end in .geo or .inp '''
    
    extension = getExtension(filename)
    if extension == 'geo' or extension == 'inp':
        return filename
    else:
        return filename + '.' + default_extension

def getExtension(filename):
    ''' returns extension of filename '''
    return filename.split(".")[-1]

''' Returns ([1,0,0],'x'),etc corresponding to var(alpha or vector) '''
def getVecAlphaDirectionFromVar(var):
  S=['x','y','z']
  V=[[1,0,0],[0,1,0],[0,0,1]]
  if var in V:
    return var, S[var.index(1)]
  elif var.lower() in S:
    return V[S.index(var.lower())],var.lower()
  else:
    print('unknown direction: '+str(var))
    sys.exit(-1)
  
''' Returns numindex(1,2,3) and char('X','Y','Z') corresponding  to var(num or alpha index) '''
def planeNumberName(var):
  S=['X','Y','Z']
  if var in [1,2,3]:
    return var, S[var-1]
  elif var.upper() in S:
    return S.index(var.upper())+1,var.upper()
  else:
    print('unknown plane: '+str(var))
    sys.exit(-1)
