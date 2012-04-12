#!/usr/bin/env python
# -*- coding: utf-8 -*-

# generate grid of woodpiles

#import math
import numpy
import os
from GWL.GWL_parser import *
from GWL.woodpile import *

def createSubFiles(DSTDIR):
  subfile_list = []
  Lambda_list = [0.780,1.550]
  wh_list = [(0.2,0.25),(0.3/numpy.sqrt(2.0),0.7/numpy.sqrt(2.0))]
  a_over_Lambda_list = [0.9199,0.8333]

  #N_list = [(12,17,17),(2*12,2*17,2*17),(12,17,17)]
  N_list = [(2*12,2*17,2*17)]

  for Lambda in Lambda_list:
    for a_over_Lambda in a_over_Lambda_list:
      for (Nlayers_Z,NRodsPerLayer_X,NRodsPerLayer_Y) in N_list:

        a = a_over_Lambda*Lambda
        woodpile_obj = Woodpile()
        woodpile_obj.BottomToTop = 0
        woodpile_obj.Nlayers_Z = Nlayers_Z
        woodpile_obj.NRodsPerLayer_X = NRodsPerLayer_X
        woodpile_obj.NRodsPerLayer_Y = NRodsPerLayer_Y
        woodpile_obj.interLayerDistance = a/4.0
        woodpile_obj.interRodDistance = a/numpy.sqrt(2.0)

        woodpile_obj.LineDistance_Vertical = 0.100
        woodpile_obj.LineNumber_Vertical = int(woodpile_obj.interLayerDistance/woodpile_obj.LineDistance_Vertical)
        woodpile_obj.LineNumber_Horizontal = 1
        woodpile_obj.LineDistance_Horizontal = 0.050

        woodpile_obj.adaptXYMinMax()
        #subfilename = 'woodpile.Lambda_'+str(Lambda)+'.a_'+str(a)+'.NX_'+str(NRodsPerLayer_X)+'.NY_'+str(NRodsPerLayer_Y)+'.Nlayers_Z_'+str(Nlayers_Z)+'.dVert_'+str(woodpile_obj.LineDistance_Vertical)+'.dHori_'+str(woodpile_obj.LineDistance_Horizontal)+'.gwl'
        subfilename = 'woodpile.interRodDist_'+str(woodpile_obj.interRodDistance)+'.interLayerDist_'+str(woodpile_obj.interLayerDistance)+'.NX_'+str(NRodsPerLayer_X)+'.NY_'+str(NRodsPerLayer_Y)+'.Nlayers_Z_'+str(Nlayers_Z)+'.dVert_'+str(woodpile_obj.LineDistance_Vertical)+'.dHori_'+str(woodpile_obj.LineDistance_Horizontal)+'.gwl'
        woodpile_obj.write_GWL(DSTDIR + os.path.sep + subfilename)
        subfile_list.append(subfilename)
  return(subfile_list)

