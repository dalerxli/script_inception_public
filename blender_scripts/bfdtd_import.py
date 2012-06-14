#!BPY
# -*- coding: utf-8 -*-

"""
Name: 'Bristol FDTD (*.in,*.geo,*.inp)'
Blender: 249
Group: 'Import'
Tooltip: 'Import from Bristol FDTD'
"""
###############################
# IMPORTS
###############################
from bfdtd.bfdtd_parser import *
from blender_scripts.FDTDGeometryObjects import *
from blender_scripts.layer_manager import *
from bfdtd.bristolFDTD_generator_functions import *
from mathutils import *
import os
import pickle
#import cPickle

#import layer_manager
#from Blender import Draw, BGL, Text, Scene, Window, Object

###############################
# INITIALIZATIONS
###############################
#cfgfile = os.path.expanduser('~')+'/BlenderImportBFDTD.txt'

# official script data location :)
# Blender >=2.5
if os.getenv('BLENDERDATADIR'):
  cfgfile = os.getenv('BLENDERDATADIR')+os.sep+'BlenderImportBFDTD.txt'
else:
  cfgfile = getuserdir()+os.sep+'BlenderImportBFDTD.txt'

# Blender <2.49b
#print('Blender.Get("datadir") = '+str(Blender.Get("datadir")))
#if Blender.Get("datadir"):
  #print('datadir defined')
  #cfgfile = Blender.Get("datadir")+'/BlenderImportBFDTD.txt'
#else:
  #print('datadir not defined or somehow broken. Make sure the directory $HOME/.blender/scripts/bpydata is present and accessible.')
  #sys.exit(0)

