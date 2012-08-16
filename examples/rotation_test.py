#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from math import *
import time
import sys
import os
import numpy
from GWL.GWL_parser import *
  
def main():
  box = GWLobject()

  box.clear()
  box.addXblock(P1=[0,0,0], P2=[1,2,3], LineDistance_Horizontal=3.7, LineDistance_Vertical=3.8)
  box.write_GWL('X.gwl')

  box.clear()
  box.addYblock(P1=[5,0,0], P2=[5+1,2,3], LineDistance_Horizontal=3.6, LineDistance_Vertical=3.5)
  box.write_GWL('Y.gwl')

  box.clear()
  box.addZblock(P1=[10,0,0], P2=[10+1,2,3], LineDistance_X=3.3, LineDistance_Y=3.4)
  box.write_GWL('Z.gwl')

  box.clear()
  box.addBlockLowerUpper([0,5,0],[10,5+2,3])
  box.write_GWL('10-2-3.gwl')

  box.clear()
  box.addBlockLowerUpper([0,5,0],[1,5+20,3])
  box.write_GWL('1-20-3.gwl')

  box.clear()
  box.addBlockLowerUpper([0,5,0],[1,5+2,30])
  box.write_GWL('1-2-30.gwl')

  box.clear()
  box.addBlockCentroSize([0,-10,0],[1,2,3])
  box.write_GWL('1-2-3.gwl')

  box.clear()
  box.addBlockCentroSize([10,-10,0],[4,5,6])
  box.write_GWL('4-5-6.gwl')

  box.clear()
  box.addBlockCentroSize([20,-10,0],[7,8,9])
  box.write_GWL('7-8-9.gwl')

  box.clear()
  box.addBlockCentroSize([0,0,0],[3,2,1])
  box.rotate(axis_point=[0,0,0], axis_direction=[0,0,1], angle_degrees=45)
  box.write_GWL('rotation_test.gwl')

if __name__ == "__main__":
  main()
