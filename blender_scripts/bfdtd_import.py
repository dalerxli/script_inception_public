#!BPY

"""
Name: 'Bristol FDTD (*.in,*.geo,*.inp)'
Blender: 249
Group: 'Import'
Tooltip: 'Import from Bristol FDTD'
"""
###############################
# IMPORTS
###############################

import Blender;
import bpy;
import BPyAddMesh;
import math;
import os;
import sys;
import re;
import array;
import cPickle;
from bfdtd_parser import *;

###############################
# INITIALIZATIONS
###############################
cfgfile = os.path.expanduser('~')+'/BlenderImport.txt';

# define Vector+Matrix
Vector = Blender.Mathutils.Vector;
Matrix = Blender.Mathutils.Matrix;

# prepare base materials
material_dict={};
frequency_snapshot_material = Blender.Material.New('frequency_snapshot');
frequency_snapshot_material.rgbCol = 0.5, 0, 0;
frequency_snapshot_material.setAlpha(0.5);

time_snapshot_material = Blender.Material.New('time_snapshot');
time_snapshot_material.rgbCol = 0.5, 1, 0;
time_snapshot_material.setAlpha(0.5);

eps_snapshot_material = Blender.Material.New('eps_snapshot');
eps_snapshot_material.rgbCol = 0.5, 0, 1;
eps_snapshot_material.setAlpha(0.5);

excitation_material = Blender.Material.New('excitation');
excitation_material.rgbCol = 1, 0, 0;
excitation_material.setAlpha(0.5);

snapshot_materials = [ frequency_snapshot_material, time_snapshot_material, eps_snapshot_material ];

probe_scalefactor_box = 0.0218;
probe_scalefactor_mesh = 0.5;
mesh_min = 0;
mesh_max = 0;
box_SizeX = 0;
box_SizeY = 0;
box_SizeZ = 0;

###############################
# FUNCTIONS
###############################

def materials(permittivity, conductivity):
    if permittivity not in material_dict:
        n = math.sqrt(permittivity)
        
        max_permittivity = 25.0;
        permittivity_material = Blender.Material.New('permittivity');
        permittivity_material.rgbCol = 0, permittivity/max_permittivity, 1.0-permittivity/max_permittivity;
        permittivity_material.setAlpha(0.5);
        
        # conductivity_material = Blender.Material.New('conductivity')
        # conductivity_material.rgbCol = 0, 1.0-conductivity/100.0, 0;
        # conductivity_material.setAlpha(0.5);

        # refractive_index_material = Blender.Material.New('refractive_index')
        # if n!=0:
            # refractive_index_material.rgbCol = 0, 0, 1.0/n;
        # else:
            # refractive_index_material.rgbCol = 0, 0, 1.0;
        # refractive_index_material.setAlpha(0.5);
          
        material_dict[permittivity] = permittivity_material;

    return [ material_dict[permittivity] ];

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

def GEOblock(lower, upper, permittivity, conductivity):
    scene = Blender.Scene.GetCurrent();
    mesh = Blender.Mesh.Primitives.Cube(1.0);
    mesh.materials = materials(permittivity, conductivity);
    for f in mesh.faces:
        f.mat = 0;

    obj = scene.objects.new(mesh, 'block');
    pos = 0.5*(lower+upper);
    diag = upper-lower;
    obj.SizeX = abs(diag[0]);
    obj.SizeY = abs(diag[1]);
    obj.SizeZ = abs(diag[2]);
    obj.setLocation(pos[0], pos[1], pos[2]);
    obj.transp = True; obj.wireMode = True;
    return;

def GEOblock_matrix(rotation_matrix, permittivity, conductivity):
    scene = Blender.Scene.GetCurrent();
    mesh = Blender.Mesh.Primitives.Cube(1.0);
    mesh.materials = materials(permittivity, conductivity);
    for f in mesh.faces:
        f.mat = 0;

    obj = scene.objects.new(mesh, 'block');
    obj.setMatrix(rotation_matrix);
    obj.transp = True; obj.wireMode = True;
    return;

def GEOcylinder(center, inner_radius, outer_radius, H, permittivity, conductivity, angle_X, angle_Y, angle_Z):
    scene = Blender.Scene.GetCurrent();
    mesh = Blender.Mesh.Primitives.Cylinder(32, 2*outer_radius, H);
    mesh.materials = materials(permittivity, conductivity);
    for f in mesh.faces:
        f.mat = 0;

    obj = scene.objects.new(mesh, 'cylinder');
    obj.setLocation(center[0], center[1], center[2]);
    obj.RotX = angle_X;
    obj.RotY = angle_Y;
    obj.RotZ = angle_Z;
    obj.transp = True; obj.wireMode = True;
    return