def createSubFiles2(DSTDIR):
  subfile_list = []

  #N_list = [(12,17,17),(2*12,2*17,2*17),(12,17,17)]
  #N_list = [(2*12,2*17,2*17)]
  N_list = [(12,17,17)]

  for nVert in [1,2,3,4]:
      for (Nlayers_Z,NRodsPerLayer_X,NRodsPerLayer_Y) in N_list:
        woodpile_obj = Woodpile()
        woodpile_obj.BottomToTop = 0
        woodpile_obj.Nlayers_Z = Nlayers_Z
        woodpile_obj.NRodsPerLayer_X = NRodsPerLayer_X
        woodpile_obj.NRodsPerLayer_Y = NRodsPerLayer_Y
        woodpile_obj.interRodDistance = 0.6
        woodpile_obj.interLayerDistance = numpy.sqrt(2.0)*woodpile_obj.interRodDistance/4.0

        woodpile_obj.LineDistance_Horizontal = 0.050
        #woodpile_obj.LineDistance_Vertical = 0.100
        #woodpile_obj.LineDistance_Vertical = 0.050
        woodpile_obj.LineNumber_Vertical = nVert #int(woodpile_obj.interLayerDistance/woodpile_obj.LineDistance_Vertical)
        woodpile_obj.LineDistance_Vertical = woodpile_obj.interLayerDistance/woodpile_obj.LineNumber_Vertical
        woodpile_obj.LineNumber_Horizontal = 1

        woodpile_obj.adaptXYMinMax()
        #subfilename = 'woodpile.Lambda_'+str(Lambda)+'.a_'+str(a)+'.NX_'+str(NRodsPerLayer_X)+'.NY_'+str(NRodsPerLayer_Y)+'.Nlayers_Z_'+str(Nlayers_Z)+'.dVert_'+str(woodpile_obj.LineDistance_Vertical)+'.dHori_'+str(woodpile_obj.LineDistance_Horizontal)+'.gwl'
        #subfilename = 'woodpile.interRodDist_'+str(woodpile_obj.interRodDistance)+'.interLayerDist_'+str(woodpile_obj.interLayerDistance)+'.NX_'+str(NRodsPerLayer_X)+'.NY_'+str(NRodsPerLayer_Y)+'.Nlayers_Z_'+str(Nlayers_Z)+'.dVert_'+str(woodpile_obj.LineDistance_Vertical)+'.dHori_'+str(woodpile_obj.LineDistance_Horizontal)+'.gwl'
        #subfilename = 'woodpile.interRodDist_'+str(woodpile_obj.interRodDistance)+'.NX_'+str(NRodsPerLayer_X)+'.NY_'+str(NRodsPerLayer_Y)+'.Nlayers_Z_'+str(Nlayers_Z)+'.dVert_'+str(woodpile_obj.LineDistance_Vertical)+'.dHori_'+str(woodpile_obj.LineDistance_Horizontal)+'.gwl'
        #subfilename = 'woodpile.interRodDist_'+str(woodpile_obj.interRodDistance)+'.NX_'+str(NRodsPerLayer_X)+'.NY_'+str(NRodsPerLayer_Y)+'.Nlayers_Z_'+str(Nlayers_Z)+'.dVert_'+str(woodpile_obj.LineDistance_Vertical)+'.gwl'
        subfilename = 'woodpile.interRodDist_'+str(woodpile_obj.interRodDistance)+'.NX_'+str(NRodsPerLayer_X)+'.NY_'+str(NRodsPerLayer_Y)+'.Nlayers_Z_'+str(Nlayers_Z)+'.nVert_'+str(woodpile_obj.LineNumber_Vertical)+'.gwl'

        woodpile_obj.write_GWL(DSTDIR + os.path.sep + subfilename)

        subfile_list.append(subfilename)
  return(subfile_list)

def single_woodpile(DSTDIR, NX, NY, NZ, interRodDistance, LaserPower, ScanSpeed, BottomToTop):
##        os.chdir(DSTDIR)

        woodpile_obj = Woodpile()
        woodpile_obj.BottomToTop = BottomToTop
        woodpile_obj.NRodsPerLayer_X = NX
        woodpile_obj.NRodsPerLayer_Y = NY
        woodpile_obj.Nlayers_Z = NZ
        woodpile_obj.interRodDistance = interRodDistance
        a = woodpile_obj.interRodDistance*numpy.sqrt(2.0)
        woodpile_obj.interLayerDistance = a/4.0
        woodpile_obj.adaptXYMinMax()
        subfilename = 'woodpile'+'.deltaH_'+str(woodpile_obj.interRodDistance)+'.a_'+str(a)+'.NX_'+str(woodpile_obj.NRodsPerLayer_X)+'.NY_'+str(woodpile_obj.NRodsPerLayer_Y)+'.Nlayers_Z_'+str(woodpile_obj.Nlayers_Z)+'.BotToTop._'+str(woodpile_obj.BottomToTop)+'.gwl'
        woodpile_obj.write_GWL(DSTDIR + os.path.sep + subfilename)
