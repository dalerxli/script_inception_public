#!/usr/bin/env python

from __future__ import division
import numpy

# TODO: sanitize class system:
#class MeshBox(Geometry_object):
#class MeshingParameters(object):
#class MeshObject(object):

# TODO: Allow delta specification directly or with factor where delta=factor*lambda/n (current system, easier to scale if needed)?
# TODO: parameter in geometry objects to enable/disable use of meshing parameters + allow custom meshing parameters per geometry object

class MeshingParameters(object):
  # TODO: think about the best way to design this class and then do it.
  # Might be better to really have delta+thickness for each object and then some global MeshingParameters with addMeshingParameters function.
  # permittivity to delta conversion could be specified differently for each object.
  # thickness <-> limits
  # delta <-factor*1/sqrt(permittivity)-> permittivity <-sqrt-> refractive index
  
  # TODO: Combine with MeshObject? Create way to merge 2 or more existing meshes (i.e. MeshObject objects)? Create MeshObject from set of MeshingParameters? Don't forget about MEEP and BFDTD subgridding.
  # TODO: support 1-D,2-D (n-D?) meshing parameters as well
  
  def __init__(self):
    self.maxPermittivityVector_X = [1]
    self.thicknessVector_X = [1]
    self.maxPermittivityVector_Y = [1]
    self.thicknessVector_Y = [1]
    self.maxPermittivityVector_Z = [1]
    self.thicknessVector_Z = [1]
    self.limits_X = [0,1]
    self.limits_Y = [0,1]
    self.limits_Z = [0,1]
    
  def __str__(self):
    ret = 'maxPermittivityVector_X = '+str(self.maxPermittivityVector_X)+'\n'
    ret += 'thicknessVector_X = '+str(self.thicknessVector_X)+'\n'
    ret += 'maxPermittivityVector_Y = '+str(self.maxPermittivityVector_Y)+'\n'
    ret += 'thicknessVector_Y = '+str(self.thicknessVector_Y)+'\n'
    ret += 'maxPermittivityVector_Z = '+str(self.maxPermittivityVector_Z)+'\n'
    ret += 'thicknessVector_Z = '+str(self.thicknessVector_Z)
    return ret
  
  def addLimits_X(self,limits,permittivity):
    #print(limits)
    #print(permittivity)
    #print(limits.shape)
    #print(permittivity.shape)
    
    self.limits_X = numpy.vstack([self.limits_X,limits])
    self.maxPermittivityVector_X = numpy.vstack([self.maxPermittivityVector_X,permittivity])
    
  def addLimits_Y(self,limits,permittivity):
    self.limits_Y = numpy.vstack([self.limits_Y,limits])
    self.maxPermittivityVector_Y = numpy.vstack([self.maxPermittivityVector_Y,permittivity])
    
  def addLimits_Z(self,limits,permittivity):
    self.limits_Z = numpy.vstack([self.limits_Z,limits])
    self.maxPermittivityVector_Z = numpy.vstack([self.maxPermittivityVector_Z,permittivity])
    