###############################
# IMPORT FUNCTION
###############################
def importBristolFDTD(filename):
    ''' import BristolFDTD geometry from .in,.geo or .inp and create corresponding structure in Blender '''
    print('----->Importing bristol FDTD geometry: '+filename)
    #Blender.Window.WaitCursor(1);

    # save import path
    # Blender.Set('tempdir',os.path.dirname(filename));
    #FILE = open(, 'w');
    #pickle.dump(, FILE);
    #FILE.close();
    
    with open(cfgfile, 'wb') as f:
      # Pickle the 'data' dictionary using the highest protocol available.
      pickle.dump(filename, f, pickle.HIGHEST_PROTOCOL)
    
    # create structured_entries
    structured_entries = readBristolFDTD(filename);
    
    FDTDGeometryObjects_obj = FDTDGeometryObjects()
    
    # Blender.Window.RedrawAll(); # This must be called before any SetActiveLayer calls!
    
    layerManager = LayerManagerObjects()
    
    # Box
    #Blender.Window.SetActiveLayer(1<<layerManager.DefaultLayers.index('box'));
    FDTDGeometryObjects_obj.GEObox(structured_entries.box.name, Vector(structured_entries.box.lower), Vector(structured_entries.box.upper));
    
    # mesh
    #Blender.Window.SetActiveLayer(1<<layerManager.DefaultLayers.index('mesh'));
    #FDTDGeometryObjects_obj.GEOmesh('mesh', False, structured_entries.delta_X_vector,structured_entries.delta_Y_vector,structured_entries.delta_Z_vector);
    #Blender.Window.SetActiveLayer(1<<layerManager.DefaultLayers.index('mesh'));
    FDTDGeometryObjects_obj.GEOmesh('mesh', False, structured_entries.mesh.getXmeshDelta(),structured_entries.mesh.getYmeshDelta(),structured_entries.mesh.getZmeshDelta());
    
    # Time_snapshot (time or EPS)
    for time_snapshot in structured_entries.time_snapshot_list:
        if time_snapshot.eps == 0:
            Blender.Window.SetActiveLayer(1<<layerManager.DefaultLayers.index('time_snapshots_'+planeNumberName(time_snapshot.plane)[1]));
            FDTDGeometryObjects_obj.GEOtime_snapshot(time_snapshot.name, time_snapshot.plane, time_snapshot.P1, time_snapshot.P2);
        else:
            Blender.Window.SetActiveLayer(1<<layerManager.DefaultLayers.index('eps_snapshots_'+planeNumberName(time_snapshot.plane)[1]));
            FDTDGeometryObjects_obj.GEOeps_snapshot(time_snapshot.name, time_snapshot.plane, time_snapshot.P1, time_snapshot.P2);
    # Frequency_snapshot
    for frequency_snapshot in structured_entries.frequency_snapshot_list:
        Blender.Window.SetActiveLayer(1<<layerManager.DefaultLayers.index('frequency_snapshots_'+planeNumberName(frequency_snapshot.plane)[1]));
        FDTDGeometryObjects_obj.GEOfrequency_snapshot(frequency_snapshot.name, frequency_snapshot.plane, frequency_snapshot.P1, frequency_snapshot.P2);

    # Excitation
    #Blender.Window.SetActiveLayer(1<<layerManager.DefaultLayers.index('excitations'));
    for excitation in structured_entries.excitation_list:
        #Blender.Window.SetActiveLayer(1<<layerManager.DefaultLayers.index('excitations'));
        #print(Blender.Window.GetActiveLayer())
        print(excitation)
        FDTDGeometryObjects_obj.GEOexcitation(excitation);
        #FDTDGeometryObjects_obj.GEOexcitation(excitation.name, Vector(excitation.P1), Vector(excitation.P2));
    # Probe
    #Blender.Window.SetActiveLayer(1<<layerManager.DefaultLayers.index('probes'));
    Nprobes = 0
    for probe in structured_entries.probe_list:
        # print('probe = ',Vector(probe.position))
        Nprobes += 1
        ProbeFileName = 'p' + str(Nprobes).zfill(2) + structured_entries.flag.id.replace('\"','') + '.prn'
        #FDTDGeometryObjects_obj.GEOprobe(probe.name+' ('+ProbeFileName+')', Vector(probe.position));
        FDTDGeometryObjects_obj.GEOprobe(ProbeFileName, Vector(probe.position));
    
    # Sphere
    #Blender.Window.SetActiveLayer(1<<layerManager.DefaultLayers.index('spheres'));
    for sphere in structured_entries.sphere_list:
        # variables
        centre = Vector(sphere.centre)

        # initialise rotation_matrix
        rotation_matrix = Matrix()
        rotation_matrix.identity();

        # scale object
        #Sx=Blender.Mathutils.ScaleMatrix(abs(2*sphere.outer_radius),4,Blender.Mathutils.Vector(1,0,0))
        #Sy=Blender.Mathutils.ScaleMatrix(abs(2*sphere.outer_radius),4,Blender.Mathutils.Vector(0,1,0))
        #Sz=Blender.Mathutils.ScaleMatrix(abs(2*sphere.outer_radius),4,Blender.Mathutils.Vector(0,0,1))
        #rotation_matrix *= Sx*Sy*Sz;

        # position object
        #T = Blender.Mathutils.TranslationMatrix(centre)
        #rotation_matrix *= T;
        
        # add rotations
        #for r in sphere.rotation_list:
          #rotation_matrix *= rotationMatrix(r.axis_point, r.axis_direction, r.angle_degrees);
          
        # create object
        FDTDGeometryObjects_obj.GEOsphere(sphere.name, sphere.centre, sphere.outer_radius, sphere.inner_radius, sphere.permittivity, sphere.conductivity)
        #FDTDGeometryObjects_obj.GEOsphere_matrix(sphere.name, rotation_matrix, sphere.outer_radius, sphere.inner_radius, sphere.permittivity, sphere.conductivity);
        #FDTDGeometryObjects_obj.GEOblock_matrix(sphere.name, rotation_matrix, sphere.permittivity, sphere.conductivity);
        
    # Block
    #Blender.Window.SetActiveLayer(1<<layerManager.DefaultLayers.index('blocks'));
    for block in structured_entries.block_list:
        # variables
        lower = Vector(block.lower)
        upper = Vector(block.upper)
        pos = 0.5*(lower+upper);
        diag = upper-lower;

        # initialise rotation_matrix
        rotation_matrix = Matrix()
        rotation_matrix.identity()

        # scale object
        Sx = Matrix.Scale(abs(diag[0]), 4, Vector((1,0,0)) )
        Sy = Matrix.Scale(abs(diag[1]), 4, Vector((0,1,0)) )
        Sz = Matrix.Scale(abs(diag[2]), 4, Vector((0,0,1)) )
        rotation_matrix *= Sx*Sy*Sz;
        # position object
        T = Matrix.Translation(pos)
        rotation_matrix *= T;
        
        # add rotations
        for r in block.rotation_list:
          rotation_matrix *= rotationMatrix(r.axis_point, r.axis_direction, r.angle_degrees);

        # create object
        #FDTDGeometryObjects_obj.GEOblock_matrix(block.name, rotation_matrix, block.permittivity, block.conductivity);
        FDTDGeometryObjects_obj.GEOblock(block.name, block.lower, block.upper, block.permittivity, block.conductivity);

    # Distorted
    for distorted in structured_entries.distorted_list:
        # create object
        #print(distorted)
        FDTDGeometryObjects_obj.GEOdistorted(distorted.name, distorted.vertices, distorted.permittivity, distorted.conductivity);
        
    # Cylinder
    #Blender.Window.SetActiveLayer(1<<layerManager.DefaultLayers.index('cylinders'));
    for cylinder in structured_entries.cylinder_list:
      
        # initialise rotation_matrix
        rotation_matrix = Blender.Mathutils.Matrix()
        rotation_matrix.identity();

        # because FDTD cylinders are aligned with the Y axis by default
        rotation_matrix *= rotationMatrix(Blender.Mathutils.Vector(0,0,0), Blender.Mathutils.Vector(1,0,0), -90)
        
        # position object
        T = Blender.Mathutils.TranslationMatrix(Blender.Mathutils.Vector(cylinder.centre[0],cylinder.centre[1],cylinder.centre[2]))
        rotation_matrix *= T;
        
        # add rotations
        for r in cylinder.rotation_list:
          rotation_matrix *= rotationMatrix(r.axis_point, r.axis_direction, r.angle_degrees);
        
        # create object
        FDTDGeometryObjects_obj.GEOcylinder_matrix(cylinder.name, rotation_matrix, cylinder.inner_radius,cylinder.outer_radius,cylinder.height,cylinder.permittivity,cylinder.conductivity);

    #########################
    # Not yet implemented:
    # Flag
    # structured_entries.flag;
    # Boundaries
    # structured_entries.boundaries;
    #########################

    # TODO: Save the layer settings somewhere for reuse
    #scene = Blender.Scene.GetCurrent()
    scene = bpy.context.scene
    
    layersOn = [layerManager.DefaultLayers.index('spheres')+1,layerManager.DefaultLayers.index('blocks')+1,layerManager.DefaultLayers.index('cylinders')+1]
    print(layersOn)
    #layersOn = [1,2,3]
    #print layersOn
    #Blender.Scene.GetCurrent().setLayers(layersOn)
    
    #scene.update(0);
    #Blender.Window.RedrawAll();
    #Blender.Window.WaitCursor(0);
    #Blender.Scene.GetCurrent().setLayers([1,3,4,5,6,7,8,9,10]);
    print('...done')
    #print Blender.Get('scriptsdir')
    #Blender.Run(Blender.Get('scriptsdir')+'/layer_manager.py')
    #layer_manager_objects = layer_manager.LayerManagerObjects()
    #Draw.Register(layer_manager_objects.gui, layer_manager_objects.event, layer_manager_objects.button_event)
    
    #print '=========================='
    #print Blender.Window.GetScreens()
    #print Blender.Window.GetAreaID()
    #print Blender.Window.GetAreaSize()
    #print Blender.Text.Get()
    #print '=========================='
    #~ Blender.Window.FileSelector(algosomething, "Import Bristol FDTD file...");
    #~ Blender.Run('~/.blender/scripts/bfdtd_import.py')

