
import sys, getopt
import math

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

import cv2

import config as cutil
import myImg as iutil
import myContours as cntrutil


class myContourProcessor:
   def __init__(self,id,contours,cntr_df,config=None,ekey=""):
      self.id = id
      self.contours = contours #refer to contours collections object i.e. myContours
      self.cntr_df = cntr_df

      if config is None:
        raise Exception("class[" + self.__class__.__name__ + "] error. Exception as config passed is Null.")
      else:
        self.config = config
      
      self.ekey = ekey
      self.key = self.__class__.__name__
       
      self.logger = self.config.logger
      self.logger.log( "myContourProcessor instance initialization. id[{}] configid[{}]".format(self.id,self.config.id))

   def process(self,y_cord=None):
      cntr_df = self.cntr_df
      text_df = pd.DataFrame() #pandas DF to hold entire master list of extraction
      
      cntr_df = cntr_df.sort_values(by=['y','x'],ascending=True)
      #cntr_df.groupby(['y']).agg({'y':'count','rh':'mean'})
      print("[{}] out of [{}] Contour's to process...".format(len(cntr_df),len(self.cntr_df)))
      
      for i,x in cntr_df.iterrows():
        #self.logger.log("idx[{}] imgpath[{}] y[{}] x[{}] h[{}] w[{}]".format(x.uid,x.imgpath,x.y,x.x,x.rh,x.rw))
        print("idx[{}] imgpath[{}] y[{}] x[{}] h[{}] w[{}]".format(x.uid,x.imgpath,x.y,x.x,x.rh,x.rw))
        contour = self.contours.getContourById(x.uid) #cntr_df.uid maps to index of myContours.dict
        contour.scanAll()
        
        text_df = text_df.append( contour.getTextAsDF())
      
      #comment csv dump for entire dataset.
      text_df.to_csv( self.config.ddir + self.id + '_text_df.csv')
      
   def processSelectedContours(self,y_cord=None):
      swr_h = self.config.getSWRHeight() #get mean height of contoru image
      swr_h_sd = self.config.getSWRSD() #get standard deviation of contour height
      text_df = pd.DataFrame() #pandas DF to hold entire master list of extraction
      
      cntr_df = self.cntr_df[(self.cntr_df.rh >= (swr_h-2*swr_h_sd)) & (self.cntr_df.rh <= (swr_h+2*swr_h_sd))]
      cntr_df = cntr_df.sort_values(by=['y','x'],ascending=True)
      #cntr_df.groupby(['y']).agg({'y':'count','rh':'mean'})
      print("[{}] out of [{}] Contour's to process...".format(len(cntr_df),len(self.cntr_df)))
      print("where height is between [{}] and [{}]".format((swr_h-2*swr_h_sd),(swr_h+2*swr_h_sd)))
      
      for i,x in cntr_df.iterrows():
        #self.logger.log("idx[{}] imgpath[{}] y[{}] x[{}] h[{}] w[{}]".format(x.uid,x.imgpath,x.y,x.x,x.rh,x.rw))
        print("idx[{}] imgpath[{}] y[{}] x[{}] h[{}] w[{}]".format(x.uid,x.imgpath,x.y,x.x,x.rh,x.rw))
        contour = self.contours.getContourById(x.uid) #cntr_df.uid maps to index of myContours.dict
        contour.scanSelected()
        text_df = text_df.append( contour.getTextAsDF())
      
      #comment csv dump for entire dataset.
      text_df.to_csv( self.config.ddir + self.id + '_text_df.csv')
    
def main(argv):
   i_imgpath = ''
   i_cdir = './'
   
   try:
      opts, args = getopt.getopt(argv,"hi:",["i_img=","cdir"])
   except getopt.GetoptError:
      print 'test.py -i <input contour file>'
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print 'myContProcessor.py -i <input contour file>'
         print 'myContProcessor.py -c <home dir> -i <input image file>'
         sys.exit()
      elif opt in ("-i", "--i_img"):
         i_imgpath = arg
      elif opt in ("-c", "--i_cdir"):
         i_cdir = arg
   print 'Input contour file is "', i_imgpath
   print 'Input working directory is "', i_cdir
   
   myId = "c12"
   config = cutil.Config(configid="myConfId",cdir=i_cdir)
    
   cntr = cntrutil.myContours(contourid=myId,config=config,ekey='e123',path=i_imgpath)
   cntr.prepareImage()
   cntr.createContours()
   cntr.printProcessedImage()
   cntr_df = cntr.getContoursAsDF()
   cntr.printContourDFOnImage()
    
   cprocessor = myContourProcessor( id=myId, config=config, ekey='e123', cntr_df=cntr_df,contours=cntr)
   cprocessor.process(y_cord=651)

if __name__ == "__main__":
   main(sys.argv[1:])
