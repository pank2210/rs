
import sys, getopt

import numpy as np
import cv2
import math

from matplotlib import pyplot as plt

import config as cutil

class myBuildLabelSet(object):
   cname = 'myBuildLabelSet'

   def __init__(self,idir,id="x123",config=None,ekey=""):
      mname = '__init__' 
      
      self.id = id

      if config is None:
        raise Exception("class[" + self.__class__.__name__ + "] error. Exception as config passed is Null.")
      else:
        self.config = config
        self.logger = self.config.logger
      
      self.ekey = ekey
      self.key = self.__class__.__name__
      
      self.idir = idir
      self.log(mname)
     
   def log(self,msg,methodName=""):
      sep = '|'
      self.logger.log( self.ekey + sep + self.key + '::' + methodName + sep + msg + sep)
   
   def readDir(self):
      rdir = self.config.cdir + self.idir
      print("Reading [{}]".format(rdir))
      
      with open( rdir, "r") as d_hd:
        for fl in d_hd:
           print("fl[{}]".format(fl))
      

def main(argv):
   i_dir = ''
   i_cdir = './'
   
   try:
      opts, args = getopt.getopt(argv,"hi:",["i_img=","cdir"])
   except getopt.GetoptError:
      print 'test.py -i <input image directory>'
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print 'myBuildLabelSet.py -c <home dir> -id <input image dir>'
         sys.exit()
      elif opt in ("-i", "--i_dir"):
         i_dir = arg
      elif opt in ("-c", "--i_cdir"):
         i_cdir = arg
   print 'Input image dir is "', i_dir
   print 'Input working directory is "', i_cdir

   config = cutil.Config(configid="myConfId",cdir=i_cdir)
   set1 = myBuildLabelSet(id="myBuildLabelSetId",config=config,ekey='x123',idir=i_dir)
   set1.readDir()

if __name__ == "__main__":
   main(sys.argv[1:])
