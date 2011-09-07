#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bfdtd.bfdtd_parser import *
from numpy import *
from utilities.common import *
from constants.constants import *
from meshing.subGridMultiLayer import *
import os
from bfdtd.triangular_prism import TriangularPrism
from bfdtd.SpecialTriangularPrism import SpecialTriangularPrism
from bfdtd.meshingparameters import *

pillar = BFDTDobject()

# define box
pillar.box.lower = [0,0,0]
pillar.box.upper = [1,1,1]

# define geometry
#prism = Block()
#prism.lower = [ 1.1,1.2,1.3 ]
#prism.upper = [ 2.4,2.5,2.6 ]
#prism.permittivity = 24
#pillar.geometry_object_list.append(prism)

#prism = Block()
#prism.lower = [ 1.5,1.5,1.5 ]
#prism.upper = [ 2.5,2.5,2.5 ]
#prism.permittivity = 10
#pillar.geometry_object_list.append(prism)

#prism = Block()
#prism.lower = [ 3.7,3.8,3.9 ]
#prism.upper = [ 4.10,4.11,4.12 ]
#prism.permittivity = 42
#pillar.geometry_object_list.append(prism)

meshing_parameters = MeshingParameters()
#meshing_parameters.

prism = Block()
prism.lower = pillar.box.lower
prism.upper = pillar.box.upper
prism.permittivity = 1
pillar.geometry_object_list.append(prism)

# define mesh
pillar.autoMeshGeometry(0.637/16.)

# write
DSTDIR = os.getenv('TESTDIR')
BASENAME = 'meshing_test'
pillar.writeAll(DSTDIR+os.sep+BASENAME, BASENAME)
print pillar.getNcells()
