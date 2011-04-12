#!/usr/bin/env python
# -*- coding: utf-8 -*-

#~ import sys
#~ import os
#~ import getopt
#~ from utilities.getuserdir import *
from bristolFDTD_generator_functions import *
from constants import *
from meshing.subGridMultiLayer import *

class pillar_1D:
  '''creates a 1D pillar with different kinds of irregularities'''
  def __init__(self):
    self.BASENAME = 'pillar_1D'
    self.DSTDIR = getuserdir()
    self.ITERATIONS = 32000,
    self.HOLE_TYPE = 'cylinder'
    self.pillar_radius_mum = 0.150/2.0,
    self.EXCITATION_FREQUENCY = get_c0()/637e-3
    self.SNAPSHOTS_FREQUENCY = []
    self.excitation_type = 1
    self.verbose = False
    self.print_mesh = True
    self.print_holes = True
    self.print_holes_top = True
    self.print_holes_bottom = True
    self.print_pillar = True
    self.print_podium = True
    self.print_snaphots = True
    self.print_freqsnap = True
    self.print_timesnap = True
    self.print_epssnap = True
    self.print_excitation = True
    self.print_probes = True
  def write(self):
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # arguments
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    if self.verbose:
      print('Reading input parameters...')
    
    if not os.path.isdir(self.DSTDIR):
      print('error: self.DSTDIR = '+self.DSTDIR+'is not a directory')
      return('error')
       
    if not os.path.isdir(self.DSTDIR+os.sep+self.BASENAME):
      os.mkdir(self.DSTDIR+os.sep+self.BASENAME)
    
    Lambda = get_c0()/self.EXCITATION_FREQUENCY
    
    # refractive indices
    n_Diamond = 2.4; #no unit
    n_Air = 1; #no unit
    n_bottom_square = n_Diamond; #3.5214; #no unit
    # distance between holes
    #d_holes_mum = 0.220; #mum
    d_holes_mum = Lambda/(4*n_Diamond)+Lambda/(4*n_Air);#mum
    # hole radius
    #hole_radius_X = 0.28*d_holes_mum; #mum
    hole_radius_X = (Lambda/(4*n_Air))/2;#mum
    hole_radius_Z = self.pillar_radius_mum - (d_holes_mum-2*hole_radius_X); #mum
    
    print >>sys.stderr, 'hole_radius_X',hole_radius_X
    print >>sys.stderr, 'hole_radius_Z',hole_radius_Z
    print >>sys.stderr, 'd_holes_mum',d_holes_mum
    print >>sys.stderr, 'self.pillar_radius_mum',self.pillar_radius_mum
    
    if hole_radius_Z<=0:
      print >>sys.stderr, 'ERROR: negative hole_radius_Z = ',hole_radius_Z
      return
    
    # number of holes on bottom
    bottom_N = 6; #no unit
    # number of holes on top
    top_N = 3; #no unit
    # distance between 2 holes around cavity
    #d_holes_cavity = 2*d_holes_mum; #mum
    d_holes_cavity = Lambda/n_Diamond + 2*hole_radius_X;#mum
    Lcav = d_holes_cavity - d_holes_mum; # mum
    # d_holes_cavity = Lcav + d_holes_mum
    # top box offset
    top_box_offset=1; #mum
    #bottom square thickness
    h_bottom_square=0.5 # mum
  
    # self.ITERATIONS = 261600; #no unit
    # self.ITERATIONS = 32000; #no unit
    # self.ITERATIONS = 10; #no unit
  
    # self.ITERATIONS=1048400
    FIRST=65400
    REPETITION=524200
    WALLTIME=360
  
    TIMESTEP=0.9; #mus
    TIME_CONSTANT=4.000000E-09; #mus
    AMPLITUDE=1.000000E+01; #V/mum???
    TIME_OFFSET=2.700000E-08; #mus
            
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # additional calculations
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    
    # max mesh intervals
    #delta_diamond = 0.5*Lambda/(15*n_Diamond)
    delta_diamond = Lambda/(10*n_Diamond);
    delta_hole = delta_diamond
    #delta_outside = 2*delta_diamond
    delta_outside = Lambda/(4*n_Air)
    delta_center = delta_diamond
    delta_boundary = delta_diamond
    
    # center area where excitation takes place (for meshing)
    center_radius = 2*delta_center
  
    # buffers (area outside pillar where mesh is fine)
    X_buffer = 4*delta_diamond; #mum
    Y_buffer = 32*delta_diamond; #mum
    Z_buffer = 4*delta_diamond; #mum
  
    # dimension and position parameters
    pillar_height = (bottom_N+top_N)*d_holes_mum + Lcav
    Xmax = h_bottom_square + pillar_height + X_buffer + top_box_offset; #mum
    #Ymax = 5*2*self.pillar_radius_mum;
    #Ymax = 2*(self.pillar_radius_mum + X_buffer + 4*delta_outside); #mum
    Ymax = 2*(self.pillar_radius_mum + 4*delta_diamond + 4*delta_outside); #mum
    Zmax = Ymax; #mum
    
    pillar_centre_Y = Ymax/2
    pillar_centre_X = bottom_N*d_holes_mum + Lcav/2
    pillar_centre_Z = Zmax/2
  
    # meshing parameters
    thicknessVector_X = [ ]
    max_delta_Vector_X = [ ]
    mesh_factor=1
    for i in range(bottom_N):
      thicknessVector_X += [ d_holes_mum/2 - hole_radius_X, 2*hole_radius_X, d_holes_mum/2 - hole_radius_X ]
      max_delta_Vector_X += [ mesh_factor*delta_diamond, mesh_factor*delta_hole, mesh_factor*delta_diamond ]
    thicknessVector_X += [ Lcav/2-center_radius, 2*center_radius, Lcav/2-center_radius ]
    max_delta_Vector_X += [ mesh_factor*delta_diamond, mesh_factor*delta_center, mesh_factor*delta_diamond ]
    for i in range(top_N):
      thicknessVector_X += [ d_holes_mum/2 - hole_radius_X, 2*hole_radius_X, d_holes_mum/2 - hole_radius_X ]
      max_delta_Vector_X += [ mesh_factor*delta_diamond, mesh_factor*delta_hole, mesh_factor*delta_diamond ]
  
    delta_min = min(max_delta_Vector_X)
  
    if self.HOLE_TYPE == 'cylinder':
      thicknessVector_Y_1 = [ Zmax/2-self.pillar_radius_mum-Z_buffer, Z_buffer, self.pillar_radius_mum-center_radius, center_radius ]
    elif self.HOLE_TYPE == 'square_holes':
      thicknessVector_Y_1 = [ Zmax/2-self.pillar_radius_mum-Z_buffer, Z_buffer, self.pillar_radius_mum-center_radius, center_radius ]
    elif self.HOLE_TYPE == 'rectangular_holes':
      thicknessVector_Y_1 = [ Zmax/2-self.pillar_radius_mum-Z_buffer, Z_buffer, self.pillar_radius_mum-center_radius, center_radius ]
    else:
      print >>sys.stderr, "ERROR: Unknown self.HOLE_TYPE "+self.HOLE_TYPE
  
    thicknessVector_Y_2 = thicknessVector_Y_1[:]; thicknessVector_Y_2.reverse()
    thicknessVector_Y = thicknessVector_Y_1 + thicknessVector_Y_2
    
    max_delta_Vector_Y_1 = [ delta_outside, delta_boundary, delta_hole, delta_center ]
    max_delta_Vector_Y_2 = max_delta_Vector_Y_1[:]; max_delta_Vector_Y_2.reverse();
    max_delta_Vector_Y = max_delta_Vector_Y_1 + max_delta_Vector_Y_2
  
    #print 'thicknessVector_Y = ', thicknessVector_Y
    #print 'max_delta_Vector_Y = ', max_delta_Vector_Y
  
    thicknessVector_Z = [ Ymax/2-self.pillar_radius_mum-X_buffer, X_buffer, self.pillar_radius_mum-hole_radius_X, hole_radius_X-center_radius, center_radius ]
    max_delta_Vector_Z = [ delta_outside, delta_boundary, delta_diamond, delta_diamond, delta_center ]
    
    #Mesh_ThicknessVector, Section_FinalDeltaVector = subGridMultiLayer([1,2,3,4,5],[5,4,3,2,1])
    #print('Mesh_ThicknessVector = '+str(Mesh_ThicknessVector))
    #print('Section_FinalDeltaVector = '+str(Section_FinalDeltaVector))
    
    #print('max_delta_Vector_X = '+str(max_delta_Vector_X))
    #print('thicknessVector_X = '+str(thicknessVector_X))
    #subGridMultiLayer(max_delta_Vector_X,thicknessVector_X)
    #print('============')
    
    delta_X_vector, local_delta_X_vector = subGridMultiLayer(max_delta_Vector_X,thicknessVector_X)
    delta_Y_vector, local_delta_Y_vector = subGridMultiLayer(max_delta_Vector_Y,thicknessVector_Y)
    delta_Z_vector, local_delta_Z_vector = subGridMultiLayer(max_delta_Vector_Z,thicknessVector_Z)
  
    # for the frequency snapshots
    
    Xplanes = [ 0,
    bottom_N/2*d_holes_mum,
    pillar_centre_X-delta_center,
    pillar_centre_X,
    pillar_centre_X+delta_center,
    bottom_N*d_holes_mum + Lcav + top_N/2*d_holes_mum,
    pillar_height ]
    
    Yplanes = [ 0,
    Zmax/2-self.pillar_radius_mum-Z_buffer,
    Zmax/2-self.pillar_radius_mum,
    Zmax/2-hole_radius_X,
    Zmax/2-2*delta_center,
    Zmax/2-delta_center,
    Zmax/2,
    Zmax/2+delta_center,
    Zmax/2+2*delta_center,
    Zmax/2+hole_radius_X,
    Zmax/2+self.pillar_radius_mum,
    Zmax/2+self.pillar_radius_mum+Z_buffer,
    Zmax ]
  
    Zplanes = [ 0,
    Ymax/2-self.pillar_radius_mum-X_buffer,
    Ymax/2-self.pillar_radius_mum,
    Ymax/2-2*delta_center,
    Ymax/2-delta_center,
    Ymax/2 ]
    
    # for probes
    probes_X_vector = Xplanes[1:len(Xplanes)-1]
    probes_Y_vector = Yplanes[1:8]
    probes_Z_vector = Zplanes[1:4]
    
    probes_X_vector_center = Xplanes[2:5]
    probes_Y_vector_center = [Yplanes[5],Yplanes[7]]
    
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Files to generate:
    # .lst
    # .in
    # .sh
    # .cmd
    # .geo
    # .inp
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # .lst file
    #~ copyfile(fullfile(getuserdir(),'MATLAB','entity.lst'),self.DSTDIR+os.sep+self.BASENAME)
    # .in file
    in_filename = self.DSTDIR+os.sep+self.BASENAME+os.sep+self.BASENAME+'.in'
    if self.verbose:
      print('Writing IN file '+in_filename+' ...')
    GEOin(in_filename, [ self.BASENAME+'.inp', self.BASENAME+'.geo' ])
    if self.verbose:
      print('...done')
    
    # .sh file
    #TODO: improve this
    # WORKDIR = ['$HOME/loncar_structure','/',self.BASENAME]
    if self.verbose:
      print('Writing shellscript '+filename+' ...')
    GEOshellscript(self.DSTDIR+os.sep+self.BASENAME+os.sep+self.BASENAME+'.sh', self.BASENAME, '$HOME/bin/fdtd', '$JOBDIR', WALLTIME)
    if self.verbose:
      print('...done')
  
    # .cmd file
    cmd_filename = self.DSTDIR+os.sep+self.BASENAME+os.sep+self.BASENAME+'.cmd'
    if self.verbose:
      print('Writing CMD file '+cmd_filename+' ...')
    GEOcommand(cmd_filename, self.BASENAME)
    if self.verbose:
      print('...done')
  
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # .geo file
    geo_filename = self.DSTDIR+os.sep+self.BASENAME+os.sep+self.BASENAME+'.geo'
    if self.verbose:
      print('Writing GEO file '+geo_filename+' ...')
  
    # open file
    
    with open(geo_filename, 'w') as out:
  
      # write header
      out.write('**GEOMETRY FILE\n')
      out.write('\n')
    
      # initialize current y
      X_current=0
      
      if self.print_podium:
        # create bottom block
        L = [ 0, 0, 0 ]
        U = [ X_current + h_bottom_square, Ymax, Zmax ]
        GEOblock(out, L, U, pow(n_bottom_square,2), 0)
  
      X_current = X_current + h_bottom_square;
      
      if self.print_pillar:
        # create main pillar
        L = [ X_current, Ymax/2 - self.pillar_radius_mum, Zmax/2 - self.pillar_radius_mum ]
        U = [ X_current + pillar_height, Ymax/2 + self.pillar_radius_mum, Zmax/2 + self.pillar_radius_mum ]
        GEOblock(out, L, U, pow(n_Diamond,2), 0)
    
      X_current = X_current + d_holes_mum/2
    
      if self.print_holes:
          # hole settings
          permittivity = pow(n_Air,2)
          conductivity = 0
          
          # create bottom holes
          for i in range(bottom_N):
            if self.print_holes_bottom:
              centre = [ X_current, Ymax/2, Zmax/2 ]
              if self.HOLE_TYPE == 'cylinder':
                GEOcylinder(out, centre, 0, hole_radius_X, 2*self.pillar_radius_mum, permittivity, conductivity, 0)
              elif self.HOLE_TYPE == 'square_holes':
                lower = [ X_current - hole_radius_X, Ymax/2 - self.pillar_radius_mum, Zmax/2 - hole_radius_X]
                upper = [ X_current + hole_radius_X, Ymax/2 + self.pillar_radius_mum, Zmax/2 + hole_radius_X]
                GEOblock(out, lower, upper, permittivity, conductivity)
              elif self.HOLE_TYPE == 'rectangular_holes':
                lower = [ X_current - hole_radius_X, Ymax/2 - self.pillar_radius_mum, Zmax/2 - hole_radius_Z]
                upper = [ X_current + hole_radius_X, Ymax/2 + self.pillar_radius_mum, Zmax/2 + hole_radius_Z]
                GEOblock(out, lower, upper, permittivity, conductivity)
              else:
                print >>sys.stderr, "ERROR: Unknown self.HOLE_TYPE "+self.HOLE_TYPE
            X_current = X_current + d_holes_mum
    
          X_current = X_current - d_holes_mum + d_holes_cavity
    
          # create top holes
          for i in range(top_N):
            if self.print_holes_top:
              centre = [ X_current, Ymax/2, Zmax/2 ]
              if self.HOLE_TYPE == 'cylinder':
                GEOcylinder(out, centre, 0, hole_radius_X, 2*self.pillar_radius_mum, permittivity, conductivity, 0)
              elif self.HOLE_TYPE == 'square_holes':
                lower = [ X_current - hole_radius_X, Ymax/2 - self.pillar_radius_mum, Zmax/2 - hole_radius_X]
                upper = [ X_current + hole_radius_X, Ymax/2 + self.pillar_radius_mum, Zmax/2 + hole_radius_X]
                GEOblock(out, lower, upper, permittivity, conductivity)
              elif self.HOLE_TYPE == 'rectangular_holes':
                lower = [ X_current - hole_radius_X, Ymax/2 - self.pillar_radius_mum, Zmax/2 - hole_radius_Z]
                upper = [ X_current + hole_radius_X, Ymax/2 + self.pillar_radius_mum, Zmax/2 + hole_radius_Z]
                GEOblock(out, lower, upper, permittivity, conductivity)
              else:
                print >>sys.stderr, "ERROR: Unknown self.HOLE_TYPE "+self.HOLE_TYPE
            X_current = X_current + d_holes_mum
          
      #write box
      L = [ 0, 0, 0 ]
      U = [ Xmax, Zmax, Ymax/2 ]
      GEObox(out, L, U)
    
      #write footer
      out.write('end\n'); #end the file
    
      #close file
      out.close()
      if self.verbose:
        print('...done')
    
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # .inp file
    inp_filename = self.DSTDIR+os.sep+self.BASENAME+os.sep+self.BASENAME+'.inp'
    if self.verbose:
      print('Writing INP file '+inp_filename+' ...')
  
    # open file
    with open(inp_filename, 'w') as out:
  
      if self.print_excitation:
        P_Xm = [ pillar_centre_X-2*delta_center, pillar_centre_Y, pillar_centre_Z ]
        P_Xp = [ pillar_centre_X+2*delta_center, pillar_centre_Y, pillar_centre_Z ]
        P_Ym1 = [ pillar_centre_X, pillar_centre_Y-1*delta_center, pillar_centre_Z ]
        P_Yp1 = [ pillar_centre_X, pillar_centre_Y+1*delta_center, pillar_centre_Z ]
        P_Ym2 = [ pillar_centre_X, pillar_centre_Y-2*delta_center, pillar_centre_Z ]
        P_Yp2 = [ pillar_centre_X, pillar_centre_Y+2*delta_center, pillar_centre_Z ]
        P_Zm1 = [ pillar_centre_X, pillar_centre_Y, pillar_centre_Z-1*delta_center ]
        P_Zp1 = [ pillar_centre_X, pillar_centre_Y, pillar_centre_Z+1*delta_center ]
        P_Zm2 = [ pillar_centre_X, pillar_centre_Y, pillar_centre_Z-2*delta_center ]
        P_Zp2 = [ pillar_centre_X, pillar_centre_Y, pillar_centre_Z+2*delta_center ]
        P_center = [ pillar_centre_X, pillar_centre_Y, pillar_centre_Z ]
        Ey = [ 0, 1, 0 ]
        Ez = [ 0, 0, 1 ]
        H = [ 0, 0, 0 ]
        type = 10
    
        if self.excitation_type == 1:
          GEOexcitation(out, 7, P_Ym1, P_center, Ey, H, type, TIME_CONSTANT, AMPLITUDE, TIME_OFFSET, self.EXCITATION_FREQUENCY, 0, 0, 0, 0)
        elif  self.excitation_type == 2:
          GEOexcitation(out, 7, P_Zm1, P_center, Ez, H, type, TIME_CONSTANT, AMPLITUDE, TIME_OFFSET, self.EXCITATION_FREQUENCY, 0, 0, 0, 0)
        elif  self.excitation_type == 3:
          GEOexcitation(out, 7, P_Ym2, P_center, Ey, H, type, TIME_CONSTANT, AMPLITUDE, TIME_OFFSET, self.EXCITATION_FREQUENCY, 0, 0, 0, 0)
        elif  self.excitation_type == 4:
          GEOexcitation(out, 7, P_Zm2, P_center, Ez, H, type, TIME_CONSTANT, AMPLITUDE, TIME_OFFSET, self.EXCITATION_FREQUENCY, 0, 0, 0, 0)
        else:
          error('invalid direction')
    
      Xpos_bc = 2; Xpos_param = [1,1,0]
      Ypos_bc = 2; Ypos_param = [1,1,0]
      Zpos_bc = 1; Zpos_param = [1,1,0]
      Xneg_bc = 2; Xneg_param = [1,1,0]
      Yneg_bc = 2; Yneg_param = [1,1,0]
      Zneg_bc = 2; Zneg_param = [1,1,0]
      GEOboundary(out, Xpos_bc, Xpos_param, Ypos_bc, Ypos_param, Zpos_bc, Zpos_param, Xneg_bc, Xneg_param, Yneg_bc, Yneg_param, Zneg_bc, Zneg_param)
      
      iteration_method = 5
      propagation_constant = 0
      flag_1 = 0
      flag_2 = 0
      id_character = 'id'
      GEOflag(out, iteration_method, propagation_constant, flag_1, flag_2, self.ITERATIONS, TIMESTEP, id_character)
    
      if self.print_mesh:
        GEOmesh(out, delta_X_vector, delta_Y_vector, delta_Z_vector)
          
      # frequency snapshots
      first = FIRST
      repetition = REPETITION
      interpolate = 1
      real_dft = 0
      mod_only = 0
      mod_all = 1
      starting_sample = 0
      E=[1,1,1]
      H=[1,1,1]
      J=[0,0,0]
      power = 0
      
      if self.print_snaphots == 1:
        #for iY in range(len(Yplanes)):
          #plane = 2
          #P1 = [0, Yplanes[iY], 0]
          #P2 = [Xmax, Yplanes[iY], Ymax/2]
          #GEOfrequency_snapshot(out, first, repetition, interpolate, real_dft, mod_only, mod_all, plane, P1, P2, self.SNAPSHOTS_FREQUENCY, starting_sample, E, H, J)
          #GEOtime_snapshot(out, first, repetition, plane, P1, P2, E, H, J, power,0)
        #for iX in range(len(Xplanes)):
          #plane = 1
          #P1 = [Xplanes[iX], 0, 0]
          #P2 = [Xplanes[iX], Zmax, Ymax/2]
          #GEOfrequency_snapshot(out, first, repetition, interpolate, real_dft, mod_only, mod_all, plane, P1, P2, self.SNAPSHOTS_FREQUENCY, starting_sample, E, H, J)
          #GEOtime_snapshot(out, first, repetition, plane, P1, P2, E, H, J, power,0)
        #for iZ in range(len(Zplanes)):
          #plane = 3
          #P1 = [0, 0, Zplanes[iZ]]
          #P2 = [Xmax, Zmax, Zplanes[iZ]]
          #GEOfrequency_snapshot(out, first, repetition, interpolate, real_dft, mod_only, mod_all, plane, P1, P2, self.SNAPSHOTS_FREQUENCY, starting_sample, E, H, J)
          #GEOtime_snapshot(out, first, repetition, plane, P1, P2, E, H, J, power,0)
    
        plane = 1
        P1 = [pillar_centre_X, 0, 0]
        P2 = [pillar_centre_X, Zmax, Ymax/2]
        GEOfrequency_snapshot(out, first, repetition, interpolate, real_dft, mod_only, mod_all, plane, P1, P2, self.SNAPSHOTS_FREQUENCY, starting_sample, E, H, J)
        GEOtime_snapshot(out, first, repetition, plane, P1, P2, E, H, J, power,0)
    
        plane = 2
        P1 = [0, Zmax/2, 0]
        P2 = [Xmax, Zmax/2, Ymax/2]
        GEOfrequency_snapshot(out, first, repetition, interpolate, real_dft, mod_only, mod_all, plane, P1, P2, self.SNAPSHOTS_FREQUENCY, starting_sample, E, H, J)
        GEOtime_snapshot(out, first, repetition, plane, P1, P2, E, H, J, power,0)
    
        plane = 3
        P1 = [0, 0, Ymax/2-2*delta_center]
        P2 = [Xmax, Zmax, Ymax/2-2*delta_center]
        GEOfrequency_snapshot(out, first, repetition, interpolate, real_dft, mod_only, mod_all, plane, P1, P2, self.SNAPSHOTS_FREQUENCY, starting_sample, E, H, J)
        GEOtime_snapshot(out, first, repetition, plane, P1, P2, E, H, J, power,0)
    
      if self.print_probes:
        # probes
        step=10
        E=[1,1,1]
        H=[1,1,1]
        J=[0,0,0]
        power = 0
        for iX in range(len(probes_X_vector)):
          # XZ probes
          for iZ in range(len(probes_Z_vector)):
            GEOprobe(out, [probes_X_vector[iX], Yplanes[5], probes_Z_vector[iZ]], step, E, H, J, power )
          # XY probes
          for iY in range(len(probes_Y_vector)):
            GEOprobe(out, [probes_X_vector[iX], probes_Y_vector[iY], Zplanes[4]], step, E, H, J, power )
        
        # XY center probes
        for iX in range(len(probes_X_vector_center)):
          for iY in range(len(probes_Y_vector_center)):
            GEOprobe(out, [probes_X_vector_center[iX], probes_Y_vector_center[iY], Zplanes[3]], step, E, H, J, power )
      
      #write footer
      out.write('end\n'); #end the file
    
      #close file
      out.close()
      if self.verbose:
        print('...done')
    
    return(in_filename)
  
