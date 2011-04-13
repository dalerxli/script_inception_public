#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TODO: Print function + print args into output files
# TODO: create FDTD object, store stuff in it and use its print function for output
# TODO: Get semiconductor micropillars working with it (BIG PROBLEM: orthogonal cylinders, cylinder in X direction => requires voxelization or working rotation FDTD or geo/inp rotation function...)
# TODO: enter a list of defect positions and sizes
# TODO: automatic meshing

from __future__ import division
from bfdtd.bristolFDTD_generator_functions import *
from constants.constants import *
from meshing.subGridMultiLayer import *
import numpy
from math import sqrt
from utilities.dumpObj import *
from bfdtd.bfdtd_parser import *

class pillar_1D:
  '''creates a 1D pillar with different kinds of irregularities'''
  def __init__(self):
    
    # filename stuff
    self.BASENAME = 'pillar_1D'
    self.DSTDIR = getuserdir()

    # debugging stuff
    self.verbose = False

    # switches
    self.print_mesh = True
    self.print_holes = True
    self.print_holes_top = True
    self.print_holes_bottom = True
    self.print_pillar = True
    self.print_podium = True
    self.print_snaphots = True
    self.print_freqsnap = True
    self.print_timesnap = True
    self.print_epssnap = True
    self.print_excitation = True
    self.print_probes = True

    # other variables
    self.HOLE_TYPE = 'rectangular_holes'
    self.bottom_N = 6; # number of holes on bottom (no unit)
    self.top_N = 3; # number of holes on top (no unit)
    self.Nvoxels = 10
    self.ITERATIONS = 32000
    self.FIRST=65400
    self.REPETITION=524200
    self.WALLTIME=360
    self.TIMESTEP=0.9; #mus
    self.TIME_CONSTANT=4.000000E-09; #mus
    self.AMPLITUDE=1.000000E+01; #V/mum???
    self.TIME_OFFSET=2.700000E-08; #mus
    self.SNAPSHOTS_FREQUENCY = []
    self.setLambda(0.637)
    self.excitation = Excitation()
    self.Ysymmetry = True
    self.Zsymmetry = False
    
    # refractive indices
    self.n_Substrate = 2.4 #no unit
    self.n_Defect = 1 #no unit
    self.n_Outside = 1
    self.n_bottomSquare = self.n_Substrate # no unit

    # distance between holes
    self.d_holes_mum = self.getLambda()/(4*self.n_Substrate)+self.getLambda()/(4*self.n_Defect) # in mum
    self.DistanceBetweenDefectBordersInCavity = self.getLambda()/self.n_Substrate
    # pillar radius
    self.radius_Y_pillar_mum = 0.200
    self.radius_Z_pillar_mum = 1
    # hole radius
    self.radius_X_hole = (self.getLambda()/(4*self.n_Defect))/2 # in mum
    self.radius_Y_hole = self.radius_Y_pillar_mum # in mum
    self.radius_Z_hole = self.radius_Z_pillar_mum - (self.d_holes_mum-2*self.radius_X_hole) # in mum
  
    # deltas (max mesh intervals)
    self.delta_X_center = self.getLambda()/(16*self.n_Substrate)
    self.delta_Y_center = self.delta_X_center
    self.delta_Z_center = self.delta_X_center

    self.delta_X_substrate = self.getLambda()/(10*self.n_Substrate)
    self.delta_Y_substrate = self.delta_X_substrate
    self.delta_Z_substrate = self.delta_X_substrate

    self.delta_X_hole = (2*self.radius_X_hole)/(2*self.Nvoxels+1)
    self.delta_Y_hole = self.getLambda()/(4*self.n_Defect)
    self.delta_Z_hole = (self.radius_Z_pillar_mum - self.radius_Z_hole)/(self.Nvoxels+1)
    
    self.delta_X_buffer = self.getLambda()/(7*self.n_Substrate)
    self.delta_Y_buffer = self.delta_X_buffer
    self.delta_Z_buffer = self.delta_X_buffer
    
    self.delta_X_outside = self.getLambda()/(4*self.n_Outside)
    self.delta_Y_outside = self.delta_X_outside
    self.delta_Z_outside = self.delta_X_outside
    
    self.delta_X_bottomSquare = self.getLambda()/(8*self.n_bottomSquare)

    # thickness of buffers (area outside pillar where mesh is fine)
    self.thickness_X_buffer = 32*self.delta_X_buffer; #mum
    self.thickness_Y_buffer = 4*self.delta_Y_buffer; #mum
    self.thickness_Z_buffer = 4*self.delta_Z_buffer; #mum

    # thickness of other
    self.thickness_X_bottomSquare = 0.5 # mum #bottom square thickness
    self.thickness_X_topBoxOffset = 1; #mum

    # center area where excitation takes place (for meshing)
    self.radius_X_center = 2*self.delta_X_center
    self.radius_Y_center = 2*self.delta_Y_center
    self.radius_Z_center = 2*self.delta_Z_center
  
    # box dimensions
    self.Xmax = self.thickness_X_bottomSquare + self.getPillarHeight() + self.thickness_X_buffer + self.thickness_X_topBoxOffset; #mum
    self.Ymax = 2*(self.radius_Y_pillar_mum + self.thickness_Y_buffer + 4*self.delta_Y_outside); #mum
    self.Zmax = 2*(self.radius_Z_pillar_mum + self.thickness_Z_buffer + 4*self.delta_Z_outside); #mum

    # 'private' variables, set when mesh() is called
    self.delta_X_vector = []
    self.delta_Y_vector = []
    self.delta_Z_vector = []
    self.probes_X_vector = []
    self.probes_Y_vector = []
    self.probes_Z_vector = []
    self.probes_X_vector_center = []
    self.probes_Y_vector_center = []
    self.probes_Z_vector_center = []

  def getPillarHeight(self):
    return (self.bottom_N+self.top_N)*self.d_holes_mum + self.getDistanceBetweenDefectBordersInCavity()

  def getLambda(self):
    return get_c0()/self.EXCITATION_FREQUENCY
    
  def getYlim(self):
    if self.Ysymmetry:
      return self.Ymax/2.0
    else:
      return self.Ymax

  def getZlim(self):
    if self.Zsymmetry:
      return self.Zmax/2.0
    else:
      return self.Zmax

  def getYoffset(self):
    if self.Ysymmetry:
      return self.delta_Y_center
    else:
      return 0

  def getZoffset(self):
    if self.Zsymmetry:
      return self.delta_Z_center
    else:
      return 0

  def setLambda(self,Lambda_mum):
    self.EXCITATION_FREQUENCY = get_c0()/Lambda_mum

  def setExcitationType(self, excitationType):

    # vars to set some parameters
    P_Ym1 = [ self.getPillarCenterX(), self.getPillarCenterY()-1*self.delta_Y_center, self.getPillarCenterZ() ]
    P_Ym2 = [ self.getPillarCenterX(), self.getPillarCenterY()-2*self.delta_Y_center, self.getPillarCenterZ() ]
    P_Zm1 = [ self.getPillarCenterX(), self.getPillarCenterY(), self.getPillarCenterZ()-1*self.delta_Z_center ]
    P_Zm2 = [ self.getPillarCenterX(), self.getPillarCenterY(), self.getPillarCenterZ()-2*self.delta_Z_center ]
    P_center = [ self.getPillarCenterX(), self.getPillarCenterY(), self.getPillarCenterZ() ]
    Ey = [ 0, 1, 0 ]
    Ez = [ 0, 0, 1 ]

    # common parameters
    self.excitation.current_source = current_source = 7
    self.excitation.H = [ 0, 0, 0 ]
    self.excitation.Type = 10
    self.excitation.time_constant = self.TIME_CONSTANT
    self.excitation.amplitude = self.AMPLITUDE
    self.excitation.time_offset = self.TIME_OFFSET
    self.excitation.frequency = self.EXCITATION_FREQUENCY
    self.excitation.param1 = 0
    self.excitation.param2 = 0
    self.excitation.param3 = 0
    self.excitation.param4 = 0
    self.excitation.P2 = P_center
  
    # distinct parameters
    if excitationType == 0:
      self.excitation.name = 'P_Ym1 excitation'
      self.excitation.P1 = P_Ym1
      self.excitation.E = Ey
      self.Ysymmetry = True
      self.Zsymmetry = False
    elif excitationType == 1:
      self.excitation.name = 'P_Zm1 excitation'
      self.excitation.P1 = P_Zm1
      self.excitation.E = Ez
      self.Ysymmetry = False
      self.Zsymmetry = True
    elif excitationType == 2:
      self.excitation.name = 'P_Ym2 excitation'
      self.excitation.P1 = P_Ym2
      self.excitation.E = Ey
      self.Ysymmetry = True
      self.Zsymmetry = False
    elif excitationType == 3:
      self.excitation.name = 'P_Zm2 excitation'
      self.excitation.P1 = P_Zm2
      self.excitation.E = Ez
      self.Ysymmetry = False
      self.Zsymmetry = True
    else:
      print('FATAL ERROR: invalid direction : '+str(excitationType))
      sys.exit(-1)

  def getExcitationType(self):
    if self.excitation.name == 'P_Ym1 excitation':
      return 'Ym1'
    elif self.excitation.name == 'P_Zm1 excitation':
      return  'Zm1'
    elif self.excitation.name == 'P_Ym2 excitation':
      return  'Ym2'
    elif self.excitation.name == 'P_Zm2 excitation':
      return 'Zm2'
    else:
      print('FATAL ERROR: invalid direction' + self.excitation.name)
      sys.exit(-1)

  def setRadiusPillarYZ(self,radius_Y,radius_Z):
    self.radius_Y_pillar_mum = radius_Y
    self.radius_Z_pillar_mum = radius_Z

  def setRadiusHole(self,radius_X,radius_Y,radius_Z):
    self.radius_X_hole = radius_X
    self.radius_Y_hole = radius_Y
    self.radius_Z_hole = radius_Z

  def setRadiusCenter(self,radius_X,radius_Y,radius_Z):
    self.radius_X_center = radius_X
    self.radius_Y_center = radius_Y
    self.radius_Z_center = radius_Z
  
  def setDeltaCenter(self,delta_X,delta_Y,delta_Z):
    self.delta_X_center = delta_X
    self.delta_Y_center = delta_Y
    self.delta_Z_center = delta_Z
    
  def setDeltaSubstrate(self,delta_X,delta_Y,delta_Z):
    self.delta_X_substrate = delta_X
    self.delta_Y_substrate = delta_Y
    self.delta_Z_substrate = delta_Z
    
  def setDeltaHole(self,delta_X,delta_Y,delta_Z):
    self.delta_X_hole = delta_X
    self.delta_Y_hole = delta_Y
    self.delta_Z_hole = delta_Z

  def setDeltaBuffer(self,delta_X,delta_Y,delta_Z):
    self.delta_X_buffer = delta_X
    self.delta_Y_buffer = delta_Y
    self.delta_Z_buffer = delta_Z
    
  def setDeltaOutside(self,delta_X,delta_Y,delta_Z):
    self.delta_X_outside = delta_X
    self.delta_Y_outside = delta_Y
    self.delta_Z_outside = delta_Z
  
  def setThicknessBuffer(self,thickness_X,thickness_Y,thickness_Z):
    self.thickness_X_buffer = thickness_X
    self.thickness_Y_buffer = thickness_Y
    self.thickness_Z_buffer = thickness_Z