###############################
# MAIN FUNCTION
###############################
def main():
  ''' MAIN FUNCTION '''
  print('sys.argv=' + str(sys.argv))
  print('len(sys.argv)=' + str(len(sys.argv)))
  
  # arg[0]='blender'
  # arg[1]='-P'
  # arg[2]='scriptname'
  # arg[3]='--'
  
  if len(sys.argv)>4:
      for i in range(len(sys.argv)- 4):
          print('Importing ' + sys.argv[4+i])
          importBristolFDTD(sys.argv[4+i]);
  else:
      ###################
      # load import path
      ###################
      # print('tempdir=',Blender.Get('tempdir'))
      # print('soundsdir=',Blender.Get('soundsdir'))
  
      # default_path = Blender.Get('tempdir');
      # if not default_path:
          # default_path = os.getenv('DATADIR');
          
      default_path = os.getenv('DATADIR')
      print('cfgfile = ', cfgfile)
  
      if os.path.isfile(cfgfile) and os.path.getsize(cfgfile) > 0:
          #with open(, 'r') as FILE:
               #= pickle.load(FILE);
        with open(cfgfile, 'rb') as f:
          # The protocol version used is detected automatically, so we do not
          # have to specify it.
          default_path = pickle.load(f)
      ###################
  
      ###################
      # import file
      ###################
      Blender.Window.FileSelector(importBristolFDTD, "Import Bristol FDTD file...", default_path);
      # TestObjects();

if __name__ == "__main__":
  main()
