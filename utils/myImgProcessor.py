
import sys, getopt
import os

import numpy as np
import cv2
import math
import re

import config as cutil
import myImg as iutil

class myImgProcessor(object):
   cname = 'myImgProcessor'

   def __init__(self,id="x123",config=None,ekey=""):
      mname = '__init__' 
      
      self.id = id
      
      if config is None:
        raise Exception("class[" + self.__class__.__name__ + "] error. Exception as config passed is Null.")
      else:
        self.config = config
        self.logger = self.config.logger
      
      self.ekey = ekey
      self.key = self.__class__.__name__
    
   def addTextToImages( self, file_pattern):
      ddir = self.config.idir
      
      filelist = os.listdir(ddir)
      
      for i,f_name in enumerate(filelist):
        m1 = re.match( file_pattern, f_name)
        #m1 = re.match( ".*?\.TIF", f_name)
        
        if m1:
          print("Processing [{}]".format(f_name))
          img1 = iutil.myImg(imageid="xx",config=self.config,ekey='x123',path=f_name)
          img1.printImageProp()
          img1.add_text( "FileName: " + f_name, x=100, y=30, image_scale=5)
          img1 = None
        
        

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
         print 'myImgProcessor.py -i <input image file name pattern>'
         print 'myImgProcessor.py -c <home dir> -i <input image file>'
         sys.exit()
      elif opt in ("-i", "--i_img"):
         i_imgpath = arg
      elif opt in ("-c", "--i_cdir"):
         i_cdir = arg
   print 'Input image file pattern is "', i_imgpath
   print 'Input working directory is "', i_cdir

   config = cutil.Config(configid="myConfId",cdir=i_cdir)
   img_proc = myImgProcessor(id="xx",config=config,ekey='x123')
   #img_proc.addTextToImages(".*?\.TIF")
   img_proc.addTextToImages(i_imgpath)

if __name__ == "__main__":
   main(sys.argv[1:])
