#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bin.bfdtd_tool import *

def main(argv=None):
  '''
  Copy src to dst
  '''
  src = sys.argv[1]
  dst = sys.argv[2]
  copyBFDTD(src, dst)

if __name__ == "__main__":
  sys.exit(main())
