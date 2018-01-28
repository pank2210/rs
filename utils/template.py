
import sys, getopt

import numpy as np
import cv2
import math

from matplotlib import pyplot as plt
from skimage import util

import config as cutil

class myBuildLabelSet(object):
   cname = 'myBuildLabelSet'

   def __init__(self,path,id="x123",config=None,ekey="",img=None):
      mname = '__init__' 
      
      self.id = imageid

      if config is None:
        raise Exception("class[" + self.__class__.__name__ + "] error. Exception as config passed is Null.")
      else:
        self.config = config
        self.logger = self.config.logger
      
      self.ekey = ekey
      self.key = self.__class__.__name__
     
   def log(self,msg,methodName=""):
      sep = '|'
      self.logger.log( self.ekey + sep + self.key + '::' + methodName + sep + msg + sep)

def main(argv):
   i_imgpath = ''
   i_cdir = './'
   
   try:
      opts, args = getopt.getopt(argv,"hi:",["i_img=","cdir"])
   except getopt.GetoptError:
      print 'test.py -i <input image file>'
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print 'myBuildLabelSet.py -i <input image file>'
         print 'myBuildLabelSet.py -c <home dir> -i <input image file>'
         sys.exit()
      elif opt in ("-i", "--i_img"):
         i_imgpath = arg
      elif opt in ("-c", "--i_cdir"):
         i_cdir = arg
   print 'Input image file is "', i_imgpath
   print 'Input working directory is "', i_cdir

   config = cutil.Config(configid="myConfId",cdir=i_cdir)
   set1 = myBuildLabelSet(imageid="myBuildLabelSetId",config=config,ekey='x123',path=i_imgpath)

if __name__ == "__main__":
   main(sys.argv[1:])
