#!/usr/bin/env python
# -*- coding: utf-8 -*-

# generate grid of woodpiles

from GWL.GWL_parser import *
import numpy as np

def createSubFiles():
  subfile_list = []
  Lambda_list = [0.780,1.550]
  wh_list = [(0.2,0.25),(0.3/sqrt(2.0),0.7/sqrt(2.0))]
  a_over_Lambda_list = [0.9199,0.8333]
  
  N_list = [(12,17,17),(2*12,2*17,2*17)]
  
  for Lambda in Lambda_list:
    for a_over_Lambda in a_over_Lambda_list:
      for (Nlayers_Z,NRodsPerLayer_X,NRodsPerLayer_Y) in N_list:
      
        a = a_over_Lambda*Lambda
        woodpile_obj = Woodpile()
        woodpile_obj.Nlayers_Z = Nlayers_Z
        woodpile_obj.NRodsPerLayer_X = NRodsPerLayer_X
        woodpile_obj.NRodsPerLayer_Y = NRodsPerLayer_Y
        woodpile_obj.interLayerDistance = a/4.0
        woodpile_obj.interRodDistance = a/sqrt(2.0)
        woodpile_obj.adaptXYMinMax()
        subfilename = 'woodpile.Lambda_'+str(Lambda)+'.a_'+str(a)+'.NX_'+str(NRodsPerLayer_X)+'.NY_'+str(NRodsPerLayer_Y)+'.Nlayers_Z_'+str(Nlayers_Z)+'.gwl'
        woodpile_obj.write_GWL(subfilename)
        subfile_list.append(subfilename)
  return(subfile_list)

def createMainFile(filename, VoxelFile):
  #deltaX = 40
  #deltaY = 40
  deltaX = 1000
  deltaY = 1000
  PowerScaling = 1
  
  #LaserPower = [1,25,50]
  #ScanSpeed = [10,30,50]
  
  VP_values = []
  VP_values.append([(1,10),(1,20),(1,30),(1,40),(1,50),(1,60)])
  VP_values.append([(10,15),(10,25),(10,35)])
  VP_values.append([(20,5),(20,7)])
  
  #VoxelFile = 'toto.gwl'
  Wait = 4
  print('Writing GWL main to '+filename)
  with open(filename, 'w') as file:
    file.write('FindInterfaceAt 0.2\n')
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
    file.write('Xoffset 50\n')
    file.write('Yoffset 75\n')
    file.write('ZOffset 0\n')

    for linio in VP_values:
      for (V,P) in linio:
        file.write('%%%%%%%\n')
        file.write('PowerScaling ' + str(PowerScaling) + '\n')
        file.write('LaserPower ' + str(P) + '\n')
        file.write('ScanSpeed ' + str(V) + '\n')
        file.write('Include ' + VoxelFile + '\n')
        file.write('write\n')
        file.write('Wait '+ str(Wait) +'\n')
        file.write('MoveStageX ' + str(deltaX) + '\n')
      file.write('MoveStageY ' + str(deltaY) + '\n')
    
if __name__ == "__main__":
  subfile_list = createSubFiles()
  for subfile in subfile_list:
    createMainFile('main_'+subfile, subfile)
