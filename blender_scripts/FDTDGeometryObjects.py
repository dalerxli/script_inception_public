#!/usr/bin/env python
# -*- coding: utf-8 -*-

#import Blender
#~ from bpy import *
import math
import bpy;
#import BPyAddMesh;
import os;
import sys;
import re;
import array;
# define Vector+Matrix
#~ from bpy.Mathutils import Vector;
#~ from bpy.Mathutils import Matrix;
#from Blender.Mathutils import Vector;
#from Blender.Mathutils import Matrix;
from mathutils import Color

class FDTDGeometryObjects:
    def __init__(self):
      # prepare base materials
      self.material_dict={};
      
      bpy.ops.material.new()
      self.frequency_snapshot_material = bpy.data.materials[-1]
      self.frequency_snapshot_material.name = 'frequency_snapshot'
      self.frequency_snapshot_material.diffuse_color = Color((0.5, 0, 0))
      self.frequency_snapshot_material.alpha = 0.5
      
      #titi.transparency_method='MASK'
      #titi.transparency_method='RAYTRACE'
      #titi.transparency_method='Z_TRANSPARENCY'
      
      bpy.ops.material.new()
      self.time_snapshot_material = bpy.data.materials[-1]
      self.time_snapshot_material.name = 'time_snapshot'
      self.time_snapshot_material.diffuse_color = Color((0.5, 1, 0))
      self.time_snapshot_material.alpha = 0.5
      
      bpy.ops.material.new()
      self.eps_snapshot_material = bpy.data.materials[-1]
      self.eps_snapshot_material.name = 'eps_snapshot'
      self.eps_snapshot_material.diffuse_color = Color((0.5, 0, 1))
      self.eps_snapshot_material.alpha = 0.5
      
      bpy.ops.material.new()
      self.excitation_material = bpy.data.materials[-1]
      self.excitation_material.name = 'excitation'
      self.excitation_material.diffuse_color = Color((1, 0, 0))
      self.excitation_material.alpha = 0.5
      
      self.snapshot_materials = [ self.frequency_snapshot_material, self.time_snapshot_material, self.eps_snapshot_material ];
      
      self.probe_scalefactor_box = 0.0218;
      self.probe_scalefactor_mesh = 0.5;
      self.mesh_min = 0;
      self.mesh_max = 0;
      self.box_SizeX = 0;
      self.box_SizeY = 0;
      self.box_SizeZ = 0;
    def materials(self,permittivity, conductivity):
        if permittivity not in self.material_dict:
            n = math.sqrt(permittivity)
            
            max_permittivity = 25.0;
            bpy.ops.material.new()
            permittivity_material = bpy.data.materials[-1]
            permittivity_material.name = 'permittivity'
            permittivity_material.diffuse_color = Color((0, permittivity/max_permittivity, 1.0-permittivity/max_permittivity))
            permittivity_material.alpha = 0.5
            
            # bpy.ops.material.new()
            # conductivity_material = bpy.data.materials[-1]
            # conductivity_material.name = 'conductivity'
            # conductivity_material.diffuse_color = Color((0, 1.0-conductivity/100.0, 0))
            # conductivity_material.alpha = 0.5
    
            # bpy.ops.material.new()
            # refractive_index_material = bpy.data.materials[-1]
            # refractive_index_material.name = 'refractive_index'
            # if n!=0:
                # refractive_index_material.diffuse_color = Color((0, 0, 1.0/n))
            # else:
                # refractive_index_material.diffuse_color = Color((0, 0, 1.0))
            # refractive_index_material.alpha = 0.5
            
            self.material_dict[permittivity] = permittivity_material;
    
        return [ self.material_dict[permittivity] ];
    ###############################
    # OBJECT CREATION FUNCTIONS
    ###############################
    def GEOblock(self, name, lower, upper, permittivity, conductivity):
        scene = Blender.Scene.GetCurrent();
        mesh = Blender.Mesh.Primitives.Cube(1.0);
        mesh.materials = self.materials(permittivity, conductivity);
        for f in mesh.faces:
            f.mat = 0;
    
        obj = scene.objects.new(mesh, name);
        pos = 0.5*(lower+upper);
        diag = upper-lower;
        obj.SizeX = abs(diag[0]);
        obj.SizeY = abs(diag[1]);
        obj.SizeZ = abs(diag[2]);
        obj.setLocation(pos[0], pos[1], pos[2]);
        obj.transp = True; obj.wireMode = True;
        return;
    
    def GEOblock_matrix(self, name, rotation_matrix, permittivity, conductivity):
        #~ Blender.Window.SetActiveLayer(1<<8);
        scene = Blender.Scene.GetCurrent();
        mesh = Blender.Mesh.Primitives.Cube(1.0);
        mesh.materials = self.materials(permittivity, conductivity);
        for f in mesh.faces:
            f.mat = 0;
    
        obj = scene.objects.new(mesh, name);
        obj.setMatrix(rotation_matrix);
        obj.transp = True; obj.wireMode = True;
        #~ obj.layers = [ 8 ];
        return;
    
    def GEOcylinder(self, name, center, inner_radius, outer_radius, H, permittivity, conductivity, angle_X, angle_Y, angle_Z):
        scene = Blender.Scene.GetCurrent();
        mesh = Blender.Mesh.Primitives.Cylinder(32, 2*outer_radius, H);
        mesh.materials = self.materials(permittivity, conductivity);
        for f in mesh.faces:
            f.mat = 0;
    
        obj = scene.objects.new(mesh, name);
        obj.setLocation(center[0], center[1], center[2]);
        obj.RotX = angle_X;
        obj.RotY = angle_Y;
        obj.RotZ = angle_Z;
        obj.transp = True; obj.wireMode = True;
        return
    
    def GEOcylinder_matrix(self, name, rotation_matrix, inner_radius, outer_radius, H, permittivity, conductivity):
        scene = Blender.Scene.GetCurrent();
        mesh = Blender.Mesh.Primitives.Cylinder(32, 2*outer_radius, H);
        mesh.materials = self.materials(permittivity, conductivity);
        for f in mesh.faces:
            f.mat = 0;
    
        obj = scene.objects.new(mesh, name)
        obj.setMatrix(rotation_matrix);
        obj.transp = True; obj.wireMode = True;
        return
    
    def GEOsphere(self, name, center, outer_radius, inner_radius, permittivity, conductivity):
        scene = Blender.Scene.GetCurrent();
        mesh = Blender.Mesh.Primitives.Icosphere(2, 2*outer_radius);
        mesh.materials = self.materials(permittivity, conductivity);
        for f in mesh.faces:
            f.mat = 0;
    
        obj = scene.objects.new(mesh, name)
        obj.setLocation(center[0], center[1], center[2]);
        obj.transp = True; obj.wireMode = True;
        return
    
    def GEOsphere_matrix(self, name, rotation_matrix, outer_radius, inner_radius, permittivity, conductivity):
        scene = Blender.Scene.GetCurrent();
        mesh = Blender.Mesh.Primitives.Icosphere(2, 2*outer_radius);
        mesh.materials = self.materials(permittivity, conductivity);
        for f in mesh.faces:
            f.mat = 0;
    
        obj = scene.objects.new(mesh, name)
        obj.setMatrix(rotation_matrix);
        obj.transp = True; obj.wireMode = True;
        return
        
    def GEObox(self, name, lower, upper):
        scene = Blender.Scene.GetCurrent();
        mesh = Blender.Mesh.Primitives.Cube(1.0);
        mesh.faces.delete(0, list(range(len(mesh.faces))));
    
        obj = scene.objects.new(mesh, name)
        pos = 0.5*(lower+upper);
        diag = upper-lower;
        
        #~ global box_SizeX;
        #~ global box_SizeY;
        #~ global box_SizeZ;
        self.box_SizeX = abs(diag[0]);
        self.box_SizeY = abs(diag[1]);
        self.box_SizeZ = abs(diag[2]);
        print(("box_SizeX = ", self.box_SizeX))
        print(("box_SizeY = ", self.box_SizeY))
        print(("box_SizeZ = ", self.box_SizeZ))
        
        obj.SizeX = self.box_SizeX;
        obj.SizeY = self.box_SizeY;
        obj.SizeZ = self.box_SizeZ;
        
        obj.setLocation(pos[0], pos[1], pos[2]);
        obj.transp = True; obj.wireMode = True;
    
        return
    
    def GEOmesh(self, name, full_mesh, delta_X_vector, delta_Y_vector, delta_Z_vector):
        if len(delta_X_vector)<=0 or len(delta_Y_vector)<=0 or len(delta_Z_vector)<=0:
          return
        
        Nx = len(delta_X_vector)+1;
        Ny = len(delta_Y_vector)+1;
        Nz = len(delta_Z_vector)+1;
        xmax = sum(delta_X_vector);
        ymax = sum(delta_Y_vector);
        zmax = sum(delta_Z_vector);
        
        delta_vector = delta_X_vector + delta_Y_vector + delta_Z_vector;
        
        # print("len(delta_X_vector) = ", len(delta_X_vector))
        # print("len(delta_Y_vector) = ", len(delta_Y_vector))
        # print("len(delta_Z_vector) = ", len(delta_Z_vector))
        # print("len(delta_vector) = ", len(delta_vector))
        #~ global mesh_min;
        #~ global mesh_max;
        self.mesh_min = min(delta_vector);
        self.mesh_max = max(delta_vector);
        # print("mesh_min = ", mesh_min)
        # print("mesh_max = ", mesh_max)
        
        # verts = array.array('d',range());
        # verts = range(Nx*Ny*Nz);
        verts = [];
        edges = [];
        faces = [];
    
        if full_mesh:
            verts = list(range(2*(Nx*Ny + Ny*Nz + Nz*Nx)));
            edges = list(range(Nx*Ny + Ny*Nz + Nz*Nx));
            faces = [];
            
            vert_idx = 0;
            edge_idx = 0;
            # Z edges
            x = 0;
            for i in range(Nx):
                if i>0:
                    x+=delta_X_vector[i-1];
                y = 0;
                for j in range(Ny):
                    if j>0:
                        y+=delta_Y_vector[j-1];
                    A = vert_idx;
                    verts[vert_idx] = Vector(x, y, 0); vert_idx+=1;
                    B = vert_idx;
                    verts[vert_idx] = Vector(x, y, zmax); vert_idx+=1;
                    edges[edge_idx] = [A, B]; edge_idx+=1;
    
            # X edges
            y = 0;
            for j in range(Ny):
                if j>0:
                    y+=delta_Y_vector[j-1];
                z = 0;
                for k in range(Nz):
                    if k>0:
                        z+=delta_Z_vector[k-1];
                    A = vert_idx;
                    verts[vert_idx] = Vector(0, y, z); vert_idx+=1;
                    B = vert_idx;
                    verts[vert_idx] = Vector(xmax, y, z); vert_idx+=1;
                    edges[edge_idx] = [A, B]; edge_idx+=1;
    
            # Y edges
            z = 0;
            for k in range(Nz):
                if k>0:
                    z+=delta_Z_vector[k-1];
                x = 0;
                for i in range(Nx):
                    if i>0:
                        x+=delta_X_vector[i-1];
                    A = vert_idx;
                    verts[vert_idx] = Vector(x, 0, z); vert_idx+=1;
                    B = vert_idx;
                    verts[vert_idx] = Vector(x, ymax, z); vert_idx+=1;
                    edges[edge_idx] = [A, B]; edge_idx+=1;
        
        else:
            verts = list(range(4*(Nx + Ny + Nz)));
            edges = list(range(4*(Nx + Ny + Nz)));
            faces = [];
            
            vert_idx = 0;
            edge_idx = 0;
            
            # X edges
            x = 0;
            for i in range(Nx):
                if i>0:
                    x+=delta_X_vector[i-1];
                A = vert_idx; verts[vert_idx] = Vector(x, 0,    0   ); vert_idx+=1;
                B = vert_idx; verts[vert_idx] = Vector(x, ymax, 0   ); vert_idx+=1;
                C = vert_idx; verts[vert_idx] = Vector(x, ymax, zmax); vert_idx+=1;
                D = vert_idx; verts[vert_idx] = Vector(x, 0,    zmax); vert_idx+=1;
                edges[edge_idx] = [A, B]; edge_idx+=1;
                edges[edge_idx] = [B, C]; edge_idx+=1;
                edges[edge_idx] = [C, D]; edge_idx+=1;
                edges[edge_idx] = [D, A]; edge_idx+=1;
                
            # Y edges
            y = 0;
            for j in range(Ny):
                if j>0:
                    y+=delta_Y_vector[j-1];
                A = vert_idx; verts[vert_idx] = Vector(0,    y, 0   ); vert_idx+=1;
                B = vert_idx; verts[vert_idx] = Vector(xmax, y, 0   ); vert_idx+=1;
                C = vert_idx; verts[vert_idx] = Vector(xmax, y, zmax); vert_idx+=1;
                D = vert_idx; verts[vert_idx] = Vector(0,    y, zmax); vert_idx+=1;
                edges[edge_idx] = [A, B]; edge_idx+=1;
                edges[edge_idx] = [B, C]; edge_idx+=1;
                edges[edge_idx] = [C, D]; edge_idx+=1;
                edges[edge_idx] = [D, A]; edge_idx+=1;
    
            # Z edges
            z = 0;
            for k in range(Nz):
                if k>0:
                    z+=delta_Z_vector[k-1];
                A = vert_idx; verts[vert_idx] = Vector(0,    0,    z); vert_idx+=1;
                B = vert_idx; verts[vert_idx] = Vector(xmax, 0,    z); vert_idx+=1;
                C = vert_idx; verts[vert_idx] = Vector(xmax, ymax, z); vert_idx+=1;
                D = vert_idx; verts[vert_idx] = Vector(0,    ymax, z); vert_idx+=1;
                edges[edge_idx] = [A, B]; edge_idx+=1;
                edges[edge_idx] = [B, C]; edge_idx+=1;
                edges[edge_idx] = [C, D]; edge_idx+=1;
                edges[edge_idx] = [D, A]; edge_idx+=1;
                
        # print(verts)
        BPyAddMesh.add_mesh_simple(name, verts, edges, faces);
        #~ bpy.data.meshes.new("Torus")
        
        obj = Blender.Object.GetSelected()[0];
        # obj.layers = [ 2 ];
        # print('Nverts=', len(verts))
        # print('Nverts=', Nx*Ny*Nz)
    
        # print('Nedges=', len(edges))
        # print('Nedges=', Nx*Ny + Ny*Nz + Nz*Nx)
    
        return
        
    def GEOexcitation(self, name, P1, P2):
        # arrow dimensions:
        arrow_length = (P2-P1).length;
        cone_length = arrow_length/5.0;
        cylinder_length = 4*cone_length;
        cone_radius = arrow_length/20.0;
        cylinder_radius = cone_radius/2.0;
        cylinder_center = P1+2./5.*(P2-P1);
        cone_center = P1+4.5/5.*(P2-P1);
            
        axisZ = -(P2-P1); # because the default primitive cone is oriented along -Z, unlike the one imported from Blender UI...
        axisX = Orthogonal(axisZ);
        axisY = axisZ.cross(axisX);
        axisX.normalize();
        axisY.normalize();
        axisZ.normalize();
        rotmat = Matrix(axisX,axisY,axisZ);
        
        scene = Blender.Scene.GetCurrent();
        
        mesh = Blender.Mesh.Primitives.Cylinder(32, 2*cylinder_radius, cylinder_length);
        mesh.materials = [ self.excitation_material ];
        for f in mesh.faces:
            f.mat = 0;
    
        arrow_cylinder_obj = scene.objects.new(mesh, name)
        arrow_cylinder_obj.setMatrix(rotmat);
        arrow_cylinder_obj.setLocation(cylinder_center[0], cylinder_center[1], cylinder_center[2]);
    
        mesh = Blender.Mesh.Primitives.Cone(32, 2*cone_radius, cone_length);
        mesh.materials = [ self.excitation_material ];
        for f in mesh.faces:
            f.mat = 0;
    
        arrow_cone_obj = scene.objects.new(mesh, name)
        arrow_cone_obj.setMatrix(rotmat);
    
        arrow_cone_obj.setLocation(cone_center[0], cone_center[1], cone_center[2]);
    
        arrow_cylinder_obj.join([arrow_cone_obj]);
        # arrow_cylinder_obj.layers = [ 5 ];
        arrow_cylinder_obj.transp = True; arrow_cylinder_obj.wireMode = True;
    
        scene.objects.unlink(arrow_cone_obj);
        
        return
    
    def snapshot(self, name, plane, P1, P2, snapshot_type):
    
        verts = [];
        if plane == 1:
            #X
            A = Vector(0.5*(P1[0]+P2[0]), P1[1], P1[2]);
            B = Vector(0.5*(P1[0]+P2[0]), P2[1], P1[2]);
            C = Vector(0.5*(P1[0]+P2[0]), P2[1], P2[2]);
            D = Vector(0.5*(P1[0]+P2[0]), P1[1], P2[2]);
            verts = [ A, B, C, D ];
        elif plane == 2:
            #Y        
            A = Vector(P1[0], 0.5*(P1[1]+P2[1]), P1[2]);
            B = Vector(P1[0], 0.5*(P1[1]+P2[1]), P2[2]);
            C = Vector(P2[0], 0.5*(P1[1]+P2[1]), P2[2]);
            D = Vector(P2[0], 0.5*(P1[1]+P2[1]), P1[2]);
            verts = [ A, B, C, D ];
        else:
            #Z
            A = Vector(P1[0], P1[1], 0.5*(P1[2]+P2[2]));
            B = Vector(P2[0], P1[1], 0.5*(P1[2]+P2[2]));
            C = Vector(P2[0], P2[1], 0.5*(P1[2]+P2[2]));
            D = Vector(P1[0], P2[1], 0.5*(P1[2]+P2[2]));
            verts = [ A, B, C, D ];
        
        edges = [];
        faces = [ 0, 1, 2, 3 ];
        #name = 'snapshot';
        #if snapshot_type == 0:
            #name = 'freq_snapshot';
        #elif snapshot_type == 1:
            #name = 'time_snapshot';
        #else:
            #name = 'eps_snapshot';
        
        # print("Adding plane at ", A, B, C, D)
        BPyAddMesh.add_mesh_simple(name, verts, edges, faces);
        obj = Blender.Object.GetSelected()[0];
        # obj.layers = [ 3 ];
        obj.transp = True; obj.wireMode = True;
        
        mesh = Blender.Mesh.Get( obj.data.name );
        mesh.materials = self.snapshot_materials;
        for f in mesh.faces:
            f.mat = snapshot_type;
    
    def GEOfrequency_snapshot(self, name, plane, P1, P2):
        self.snapshot(name, plane, P1, P2, 0);
        return
        
    def GEOtime_snapshot(self, name, plane, P1, P2):
        self.snapshot(name, plane, P1, P2, 1);
        return
    
    def GEOeps_snapshot(self, name, plane, P1, P2):
        self.snapshot(name, plane, P1, P2, 2);
        return
    
    def GEOprobe(self, name, position):
        scene = Blender.Scene.GetCurrent();
        
        #~ probe_size = probe_scalefactor_box*max(box_SizeX,box_SizeY,box_SizeZ);
        probe_size = self.probe_scalefactor_mesh*self.mesh_min;
        # print("probe_size = ", probe_scalefactor_box,"*max(",box_SizeX,",",box_SizeY,",",box_SizeZ,")=", probe_scalefactor_box,"*",max(box_SizeX,box_SizeY,box_SizeZ),"=", probe_size)
        
        mesh = Blender.Mesh.Primitives.Cube(probe_size);
    
        obj = scene.objects.new(mesh, name)
        # obj = Blender.Object.GetSelected()[0];
        obj.setLocation(position[0], position[1], position[2]);
        # obj.layers = [ 4 ];
        obj.transp = True; obj.wireMode = True;
        return

