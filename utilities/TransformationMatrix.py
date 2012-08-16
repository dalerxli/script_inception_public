import numpy
import numpy.matlib
import sys
import math

def Identity(size):
  '''
  Create an identity matrix.
  Parameters:
    size (int) – The size of the identity matrix to construct [2, 4].
  Returns:
    A new identity matrix.
  Return type:
    Matrix
  '''
  return numpy.matlib.identity(size)
    
def rotationMatrix(axis_point, axis_direction, angle_degrees):
  ''' return a rotation matrix for a rotation around an arbitrary axis '''
  axis_direction = numpy.array(axis_direction)
  axis_point = numpy.array(axis_point)
  T = Translation(axis_point)
  Tinv = Translation(-axis_point)
  R = Rotation(math.radians(angle_degrees), 4, axis_direction)
  return T*R*Tinv
    
def Rotation(angle_rad, size, axis = None):
  '''
  Create a matrix representing a rotation.
  Parameters:
    angle_rad (float) – The angle of rotation desired, in radians.
    size (int) – The size of the rotation matrix to construct [2, 4].
    axis (string or Vector) – a string in [‘X’, ‘Y’, ‘Z’] or a 3D Vector Object (optional when size is 2).
  Returns:
    A new rotation matrix.
  Return type:
    Matrix
  '''
  
  S = ['X','Y','Z']
  V = [[1,0,0],[0,1,0],[0,0,1]]

  axis_letter = None
  
  if isinstance(axis,str):
    axis_letter = axis.upper()
    if axis_letter in S:
      axis = V[S.index(axis_letter)]
  else:
    # list(axis) converts axis to list if it is a numpy.array
    if list(axis) in V:
      axis_letter = S[V.index(list(axis))]

  if axis is not None and len(axis) != 3:
    print("ERROR: Matrix.Rotation(angle_rad, size, axis), invalid 'axis' arg", file = sys.stderr)
    sys.exit(-1)

  if size<2 or size>4:
    print('ERROR: Invalid size = '+str(size), file = sys.stderr)
    sys.exit(-1)
  if (size == 2 and axis is not None):
    print("ERROR: Matrix.Rotation(): cannot create a 2x2 rotation matrix around arbitrary axis", file = sys.stderr)
    sys.exit(-1)
  if ((size == 3 or size == 4) and (axis is None) ):
    print("ERROR: Matrix.Rotation(): axis of rotation for 3d and 4d matrices is required", file = sys.stderr)
    sys.exit(-1)

  mat = numpy.matlib.identity(size)

  angle_cos = math.cos(angle_rad)
  angle_sin = math.sin(angle_rad)

  if (size == 2):
    # 2D rotation matrix
    mat[0,0] =  angle_cos
    mat[0,1] = -angle_sin
    mat[1,0] =  angle_sin
    mat[1,1] =  angle_cos
    
  elif axis_letter:
    # X, Y or Z axis
    if axis_letter == 'X': # rotation around X
      mat[0,0] = 1
      mat[0,1] = 0
      mat[0,2] = 0
      mat[1,0] = 0
      mat[1,1] = angle_cos
      mat[1,2] = -angle_sin
      mat[2,0] = 0
      mat[2,1] = angle_sin
      mat[2,2] = angle_cos
    elif axis_letter == 'Y': # rotation around Y
      mat[0,0] = angle_cos
      mat[0,1] = 0
      mat[0,2] = angle_sin
      mat[1,0] = 0
      mat[1,1] = 1
      mat[1,2] = 0
      mat[2,0] = -angle_sin
      mat[2,1] = 0
      mat[2,2] = angle_cos
    elif axis_letter == 'Z': # rotation around Z
      mat[0,0] = angle_cos
      mat[0,1] = -angle_sin
      mat[0,2] = 0
      mat[1,0] = angle_sin
      mat[1,1] = angle_cos
      mat[1,2] = 0
      mat[2,0] = 0
      mat[2,1] = 0
      mat[2,2] = 1
      
  else:
    # other axis

    axis_norm = numpy.linalg.norm(axis)

    if axis_norm == 0:
      return numpy.matlib.identity(size)
    
    # normalize the axis first (to remove unwanted scaling)
    nor = axis/axis_norm

    ico = (1 - angle_cos)
    
    nsi = nor*angle_sin

    mat[0,0] = ((nor[0] * nor[0]) * ico) + angle_cos
    mat[0,1] = ((nor[0] * nor[1]) * ico) - nsi[2]
    mat[0,2] = ((nor[0] * nor[2]) * ico) + nsi[1]
    mat[1,0] = ((nor[0] * nor[1]) * ico) + nsi[2]
    mat[1,1] = ((nor[1] * nor[1]) * ico) + angle_cos
    mat[1,2] = ((nor[1] * nor[2]) * ico) - nsi[0]
    mat[2,0] = ((nor[0] * nor[2]) * ico) - nsi[1]
    mat[2,1] = ((nor[1] * nor[2]) * ico) + nsi[0]
    mat[2,2] = ((nor[2] * nor[2]) * ico) + angle_cos
  
  return mat

