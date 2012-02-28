#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import numpy

class GWLobject:
  def __init__(self):
    self.GWL_voxels = []
    self.voxel_offset = [0,0,0,0]
  
  def addLine(self,P1,P2):
    write_sequence = [P1,P2]
    self.GWL_voxels.append(write_sequence)

  def addZGrating(self, P1, P2, LineNumber, LineDistance, BottomToTop = False):
    Zcenter = 0.5*(P1[2] + P2[2])
    zlist = []
    L = (LineNumber-1)*LineDistance
    if BottomToTop:
      zlist = numpy.linspace(Zcenter-0.5*L, Zcenter+0.5*L, LineNumber)
    else:
      zlist = numpy.linspace(Zcenter+0.5*L, Zcenter-0.5*L, LineNumber)
    #if LineNumber%2: #odd LineNumber
      #zlist = numpy.linspace(Zcenter-0.5*L, Zcenter+0.5*L, LineNumber)
    #else: #even LineNumber
      #zlist = numpy.arange(Zcenter-LineNumber/2*LineDistance, Zcenter+((LineNumber-1)/2+1)*LineDistance, LineDistance)
    for z in zlist:
      A = [P1[0],P1[1],z]
      B = [P2[0],P2[1],z]
      self.GWL_voxels.append([A,B])

  def addXblock(self, P1, P2, LineNumber_Horizontal, LineDistance_Horizontal, LineNumber_Vertical, LineDistance_Vertical, BottomToTop = False):
    Xcenter = 0.5*(P1[0] + P2[0])
    Ycenter = 0.5*(P1[1] + P2[1])
    Zcenter = 0.5*(P1[2] + P2[2])
    #print Zcenter
    #print LineNumber_Vertical

    ylist = []
    L = (LineNumber_Horizontal-1)*LineDistance_Horizontal
    ylist = numpy.linspace(Ycenter-0.5*L, Ycenter+0.5*L, LineNumber_Horizontal)
    
    zlist = []
    L = (LineNumber_Vertical-1)*LineDistance_Vertical
    if BottomToTop:
      zlist = numpy.linspace(Zcenter-0.5*L, Zcenter+0.5*L, LineNumber_Vertical)
    else:
      zlist = numpy.linspace(Zcenter+0.5*L, Zcenter-0.5*L, LineNumber_Vertical)

    for z in zlist:
      for y in ylist:
        A = [P1[0],y,z]
        B = [P2[0],y,z]
        self.GWL_voxels.append([A,B])

  def addYblock(self, P1, P2, LineNumber_Horizontal, LineDistance_Horizontal, LineNumber_Vertical, LineDistance_Vertical, BottomToTop = False):
    Xcenter = 0.5*(P1[0] + P2[0])
    Ycenter = 0.5*(P1[1] + P2[1])
    Zcenter = 0.5*(P1[2] + P2[2])

    xlist = []
    L = (LineNumber_Horizontal-1)*LineDistance_Horizontal
    xlist = numpy.linspace(Xcenter-0.5*L, Xcenter+0.5*L, LineNumber_Horizontal)
    
    zlist = []
    L = (LineNumber_Vertical-1)*LineDistance_Vertical
    if BottomToTop:
      zlist = numpy.linspace(Zcenter-0.5*L, Zcenter+0.5*L, LineNumber_Vertical)
    else:
      zlist = numpy.linspace(Zcenter+0.5*L, Zcenter-0.5*L, LineNumber_Vertical)

    for z in zlist:
      for x in xlist:
        A = [x,P1[1],z]
        B = [x,P2[1],z]
        self.GWL_voxels.append([A,B])

  def addHorizontalCircle(self, center, radius, power, PointDistance):
    #print radius
    write_sequence = []
    if radius == 0:
      write_sequence.append(center)
    else:
      alphaStep = 2*numpy.arcsin(PointDistance/float(2*radius))
      N = int(2*numpy.pi/alphaStep)
      for i in range(N):
        P = [center[0]+radius*numpy.cos(i*2*numpy.pi/float(N)),center[1]+radius*numpy.sin(i*2*numpy.pi/float(N)),center[2],power]
        write_sequence.append(P)
    self.GWL_voxels.append(write_sequence)

  def addHorizontalDisk(self, center, radius, power, PointDistance):
    N = int(radius/float(PointDistance))
    #print(('N = ',N))
    for i in range(N+1):
      if i==0:
        self.addHorizontalCircle(center, 0, power, PointDistance)
        ##print center
        #self.GWL_voxels.append([center])
      else:
        self.addHorizontalCircle(center, i*radius/float(N), power, PointDistance)

  def addSphere(self, center, radius, power, HorizontalPointDistance, VerticalPointDistance, solid = False):
    N = int(radius/float(VerticalPointDistance))
    for i in range(-N,N+1):
      z = i*radius/float(N)
      local_radius = numpy.sqrt(pow(radius,2)-pow(z,2))
      #print 'local_radius = ', local_radius
      if solid:
        self.addHorizontalDisk([center[0],center[1],center[2]+z], local_radius, power, HorizontalPointDistance)
      else:
        self.addHorizontalCircle([center[0],center[1],center[2]+z], local_radius, power, HorizontalPointDistance)

  def addWrite(self):
    write_sequence = []
    self.GWL_voxels.append(write_sequence)

  def readGWL(self,filename):
    Nvoxels = 0
    write_sequence = []
    with open(filename, 'r') as file:
      for line in file:
        #print line
        line_stripped = line.strip()
        # TODO: handle comments and other commands
        if len(line_stripped)>0 and line_stripped[0]!='%':
          cmd = re.split('[^a-zA-Z0-9_+-.]+',line_stripped)
          #cmd = [ i.lower() for i in cmd ]
          #print cmd
          if re.match(r"[a-zA-Z]",cmd[0][0]) or cmd[0]=='-999':
            #print '=>COMMAND'
            if cmd[0].lower()=='-999':
              if cmd[1]=='-999':
                #print 'write'
                self.GWL_voxels.append(write_sequence)
                write_sequence = []
            else:
              if cmd[0].lower()=='write':
                #print 'write'
                self.GWL_voxels.append(write_sequence)
                write_sequence = []
              elif cmd[0].lower()=='include':
                print 'including cmd[1]'
                self.readGWL(cmd[1])
              elif cmd[0].lower()=='movestagex':
                print 'Moving X by '+cmd[1]
                self.voxel_offset[0] = self.voxel_offset[0] + float(cmd[1])
              elif cmd[0].lower()=='movestagey':
                print 'Moving Y by '+cmd[1]
                self.voxel_offset[1] = self.voxel_offset[1] + float(cmd[1])
              #elif cmd[0].lower()=='defocusfactor':
                #print 'defocusfactor'
              #elif cmd[0].lower()=='laserpower':
                #print 'laserpower'
              else:
                print('UNKNOWN COMMAND: '+cmd[0])
                #sys.exit(-1)
          else:
            #print '=>VOXEL'
            voxel = []
            for i in range(len(cmd)):
              voxel.append(float(cmd[i])+self.voxel_offset[i])
            #voxel = [ float(i) for i in cmd ]
            write_sequence.append(voxel)
            Nvoxels = Nvoxels + 1
            
    print('Nvoxels = '+str(Nvoxels))
    #return GWL_voxels
  
  def write_GWL(self,filename):
    print('Writing GWL to '+filename)
    with open(filename, 'w') as file:
      for write_sequence in self.GWL_voxels:
        for voxel in write_sequence:
          for i in range(len(voxel)):
            file.write(str(voxel[i]))
            if i<len(voxel)-1:
              file.write('\t')
            else:
              file.write('\n')
        #file.write('-999\t-999\t-999\n')
        file.write('Write\n')
        