########################################################################
  # "distance between defect centers in cavity"
  def getDistanceBetweenDefectCentersInCavity(self):
    return self.getDistanceBetweenDefectBordersInCavity() + 2*self.radius_X_hole
  def setDistanceBetweenDefectCentersInCavity(self,value):
    self.setDistanceBetweenDefectBordersInCavity(value - 2*self.radius_X_hole)
    
  # "distance between defect borders in cavity"
  def getDistanceBetweenDefectBordersInCavity(self):
    return self.DistanceBetweenDefectBordersInCavity
  def setDistanceBetweenDefectBordersInCavity(self,value):
    self.DistanceBetweenDefectBordersInCavity = value
  
  # "distance between defect pairs in cavity"
  def getDistanceBetweenDefectPairsInCavity(self):
    return self.getDistanceBetweenDefectBordersInCavity() + 2*self.radius_X_hole - self.d_holes_mum
  def setDistanceBetweenDefectPairsInCavity(self,value):
    self.setDistanceBetweenDefectBordersInCavity(value - 2*self.radius_X_hole + self.d_holes_mum)
    
########################################################################
  def getPillarCenterX(self):
    return self.thickness_X_bottomSquare + self.bottom_N*self.d_holes_mum + self.getDistanceBetweenDefectBordersInCavity()/2
    
  def getPillarCenterY(self):
    return self.Ymax/2
    
  def getPillarCenterZ(self):
    return self.Zmax/2

  def write(self):
    if not os.path.isdir(self.DSTDIR+os.sep+self.BASENAME):
      os.mkdir(self.DSTDIR+os.sep+self.BASENAME)
    self.mesh()
    print self.writeIN()
    self.writeSH()
    self.writeCMD()
    self.writeGEO()
    self.writeINP()

  def mesh(self):
    
    if not os.path.isdir(self.DSTDIR):
      print('error: self.DSTDIR = '+self.DSTDIR+'is not a directory')
      return('error')

    #print >>sys.stderr, 'self.radius_X_hole',self.radius_X_hole
    #print >>sys.stderr, 'self.radius_Z_hole',self.radius_Z_hole
    #print >>sys.stderr, 'self.d_holes_mum',self.d_holes_mum
    
    if self.radius_Z_hole<=0:
      if self.HOLE_TYPE == 'rectangular_holes':
        print >>sys.stderr, 'FATAL ERROR: negative self.radius_Z_hole = ',self.radius_Z_hole
        sys.exit(-1)
      #else:
        #print >>sys.stderr, 'WARNING: negative self.radius_Z_hole = ',self.radius_Z_hole

    if self.radius_Y_pillar_mum<self.radius_Y_hole:
      print >>sys.stderr, 'ERROR: self.radius_Y_pillar_mum = '+str(self.radius_Y_pillar_mum)+' < self.radius_Y_hole = '+str(self.radius_Y_hole)
      sys.exit(-1)

    if self.radius_Z_pillar_mum<self.radius_Z_hole:
      print >>sys.stderr, 'ERROR: self.radius_Z_pillar_mum = '+str(self.radius_Z_pillar_mum)+' < self.radius_Z_hole = '+str(self.radius_Z_hole)
      sys.exit(-1)

    ########################################################################
    # meshing parameters
    ########################################################################
    # adpapt mesh to excitation!!! excitation should go "into mesh", i.e. Y excitation=>cut box in Y plane, = Z excitation=>cut box in Z plane, Y+Z excitation=>do not cut box
    
    ###########################
    # X direction
    ###########################
    thicknessVector_X = [ ]
    max_delta_Vector_X = [ ]

    #print thicknessVector_X
    # under the pillar
    if self.thickness_X_bottomSquare>0:
      #print('self.thickness_X_bottomSquare = '+str(self.thickness_X_bottomSquare))
      thicknessVector_X += [ self.thickness_X_bottomSquare ]
      max_delta_Vector_X += [ self.delta_X_bottomSquare ]

    # bottom part
    for i in range(self.bottom_N):
      thicknessVector_X += [ self.d_holes_mum - 2*self.radius_X_hole, 2*self.radius_X_hole ]
      max_delta_Vector_X += [ self.delta_X_substrate, self.delta_X_hole ]
    # cavity
    thicknessVector_X += [ self.getDistanceBetweenDefectBordersInCavity()/2-self.radius_X_center, 2*self.radius_X_center, self.getDistanceBetweenDefectBordersInCavity()/2-self.radius_X_center ]
    max_delta_Vector_X += [ self.delta_X_substrate, self.delta_X_center, self.delta_X_substrate ]
    # top part
    for i in range(self.top_N):
      thicknessVector_X += [ 2*self.radius_X_hole, self.d_holes_mum - 2*self.radius_X_hole ]
      max_delta_Vector_X += [ self.delta_X_hole, self.delta_X_substrate ]
    
    # over the pillar
    if self.thickness_X_buffer>0:
      #print('self.thickness_X_buffer = '+str(self.thickness_X_buffer))
      thicknessVector_X +=[ self.thickness_X_buffer ];
      max_delta_Vector_X += [ self.delta_X_buffer ];
    if self.thickness_X_topBoxOffset>0:
      #print('self.thickness_X_topBoxOffset = '+str(self.thickness_X_topBoxOffset))
      thicknessVector_X +=[ self.thickness_X_topBoxOffset ];
      max_delta_Vector_X += [ self.delta_X_outside ];
      
    if self.verbose:
      print('==============')
      print 'thicknessVector_X = ', thicknessVector_X
      print('==============')
  
    delta_min = min(max_delta_Vector_X)
    ###########################
  
    ###########################
    # Y direction
    ###########################
    Y_BoxToBuffer = self.Ymax/2.0-self.radius_Y_pillar_mum-self.thickness_Y_buffer
    thicknessVector_Y_1 = [ Y_BoxToBuffer,
    self.thickness_Y_buffer,
    self.radius_Y_pillar_mum-self.radius_Y_hole,
    self.radius_Y_hole-self.radius_Y_center,
    self.radius_Y_center ]
    max_delta_Vector_Y_1 = [ self.delta_Y_outside, self.delta_Y_buffer, self.delta_Y_substrate, self.delta_Y_hole, self.delta_Y_center ]
    
    thicknessVector_Y_2 = thicknessVector_Y_1[:]; thicknessVector_Y_2.reverse()
    max_delta_Vector_Y_2 = max_delta_Vector_Y_1[:]; max_delta_Vector_Y_2.reverse();
    
    if self.Ysymmetry:
      thicknessVector_Y = thicknessVector_Y_1
      max_delta_Vector_Y = max_delta_Vector_Y_1
    else:
      thicknessVector_Y = thicknessVector_Y_1 + thicknessVector_Y_2
      max_delta_Vector_Y = max_delta_Vector_Y_1 + max_delta_Vector_Y_2
  
    #print 'thicknessVector_Y = ', thicknessVector_Y
    #print 'max_delta_Vector_Y = ', max_delta_Vector_Y

    if self.verbose:
      print('==============')
      print 'thicknessVector_Y = ', thicknessVector_Y
      print('==============')
    ###########################
  
    ###########################
    # Z direction
    ###########################
    Z_BoxToBuffer = self.Zmax/2.0-self.radius_Z_pillar_mum-self.thickness_Z_buffer
    if self.HOLE_TYPE == 'cylinder':
      thicknessVector_Z_1 = [ Z_BoxToBuffer,
      self.thickness_Z_buffer,
      self.radius_Z_pillar_mum-self.radius_Z_hole,
      self.radius_Z_hole-self.radius_Z_center,
      self.radius_Z_center ]
      max_delta_Vector_Z_1 = [ self.delta_Z_outside, self.delta_Z_buffer, self.delta_Z_substrate, self.delta_Z_hole, self.delta_Z_center ]
    elif self.HOLE_TYPE == 'square_holes':
      thicknessVector_Z_1 = [ Z_BoxToBuffer,
      self.thickness_Z_buffer,
      self.radius_Z_pillar_mum-self.radius_Z_hole,
      self.radius_Z_hole-self.radius_Z_center,
      self.radius_Z_center ]
      max_delta_Vector_Z_1 = [ self.delta_Z_outside, self.delta_Z_buffer, self.delta_Z_substrate, self.delta_Z_hole, self.delta_Z_center ]
    elif self.HOLE_TYPE == 'rectangular_holes':
      thicknessVector_Z_1 = [ Z_BoxToBuffer,
      self.thickness_Z_buffer,
      self.radius_Z_pillar_mum-self.radius_Z_hole,
      self.radius_Z_hole-self.radius_Z_center,
      self.radius_Z_center ]
      max_delta_Vector_Z_1 = [ self.delta_Z_outside, self.delta_Z_buffer, self.delta_Z_substrate, self.delta_Z_hole, self.delta_Z_center ]
    elif self.HOLE_TYPE == 'rectangular_yagi':
      thicknessVector_Z_1 = [ Z_BoxToBuffer,
      self.thickness_Z_buffer - (self.radius_Z_pillar_mum-self.radius_Z_hole),
      self.radius_Z_pillar_mum-self.radius_Z_hole,
      self.radius_Z_pillar_mum-self.radius_Z_hole,
      self.radius_Z_hole-self.radius_Z_center,
      self.radius_Z_center ]
      max_delta_Vector_Z_1 = [ self.delta_Z_outside, self.delta_Z_buffer, self.delta_Z_hole, self.delta_Z_hole, self.delta_Z_substrate, self.delta_Z_center ]
    elif self.HOLE_TYPE == 'triangular_yagi':
      radius_Z_piercer = self.radius_X_hole
      thicknessVector_Z_1 = [ Z_BoxToBuffer,
      self.thickness_Z_buffer - radius_Z_piercer,
      radius_Z_piercer,
      radius_Z_piercer,
      (self.radius_Z_pillar_mum - radius_Z_piercer)-self.radius_Z_center,
      self.radius_Z_center ]
      max_delta_Vector_Z_1 = [ self.delta_Z_outside, self.delta_Z_buffer, self.delta_Z_hole, self.delta_Z_hole, self.delta_Z_substrate, self.delta_Z_center ]
    elif self.HOLE_TYPE == 'triangular_yagi_voxel':
      thicknessVector_Z_1 = [ Z_BoxToBuffer,
      self.thickness_Z_buffer - (self.radius_Z_pillar_mum-self.radius_Z_hole),
      self.radius_Z_pillar_mum-self.radius_Z_hole,
      self.radius_Z_pillar_mum-self.radius_Z_hole,
      self.radius_Z_hole-self.radius_Z_center,
      self.radius_Z_center ]
      max_delta_Vector_Z_1 = [ self.delta_Z_outside, self.delta_Z_buffer, self.delta_Z_hole, self.delta_Z_hole, self.delta_Z_substrate, self.delta_Z_center ]
    elif self.HOLE_TYPE == 'triangular_yagi_voxel_sym':
      thicknessVector_Z_1 = [ Z_BoxToBuffer,
      self.thickness_Z_buffer - (self.radius_Z_pillar_mum-self.radius_Z_hole),
      self.radius_Z_pillar_mum-self.radius_Z_hole,
      self.radius_Z_pillar_mum-self.radius_Z_hole,
      self.radius_Z_hole-self.radius_Z_center,
      self.radius_Z_center ]
      max_delta_Vector_Z_1 = [ self.delta_Z_outside, self.delta_Z_buffer, self.delta_Z_hole, self.delta_Z_hole, self.delta_Z_substrate, self.delta_Z_center ]
    else:
      print >>sys.stderr, "ERROR: Unknown self.HOLE_TYPE "+self.HOLE_TYPE
      sys.exit(-1)

    thicknessVector_Z_2 = thicknessVector_Z_1[:]; thicknessVector_Z_2.reverse()
    max_delta_Vector_Z_2 = max_delta_Vector_Z_1[:]; max_delta_Vector_Z_2.reverse();
    
    if self.Zsymmetry:
      thicknessVector_Z = thicknessVector_Z_1
      max_delta_Vector_Z = max_delta_Vector_Z_1
    else:
      thicknessVector_Z = thicknessVector_Z_1 + thicknessVector_Z_2
      max_delta_Vector_Z = max_delta_Vector_Z_1 + max_delta_Vector_Z_2
    
    if self.verbose:
      print('==============')
      print 'thicknessVector_Z = ', thicknessVector_Z
      print('==============')
    #Mesh_ThicknessVector, Section_FinalDeltaVector = subGridMultiLayer([1,2,3,4,5],[5,4,3,2,1])
    #print('Mesh_ThicknessVector = '+str(Mesh_ThicknessVector))
    #print('Section_FinalDeltaVector = '+str(Section_FinalDeltaVector))
    
    #print('max_delta_Vector_X = '+str(max_delta_Vector_X))
    #print('thicknessVector_X = '+str(thicknessVector_X))
    #subGridMultiLayer(max_delta_Vector_X,thicknessVector_X)
    #print('============')
    
    if self.verbose:
      print max_delta_Vector_X; print thicknessVector_X
    self.delta_X_vector, local_delta_X_vector = subGridMultiLayer(max_delta_Vector_X,thicknessVector_X)

    if self.verbose:
      print max_delta_Vector_Y; print thicknessVector_Y
    self.delta_Y_vector, local_delta_Y_vector = subGridMultiLayer(max_delta_Vector_Y,thicknessVector_Y)

    if self.verbose:
      print max_delta_Vector_Z; print thicknessVector_Z
    self.delta_Z_vector, local_delta_Z_vector = subGridMultiLayer(max_delta_Vector_Z,thicknessVector_Z)
    ###########################
    ########################################################################
  
    ########################################################################
    # for snapshots
    ########################################################################

    self.Xplanes = [ 0, # 0 / 0
    self.thickness_X_bottomSquare, # 1 / -
    self.thickness_X_bottomSquare + (self.bottom_N//2)*self.d_holes_mum, # 2 / 1
    self.getPillarCenterX()-self.delta_X_center, # 3 / 2
    self.getPillarCenterX(), # 4 / 3
    self.getPillarCenterX()+self.delta_X_center, # 5 / 4
    self.thickness_X_bottomSquare + self.bottom_N*self.d_holes_mum + self.getDistanceBetweenDefectBordersInCavity() + (self.top_N//2)*self.d_holes_mum, # 6 / 5
    self.thickness_X_bottomSquare + self.getPillarHeight(), # 7 / 6
    self.thickness_X_bottomSquare + self.getPillarHeight()+1*self.delta_X_buffer,# 8 / -
    self.thickness_X_bottomSquare + self.getPillarHeight()+8*self.delta_X_buffer, # 9 / -
    self.thickness_X_bottomSquare + self.getPillarHeight()+32*self.delta_X_buffer, # 10 / -
    self.Xmax ] # 11 / -
    
    Yplanes_1 = [ 0,
    self.Ymax/2-self.radius_Y_pillar_mum-self.thickness_Y_buffer,
    self.Ymax/2-self.radius_Y_pillar_mum,
    self.Ymax/2-2*self.delta_Y_center,#3
    self.Ymax/2-self.delta_Y_center,#4
    self.Ymax/2 ]
    
    Zplanes_1 = [ 0,
    self.Zmax/2-self.radius_Z_pillar_mum-self.thickness_Z_buffer,
    self.Zmax/2-self.radius_Z_pillar_mum,
    self.Zmax/2-self.radius_Z_hole,#3
    self.Zmax/2-2*self.delta_Z_center,
    self.Zmax/2-self.delta_Z_center,#5
    self.Zmax/2 ]
    
    #print 'self.delta_X_center = ', self.delta_X_center
    #print 'self.delta_Y_center = ', self.delta_Y_center
    #print 'self.delta_Z_center = ', self.delta_Z_center
    #print 'self.Zmax/2 =', self.Zmax/2
    
    if self.Ysymmetry:
      self.Yplanes = Yplanes_1
    else:
      tmp = Yplanes_1[:]
      tmp.reverse()
      Yplanes_2 = [self.Ymax-x for x in tmp[1:]]
      self.Yplanes = Yplanes_1 + Yplanes_2

    if self.Zsymmetry:
      self.Zplanes = Zplanes_1
    else:
      tmp = Zplanes_1[:]
      tmp.reverse()
      Zplanes_2 = [self.Zmax-x for x in tmp[1:]]
      self.Zplanes = Zplanes_1 + Zplanes_2
    
    # remove duplicates (order of snapshots not important, in fact, ordered is better)
    self.Xplanes = list(set(self.Xplanes))
    self.Yplanes = list(set(self.Yplanes))
    self.Zplanes = list(set(self.Zplanes))
    self.Xplanes.sort()
    self.Yplanes.sort()
    self.Zplanes.sort()
    ########################################################################
    
    ########################################################################
    # for probes
    ########################################################################
    self.probes_X_vector = self.Xplanes[1:len(self.Xplanes)-1]
    self.probes_Y_vector = self.Yplanes[1:len(self.Yplanes)-1]
    self.probes_Z_vector = self.Zplanes[1:len(self.Zplanes)-1]

    self.probes_X_vector_center = [self.getPillarCenterX()-self.delta_X_center,
                                   self.getPillarCenterX(),
                                   self.getPillarCenterX()+self.delta_X_center]
    if self.Ysymmetry:
      self.probes_Y_vector_center = [self.getPillarCenterY()-self.delta_Y_center]
    else:
      self.probes_Y_vector_center = [self.getPillarCenterY()-self.delta_Y_center,
                                     self.getPillarCenterY(),
                                     self.getPillarCenterY()+self.delta_Y_center]
    if self.Zsymmetry:
      self.probes_Z_vector_center = [self.getPillarCenterZ()-self.delta_Z_center]
    else:
      self.probes_Z_vector_center = [self.getPillarCenterZ()-self.delta_Z_center,
                                     self.getPillarCenterZ(),
                                     self.getPillarCenterZ()+self.delta_Z_center]

    ########################################################################

    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Files to generate:
    # .in
    # .sh
    # .cmd
    # .geo
    # .inp
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  def writeIN(self):
    # .in file
    in_filename = self.DSTDIR+os.sep+self.BASENAME+os.sep+self.BASENAME+'.in'
    if self.verbose:
      print('Writing IN file '+in_filename+' ...')
    GEOin(in_filename, [ self.BASENAME+'.inp', self.BASENAME+'.geo' ])
    if self.verbose:
      print('...done')
    return(in_filename)
    
  def writeSH(self):
    # .sh file
    sh_filename = self.DSTDIR+os.sep+self.BASENAME+os.sep+self.BASENAME+'.sh';
    if self.verbose:
      print('Writing shellscript '+sh_filename+' ...')
    GEOshellscript(sh_filename, self.BASENAME, '$HOME/bin/fdtd', '$JOBDIR', self.WALLTIME)
    if self.verbose:
      print('...done')
    return(sh_filename)

  def writeCMD(self):
    # .cmd file
    cmd_filename = self.DSTDIR+os.sep+self.BASENAME+os.sep+self.BASENAME+'.cmd'
    if self.verbose:
      print('Writing CMD file '+cmd_filename+' ...')
    GEOcommand(cmd_filename, self.BASENAME)
    if self.verbose:
      print('...done')
    return(cmd_filename)
  
  def addHole(self, FILE, COMMENT, X_current, permittivity, conductivity):
    ''' adds a hole centered at  X_current '''
    centre = [ X_current, self.Ymax/2, self.Zmax/2 ]
    if self.HOLE_TYPE == 'cylinder':
      GEOcylinder(FILE, COMMENT, centre, 0, self.radius_X_hole, 2*self.radius_Y_pillar_mum, permittivity, conductivity, 0)
    elif self.HOLE_TYPE == 'square_holes':
      lower = [ X_current - self.radius_X_hole, self.Ymax/2 - self.radius_Y_pillar_mum, self.Zmax/2 - self.radius_X_hole]
      upper = [ X_current + self.radius_X_hole, self.Ymax/2 + self.radius_Y_pillar_mum, self.Zmax/2 + self.radius_X_hole]
      GEOblock(FILE, COMMENT, lower, upper, permittivity, conductivity)
    elif self.HOLE_TYPE == 'rectangular_holes':
      lower = [ X_current - self.radius_X_hole, self.Ymax/2 - self.radius_Y_pillar_mum, self.Zmax/2 - self.radius_Z_hole]
      upper = [ X_current + self.radius_X_hole, self.Ymax/2 + self.radius_Y_pillar_mum, self.Zmax/2 + self.radius_Z_hole]
      GEOblock(FILE, COMMENT, lower, upper, permittivity, conductivity)
    elif self.HOLE_TYPE == 'rectangular_yagi':
      lower = [ X_current - self.radius_X_hole, self.Ymax/2 - self.radius_Y_pillar_mum, self.Zmax/2 - self.radius_Z_pillar_mum - (self.radius_Z_pillar_mum - self.radius_Z_hole)]
      upper = [ X_current + self.radius_X_hole, self.Ymax/2 + self.radius_Y_pillar_mum, self.Zmax/2 - self.radius_Z_hole]
      GEOblock(FILE, COMMENT, lower, upper, permittivity, conductivity)
      lower = [ X_current - self.radius_X_hole, self.Ymax/2 - self.radius_Y_pillar_mum, self.Zmax/2 + self.radius_Z_hole]
      upper = [ X_current + self.radius_X_hole, self.Ymax/2 + self.radius_Y_pillar_mum, self.Zmax/2 + self.radius_Z_pillar_mum + (self.radius_Z_pillar_mum - self.radius_Z_hole)]
      GEOblock(FILE, COMMENT, lower, upper, permittivity, conductivity)
    elif self.HOLE_TYPE == 'triangular_yagi':
      lower = [ X_current - self.radius_X_hole/sqrt(2), self.Ymax/2 - self.radius_Y_pillar_mum, self.Zmax/2 - self.radius_Z_pillar_mum - self.radius_X_hole/sqrt(2)]
      upper = [ X_current + self.radius_X_hole/sqrt(2), self.Ymax/2 + self.radius_Y_pillar_mum, self.Zmax/2 - self.radius_Z_pillar_mum + self.radius_X_hole/sqrt(2)]
      GEOblock(FILE, COMMENT, lower, upper, permittivity, conductivity)
      GEOrotation(FILE, COMMENT, numpy.add(lower,upper)/2.0, [0,1,0], 45)
      lower = [ X_current - self.radius_X_hole/sqrt(2), self.Ymax/2 - self.radius_Y_pillar_mum, self.Zmax/2 + self.radius_Z_pillar_mum - self.radius_X_hole/sqrt(2)]
      upper = [ X_current + self.radius_X_hole/sqrt(2), self.Ymax/2 + self.radius_Y_pillar_mum, self.Zmax/2 + self.radius_Z_pillar_mum + self.radius_X_hole/sqrt(2)]
      GEOblock(FILE, COMMENT, lower, upper, permittivity, conductivity)
      GEOrotation(FILE, COMMENT, numpy.add(lower,upper)/2.0, [0,1,0], 45)
    elif self.HOLE_TYPE == 'triangular_yagi_voxel':
      voxel_Ymin = self.Ymax/2.0 - self.radius_Y_pillar_mum
      voxel_Ymax = self.Ymax/2.0 + self.radius_Y_pillar_mum
      voxel_radius_X = self.radius_X_hole/( 2.*self.Nvoxels + 1.)
      D = self.radius_Z_pillar_mum - self.radius_Z_hole
      R = self.radius_X_hole
      N = self.Nvoxels
      Z_left = self.Zmax/2.0 - self.radius_Z_pillar_mum
      Z_right = self.Zmax/2.0 + self.radius_Z_pillar_mum
      offset = X_current - self.radius_X_hole
      for i in range(self.Nvoxels):
        # bottom left blocks
        lower = [ offset+2*R*(i)/(2*N+1), voxel_Ymin, Z_left+D*(0)/(N+1)]
        upper = [ offset+2*R*(i + 1)/(2*N+1), voxel_Ymax, Z_left+D*(i + 1)/(N+1)]
        GEOblock(FILE, COMMENT, lower, upper, permittivity, conductivity)
        # top left blocks
        lower = [ offset+2*R*((2*N+1)-(i))/(2*N+1), voxel_Ymin, Z_left+D*(0)/(N+1)]
        upper = [ offset+2*R*((2*N+1)-(i + 1))/(2*N+1), voxel_Ymax, Z_left+D*(i + 1)/(N+1)]
        GEOblock(FILE, COMMENT, lower, upper, permittivity, conductivity)
        # bottom right blocks
        lower = [ offset+2*R*(i)/(2*N+1), voxel_Ymin, Z_right-D*(0)/(N+1)]
        upper = [ offset+2*R*(i + 1)/(2*N+1), voxel_Ymax, Z_right-D*(i + 1)/(N+1)]
        GEOblock(FILE, COMMENT, lower, upper, permittivity, conductivity)
        # top right blocks
        lower = [ offset+2*R*((2*N+1)-(i))/(2*N+1), voxel_Ymin, Z_right-D*(0)/(N+1)]
        upper = [ offset+2*R*((2*N+1)-(i + 1))/(2*N+1), voxel_Ymax, Z_right-D*(i + 1)/(N+1)]
        GEOblock(FILE, COMMENT, lower, upper, permittivity, conductivity)
      ## middle left block
      lower = [ offset+2*R*(N)/(2*N+1), voxel_Ymin, Z_left+D*(0)/(N+1)]
      upper = [ offset+2*R*(N + 1)/(2*N+1), voxel_Ymax, Z_left+D*(N + 1)/(N+1)]# - self.radius_Z_pillar_mum + D]
      GEOblock(FILE, COMMENT, lower, upper, permittivity, conductivity)
      ## middle right block
      lower = [ offset+2*R*(N)/(2*N+1), voxel_Ymin, Z_right-D*(0)/(N+1)]
      upper = [ offset+2*R*(N + 1)/(2*N+1), voxel_Ymax, Z_right-D*(N + 1)/(N+1)]# - self.radius_Z_pillar_mum + D]
      GEOblock(FILE, COMMENT, lower, upper, permittivity, conductivity)
    elif self.HOLE_TYPE == 'triangular_yagi_voxel_sym':
      voxel_Ymin = self.Ymax/2.0 - self.radius_Y_pillar_mum
      voxel_Ymax = self.Ymax/2.0 + self.radius_Y_pillar_mum
      voxel_radius_X = self.radius_X_hole/( 2.*self.Nvoxels + 1.)
      D = self.radius_Z_pillar_mum - self.radius_Z_hole
      R = self.radius_X_hole
      N = self.Nvoxels
      Z_left = self.Zmax/2.0 - self.radius_Z_pillar_mum
      Z_right = self.Zmax/2.0 + self.radius_Z_pillar_mum
      offset = X_current - self.radius_X_hole
      for i in range(self.Nvoxels):
        # bottom left blocks
        lower = [ offset+2*R*(i)/(2*N+1), voxel_Ymin, Z_left - D*(i + 1)/(N+1)]
        upper = [ offset+2*R*(i + 1)/(2*N+1), voxel_Ymax, Z_left + D*(i + 1)/(N+1)]
        GEOblock(FILE, COMMENT, lower, upper, permittivity, conductivity)
        # top left blocks
        lower = [ offset+2*R*((2*N+1)-(i))/(2*N+1), voxel_Ymin, Z_left - D*(i + 1)/(N+1)]
        upper = [ offset+2*R*((2*N+1)-(i + 1))/(2*N+1), voxel_Ymax, Z_left + D*(i + 1)/(N+1)]
        GEOblock(FILE, COMMENT, lower, upper, permittivity, conductivity)
        # bottom right blocks
        lower = [ offset+2*R*(i)/(2*N+1), voxel_Ymin, Z_right + D*(i + 1)/(N+1)]
        upper = [ offset+2*R*(i + 1)/(2*N+1), voxel_Ymax, Z_right - D*(i + 1)/(N+1)]
        GEOblock(FILE, COMMENT, lower, upper, permittivity, conductivity)
        # top right blocks
        lower = [ offset+2*R*((2*N+1)-(i))/(2*N+1), voxel_Ymin, Z_right + D*(i + 1)/(N+1)]
        upper = [ offset+2*R*((2*N+1)-(i + 1))/(2*N+1), voxel_Ymax, Z_right - D*(i + 1)/(N+1)]
        GEOblock(FILE, COMMENT, lower, upper, permittivity, conductivity)
      ## middle left block
      lower = [ offset+2*R*(N)/(2*N+1), voxel_Ymin, Z_left - D*(N + 1)/(N+1)]
      upper = [ offset+2*R*(N + 1)/(2*N+1), voxel_Ymax, Z_left + D*(N + 1)/(N+1)]# - self.radius_Z_pillar_mum + D]
      GEOblock(FILE, COMMENT, lower, upper, permittivity, conductivity)
      ## middle right block
      lower = [ offset+2*R*(N)/(2*N+1), voxel_Ymin, Z_right + D*(N + 1)/(N+1)]
      upper = [ offset+2*R*(N + 1)/(2*N+1), voxel_Ymax, Z_right - D*(N + 1)/(N+1)]# - self.radius_Z_pillar_mum + D]
      GEOblock(FILE, COMMENT, lower, upper, permittivity, conductivity)
    else:
      print >>sys.stderr, "WARNING: Unknown self.HOLE_TYPE "+self.HOLE_TYPE
    
  def writeGEO(self):
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # .geo file
    geo_filename = self.DSTDIR+os.sep+self.BASENAME+os.sep+self.BASENAME+'.geo'
    if self.verbose:
      print('Writing GEO file '+geo_filename+' ...')
  
    # open file
    with open(geo_filename, 'w') as out:
  
      # write header
      out.write('**GEOMETRY FILE\n')
      out.write('\n')
    
      # initialize current y
      X_current = 0
      
      if self.print_podium:
        # create bottom block
        L = [ 0, 0, 0 ]
        U = [ X_current + self.thickness_X_bottomSquare, self.Ymax, self.Zmax ]
        GEOblock(out, 'podium', L, U, pow(self.n_bottomSquare,2), 0)
  
      X_current = X_current + self.thickness_X_bottomSquare;
      
      if self.print_pillar:
        # create main pillar
        L = [ X_current, self.Ymax/2 - self.radius_Y_pillar_mum, self.Zmax/2 - self.radius_Z_pillar_mum ]
        U = [ X_current + self.getPillarHeight(), self.Ymax/2 + self.radius_Y_pillar_mum, self.Zmax/2 + self.radius_Z_pillar_mum ]
        GEOblock(out, 'main pillar', L, U, pow(self.n_Substrate,2), 0)
    
      X_current = X_current + (self.d_holes_mum - self.radius_X_hole)
    
      if self.print_holes:
          # hole settings
          permittivity = pow(self.n_Defect,2)
          conductivity = 0
          
          # create bottom holes
          for i in range(self.bottom_N):
            if self.print_holes_bottom:
              self.addHole(out, 'bottom hole', X_current, permittivity, conductivity)
            X_current = X_current + self.d_holes_mum
    
          X_current = X_current - self.d_holes_mum + self.getDistanceBetweenDefectCentersInCavity()
    
          # create top holes
          for i in range(self.top_N):
            if self.print_holes_top:
              self.addHole(out, 'top hole', X_current, permittivity, conductivity)
            X_current = X_current + self.d_holes_mum
          
      #write box
      L = [ 0, 0, 0 ]
      U = [ self.Xmax, self.getYlim(), self.getZlim() ]
      GEObox(out, 'box', L, U)
    
      #write footer
      out.write('end\n'); #end the file
    
      #close file
      out.close()
      if self.verbose:
        print('...done')
        
      return(geo_filename)

  def writeINP(self):
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # .inp file
    inp_filename = self.DSTDIR+os.sep+self.BASENAME+os.sep+self.BASENAME+'.inp'
    if self.verbose:
      print('Writing INP file '+inp_filename+' ...')
  
    # open file
    with open(inp_filename, 'w') as out:
  
      if self.print_excitation:
        self.excitation.write_entry(out)

      Xpos_bc = 2; Xpos_param = [1,1,0]
      if self.Ysymmetry:
        Ypos_bc = 1; Ypos_param = [1,1,0]
      else:
        Ypos_bc = 2; Ypos_param = [1,1,0]
      if self.Zsymmetry:
        Zpos_bc = 1; Zpos_param = [1,1,0]
      else:
        Zpos_bc = 2; Zpos_param = [1,1,0]
      Xneg_bc = 2; Xneg_param = [1,1,0]
      Yneg_bc = 2; Yneg_param = [1,1,0]
      Zneg_bc = 2; Zneg_param = [1,1,0]
      GEOboundary(out, 'boundary', Xpos_bc, Xpos_param, Ypos_bc, Ypos_param, Zpos_bc, Zpos_param, Xneg_bc, Xneg_param, Yneg_bc, Yneg_param, Zneg_bc, Zneg_param)
      
      iteration_method = 5
      propagation_constant = 0
      flag_1 = 0
      flag_2 = 0
      id_character = 'id'
      GEOflag(out, 'flag', iteration_method, propagation_constant, flag_1, flag_2, self.ITERATIONS, self.TIMESTEP, id_character)
    
      if self.print_mesh:
        GEOmesh(out, 'mesh', self.delta_X_vector, self.delta_Y_vector, self.delta_Z_vector)
          
      # frequency snapshots
      first = self.FIRST
      repetition = self.REPETITION
      interpolate = 1
      real_dft = 0
      mod_only = 0
      mod_all = 1
      starting_sample = 0
      E=[1,1,1]
      H=[1,1,1]
      J=[0,0,0]
      power = 0
      
      if self.print_snaphots == 1:
        
        #for iX in range(len(self.Xplanes)):
          #plane = 1
          #P1 = [self.Xplanes[iX], 0, 0]
          #P2 = [self.Xplanes[iX], self.getYlim(), self.getZlim()]
          #GEOfrequency_snapshot(out, 'X frequency snapshot', first, repetition, interpolate, real_dft, mod_only, mod_all, plane, P1, P2, self.SNAPSHOTS_FREQUENCY, starting_sample, E, H, J)
          #GEOtime_snapshot(out, 'X time snapshot', first, repetition, plane, P1, P2, E, H, J, power,0)
        #for iY in range(len(self.Yplanes)):
          #plane = 2
          #P1 = [0, self.Yplanes[iY], 0]
          #P2 = [self.Xmax, self.Yplanes[iY], self.getZlim()]
          #GEOfrequency_snapshot(out, 'Y frequency snapshot', first, repetition, interpolate, real_dft, mod_only, mod_all, plane, P1, P2, self.SNAPSHOTS_FREQUENCY, starting_sample, E, H, J)
          #GEOtime_snapshot(out, 'Y time snapshot', first, repetition, plane, P1, P2, E, H, J, power,0)
        #for iZ in range(len(self.Zplanes)):
          #plane = 3
          #P1 = [0, 0, self.Zplanes[iZ]]
          #P2 = [self.Xmax, self.getYlim(), self.Zplanes[iZ]]
          #GEOfrequency_snapshot(out, 'Z frequency snapshot', first, repetition, interpolate, real_dft, mod_only, mod_all, plane, P1, P2, self.SNAPSHOTS_FREQUENCY, starting_sample, E, H, J)
          #GEOtime_snapshot(out, 'Z time snapshot', first, repetition, plane, P1, P2, E, H, J, power,0)
        
        plane = 1
        P1 = [self.getPillarCenterX(), 0, 0]
        P2 = [self.getPillarCenterX(), self.getYlim(), self.getZlim()]
        GEOfrequency_snapshot(out, 'X frequency snapshot', first, repetition, interpolate, real_dft, mod_only, mod_all, plane, P1, P2, self.SNAPSHOTS_FREQUENCY, starting_sample, E, H, J)
        GEOtime_snapshot(out, 'X time snapshot', first, repetition, plane, P1, P2, E, H, J, power,0)
    
        plane = 2
        P1 = [0, self.Ymax/2-self.getYoffset(), 0]
        P2 = [self.Xmax, self.Ymax/2-self.getYoffset(), self.getZlim()]
        GEOfrequency_snapshot(out, 'Y frequency snapshot', first, repetition, interpolate, real_dft, mod_only, mod_all, plane, P1, P2, self.SNAPSHOTS_FREQUENCY, starting_sample, E, H, J)
        GEOtime_snapshot(out, 'Y time snapshot', first, repetition, plane, P1, P2, E, H, J, power,0)
    
        plane = 3
        P1 = [0, 0, self.Zmax/2-self.getZoffset()]
        P2 = [self.Xmax, self.getYlim(), self.Zmax/2-self.getZoffset()]
        GEOfrequency_snapshot(out, 'Z frequency snapshot', first, repetition, interpolate, real_dft, mod_only, mod_all, plane, P1, P2, self.SNAPSHOTS_FREQUENCY, starting_sample, E, H, J)
        GEOtime_snapshot(out, 'Z time snapshot', first, repetition, plane, P1, P2, E, H, J, power,0)
    
      if self.print_probes:
        # probes
        step=10
        E=[1,1,1]
        H=[1,1,1]
        J=[0,0,0]
        power = 0
        for iX in range(len(self.probes_X_vector)):
          # XY probes
          for iY in range(len(self.probes_Y_vector)):
            x = self.probes_X_vector[iX]
            y = self.probes_Y_vector[iY]
            z = self.Zmax/2-self.getZoffset()
            if not(x in self.probes_X_vector_center ) or not(y in self.probes_Y_vector_center ) or not(z in self.probes_Z_vector_center ):
              GEOprobe(out, 'XY probes', [x, y, z], step, E, H, J, power )
          # XZ probes
          for iZ in range(len(self.probes_Z_vector)):
            x = self.probes_X_vector[iX]
            y = self.Ymax/2-self.getYoffset()
            z = self.probes_Z_vector[iZ]
            if not(x in self.probes_X_vector_center ) or not(y in self.probes_Y_vector_center ) or not(z in self.probes_Z_vector_center ):
              GEOprobe(out, 'XZ probes', [x, y, z], step, E, H, J, power )
        
        # center probes
        for iX in range(len(self.probes_X_vector_center)):
          for iY in range(len(self.probes_Y_vector_center)):
            for iZ in range(len(self.probes_Z_vector_center)):
              GEOprobe(out, 'center probe ('+str(iX-1)+','+str(iY-1)+','+str(iZ-1)+')', [self.probes_X_vector_center[iX], self.probes_Y_vector_center[iY], self.probes_Z_vector_center[iZ]], step, E, H, J, power )
      
      #write footer
      out.write('end\n'); #end the file
    
      #close file
      out.close()
      if self.verbose:
        print('...done')
    
    return(inp_filename)

def main(argv=None):
  if argv is None:
      argv = sys.argv
  try:
    try:
      opts, args = getopt.getopt(argv[1:], "h", ["help"])
    except getopt.error, msg:
      raise Usage(msg)
    # main function
    P = pillar_1D()
    P.write()
    
  except Usage, err:
    print >>sys.stderr, err.msg
    print >>sys.stderr, "for help use --help"
    return 2

if __name__ == "__main__":
  sys.exit(main())