def GEOcylinder_matrix(rotation_matrix, inner_radius, outer_radius, H, permittivity, conductivity):
    scene = Blender.Scene.GetCurrent();
    mesh = Blender.Mesh.Primitives.Cylinder(32, 2*outer_radius, H);
    mesh.materials = materials(permittivity, conductivity);
    for f in mesh.faces:
        f.mat = 0;

    obj = scene.objects.new(mesh, 'cylinder');
    obj.setMatrix(rotation_matrix);
    obj.transp = True; obj.wireMode = True;
    return

def GEOsphere(center, outer_radius, inner_radius, permittivity, conductivity):
    scene = Blender.Scene.GetCurrent();
    mesh = Blender.Mesh.Primitives.Icosphere(2, 2*outer_radius);
    mesh.materials = materials(permittivity, conductivity);
    for f in mesh.faces:
        f.mat = 0;

    obj = scene.objects.new(mesh, 'sphere');
    obj.setLocation(center[0], center[1], center[2]);
    obj.transp = True; obj.wireMode = True;
    return

def GEOsphere_matrix(rotation_matrix, outer_radius, inner_radius, permittivity, conductivity):
    scene = Blender.Scene.GetCurrent();
    mesh = Blender.Mesh.Primitives.Icosphere(2, 2*outer_radius);
    mesh.materials = materials(permittivity, conductivity);
    for f in mesh.faces:
        f.mat = 0;

    obj = scene.objects.new(mesh, 'sphere');
    obj.setMatrix(rotation_matrix);
    obj.transp = True; obj.wireMode = True;
    return
    
def GEObox(lower, upper):
    scene = Blender.Scene.GetCurrent();
    mesh = Blender.Mesh.Primitives.Cube(1.0);
    mesh.faces.delete(0, range(len(mesh.faces)));

    obj = scene.objects.new(mesh, 'box');
    pos = 0.5*(lower+upper);
    diag = upper-lower;
    
    global box_SizeX;
    global box_SizeY;
    global box_SizeZ;
    box_SizeX = abs(diag[0]);
    box_SizeY = abs(diag[1]);
    box_SizeZ = abs(diag[2]);
    print "box_SizeX = ", box_SizeX;
    print "box_SizeY = ", box_SizeY;
    print "box_SizeZ = ", box_SizeZ;
    
    obj.SizeX = box_SizeX;
    obj.SizeY = box_SizeY;
    obj.SizeZ = box_SizeZ;
    
    obj.setLocation(pos[0], pos[1], pos[2]);
    obj.transp = True; obj.wireMode = True;

    return

def GEOmesh(full_mesh, delta_X_vector, delta_Y_vector, delta_Z_vector):
    if len(delta_X_vector)<=0 or len(delta_Y_vector)<=0 or len(delta_Z_vector)<=0:
      return
    
    Nx = len(delta_X_vector)+1;
    Ny = len(delta_Y_vector)+1;
    Nz = len(delta_Z_vector)+1;
    xmax = sum(delta_X_vector);
    ymax = sum(delta_Y_vector);
    zmax = sum(delta_Z_vector);
    
    delta_vector = delta_X_vector + delta_Y_vector + delta_Z_vector;
    
    # print "len(delta_X_vector) = ", len(delta_X_vector);
    # print "len(delta_Y_vector) = ", len(delta_Y_vector);
    # print "len(delta_Z_vector) = ", len(delta_Z_vector);
    # print "len(delta_vector) = ", len(delta_vector);
    global mesh_min;
    global mesh_max;
    mesh_min = min(delta_vector);
    mesh_max = max(delta_vector);
    # print "mesh_min = ", mesh_min;
    # print "mesh_max = ", mesh_max;
    
    # verts = array.array('d',range());
    # verts = range(Nx*Ny*Nz);
    verts = [];
    edges = [];
    faces = [];

    if full_mesh:
        verts = range(2*(Nx*Ny + Ny*Nz + Nz*Nx));
        edges = range(Nx*Ny + Ny*Nz + Nz*Nx);
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
        verts = range(4*(Nx + Ny + Nz));
        edges = range(4*(Nx + Ny + Nz));
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
            
    # print verts;
    BPyAddMesh.add_mesh_simple('mesh', verts, edges, faces);
    obj = Blender.Object.GetSelected()[0];
    # obj.layers = [ 2 ];
    # print 'Nverts=', len(verts);
    # print 'Nverts=', Nx*Ny*Nz;

    # print 'Nedges=', len(edges);
    # print 'Nedges=', Nx*Ny + Ny*Nz + Nz*Nx;

    return
    
