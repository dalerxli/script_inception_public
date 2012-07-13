#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import numpy
import os

class GWLobject:
  def __init__(self):
    self.verbosity = 0
    self.GWL_voxels = []
    self.voxel_offset = [0,0,0,0]
    self.FindInterfaceAt = [0,0,0,0]
    self.stage_position = [0,0,0,0]
    self.LineNumber = 1
    self.LineDistance = 0
    self.PowerScaling = 1
    self.LaserPower = 100
    self.ScanSpeed = 200
    self.Repeat = 1
    self.path_substitutes = []
    self.writingTimeInSeconds = 0
    self.writingDistanceInMum = 0
    self.DwellTime = 200 # in ms = 1e-3 seconds
    self.minDistanceBetweenLines = 1000 # shortest distance from end of one line to start of next one
    self.maxDistanceBetweenLines = 0 # maximum acceptable distance from end of one line to start of next one
    self.LastVoxel = [0,0,0,0]
    self.LastVoxelSet = False
    self.out_of_range = False

  # TODO
  def getMinDistanceBetweenVoxels():
    return(0)

  def getLimits(self):
    Pmin = 4*[0]
    Pmax = 4*[0]
    first = True
    for write_sequence in self.GWL_voxels:
      for voxel in write_sequence:
        if first:
            for i in range(len(voxel)):
                Pmin[i] = voxel[i]
                Pmax[i] = voxel[i]
            first = False
        else:
            for i in range(len(voxel)):
                if voxel[i] < Pmin[i]:
                    Pmin[i] = voxel[i]
                if Pmax[i] < voxel[i]:
                    Pmax[i] = voxel[i]
    return (Pmin,Pmax)

  def getLastVoxel(self):
    found = False
    voxel = [0,0,0,0]
    for i in range(len(self.GWL_voxels)):
        write_sequence = self.GWL_voxels[-i]
        if len(write_sequence)>0:
            voxel = write_sequence[-1]
            found = True
            break
    return (voxel,found)

  def getNvoxels():
    print('ok')

  def clear(self):
    self.GWL_voxels = []
    self.voxel_offset = [0,0,0,0]

  def addLine(self,P1,P2,power=-1):
    write_sequence = [P1,P2]
    self.GWL_voxels.append(write_sequence)

  def addLineCylinder(self, P1, P2, power, inner_radius, outer_radius, PointDistance_r, PointDistance_theta):
    # prepare some variables
    v = numpy.array(P2)-numpy.array(P1) # vector to rotate
    centro = 0.5*(numpy.array(P2)+numpy.array(P1)) # center of LineCylinder
    u = numpy.array([0,0,1]) # direction of standard TubeWithVerticalLines
    theta = Angle(u,v) # angle by which to rotate
    rotation_axis = numpy.cross(u,v) # axis around which to rotate
    height = numpy.norm(v)
    
    # build a basis from the P1-P2 direction
    i = v
    j = Orthogonal(i)
    k = numpy.cross(i,j)
    
    # transformation matrix from (x,y,z) into (i,j,k)
    P = numpy.transpose(numpy.matrix([i,j,k]))

    # create a vertical tube and rotate it
    tube = GWLobject()
    tube.addTubeWithVerticalLines(centro, inner_radius, outer_radius, height, power, PointDistance_r, PointDistance_theta, downwardWriting=False)
    tube.applyTransformationMatrix(P.getI(), centro)
    self.addGWLobject(tube)
    return

  def addGWLobject(self, obj):
    self.GWL_voxels += obj.GWL_voxels
    #for write_sequence in tube.GWL_voxels:
          #self.GWL_voxels.append(write_sequence)

      #for voxel in write_sequence:
        #for i in range(len(voxel)):
          #value = voxel[i] + writingOffset[i]
          #if i!=3: #coordinates
            #file.write( str( "%.3f" % (value) ) )
          #else: #power
            #if 0<=value and value<=100:
              #file.write( str( "%.3f" % (value) ) )
          ## add tab or line ending
          #if i<len(voxel)-1:
            #file.write('\t')
          #else:
            #file.write('\n')

            
      #self.addWrite()

    #for write_sequence in obj.GWL_voxels:
      #for voxel in write_sequence:
        #self.add
          
        #voxel = write_sequence[i]
        #location = [voxel[0],voxel[1],voxel[2]]
        #if len(voxel)>3:
          #power = voxel[3]
        #else:
          #power = -1
        ##point = point - centro
        #location = P.getI()*numpy.transpose(numpy.matrix(location))
        #location = centro + location
        #write_sequence[i] = [location[0],location[1],location[2],power]
    

  def addTubeWithVerticalLines(self, centro, inner_radius, outer_radius, height, power, PointDistance_r, PointDistance_theta, downwardWriting=True):
    for radius in numpy.linspace(inner_radius, outer_radius, float(1+(outer_radius - inner_radius)/PointDistance_r)):
      if radius < 0.5*PointDistance_theta:
        # TODO: power argument could probably be passed through centro?
        P = numpy.array([centro[0],centro[1],centro[2],power])
        if downwardWriting:
          self.addLine(P+0.5*height*numpy.array([0,0,1,0]),P-0.5*height*numpy.array([0,0,1,0]), power) # Downward writing
        else:
          self.addLine(P-0.5*height*numpy.array([0,0,1,0]),P+0.5*height*numpy.array([0,0,1,0]), power) # Upward writing
      else:
        alphaStep = 2*numpy.arcsin(PointDistance_theta/float(2*radius))
        N = int(2*numpy.pi/alphaStep)
        for i in range(N):
          P = numpy.array([centro[0]+radius*numpy.cos(i*2*numpy.pi/float(N)),centro[1]+radius*numpy.sin(i*2*numpy.pi/float(N)),centro[2],power])
          if downwardWriting:
            self.addLine(P+0.5*height*numpy.array([0,0,1,0]),P-0.5*height*numpy.array([0,0,1,0]), power) # Downward writing
          else:
            self.addLine(P-0.5*height*numpy.array([0,0,1,0]),P+0.5*height*numpy.array([0,0,1,0]), power) # Upward writing
    return
    
  def rotate(self, rotation_axis, theta):
    #TODO    
    #numpy.dot(rotation_matrix(rotation_axis,theta),P)
    return
    
  # TODO: Use better names/transformation system to implement translations
  def applyTransformationMatrix(P, centro):
    for write_sequence in self.GWL_voxels:
      for i in range(len(write_sequence)):
        voxel = write_sequence[i]
        location = [voxel[0],voxel[1],voxel[2]]
        if len(voxel)>3:
          power = voxel[3]
        else:
          power = -1
        #point = point - centro
        location = P.getI()*numpy.transpose(numpy.matrix(location))
        location = centro + location
        write_sequence[i] = [location[0],location[1],location[2],power]
    return

  def addHorizontalGrating(self, P1, P2, LineNumber, LineDistance):
    u = numpy.array(P2)-numpy.array(P1)
    u = u*1.0/numpy.sqrt(pow(u[0],2)+pow(u[1],2)+pow(u[2],2))
    v = numpy.array([-u[1],u[0],0])
    L = (LineNumber-1)*LineDistance
    P1_min = P1 - 0.5*L*v

    plist = []
    for k in range(LineNumber):
        A = P1_min + k*LineDistance*v
        B = A + (P2-P1)
        plist.append((A,B))

    counter = 0
    for (A,B) in plist:
      if counter%2 == 0:
        self.GWL_voxels.append([A,B])
      else:
        self.GWL_voxels.append([B,A])
      counter = counter + 1

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
    counter = 0
    for z in zlist:
      A = [P1[0],P1[1],z]
      B = [P2[0],P2[1],z]
      if counter%2 == 0:
        self.GWL_voxels.append([A,B])
      else:
        self.GWL_voxels.append([B,A])
      counter = counter + 1

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

    counter = 0
    for z in zlist:
      for y in ylist:
        A = [P1[0],y,z]
        B = [P2[0],y,z]
        if counter%2 == 0:
          self.GWL_voxels.append([A,B])
        else:
          self.GWL_voxels.append([B,A])
        counter = counter + 1

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

    counter = 0
    for z in zlist:
      for x in xlist:
        A = [x,P1[1],z]
        B = [x,P2[1],z]
        if counter%2 == 0:
          self.GWL_voxels.append([A,B])
        else:
          self.GWL_voxels.append([B,A])
        counter = counter + 1

  def addTube(self, centro, inner_radius, outer_radius, height, power, PointDistance_r, PointDistance_theta, PointDistance_z):
    print('=== addTube ===')
    #print((numpy.linspace(inner_radius, outer_radius, float((outer_radius - inner_radius)/PointDistance_r))))
    for radius in numpy.linspace(inner_radius, outer_radius, float(1+(outer_radius - inner_radius)/PointDistance_r)):
      for z in numpy.linspace(centro[2]+0.5*height, centro[2]-0.5*height, float(1+height/PointDistance_z)):
        print((radius,z))
      #for i_theta in numpy.linspace(0, 2*numpy.pi, (outer_radius - inner_radius)/PointDistance_r):
        self.addHorizontalCircle([centro[0],centro[1],z], radius, power, PointDistance_theta)
    return

  def addHorizontalCircle(self, center, radius, power, PointDistance):
    #print radius
    write_sequence = []
    if radius < 0.5*PointDistance:
      write_sequence.append(center)
    else:
      #print(('PointDistance = ', PointDistance))
      #print radius
      #print PointDistance/float(2*radius)
      alphaStep = 2*numpy.arcsin(PointDistance/float(2*radius))
      N = int(2*numpy.pi/alphaStep)
      for i in range(N):
        if 0<=power and power<=100:
          P = [center[0]+radius*numpy.cos(i*2*numpy.pi/float(N)),center[1]+radius*numpy.sin(i*2*numpy.pi/float(N)),center[2],power]
        else:
          P = [center[0]+radius*numpy.cos(i*2*numpy.pi/float(N)),center[1]+radius*numpy.sin(i*2*numpy.pi/float(N)),center[2]]
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

    PointDistance = numpy.sqrt(pow(HorizontalPointDistance,2)+pow(VerticalPointDistance,2))
    #print PointDistance
    if radius == 0:
      self.GWL_voxels.append([center])
    else:
      alphaStep = 2*numpy.arcsin(PointDistance/float(2*radius))
      N = int(0.5*numpy.pi/alphaStep)
      zlist = []
      for i in range(N+1):
        #print(('i = ',i,' N = ',N))
        z = radius*numpy.cos(i*0.5*numpy.pi/float(N))
        zlist.append(z)

      # symetrify list
      zlist = zlist + [ -i for i in zlist[len(zlist)-2::-1] ]

      for z in sorted(zlist, reverse=True):
        local_radius = numpy.sqrt(pow(radius,2)-pow(z,2))
        #print(('local_radius 1 = ',local_radius))
        #local_radius = radius*numpy.sin(i*numpy.pi/float(N))
        #print(('local_radius 2 = ',local_radius))
        if solid:
          self.addHorizontalDisk([center[0],center[1],center[2]+z], local_radius, power, HorizontalPointDistance)
        else:
          self.addHorizontalCircle([center[0],center[1],center[2]+z], local_radius, power, HorizontalPointDistance)

    #N = int(radius/float(VerticalPointDistance))
    #for i in range(-N,N+1):
      #z = i*radius/float(N)
      #local_radius = numpy.sqrt(pow(radius,2)-pow(z,2))
      ##print 'local_radius = ', local_radius
      #if solid:
        #self.addHorizontalDisk([center[0],center[1],center[2]+z], local_radius, power, HorizontalPointDistance)
      #else:
        #self.addHorizontalCircle([center[0],center[1],center[2]+z], local_radius, power, HorizontalPointDistance)

  def addWrite(self):
    write_sequence = []
    self.GWL_voxels.append(write_sequence)

  def readSubstitutes(self, subsFile):
    print(('Reading substitution pairs from '+subsFile))
    self.path_substitutes = []
    try:
      with open(subsFile, 'r') as file:
        for line in file:
          t = line.strip().split('->')
          if len(t)==2:
            old = t[0].strip()
            new = t[1].strip()
            old = old.replace('\\',os.path.sep).replace('/',os.path.sep)
            new = new.replace('\\',os.path.sep).replace('/',os.path.sep)
            print((old+' -> '+new))
            self.path_substitutes.append((old,new))
    #TODO: reimplement nice exception system
    #except IOError as (errno, strerror):
    except:
      #print "I/O error({0}): {1}".format(errno, strerror)
      print(('Failed to open '+subsFile))

    return self.path_substitutes

  def readGWL(self, filename):
    Nvoxels = 0
    write_sequence = []
    try:
      with open(filename, 'r') as file:
        for line in file:
          #print line
          line_stripped = line.strip()
          # TODO: handle comments and other commands
          if len(line_stripped)>0 and line_stripped[0]!='%':
            #print 'pre-split: ', line_stripped
            #cmd = re.split('[^a-zA-Z0-9_+-.]+',line_stripped)
            #cmd = re.split('[^a-zA-Z0-9_+-.:\\/]+',line_stripped)
            #cmd = re.split('[ \t]',line_stripped)
            cmd = re.split('\s+',line_stripped)
            #cmd = [ i.lower() for i in cmd ]
            #print 'post-split: ', cmd
            stopRepeat = True
            for i in range(self.Repeat):
              if re.match(r"[a-zA-Z]",cmd[0][0]) or cmd[0]=='-999' or cmd[0].lower()=='-999.000':
                if cmd[0].lower()=='-999' or cmd[0].lower()=='-999.000':
                  #print('match 999')
                  if cmd[1]=='-999' or cmd[1].lower()=='-999.000':
                    self.GWL_voxels.append(write_sequence)
                    write_sequence = []
                    self.writingTimeInSeconds = self.writingTimeInSeconds + 1e-3*self.DwellTime
                    self.maxDistanceBetweenLines = self.ScanSpeed*1e-3*self.DwellTime
                else:
                  #print('other match')
                  if cmd[0].lower()=='write':
                    self.GWL_voxels.append(write_sequence)
                    write_sequence = []
                    self.writingTimeInSeconds = self.writingTimeInSeconds + 1e-3*self.DwellTime
                    self.maxDistanceBetweenLines = self.ScanSpeed*1e-3*self.DwellTime
                  elif cmd[0].lower()=='include':
                    print(('line_stripped = ' + line_stripped))
                    file_to_include = re.split('\s+',line_stripped,1)[1]
                    print(('including file_to_include = ' + file_to_include))
                    print('Fixing file separators')
                    file_to_include = file_to_include.replace('\\',os.path.sep).replace('/',os.path.sep)
                    print(('including file_to_include = ' + file_to_include))
                    file_to_include_fullpath = os.path.normpath(os.path.join(os.path.dirname(filename), os.path.expanduser(file_to_include)))
                    print(file_to_include_fullpath)
                    if not os.path.isfile(file_to_include_fullpath):
                      print('WARNING: File not found. Attempting path substitutions')
                      for (old,new) in self.path_substitutes:
                        file_to_try = file_to_include.replace(old,new)
                        #print('file_to_try = ',file_to_try)
                        #print('filename = ',filename)
                        #print('os.path.dirname(filename) = ',os.path.dirname(filename))
                        file_to_try = os.path.normpath(os.path.join(os.path.dirname(filename), os.path.expanduser(file_to_try)))
                        if self.verbosity > 10:
                          print(('old = ' + old))
                          print(('new = ' + new))
                          print(('file_to_include = ' + file_to_include))
                          print(('filename = ' + filename))
                        print(('Trying file_to_try = ' + file_to_try))
                        if os.path.isfile(file_to_try):
                          file_to_include_fullpath = file_to_try
                          break
                    self.readGWL(file_to_include_fullpath)

                  elif cmd[0].lower()=='movestagex':
                    print(('Moving X by '+cmd[1]))
                    self.stage_position[0] = self.stage_position[0] + float(cmd[1])
                  elif cmd[0].lower()=='movestagey':
                    print(('Moving Y by '+cmd[1]))
                    self.stage_position[1] = self.stage_position[1] + float(cmd[1])

                  elif cmd[0].lower()=='addxoffset':
                    print('Adding X offset of '+cmd[1])
                    self.voxel_offset[0] = self.voxel_offset[0] + float(cmd[1])
                  elif cmd[0].lower()=='addyoffset':
                    print('Adding Y offset of '+cmd[1])
                    self.voxel_offset[1] = self.voxel_offset[1] + float(cmd[1])
                  elif cmd[0].lower()=='addzoffset':
                    print('Adding Z offset of '+cmd[1])
                    self.voxel_offset[2] = self.voxel_offset[2] + float(cmd[1])

                  elif cmd[0].lower()=='xoffset':
                    print('Setting X offset to '+cmd[1])
                    self.voxel_offset[0] = float(cmd[1])
                  elif cmd[0].lower()=='yoffset':
                    print('Setting Y offset to '+cmd[1])
                    self.voxel_offset[1] = float(cmd[1])
                  elif cmd[0].lower()=='zoffset':
                    print('Setting Z offset to '+cmd[1])
                    self.voxel_offset[2] = float(cmd[1])

                  elif cmd[0].lower()=='linenumber':
                    print('Setting LineNumber to '+cmd[1])
                    self.LineNumber = float(cmd[1])
                  elif cmd[0].lower()=='linedistance':
                    print('Setting LineDistance to '+cmd[1])
                    self.LineDistance = float(cmd[1])
                  elif cmd[0].lower()=='powerscaling':
                    print('Setting PowerScaling to '+cmd[1])
                    self.PowerScaling = float(cmd[1])
                  elif cmd[0].lower()=='laserpower':
                    if self.verbosity > 5:
                      print('Setting LaserPower to '+cmd[1])
                    self.LaserPower = float(cmd[1])
                  elif cmd[0].lower()=='scanspeed':
                    print('Setting ScanSpeed to '+cmd[1])
                    self.ScanSpeed = float(cmd[1])

                  elif cmd[0].lower()=='repeat':
                    print('Repeating next command '+cmd[1]+' times.')
                    self.Repeat = int(cmd[1])
                    stopRepeat = False

                  #elif cmd[0].lower()=='defocusfactor':
                    #print 'defocusfactor'

                  elif cmd[0].lower()=='findinterfaceat':
                    print('Setting FindInterfaceAt to '+cmd[1])
                    self.FindInterfaceAt = [0,0,float(cmd[1]),0]

                  elif cmd[0].lower()=='dwelltime':
                    print('Setting DwellTime to '+cmd[1])
                    self.DwellTime = float(cmd[1])


                  else:
                    print(('UNKNOWN COMMAND: '+cmd[0]))
                    #sys.exit(-1)
              else:
                #print '=>VOXEL'
                voxel = []
                for i in range(len(cmd)):
                  piezo_position = float(cmd[i]) + self.voxel_offset[i]
                  if piezo_position<0 or piezo_position>300:
                    if not self.out_of_range:
                      print('ERROR: voxel out of range! len(voxel) = '+str(len(voxel))+' piezo_position = '+str(piezo_position)+' i = '+str(i), file=sys.stderr)
                      print('piezo_position = float(cmd[i]) + self.voxel_offset[i]', file=sys.stderr)
                      print(str(piezo_position)+' = '+str(float(cmd[i]))+' + '+str(self.voxel_offset[i]), file=sys.stderr)
                      print('filename = '+str(filename), file=sys.stderr)
                      print('cmd = '+str(cmd), file=sys.stderr)
                      self.out_of_range = True
                    #sys.exit(-1)
                  voxel.append( piezo_position + self.stage_position[i] - self.FindInterfaceAt[i] )
                #voxel = [ float(i) for i in cmd ]
                (last_voxel,found_last_voxel) = self.getLastVoxel()
                write_sequence.append(voxel)
                if len(write_sequence)>=2:
                    a = write_sequence[-2][0:3]
                    b = write_sequence[-1][0:3]
                    newDist = numpy.linalg.norm(numpy.array(b)-numpy.array(a))
                    newTime = newDist/self.ScanSpeed
                    self.writingTimeInSeconds = self.writingTimeInSeconds + newTime
                    self.writingDistanceInMum = self.writingDistanceInMum + newDist
                elif found_last_voxel:
                    a = last_voxel[0:3]
                    b = write_sequence[-1][0:3]
                    newDist = numpy.linalg.norm(numpy.array(b)-numpy.array(a))
                    newTime = newDist/self.ScanSpeed
                    self.writingTimeInSeconds = self.writingTimeInSeconds + newTime
                    self.writingDistanceInMum = self.writingDistanceInMum + newDist

                Nvoxels = Nvoxels + 1

            # reset repeat
            if stopRepeat:
                self.Repeat = 1
    except IOError as xxx_todo_changeme:
      (errno, strerror) = xxx_todo_changeme.args
      print("I/O error({0}): {1}".format(errno, strerror))
      print('Failed to open '+filename)

    print(('Nvoxels = '+str(Nvoxels)))
    if self.verbosity >= 0:
      print(('self.writingTimeInSeconds = '+str(self.writingTimeInSeconds)))
      print(('self.writingTimeInMinutes = '+str(self.writingTimeInSeconds/60.)))
      print(('self.writingTimeInHours = '+str(self.writingTimeInSeconds/(60.*60.))))
      print(('self.writingDistanceInMum = '+str(self.writingDistanceInMum)))
    #return GWL_voxels

  def write_GWL(self, filename, writingOffset = [0,0,0,0]):
    print(('Writing GWL to '+filename))
    with open(filename, 'w') as file:
      for write_sequence in self.GWL_voxels:
        for voxel in write_sequence:
          
          # TODO: add options to enable/disable warnings for coords/power out of range or invalid voxel sizes
          
          ## only for standard voxels (length 3 or 4)
          #if len(voxel)>4:
            #print('ERROR: voxel with more than 4 parameters',file=stderr)
            #sys.exit(-1)
          for i in range(len(voxel)):
            value = voxel[i] + writingOffset[i]
            if i!=3: #coordinates
              file.write( str( "%.3f" % (value) ) )
            else: #power
              if 0<=value and value<=100:
                file.write( str( "%.3f" % (value) ) )
            # add tab or line ending
            if i<len(voxel)-1:
              file.write('\t')
            else:
              file.write('\n')

          ## general method for voxels of any length
          #for i in range(len(voxel)):
            #file.write( str( "%.3f" % (voxel[i] + writingOffset[i]) ) )
            #if i<len(voxel)-1:
              #file.write('\t')
            #else:
              #file.write('\n')
              
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
  VerticalPointDistance = 0.5
  center = [30,0,3]
  radius = 3
  GWL_obj.addHorizontalCircle(center, radius, power, HorizontalPointDistance)
  GWL_obj.addHorizontalDisk([center[0],center[1],center[2]+1], radius, power, HorizontalPointDistance)
  GWL_obj.addSphere([center[0],center[1],center[2]+1+11], radius, power, HorizontalPointDistance, VerticalPointDistance, False)
  GWL_obj.addSphere([center[0],center[1],center[2]+1+22], radius, power, HorizontalPointDistance, VerticalPointDistance, True)

  HorizontalPointDistance = 1
  VerticalPointDistance = 1
  center = [40,0,3]
  radius = 3
  GWL_obj.addHorizontalCircle(center, radius, power, HorizontalPointDistance)
  GWL_obj.addHorizontalDisk([center[0],center[1],center[2]+1], radius, power, HorizontalPointDistance)
  GWL_obj.addSphere([center[0],center[1],center[2]+1+11], radius, power, HorizontalPointDistance, VerticalPointDistance, False)
  GWL_obj.addSphere([center[0],center[1],center[2]+1+22], radius, power, HorizontalPointDistance, VerticalPointDistance, True)

  HorizontalPointDistance = 1
  VerticalPointDistance = 2
  center = [50,0,3]
  radius = 3
  GWL_obj.addHorizontalCircle(center, radius, power, HorizontalPointDistance)
  GWL_obj.addHorizontalDisk([center[0],center[1],center[2]+1], radius, power, HorizontalPointDistance)
  GWL_obj.addSphere([center[0],center[1],center[2]+1+11], radius, power, HorizontalPointDistance, VerticalPointDistance, False)
  GWL_obj.addSphere([center[0],center[1],center[2]+1+22], radius, power, HorizontalPointDistance, VerticalPointDistance, True)

  print('300')
  HorizontalPointDistance = 0.050
  VerticalPointDistance = 0.100
  center = [60,0,3]
  radius = 0.5*0.300
  GWL_obj.addHorizontalCircle(center, radius, power, HorizontalPointDistance)
  GWL_obj.addHorizontalDisk([center[0],center[1],center[2]+1], radius, power, HorizontalPointDistance)
  GWL_obj.addSphere([center[0],center[1],center[2]+1+11], radius, power, HorizontalPointDistance, VerticalPointDistance, False)
  GWL_obj.addSphere([center[0],center[1],center[2]+1+22], radius, power, HorizontalPointDistance, VerticalPointDistance, True)

  print('350')
  center = [70,0,3]
  radius = 0.5*0.350
  GWL_obj.addHorizontalCircle(center, radius, power, HorizontalPointDistance)
  GWL_obj.addHorizontalDisk([center[0],center[1],center[2]+1], radius, power, HorizontalPointDistance)
  GWL_obj.addSphere([center[0],center[1],center[2]+1+11], radius, power, HorizontalPointDistance, VerticalPointDistance, False)
  GWL_obj.addSphere([center[0],center[1],center[2]+1+22], radius, power, HorizontalPointDistance, VerticalPointDistance, True)

  print('400')
  center = [80,0,3]
  radius = 0.5*0.400
  GWL_obj.addHorizontalCircle(center, radius, power, HorizontalPointDistance)
  GWL_obj.addHorizontalDisk([center[0],center[1],center[2]+1], radius, power, HorizontalPointDistance)
  GWL_obj.addSphere([center[0],center[1],center[2]+1+11], radius, power, HorizontalPointDistance, VerticalPointDistance, False)
  GWL_obj.addSphere([center[0],center[1],center[2]+1+22], radius, power, HorizontalPointDistance, VerticalPointDistance, True)


  GWL_obj.write_GWL('xblock.gwl')

  GWL_obj.clear()
  GWL_obj.addXblock([0,0,2.75],[10,0,2.75],5,0.050,8,0.100)
  GWL_obj.addYblock([1,0,2.75],[1,20,2.75],5,0.050,8,0.100)
  GWL_obj.write_GWL('xblock2.gwl')
