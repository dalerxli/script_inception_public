#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bfdtd.ellipsoid import *

DSTDIR = sys.argv[1]
if not os.path.isdir(DSTDIR):
  os.mkdir(DSTDIR)

N = 11

Dx = 3.15
Dz = 3
block_direction = 'x'

depth_factor = 7
thickness = 0.200

#Dx = 3
#Dz = 3.15
#block_direction = 'z'

sim=readBristolFDTD('qedc3_2_05.in')

first = True

BASENAME = "ellipsoid.x%.2f.z%.2f" % (Dx,Dz)

C = [0,0,0]
radius = 0
mirror_pair_height = 0

Nlayers = 0

for i in range(len(sim.geometry_object_list)):
  obj = sim.geometry_object_list[i]
  if isinstance(obj,Cylinder):
    
    C_current = obj.getCentro()
    upper_current = obj.getUpper()

    if Nlayers<2:
      mirror_pair_height += obj.height

    Nlayers += 1
    
    if upper_current[1]>C[1]:
      C = [C_current[0],upper_current[1],C_current[2]]

    ellipsoid = Ellipsoid()
    ellipsoid.setCentro(obj.getCentro())
    size = obj.getSize()
    ellipsoid.setSize([Dx,obj.height,Dz])
    ellipsoid.permittivity = obj.permittivity
    ellipsoid.conductivity = obj.conductivity
    ellipsoid.mesh.setSizeAndResolution(ellipsoid.getSize(),[N,N,N])
    ellipsoid.block_direction = block_direction
    sim.geometry_object_list[i] = ellipsoid
    #print(id(obj))

    if first:
      first=False
      ref=BFDTDobject()
      ref.box = sim.box
      ref.geometry_object_list.append(obj)
      ref.geometry_object_list.append(ellipsoid)
      ref.writeGeoFile(DSTDIR+os.sep+BASENAME+'.ref.geo')
      radius = obj.outer_radius

depth = depth_factor*mirror_pair_height

block_xminus = Block()
block_xminus.name = 'airblock'
block_xminus.setRefractiveIndex(1)
block_xminus.setSize([thickness,depth,Dz])
block_xminus.setCentro([C[0]-(0.5*Dx-0.5*thickness),C[1]-0.5*depth,C[2]])

block_xplus = Block()
block_xplus.name = 'airblock'
block_xplus.setRefractiveIndex(1)
block_xplus.setSize([thickness,depth,Dz])
block_xplus.setCentro([C[0]+(0.5*Dx-0.5*thickness),C[1]-0.5*depth,C[2]])

sim.geometry_object_list.extend([block_xminus, block_xplus])
    
Lambda = sim.excitation_list[0].getLambda()
# define mesh
a = 10
sim.autoMeshGeometry(Lambda/a)
#MAXCELLS=8000000;
MAXCELLS=1000000;
while(sim.getNcells()>MAXCELLS and a>1):
  a = a-1
  sim.autoMeshGeometry(Lambda/a)

#sim.writeGeoFile('ellipsoid.Yx.geo')
#sim.writeInpFile('ellipsoid.Yx.inp')
sim.fileList = []
print('number of geometry objects = '+str(N*len(sim.geometry_object_list)))
sim.writeAll(DSTDIR,BASENAME)
