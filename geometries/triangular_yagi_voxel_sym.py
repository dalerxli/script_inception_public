from geometries.pillar_1D import *

def triangular_yagi_voxel_sym(DSTDIR, bottomN, topN, excitationType):
  P = pillar_1D()
  print('======== triangular_yagi_voxel_sym START ============')
  P.DSTDIR = DSTDIR
  P.ITERATIONS = 32000
  P.print_holes_top = True
  P.print_holes_bottom = True
  P.setLambda(0.637)
  P.SNAPSHOTS_FREQUENCY = [get_c0()/0.637, get_c0()/0.637-1, get_c0()/0.637+1]

  P.Nvoxels = 10;
  
  P.HOLE_TYPE = 'triangular_yagi_voxel_sym'
  
  n_Eff = 2.2
  n_Diamond = 2.4
  n_Air = 1
  
  # refractive indices
  P.n_Substrate = n_Diamond
  P.n_Defect = n_Diamond
  P.n_Outside = n_Air
  P.n_bottomSquare = n_Diamond
  
  P.setRadiusPillarYZ(0.5,0.5)
  P.print_podium = True
  P.print_pillar = True
  
  P.d_holes_mum = P.getLambda()/(2*n_Eff);#mum
  radius_Z_piercer = 0.100
  P.setRadiusHole((P.getLambda()/(4*P.n_Defect))/2,P.radius_Y_pillar_mum,P.radius_Z_pillar_mum-radius_Z_piercer)
  
  P.bottom_N = bottomN; #no unit
  P.top_N = topN; #no unit
  
  P.setDistanceBetweenDefectBordersInCavity(P.getLambda()/n_Eff)
  delta_diamond = P.getLambda()/(10*P.n_Substrate);
  P.delta_X_bottomSquare = delta_diamond
  P.setDeltaHole(delta_diamond,delta_diamond,delta_diamond)
  P.setDeltaSubstrate(delta_diamond,delta_diamond,delta_diamond)
  P.setDeltaOutside(P.getLambda()/(4*P.n_Defect),P.getLambda()/(4*P.n_Defect),P.getLambda()/(4*P.n_Defect))
  P.setDeltaCenter(delta_diamond,delta_diamond,delta_diamond)
  P.setDeltaBuffer(delta_diamond,delta_diamond,delta_diamond)
  P.setThicknessBuffer(32*delta_diamond,4*delta_diamond,12*delta_diamond)
  P.setRadiusCenter(2*P.delta_X_center,2*P.delta_Y_center,2*P.delta_Z_center)
  
  P.thickness_X_bottomSquare = 0.5 # mum #bottom square thickness
  P.thickness_X_topBoxOffset = 1
  
  P.Xmax = P.thickness_X_bottomSquare + P.getPillarHeight() + P.thickness_X_buffer + P.thickness_X_topBoxOffset; #mum
  P.Ymax = 2*(P.radius_Y_pillar_mum + 4*delta_diamond + 4*P.delta_Y_outside); #mum
  P.Zmax = 2*(P.radius_Z_pillar_mum + 4*delta_diamond + 4*P.delta_Z_outside); #mum

  P.setExcitationType(excitationType)
  P.BASENAME = P.HOLE_TYPE+'.bottomN_'+str(bottomN)+'.topN_'+str(topN)+'.excitationType_'+P.getExcitationType()

  P.write()