###############################
# UTILITY FUNCTIONS
###############################
def grid_index(Nx, Ny, Nz, i, j, k):
    return (Ny*Nz*i + Nz*j + k);

def Orthogonal(vec):
    xx = abs(vec.x);
    yy = abs(vec.y);
    zz = abs(vec.z);
    if (xx < yy):
        if xx < zz:
            return Vector(0,vec.z,-vec.y);
        else:
            return Vector(vec.y,-vec.x,0);
    else:
        if yy < zz:
            return Vector(-vec.z,0,vec.x)
        else:
            return Vector(vec.y,-vec.x,0);

def rotationMatrix(axis_point, axis_direction, angle_degrees):
  ''' return a rotation matrix for a rotation around an arbitrary axis '''
  axis = Blender.Mathutils.Vector(axis_direction[0],axis_direction[1],axis_direction[2])
  C = Blender.Mathutils.Vector(axis_point[0],axis_point[1],axis_point[2]);
  T = Blender.Mathutils.TranslationMatrix(C)
  Tinv = Blender.Mathutils.TranslationMatrix(-C)
  R = Blender.Mathutils.RotationMatrix(angle_degrees, 4, 'r', axis)
  return Tinv*R*T;

###############################
# TEST FUNCTIONS
###############################
def TestObjects():
    ''' test objects '''
    Blender.Window.SetActiveLayer(1<<0);
    GEOmesh(False, [1, 1], [1, 2, 3], [4, 3, 2, 1]);
    
    Blender.Window.SetActiveLayer(1<<1);
    GEOexcitation(Vector(0,0,0), Vector(1,0,0));
    GEOexcitation(Vector(0,0,0), Vector(0,1,0));
    GEOexcitation(Vector(0,0,0), Vector(0,0,1));

    GEOexcitation(Vector(1,0,0), Vector(2,0,0));
    GEOexcitation(Vector(0,1,0), Vector(0,2,0));
    GEOexcitation(Vector(0,0,1), Vector(0,0,2));

    GEOexcitation(Vector(0,0,0), Vector(1,1,1));
    GEOexcitation(Vector(1,1,1), Vector(2,2,2));
    GEOexcitation(Vector(2,2,2), Vector(3,3,3));

    GEOexcitation(Vector(1,1,1), Vector(2,1,2));
    GEOexcitation(Vector(2,1,2), Vector(2,2,3));
    GEOexcitation(Vector(2,2,3), Vector(1,2,4));

    # The death spiral!
    # x1=0;y1=0;z1=0;
    # x2=0;y2=0;z2=0;
    # for i in range(10*36):
        # x2=math.cos(math.radians(10*i));
        # y2=math.sin(math.radians(10*i));
        # z2=(10.*i)/360.;
        # GEOexcitation(Vector(x1,y1,z1), Vector(x2,y2,z2));
        # x1=x2;y1=y2;z1=z2;

    Blender.Window.SetActiveLayer(1<<2);
    GEOfrequency_snapshot(1, Vector(-1, -1, -1), Vector(1, 1, 1));
    GEOfrequency_snapshot(2, Vector(-1, -1, -1), Vector(1, 1, 1));
    GEOfrequency_snapshot(3, Vector(-1, -1, -1), Vector(1, 1, 1));

    Blender.Window.SetActiveLayer(1<<3);
    GEOtime_snapshot(1, Vector(2, -1, -1), Vector(4, 1, 1));
    GEOtime_snapshot(2, Vector(2, -1, -1), Vector(4, 1, 1));
    GEOtime_snapshot(3, Vector(2, -1, -1), Vector(4, 1, 1));

    Blender.Window.SetActiveLayer(1<<4);
    GEOeps_snapshot(1, Vector(5, -1, -1), Vector(7, 1, 1));
    GEOeps_snapshot(2, Vector(5, -1, -1), Vector(7, 1, 1));
    GEOeps_snapshot(3, Vector(5, -1, -1), Vector(7, 1, 1));

    Blender.Window.SetActiveLayer(1<<5);
    GEOfrequency_snapshot(1, Vector(-1, -1, -1), Vector(-1, 1, 1));
    GEOfrequency_snapshot(2, Vector(-1, -1, -1), Vector(1, -1, 1));
    GEOfrequency_snapshot(3, Vector(-1, -1, -1), Vector(1, 1, -1));

    Blender.Window.SetActiveLayer(1<<6);
    GEOtime_snapshot(1, Vector(2, -1, -1), Vector(2, 1, 1));
    GEOtime_snapshot(2, Vector(2, -1, -1), Vector(4, -1, 1));
    GEOtime_snapshot(3, Vector(2, -1, -1), Vector(4, 1, -1));

    Blender.Window.SetActiveLayer(1<<7);
    GEOeps_snapshot(1, Vector(5, -1, -1), Vector(5, 1, 1));
    GEOeps_snapshot(2, Vector(5, -1, -1), Vector(7, -1, 1));
    GEOeps_snapshot(3, Vector(5, -1, -1), Vector(7, 1, -1));

    for i in range(11):
        Blender.Window.SetActiveLayer(1<<8);
        GEOblock(Vector(0, 0, i), Vector(1, 1, i+1), 10*i, 0);
        GEObox(Vector(1, 1, i), Vector(2, 2, i+1));
        GEOblock(Vector(2, 2, i), Vector(3, 3, i+1), 10*i, 100);
        GEOcylinder(Vector(3.5, 3.5, i+0.5), 0, 0.5, 1, 100-10*i, 200, 0);
        GEOcylinder(Vector(4.5, 4.5, i+0.5), 0, 0.5, 1, 10*i, 200, 45);
        GEOsphere(Vector(5.5, 5.5, i+0.5), 0.5, 0, i, 0);
        Blender.Window.SetActiveLayer(1<<9);
        GEOprobe(Vector(0, 0, i));

    Blender.Scene.GetCurrent().setLayers([1,2,3,4,5,6,7,8,9,10]);