def main(argv=None):
  if argv is None:
      argv = sys.argv
  try:
    try:
      opts, args = getopt.getopt(argv[1:], "h", ["help"])
    except getopt.error, msg:
      raise Usage(msg)
    # more code, unchanged
    #print('hello')
    #in_filename = pillar_1D('test', os.getenv('TESTDIR'), 32000, 1, 1, 'cylinder', 0.150/2.0, get_c0()/0.637, [get_c0()/0.637, get_c0()/0.637-1, get_c0()/0.637+1],1)
    #in_filename = pillar_1D('test', os.getenv('TESTDIR'), 32000, 1, 1, 'square_holes', 0.150/2.0, get_c0()/0.637, [get_c0()/0.637, get_c0()/0.637-1, get_c0()/0.637+1],1)
    #in_filename = pillar_1D('test', os.getenv('TESTDIR'), 32000, 1, 1, 'rectangular_holes', 0.150/2.0, get_c0()/0.637, [get_c0()/0.637, get_c0()/0.637-1, get_c0()/0.637+1],1)
    #in_filename = pillar_1D('test', os.getenv('TESTDIR'), 32000, True, True, 'rectangular_holes', 1, get_c0()/0.637, [get_c0()/0.637, get_c0()/0.637-1, get_c0()/0.637+1],1)
    
    P = pillar_1D()
    P.BASENAME = 'test'
    P.DSTDIR = os.getenv('TESTDIR')
    P.ITERATIONS = 32000
    P.print_holes_top = True
    P.print_holes_bottom = True
    P.HOLE_TYPE = 'rectangular_holes'
    P.pillar_radius_mum = 1
    P.EXCITATION_FREQUENCY = get_c0()/0.637
    P.SNAPSHOTS_FREQUENCY = [get_c0()/0.637, get_c0()/0.637-1, get_c0()/0.637+1]
    P.excitation_type = 1
    in_filename = P.write()
    
    print(in_filename)
    
  except Usage, err:
    print >>sys.stderr, err.msg
    print >>sys.stderr, "for help use --help"
    return 2

if __name__ == "__main__":
  sys.exit(main())