def GEOexcitation(P1, P2):
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
    mesh.materials = [ excitation_material ];
    for f in mesh.faces:
        f.mat = 0;

    arrow_cylinder_obj = scene.objects.new(mesh, 'excitation');
    arrow_cylinder_obj.setMatrix(rotmat);
    arrow_cylinder_obj.setLocation(cylinder_center[0], cylinder_center[1], cylinder_center[2]);

    mesh = Blender.Mesh.Primitives.Cone(32, 2*cone_radius, cone_length);
    mesh.materials = [ excitation_material ];
    for f in mesh.faces:
        f.mat = 0;

    arrow_cone_obj = scene.objects.new(mesh, 'arrow_cone');
    arrow_cone_obj.setMatrix(rotmat);

    arrow_cone_obj.setLocation(cone_center[0], cone_center[1], cone_center[2]);

    arrow_cylinder_obj.join([arrow_cone_obj]);
    # arrow_cylinder_obj.layers = [ 5 ];
    arrow_cylinder_obj.transp = True; arrow_cylinder_obj.wireMode = True;

    scene.objects.unlink(arrow_cone_obj);
    
    return

def snapshot(plane, P1, P2, snapshot_type):

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
    name = 'snapshot';
    if snapshot_type == 0:
        name = 'freq_snapshot';
    elif snapshot_type == 1:
        name = 'time_snapshot';
    else:
        name = 'eps_snapshot';
    
    # print "Adding plane at ", A, B, C, D;
    BPyAddMesh.add_mesh_simple(name, verts, edges, faces);
    obj = Blender.Object.GetSelected()[0];
    # obj.layers = [ 3 ];
    obj.transp = True; obj.wireMode = True;
    
    mesh = Blender.Mesh.Get( obj.data.name );
    mesh.materials = snapshot_materials;
    for f in mesh.faces:
        f.mat = snapshot_type;

def GEOfrequency_snapshot(plane, P1, P2):
    snapshot(plane, P1, P2, 0);
    return
    
def GEOtime_snapshot(plane, P1, P2):
    snapshot(plane, P1, P2, 1);
    return

def GEOeps_snapshot(plane, P1, P2):
    snapshot(plane, P1, P2, 2);
    return

def GEOprobe(position):
    scene = Blender.Scene.GetCurrent();
    
    #~ probe_size = probe_scalefactor_box*max(box_SizeX,box_SizeY,box_SizeZ);
    probe_size = probe_scalefactor_mesh*mesh_min;
    # print "probe_size = ", probe_scalefactor_box,"*max(",box_SizeX,",",box_SizeY,",",box_SizeZ,")=", probe_scalefactor_box,"*",max(box_SizeX,box_SizeY,box_SizeZ),"=", probe_size;
    
    mesh = Blender.Mesh.Primitives.Cube(probe_size);

    obj = scene.objects.new(mesh, 'probe');
    # obj = Blender.Object.GetSelected()[0];
    obj.setLocation(position[0], position[1], position[2]);
    # obj.layers = [ 4 ];
    obj.transp = True; obj.wireMode = True;
    return