##        Xoffset = 0.5*(woodpile_obj.Xmax - woodpile_obj.Xmin)
##        Yoffset = 0.5*(woodpile_obj.Ymax - woodpile_obj.Ymin)
        Xoffset = -woodpile_obj.Xmin
        Yoffset = -woodpile_obj.Ymin
##        LaserPower = 40
##        ScanSpeed = 200
        createSingleMainFile(DSTDIR + os.path.sep + 'main.P_'+str(LaserPower)+'.V_'+str(ScanSpeed)+'.'+subfilename, subfilename, LaserPower, ScanSpeed, Xoffset, Yoffset)
##        LaserPower = 50
##        ScanSpeed = 200
##        createSingleMainFile('main.P_'+str(LaserPower)+'.V_'+str(ScanSpeed)+'.'+subfilename, subfilename, LaserPower, ScanSpeed, Xoffset, Yoffset)

def createSingleMainFile(filename, VoxelFile, LaserPower, ScanSpeed, Xoffset, Yoffset):
  PowerScaling = 1
  print('Writing GWL main to '+filename)
  with open(filename, 'w') as file:
    commonHeader(file)

    file.write('Xoffset '+str(Xoffset)+'\n')
    file.write('Yoffset '+str(Yoffset)+'\n')
    file.write('ZOffset 0\n')
    file.write('%%%%%%%\n')
    file.write('PowerScaling ' + str(PowerScaling) + '\n')
    file.write('LaserPower ' + str(LaserPower) + '\n')
    file.write('ScanSpeed ' + str(ScanSpeed) + '\n')
    file.write('Include ' + VoxelFile + '\n')
    file.write('Write\n')
    file.write('%%%%%%%\n')

def commonHeader(file):
  file.write('FindInterfaceAt 0.2\n')
  file.write('Scanmode 0\n')
  file.write('OperationMode 1\n')
  file.write('%%%%%%%\n')
  file.write('ConnectPointsOn\n')
  file.write('LineDistance 0\n')
  file.write('LineNumber 1\n')
  file.write('ZOffset 0\n')
  file.write('Defocusfactor 1.1\n')
  file.write('PerfectShapeOff\n')
  file.write('%%%%%%%\n')
  file.write('PointDistance 25\n')
  file.write('UpdateRate 1000\n')
  file.write('DwellTime 200\n')
  file.write('%%%%%%%\n')
##  file.write('Xoffset 50\n')
##  file.write('Yoffset 75\n')
##  file.write('ZOffset 0\n')


def createMainFile(filename, VoxelFile):
  #deltaX = 40
  #deltaY = 40
  deltaX = 1000
  deltaY = 1000
  PowerScaling = 1

  #LaserPower = [1,25,50]
  #ScanSpeed = [10,30,50]

  VP_values = []
  VP_values.append([ (5,i) for i in numpy.arange(5,25.1,5) ])
  VP_values.append([ (10,i) for i in numpy.arange(5,25.1,5) ])
  VP_values.append([ (20,i) for i in numpy.arange(5,30.1,5) ])
  VP_values.append([ (25,i) for i in numpy.arange(5,30.1,5) ])
  VP_values.append([ (30,i) for i in numpy.arange(5,30.1,5) ])
  VP_values.append([ (40,i) for i in numpy.arange(5,30.1,5) ])
  VP_values.append([ (50,i) for i in numpy.arange(5,30.1,5) ])
  VP_values.append([ (100,i) for i in numpy.arange(5,40.1,5) ])
  VP_values.append([ (150,i) for i in numpy.arange(5,40.1,5) ])
  VP_values.append([ (200,i) for i in numpy.arange(5,40.1,5) ])

  #VoxelFile = 'toto.gwl'
  Wait = 4
  print('Writing GWL main to '+filename)
  with open(filename, 'w') as file:
    commonHeader(file)

    Ntotal = 0
    for linio in VP_values:
      file.write('%%%%%%% NEW LINE \n')
      for (V,P) in linio:
        Ntotal = Ntotal + 1
        file.write('%%%%%%%\n')
        file.write('PowerScaling ' + str(PowerScaling) + '\n')
        file.write('LaserPower ' + str(P) + '\n')
        file.write('ScanSpeed ' + str(V) + '\n')
        file.write('Include ' + VoxelFile + '\n')
        file.write('write\n')
        file.write('Wait '+ str(Wait) +'\n')
        file.write('MoveStageX ' + str(deltaX) + '\n')
      file.write('%%%%%%% END OF LINE \n')
      file.write('MoveStageY ' + str(deltaY) + '\n')
      file.write('MoveStageX ' + str(-len(linio)*deltaX) + '\n')

    # move back to origin
    #file.write('MoveStageY ' + str(-len(VP_values)*deltaY) + '\n')
    print('number of woodpiles in this grid: ' + str(Ntotal))