def Scale(factor, size, axis=None):
  '''
  Create a matrix representing a scaling.
  Parameters:
    factor (float) – The factor of scaling to apply.
    size (int) – The size of the scale matrix to construct [2, 4].
    axis (Vector) – Direction to influence scale. (optional).
  Returns:
    A new scale matrix.
  Return type:
    Matrix
  '''
  if size<2 or size>4:
    print('ERROR: Invalid size = '+str(size),file=sys.stderr)
    sys.exit(-1)
  
  mat = numpy.matlib.identity(size)
  if axis is None:
    mat *= factor
    if size>3:
      mat[3,3] = 1
    return mat
  else:
    tvec = Unit(axis)
    if size == 2:
      mat[0,0] = 1 + ((factor - 1) * (tvec[0] * tvec[0]))
      mat[0,1] =     ((factor - 1) * (tvec[0] * tvec[1]))
      mat[1,0] =     ((factor - 1) * (tvec[0] * tvec[1]))
      mat[1,1] = 1 + ((factor - 1) * (tvec[1] * tvec[1]))
    else:
      mat[0,0] = 1 + ((factor - 1) * (tvec[0] * tvec[0]))
      mat[0,1] =     ((factor - 1) * (tvec[0] * tvec[1]))
      mat[0,2] =     ((factor - 1) * (tvec[0] * tvec[2]))
      mat[1,0] =     ((factor - 1) * (tvec[0] * tvec[1]))
      mat[1,1] = 1 + ((factor - 1) * (tvec[1] * tvec[1]))
      mat[1,2] =     ((factor - 1) * (tvec[1] * tvec[2]))
      mat[2,0] =     ((factor - 1) * (tvec[0] * tvec[2]))
      mat[2,1] =     ((factor - 1) * (tvec[1] * tvec[2]))
      mat[2,2] = 1 + ((factor - 1) * (tvec[2] * tvec[2]))
    return mat

def Translation(vector):
  '''
  Create a matrix representing a translation.
  Parameters: vector (Vector) – The translation vector.
  Returns:
    An identity matrix with a translation.
  Return type:
    Matrix
  '''
  mat = numpy.matlib.identity(4)
  mat[0,3] = vector[0]
  mat[1,3] = vector[1]
  mat[2,3] = vector[2]
  return mat

def Unit(vec):
  ''' return unit vector parallel to vec. '''
  vec = numpy.array(vec)
  tot = numpy.linalg.norm(vec)
  if tot > 0.0:
    return vec/tot
  else:
    return vec

  # potentially faster version (also does not require numpy)
  #tot = Mag2(vec)
  #if tot > 0.0:
    #return vec*(1.0/math.sqrt(tot))
  #else:
    #return vec

def Mag2(vec):
  ''' return the magnitude squared (faster than Mag for comparisons) '''
  return vec[0]*vec[0] + vec[1]*vec[1] + vec[2]*vec[2]

def Mag(vec):
  ''' return the magnitude (rho in spherical coordinate system) '''
  return math.sqrt(Mag2(vec))