def TestObjects():
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
  u=Blender.Mathutils.Vector(1,2,3)
  v=Blender.Mathutils.Vector(4,5,6)
  w=Blender.Mathutils.Vector(7,8,9)
  M=Blender.Mathutils.Matrix(u,v,w)
  print '============'
  print u
  print v
  print w
  print '============'
  print M
  print '============'
  print Blender.Mathutils.RotationMatrix(math.radians(0), 2)
  print Blender.Mathutils.RotationMatrix(math.radians(45), 2)
  print Blender.Mathutils.RotationMatrix(math.radians(90), 2)
  print Blender.Mathutils.RotationMatrix(0, 2)
  print Blender.Mathutils.RotationMatrix(45, 2)
  print Blender.Mathutils.RotationMatrix(90, 2)
  M=Blender.Mathutils.RotationMatrix(45, 3, 'x' )
  print '======QUAT======'
  print M
  print M.toQuat()
  print '============'
  Q=Blender.Mathutils.RotationMatrix(45, 4, 'x' )
  print Q;
  print '============'
  u1=Blender.Mathutils.Vector(1,2,3,4)
  u2=Blender.Mathutils.Vector(5,6,7,8)
  u3=Blender.Mathutils.Vector(9,10,11,12)
  u4=Blender.Mathutils.Vector(13,14,15,16)        
  print '============'
  Q=Blender.Mathutils.Matrix(u1,u2,u3,u4)
  print Q
  print '============'
  print Q.translationPart()
  print Q.scalePart()
  print Q.rotationPart()
  print '====Q=R*Sx*Sy*Sz*T========'
  R=Blender.Mathutils.RotationMatrix(45, 4, 'r', Blender.Mathutils.Vector(17,18,19))
  T=Blender.Mathutils.TranslationMatrix(Blender.Mathutils.Vector(14,15,16))
  Sx=Blender.Mathutils.ScaleMatrix(2,4,Blender.Mathutils.Vector(1,0,0))
  Sy=Blender.Mathutils.ScaleMatrix(3,4,Blender.Mathutils.Vector(0,1,0))
  Sz=Blender.Mathutils.ScaleMatrix(4,4,Blender.Mathutils.Vector(0,0,1))
  print Sx
  print Sy
  print Sz
  S=Sx*Sy*Sz
  print S.scalePart()
  print T
  print R
  Q=S*R*T
  #~ Q=R*T
  print '============'
  print Q
  print '============'
  print Q.translationPart()
  print Q.scalePart()
  print Q.rotationPart()
  print '============'
  
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
  print '############'
  print M
  print T
  print Tinv
  print M*Tinv
  print M*Tinv*R*T
  print '############'
  obj.setMatrix(M*Tinv*R*T);
  print '# EULER ###########'
  print obj.getMatrix().toEuler()
  print '############'
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
  