def createMasterFile(filename, mainfile_list):
  #deltaX = 40
  #deltaY = 40
  deltaX = 1000
  deltaY = 1000
  PowerScaling = 1
  Wait = 4
  print('Writing GWL master to '+filename)
  with open(filename, 'w') as file:
    commonHeader(file)

    for f in mainfile_list:
      file.write('%%%%%%%\n')
      file.write('Include ' + f + '\n')
      file.write('write\n')
      file.write('Wait '+ str(Wait) +'\n')
      #file.write('MoveStageX ' + str(deltaX) + '\n')
      #file.write('MoveStageY ' + str(deltaY) + '\n')

def createMainFile2(filename, file_list):
  #deltaX = 40
  #deltaY = 40
  deltaX = 1000
  deltaY = 1000
  PowerScaling = 1

  LaserPower = [15,20,25,30,35]
  ScanSpeed = 200

  #VoxelFile = 'toto.gwl'
  Wait = 4
  print('Writing GWL main to '+filename)
  with open(filename, 'w') as file:
    commonHeader(file)

    Ntotal = 0
    for VoxelFile in file_list:
      file.write('%%%%%%% NEW LINE \n')
      for P in LaserPower:
        Ntotal = Ntotal + 1
        file.write('%%%%%%%\n')
        file.write('PowerScaling ' + str(PowerScaling) + '\n')
        file.write('LaserPower ' + str(P) + '\n')
        file.write('ScanSpeed ' + str(ScanSpeed) + '\n')
        file.write('Include ' + VoxelFile + '\n')
        file.write('Write\n')
        file.write('Wait '+ str(Wait) +'\n')
        file.write('MoveStageX ' + str(deltaX) + '\n')
      file.write('%%%%%%% END OF LINE \n')
      file.write('MoveStageY ' + str(deltaY) + '\n')
      file.write('MoveStageX ' + str(-len(LaserPower)*deltaX) + '\n')
    print('number of woodpiles in this grid: ' + str(Ntotal))


if __name__ == "__main__":

    if len(sys.argv)>1:
        DSTDIR = sys.argv[1]
    else:
        DSTDIR = os.getcwd()

    # Alex woodpiles
    #subfile_list = createSubFiles(DSTDIR)
    subfile_list = createSubFiles2(DSTDIR)
    #mainfile_list = []
    #for subfile in subfile_list:
      #mainfilename = 'main_'+subfile
      #createMainFile(mainfilename, subfile)
      #mainfile_list.append(mainfilename)
    #createMasterFile('master.gwl',mainfile_list)
    #createMainFile2('grid_8x5.gwl',subfile_list)

##    single_woodpile(DSTDIR, NX, NY, NZ, interRodDistance, LaserPower, ScanSpeed, BottomToTop)
    #single_woodpile(DSTDIR, 17, 17, 12, 0.6, 50, 200, 0)
    #single_woodpile(DSTDIR, 17, 17, 12, 0.6, 50, 200, 1)

    # Alex woodpiles:
    #single_woodpile(DSTDIR, 34, 34, 24, 0.6, 50, 200, 0)
    #single_woodpile(DSTDIR, 34, 34, 24, 0.6, 50, 200, 1)

    print( 'Output in ' + os.getcwd())
