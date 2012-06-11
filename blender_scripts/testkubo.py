#!/usr/bin/env python
# -*- coding: utf-8 -*-

import bpy
import os
from blender_scripts.FDTDGeometryObjects import *
from blender_scripts.bfdtd_import import *

def testkubo():
  verts = [(1.0, 1.0, -1.0),
           (1.0, -1.0, -1.0),
          (-1.0, -1.0, -1.0),
          (-1.0, 1.0, -1.0),
           (1.0, 1.0, 1.0),
           (1.0, -1.0, 1.0),
          (-1.0, -1.0, 1.0),
          (-1.0, 1.0, 1.0)]
  
  #faces = [(0, 1, 2, 3),
           #(4, 7, 6, 5),
           #(0, 4, 5, 1),
           #(1, 5, 6, 2),
           #(2, 6, 7, 3),
           #(4, 0, 3, 7)]

  edges = [(0, 1),
          (1, 2),
          (2, 3),
          (3, 0),
          (4, 7),
          (7, 6),
          (6, 5),
          (5, 4),
          (0, 4),
          (5, 1),
          (2, 6),
          (7, 3)]
  
  faces = []
  
  mesh_data = bpy.data.meshes.new("cube_mesh_data")
  mesh_data.from_pydata(verts, edges, faces)
  mesh_data.update() # (calc_edges=True) not needed here
  
  cube_object = bpy.data.objects.new("superBox", mesh_data)
  
  scene = bpy.context.scene  
  scene.objects.link(cube_object)  
  cube_object.select = True

def testkubo2():
  # add cube
  bpy.ops.mesh.primitive_cube_add(location=(0,0,0),rotation=(0,0,0))
  
  # get added object
  obj = bpy.context.active_object
  print(obj)
  #for obj in bpy.data.objects:
    #print(obj.name)
    
  #bpy.data.objects[-1].name = 'testkubo2'
  obj.name = 'testkubo2'
  obj.scale = Vector((1,2,3))
  
  # deleting faces fails when in object mode, so change.
  bpy.ops.object.mode_set(mode = 'EDIT') 
  bpy.ops.mesh.delete(type='ONLY_FACE')
  bpy.ops.object.mode_set(mode = 'OBJECT')
    
#bpy.ops.object.add_named(linked=False, name="Cube")

def boxtest():
	FDTDGeometryObjects_obj = FDTDGeometryObjects()
	FDTDGeometryObjects_obj.GEObox('GEObox', Vector([1,1,1]), Vector([2,3,4]))
	FDTDGeometryObjects_obj.GEOblock('GEOblock', Vector([2,3,4]), Vector([5,5,5]), 1, 1)
	# initialise rotation_matrix
	rotation_matrix = Matrix()
	rotation_matrix.identity()
	# scale object
	Sx = Matrix.Scale(abs(2), 4, Vector((1,0,0)) )
	Sy = Matrix.Scale(abs(5), 4, Vector((0,1,0)) )
	Sz = Matrix.Scale(abs(7), 4, Vector((0,0,1)) )
	rotation_matrix *= Sx*Sy*Sz;
	# position object
	T = Matrix.Translation(Vector([-1,-2,-3]))
	rotation_matrix *= T;
	# add rotations
	rotation_matrix *= rotationMatrix(Vector([1,1,1]), Vector([1,2,0]),25);
	FDTDGeometryObjects_obj.GEOblock_matrix('GEOblock_matrix', rotation_matrix, 3, 2)

def importTest():
  importBristolFDTD(os.getenv("HOME")+'/Development/script_inception_public/geometries/qedc3_3_0525b.geo')
  
if __name__ == "__main__":
  #testkubo()
  boxtest()
  #testkubo2()
  #importTest()