def importBristolFDTD(filename):
    print '----->Importing bristol FDTD geometry...';
    Blender.Window.WaitCursor(1);

    # save import path
    # Blender.Set('tempdir',os.path.dirname(filename));
    FILE = open(cfgfile, 'w');
    cPickle.dump(filename, FILE);
    FILE.close();
    
    # create structured_entries
    structured_entries = readBristolFDTD(filename);
    
    # Box
    Blender.Window.SetActiveLayer(1<<0);
    GEObox(Vector(structured_entries.box.lower), Vector(structured_entries.box.upper));
    Blender.Window.SetActiveLayer(1<<1);
    GEOmesh(False, structured_entries.xmesh,structured_entries.ymesh,structured_entries.zmesh);
    
    # Time_snapshot (time or EPS)
    for time_snapshot in structured_entries.time_snapshot_list:
        if time_snapshot.eps == 0:
            Blender.Window.SetActiveLayer(1<<2);
            GEOtime_snapshot(time_snapshot.plane, time_snapshot.P1, time_snapshot.P2);
        else:
            Blender.Window.SetActiveLayer(1<<3);
            GEOeps_snapshot(time_snapshot.plane, time_snapshot.P1, time_snapshot.P2);
    # Frequency_snapshot
    Blender.Window.SetActiveLayer(1<<4);
    for frequency_snapshot in structured_entries.frequency_snapshot_list:
        GEOfrequency_snapshot(frequency_snapshot.plane, frequency_snapshot.P1, frequency_snapshot.P2);

    # Excitation
    Blender.Window.SetActiveLayer(1<<5);
    for excitation in structured_entries.excitation_list:
        GEOexcitation(Vector(excitation.P1), Vector(excitation.P2));
    # Probe
    Blender.Window.SetActiveLayer(1<<6);
    for probe in structured_entries.probe_list:
        # print 'probe = ',Vector(probe.position);
        GEOprobe(Vector(probe.position));
    
    # Sphere
    Blender.Window.SetActiveLayer(1<<7);
    for sphere in structured_entries.sphere_list:
        # variables
        center = Vector(sphere.center)

        # initialise rotation_matrix
        rotation_matrix = Blender.Mathutils.Matrix()
        rotation_matrix.identity();

        # position object
        T = Blender.Mathutils.TranslationMatrix(center)
        rotation_matrix *= T;
        
        # add rotations
        for r in sphere.rotation_list:
          rotation_matrix *= rotationMatrix(r.axis_point, r.axis_direction, r.angle_degrees);
          
        # create object
        GEOsphere_matrix(rotation_matrix, sphere.outer_radius, sphere.inner_radius, sphere.permittivity, sphere.conductivity);
        
    # Block
    Blender.Window.SetActiveLayer(1<<8);
    for block in structured_entries.block_list:
        # variables
        lower = Vector(block.lower)
        upper = Vector(block.upper)
        pos = 0.5*(lower+upper);
        diag = upper-lower;

        # initialise rotation_matrix
        rotation_matrix = Blender.Mathutils.Matrix()
        rotation_matrix.identity();

        # scale object
        Sx=Blender.Mathutils.ScaleMatrix(abs(diag[0]),4,Blender.Mathutils.Vector(1,0,0))
        Sy=Blender.Mathutils.ScaleMatrix(abs(diag[1]),4,Blender.Mathutils.Vector(0,1,0))
        Sz=Blender.Mathutils.ScaleMatrix(abs(diag[2]),4,Blender.Mathutils.Vector(0,0,1))
        rotation_matrix *= Sx*Sy*Sz;
        # position object
        T = Blender.Mathutils.TranslationMatrix(pos)
        rotation_matrix *= T;
        
        # add rotations
        for r in block.rotation_list:
          rotation_matrix *= rotationMatrix(r.axis_point, r.axis_direction, r.angle_degrees);

        # create object
        GEOblock_matrix(rotation_matrix, block.permittivity, block.conductivity);
    
    # Cylinder
    Blender.Window.SetActiveLayer(1<<9);
    for cylinder in structured_entries.cylinder_list:
      
        # initialise rotation_matrix
        rotation_matrix = Blender.Mathutils.Matrix()
        rotation_matrix.identity();

        # because FDTD cylinders are aligned with the Y axis by default
        rotation_matrix *= rotationMatrix(Blender.Mathutils.Vector(0,0,0), Blender.Mathutils.Vector(1,0,0), -90)
        
        # position object
        T = Blender.Mathutils.TranslationMatrix(Blender.Mathutils.Vector(cylinder.center[0],cylinder.center[1],cylinder.center[2]))
        rotation_matrix *= T;
        
        # add rotations
        for r in cylinder.rotation_list:
          rotation_matrix *= rotationMatrix(r.axis_point, r.axis_direction, r.angle_degrees);
        
        # create object
        GEOcylinder_matrix(rotation_matrix, cylinder.inner_radius,cylinder.outer_radius,cylinder.height,cylinder.permittivity,cylinder.conductivity);

    #########################
    # Not yet implemented:
    # Flag
    # structured_entries.flag;
    # Boundaries
    # structured_entries.boundaries;
    #########################

    scene = Blender.Scene.GetCurrent();
    scene.update(0);
    Blender.Window.RedrawAll();
    Blender.Window.WaitCursor(0);
    Blender.Scene.GetCurrent().setLayers([1,3,4,5,6,7,8,9,10]);
    print '...done';

###############################
# MAIN FUNCTION
###############################
def main():
  print 'sys.argv=',sys.argv;
  print 'len(sys.argv)=',len(sys.argv);
  
  # arg[0]='blender'
  # arg[1]='-P'
  # arg[2]='scriptname'
  # arg[3]='--'
  
  if len(sys.argv)>4:
      for i in range(len(sys.argv)- 4):
          print 'Importing ', sys.argv[4+i];
          importBristolFDTD(sys.argv[4+i]);
  else:
      ###################
      # load import path
      ###################
      # print 'tempdir=',Blender.Get('tempdir');
      # print 'soundsdir=',Blender.Get('soundsdir');
  
      # default_path = Blender.Get('tempdir');
      # if not default_path:
          # default_path = 'H:\DATA';
          
      default_path = 'H:\DATA';
      print 'cfgfile = ', cfgfile;
  
      if os.path.isfile(cfgfile) and os.path.getsize(cfgfile) > 0:
          with open(cfgfile, 'r') as FILE:
              default_path = cPickle.load(FILE);
  
      ###################
  
      ###################
      # import file
      ###################
      Blender.Window.FileSelector(importBristolFDTD, "Import Bristol FDTD file...", default_path);
      # importBristolFDTD('H:\\MATLAB\\blender_scripts\\rotated_cylinder.in');
      # TestObjects();

if __name__ == "__main__":
    main()