def TestMatrix():
  ''' test Blender matrix object '''
  u=Blender.Mathutils.Vector(1,2,3)
  v=Blender.Mathutils.Vector(4,5,6)
  w=Blender.Mathutils.Vector(7,8,9)
  M=Blender.Mathutils.Matrix(u,v,w)
  print('============')
  print(u)
  print(v)
  print(w)
  print('============')
  print(M)
  print('============')
  print((Blender.Mathutils.RotationMatrix(math.radians(0), 2)))
  print((Blender.Mathutils.RotationMatrix(math.radians(45), 2)))
  print((Blender.Mathutils.RotationMatrix(math.radians(90), 2)))
  print((Blender.Mathutils.RotationMatrix(0, 2)))
  print((Blender.Mathutils.RotationMatrix(45, 2)))
  print((Blender.Mathutils.RotationMatrix(90, 2)))
  M=Blender.Mathutils.RotationMatrix(45, 3, 'x' )
  print('======QUAT======')
  print(M)
  print((M.toQuat()))
  print('============')
  Q=Blender.Mathutils.RotationMatrix(45, 4, 'x' )
  print(Q)
  print('============')
  u1=Blender.Mathutils.Vector(1,2,3,4)
  u2=Blender.Mathutils.Vector(5,6,7,8)
  u3=Blender.Mathutils.Vector(9,10,11,12)
  u4=Blender.Mathutils.Vector(13,14,15,16)        
  print('============')
  Q=Blender.Mathutils.Matrix(u1,u2,u3,u4)
  print(Q)
  print('============')
  print((Q.translationPart()))
  print((Q.scalePart()))
  print((Q.rotationPart()))
  print('====Q=R*Sx*Sy*Sz*T========')
  R=Blender.Mathutils.RotationMatrix(45, 4, 'r', Blender.Mathutils.Vector(17,18,19))
  T=Blender.Mathutils.TranslationMatrix(Blender.Mathutils.Vector(14,15,16))
  Sx=Blender.Mathutils.ScaleMatrix(2,4,Blender.Mathutils.Vector(1,0,0))
  Sy=Blender.Mathutils.ScaleMatrix(3,4,Blender.Mathutils.Vector(0,1,0))
  Sz=Blender.Mathutils.ScaleMatrix(4,4,Blender.Mathutils.Vector(0,0,1))
  print(Sx)
  print(Sy)
  print(Sz)
  S=Sx*Sy*Sz
  print((S.scalePart()))
  print(T)
  print(R)
  Q=S*R*T
  #~ Q=R*T
  print('============')
  print(Q)
  print('============')
  print((Q.translationPart()))
  print((Q.scalePart()))
  print((Q.rotationPart()))
  print('============')
  
  scene = Blender.Scene.GetCurrent();
  #~ mesh = Blender.Mesh.Primitives.Cylinder(32, 2, 5);
  mesh = Blender.Mesh.Primitives.Cone(32, 2, 3);
  mesh = Blender.Mesh.Primitives.Cube(1.0);
  obj = scene.objects.new(mesh, 'test_object');
  #~ obj.setMatrix(rotmat);
  #~ obj.setLocation(cone_center[0], cone_center[1], cone_center[2]);

  #~ obj.setLocation(center[0], center[1], center[2]);
  #~ obj.RotX = angle_X;
  #~ obj.RotY = angle_Y;
  #~ obj.RotZ = angle_Z;
  #~ obj.transp = True; obj.wireMode = True;

  #~ pos = 0.5*(lower+upper);
  #~ diag = upper-lower;
  obj.SizeX = 1;
  obj.SizeY = 2;
  obj.SizeZ = 3;
  L=Blender.Mathutils.Vector(1,0,0);
  obj.setLocation(L);
  M=obj.getMatrix()
  C=Blender.Mathutils.Vector(-1,0,0);
  T=Blender.Mathutils.TranslationMatrix(C)
  Tinv=Blender.Mathutils.TranslationMatrix(-(C))
  R=Blender.Mathutils.RotationMatrix(45, 4, 'r', Blender.Mathutils.Vector(0,0,1))
  #~ T=Blender.Mathutils.TranslationMatrix(-2,0,0)
  print('############')
  print(M)
  print(T)
  print(Tinv)
  print((M*Tinv))
  print((M*Tinv*R*T))
  print('############')
  obj.setMatrix(M*Tinv*R*T);
  print('# EULER ###########')
  print((obj.getMatrix().toEuler()))
  print('############')
  #~ obj.RotX = 90;
  #~ obj.RotY = 45;
  #~ obj.RotZ = 0;

  #~ sys.exit(0)

  #~ Vector object 	
  #~ ProjectVecs(vec1, vec2)
  #~ Return the projection of vec1 onto vec2. 	source code
  #~ Matrix object. 	
  #~ RotationMatrix(angle, matSize, axisFlag, axis)
  #~ Create a matrix representing a rotation. 	source code
  #~ Matrix object. 	
  #~ TranslationMatrix(vector)
  #~ Create a matrix representing a translation 	source code
  #~ Matrix object. 	
  #~ ScaleMatrix(factor, matSize, axis)
  #~ Create a matrix representing a scaling. 	source code
  #~ Matrix object. 	
  #~ OrthoProjectionMatrix(plane, matSize, axis)
  #~ Create a matrix to represent an orthographic projection