if __name__ == "__main__":
  #GWL_obj = GWLobject()
  #GWL_obj.readGWL(sys.argv[1])
  ##print GWL_obj.GWL_voxels
  #GWL_obj.write_GWL('copy.gwl')

  GWL_obj = GWLobject()
  GWL_obj.addXblock([0,0,0],[1,0,0],2,0.050,3,0.100)
  GWL_obj.addXblock([0,0,1.5],[1,0,1.5],2,0.050,3,0.100)
  GWL_obj.addXblock([0,0,2.75],[1,0,2.75],2,0.050,3,0.100)
  z = 7.1038825; GWL_obj.addXblock([0,0,z],[1,0,z],2,0.050,3,0.100)

  power = 75
  
  center = [0,0,3]
  HorizontalPointDistance = 0.050
  VerticalPointDistance = 0.100
  radius = 1
  
  #print 'addHorizontalCircle'
  GWL_obj.addHorizontalCircle(center, radius, power, HorizontalPointDistance)
  #print 'addHorizontalDisk'
  GWL_obj.addHorizontalDisk([center[0],center[1],center[2]+1], radius, power, HorizontalPointDistance)
  #print 'addSphere non-solid'
  GWL_obj.addSphere([center[0],center[1],center[2]+1+11], radius, power, HorizontalPointDistance, VerticalPointDistance, False)
  #print 'addSphere solid'
  GWL_obj.addSphere([center[0],center[1],center[2]+1+22], radius, power, HorizontalPointDistance, VerticalPointDistance, True)

  HorizontalPointDistance = 0.100
  VerticalPointDistance = 0.200
  center = [10,0,3]
  radius = 2
  GWL_obj.addHorizontalCircle(center, radius, power, HorizontalPointDistance)
  GWL_obj.addHorizontalDisk([center[0],center[1],center[2]+1], radius, power, HorizontalPointDistance)
  GWL_obj.addSphere([center[0],center[1],center[2]+1+11], radius, power, HorizontalPointDistance, VerticalPointDistance, False)
  GWL_obj.addSphere([center[0],center[1],center[2]+1+22], radius, power, HorizontalPointDistance, VerticalPointDistance, True)

  HorizontalPointDistance = 1
  VerticalPointDistance = 2
  center = [30,0,3]
  radius = 3
  GWL_obj.addHorizontalCircle(center, radius, power, HorizontalPointDistance)
  GWL_obj.addHorizontalDisk([center[0],center[1],center[2]+1], radius, power, HorizontalPointDistance)
  GWL_obj.addSphere([center[0],center[1],center[2]+1+11], radius, power, HorizontalPointDistance, VerticalPointDistance, False)
  GWL_obj.addSphere([center[0],center[1],center[2]+1+22], radius, power, HorizontalPointDistance, VerticalPointDistance, True)

  GWL_obj.write_GWL('xblock.gwl')
  
