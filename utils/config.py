
import sys

import logger as util

class Config:
  #init configuration
  def __init__(self,configid,cdir=None):
    self.id = configid
    if cdir == None:
      self.cdir = "./"
    else:
      self.cdir = cdir
    self.logFileName = '/tmp/' + self.id + '.log'
    self.logger = util.myLogger(logFileName=self.logFileName)
    self.logger.log('Config[{}] initialize. logFileName[{}]'.format(self.id,self.logFileName))
    
    #initialize various diretories.
    self.idir = self.cdir + 'img/'
    self.odir = self.cdir + 'img/'
    self.ddir = self.cdir + 'data/'
    
    #decouple python specific hardcoding
    self.typeNone = 'NoneType'
     
    #font scanning window related config
    self.swr_aspect_ratio = 1.5
    self.swr_h = 0  #will be predicted at runtime during processing.
    self.swr_h_sd = 0 #will be derived from predicted as sd for swr_h
    self.swr_move_interval = 4
    self.swr_move_interval_ratio = 8
   
  def setSWRHeightAndSD(self,yhat,yhat_sd):
    self.swr_h = yhat
    self.swr_h_sd = yhat_sd
   
  def getSWRHeight(self):
    return self.swr_h
   
  def getSWRSD(self):
    return self.swr_h_sd
   
if __name__ == "__main__":
  config = Config(configid="myImgProc")
