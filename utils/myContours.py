
import sys, getopt
import math

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

import cv2

import config as cutil
import myImg as iutil

class myUnitText:
   def __init__(self,id,cntrid,uid,x,y,img,text="",config=None,ekey=""):
      self.id = id  #own id
      self.cntrid = cntrid #Contour uid
      self.uid = uid #unique id for this instance

      if config is None:
        raise Exception("class[" + self.__class__.__name__ + "] error. Exception as config passed is Null.")
      else:
        self.config = config
      
      self.ekey = ekey
      self.key = self.__class__.__name__
       
      self.logger = self.config.logger
      self.logger.log( "myUnitText instance initialization. id[{}] configid[{}]".format(self.id,self.config.id))
      
      self.x = x
      self.y = y
      self.text = text
      self.img = iutil.myImg(imageid=self.id,config=self.config,ekey=self.ekey,path=None,img=img)
      self.imgpath = self.img.getImagePath()
      self.iw, self.ih = self.img.getImageDim()
   
   def getUnitTextAsDF(self):
      colnames = ['id','cntrid','uid','x','y','iw','ih','size','imgpath']
      cpd = pd.DataFrame(columns=colnames)
      cpd.loc[cpd.shape[0]] = [ self.id, self.cntrid, self.uid, self.x, self.y, self.iw, self.ih, (self.iw*self.ih), self.imgpath]
      
      return cpd
      

class myContour:
   def __init__(self,cindex,uid,contour,img=None,config=None,ekey=""):
      self.id = cindex #regular instance key
      self.uid = uid #points back to original contour id from findContours for reverse tracebility.
      self.contour = contour #points to original cv2.contour object available from findContours
      self.img = img #Custom myImg object corresponding to each of extracted contour. Initialize by caller.
      
      if config is None:
        raise Exception("class[" + self.__class__.__name__ + "] error. Exception as config passed is Null.")
      else:
        self.config = config
      
      self.ekey = ekey
      self.key = self.__class__.__name__
       
      self.logger = self.config.logger
      #self.logger.log( "myContour instance initialization. id[{}] configid[{}] imgid[{}]".format(self.id,self.config.id,self.img.id))
      self.logger.log( "myContour instance initialization. id[{}] configid[{}]".format(self.id,self.config.id))
      
      #initialize key image variables.
      self.x, self.y, self.rw, self.rh = cv2.boundingRect(self.contour)
      
      #Initialize remaining variables to null or None 
      self.iw = 0
      self.ih = 0
      self.imgpath = ""
      self.iqr_df = None
      self.lower_quartile_df = None
      self.upper_quartile_df = None
      self.text = {}
   
   def getContourCordinate(self):
      return self.x, self.y
    
   def getContourSize(self):
      return self.rw, self.rh
    
   def getContourParam(self):
      contour = {}
      contour['id'] = self.id
      contour['uid'] = self.uid
      contour['imgid'] = self.img.id
      contour['x'] = self.x
      contour['y'] = self.y
      contour['iw'] = self.rw
      contour['ih'] = self.rh
      contour['rw'] = self.rw
      contour['rh'] = self.rh
      contour['size'] = self.size
      contour['pxsize'] = type(self.img.img)
      contour['imgpath'] = self.imgpath
        
      return contour

   def extractContour(self,img):
      #self.img = cv2.rectangle( img, (self.x, self.y+self.rh), (self.x+self.rw, self.y))
      self.img = iutil.myImg(imageid=self.id,config=self.config,ekey=self.ekey,path=None,img=img)
      self.imgpath = self.img.getImagePath()
      self.ih, self.iw = self.img.getImageDim()
      #self.img.saveImage()
    
   def getContourAsDF(self):
      colnames = ['id','uid','x','y','rw','rh','iw','ih','size','imgpath']
      cpd = pd.DataFrame(columns=colnames)
      cpd.loc[cpd.shape[0]] = [ self.id, self.uid, self.x, self.y, self.rw, self.rh, self.iw, self.ih, (self.rw*self.rh), self.imgpath]
      
      return cpd
     
   def setY(self,y):
      self.y = y
    
   def scanSelected(self):
      swr_h = self.config.getSWRHeight() #get mean height of contoru image
      swr_h_sd = self.config.getSWRSD() #get standard deviation of contour height
      swr_move_interval = self.config.swr_move_interval
      
      #create array of different size windows that we want to run
      #swr_h is better choice compare to rh as for our problem fonts size doesn't vary much
      #swr_h = self.rh if self.rh < swr_h else swr_h #fix the permissible lower band
      #swr_w = math.floor(self.rh / self.config.swr_aspect_ratio)
      #swr_w = [math.floor(swr_w * .5), math.floor(swr_w - swr_w * .25), swr_w, math.floor(swr_w + swr_w * .25)]
      swr_w = math.floor(swr_h / self.config.swr_aspect_ratio)
      swr_w = [swr_w]
      
      for i in swr_w:
        w = int(i)        #swr window width
        x = int(self.x)
        y = int(self.y)
        h = int(self.rh)
        binaryimg = self.img.getImage()
        
        #get image center required to do reverse calc to fix y
        c = y + h/2 #for future use
        
        #check if h > rh.mean + rh.sd
        if h > (swr_h + 2*swr_h_sd): #increase y to start at our desire point we have limit image size.
          #adjust h to new condition.
          h = int(math.ceil(swr_h + 2*swr_h_sd))  #round up
          #h = int(math.ceil(swr_h))  #round up
        
        #check if scan window move param is defined
        if swr_move_interval == 0 or swr_move_interval == None:
          swr_move_interval = int(i) 
       
        #loop to chop contour using scanning window 
        offset = int(0)  #initialize offset to keeps track of increment in x cordinate
        index = 0 #keeps track of index of text dictionary, required to handle last window
        for ind,j in enumerate(range(0,self.rw,swr_move_interval)):
          offset = j #track offset
          
          if self.rw < (offset+w): #check for boundary case, if swr width is more then actual image width
            w = self.rw - offset
          
          #Extract the area of scan window from contour image 
          buf = binaryimg[0:h,offset:(offset+w)] #Extract char text at the position for given width size.
          
          #create image buf area place for holding image. Add 1 pixel each as buffer
          tmpimage = np.zeros([h+1,int(i)+1], np.uint8) #buf should of width=i as w may get change in some cases.
          tmpimage[0:h,0:w] = buf
          print("***i[{}] j[{}] x[{}] y[{}] h[{}] rw[{}] w[{}]".format(i,j,x,y,h,self.rw,w))
           
          #create full blown myUnitText object for each instance of window scroll.
          self.text[ind] = myUnitText( 
                                  id=self.id + '_' + 
                                  str(y) + '_' + 
                                  str(offset), 
                                  cntrid=self.uid,  
                                  uid=ind, 
                                  x=(x+offset), 
                                  y=y, 
                                  img=tmpimage, 
                                  config=self.config, 
                                  ekey=self.ekey)
          index = ind #keep track of index
            
        #handle the last piece of width
        w = (self.rw - offset) if ((self.rw - offset) > 0) else 0
        if w > 0:
          index += 1 #increment index by 1 for last element.
          #Extract the area of scan window from contour image 
          buf = binaryimg[0:h,offset:(offset+w)] #Extract char text at the position for given width size.
          #create image buf area place for holding image. 
          tmpimage = np.zeros([h,int(i)], np.uint8)
          tmpimage[0:h,0:w] = buf
          #create full blown myUnitText object for each instance of window scroll.
          self.text[index] = myUnitText( 
                                  id=self.id + '_' + 
                                  str(y) + '_' + 
                                  str(offset), 
                                  cntrid=self.uid,  
                                  uid=index, 
                                  x=(x+offset), 
                                  y=y, 
                                  img=tmpimage, 
                                  config=self.config, 
                                  ekey=self.ekey)
    
   
   #Scan all contours irrespective of there size by dynamically determining the height & width 
   def scanAll(self):
      swr_h = self.ih #set scan window height to contoru image height
      
      #create array of different size windows that we want to run
      swr_w = math.floor(swr_h / self.config.swr_aspect_ratio)
      
      #initialize move interval using pre difined ratio and width
      swr_move_interval = int(swr_w / self.config.swr_move_interval_ratio)
      if swr_move_interval < self.config.swr_move_interval: #update move interval if it below threshold.
        swr_move_interval = self.config.swr_move_interval
      swr_w = [swr_w]
      
      for i in swr_w:
        w = int(i)        #swr window width
        x = int(self.x)
        y = int(self.y)
        h = int(self.ih)
        binaryimg = self.img.getImage()
        
        #get image center required to do reverse calc to fix y
        c = y + h/2 #for future use
        
        #check if scan window move param is defined
        if swr_move_interval == 0 or swr_move_interval == None:
          swr_move_interval = int(i) 
       
        #loop to chop contour using scanning window 
        offset = int(0)  #initialize offset to keeps track of increment in x cordinate
        index = 0 #keeps track of index of text dictionary, required to handle last window
        for ind,j in enumerate(range(0,self.rw,swr_move_interval)):
        
          if w < int(i): #Check is reamining width is less then window width. if yes then exit
            break
          
          offset = j #track offset
          
          if self.rw < (offset+w): #check for boundary case, if swr width is more then actual image width
            w = self.rw - offset
          
          #Extract the area of scan window from contour image 
          buf = binaryimg[0:h,offset:(offset+w)] #Extract char text at the position for given width size.
          
          #create image buf area place for holding image. Add 1 pixel each as buffer
          tmpimage = np.zeros([h+1,w+1], np.uint8) #buf should of width=i as w may get change in some cases.
          print("***i[{}] j[{}] from[{}] to[{}] h[{}] rw[{}] w[{}]".format(i,j,offset,(offset+w),h,self.rw,w))
          tmpimage[0:h,0:w] = buf
           
          #create full blown myUnitText object for each instance of window scroll.
          self.text[ind] = myUnitText( 
                                  id=self.id + '_' + 
                                  str(y) + '_' + 
                                  str(offset), 
                                  cntrid=self.uid,  
                                  uid=ind, 
                                  x=(x+offset), 
                                  y=y, 
                                  img=tmpimage, 
                                  config=self.config, 
                                  ekey=self.ekey)
          index = ind #keep track of index
            
        #handle the last piece of width
        w = (self.rw - offset) if ((self.rw - offset) > 0) else 0
        if w > 0:
          index += 1 #increment index by 1 for last element.
          #Extract the area of scan window from contour image 
          buf = binaryimg[0:h,offset:(offset+w)] #Extract char text at the position for given width size.
          #create image buf area place for holding image. 
          tmpimage = np.zeros([h,int(i)], np.uint8)
          tmpimage[0:h,0:w] = buf
          #create full blown myUnitText object for each instance of window scroll.
          self.text[index] = myUnitText( 
                                  id=self.id + '_' + 
                                  str(y) + '_' + 
                                  str(offset), 
                                  cntrid=self.uid,  
                                  uid=index, 
                                  x=(x+offset), 
                                  y=y, 
                                  img=tmpimage, 
                                  config=self.config, 
                                  ekey=self.ekey)
    
   def getTextAsDF(self):
      keys = self.text.keys()
      text_df = pd.DataFrame()
      
      for key in keys:
        text_df = text_df.append(self.text[key].getUnitTextAsDF())
     
      #comment csv dump if not required at Contour level 
      #text_df.to_csv( self.config.ddir + self.id + '_text_df.csv')
       
      self.text_df = text_df
       
      return text_df
    
     
class myContours(object):
   cname = 'myContours'
    
   def __init__(self,path,contourid="x123",config=None,ekey=""):
      mname = '__init__' 
      
      self.id = contourid
      self.path = path
      self.ekey = ekey
      self.key = self.__class__.__name__

      if config is None:
        raise Exception("class[" + self.__class__.__name__ + "] error. Exception as config passed is Null.")
      else:
        self.config = config
      
      self.logger = self.config.logger
      self.logger.log( "myContours instance initialization. id[{}] configid[{}] path[{}]".format(self.id,self.config.id,self.path))
      self.dict = {} #initialize contour dictionay
      
      #create Image Processing object for main image. 
      self.img = iutil.myImg(imageid=self.id,config=self.config,ekey=self.ekey,path=self.path)
      self.imgbuf = None #placeholder for any processing
    
   def getContourById(self,idx):
     
     return self.dict[idx]
      
   def prepareImage(self):
     #this function needs to be adjusted as per need in order to image in right state.
     self.imgbuf = self.img.getHorizontalDialtedImageWithRect()
     #self.img.writeDictImages()
     self.imgresult = self.img.getGrayImage()
   
   def createContours(self):
     #Main code to create Contour and simultaneously extarct base data to word segments.
     
     #Get image on which contour extarct needs to be exeuted to extract submap within image.
     #binaryimg = self.img.getGrayImage() #cannot use this as it has 3 array unline Binary one array
     binaryimg = self.img.getBinaryImage() #this works best as it will be more consistent compare to others.
     #binaryimg = self.img.getGBinaryImage() #this is better then binary image by dark at center is problem
     #binaryimg = self.img.getMorphGradientImage()
     
     mask = np.zeros(self.imgbuf.shape, np.uint8)
     # find contours
     im2, contours, hierarchy = cv2.findContours( self.imgbuf, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
     # filter contours
     for idx in range(0, len(hierarchy[0])):
       #initialize Contour
       self.dict[idx] = myContour( cindex=self.id + '_' + str(idx), uid=idx, contour=contours[idx], img=None, config=self.config, ekey=self.ekey)
       x, y = self.dict[idx].getContourCordinate()
       w, h = self.dict[idx].getContourSize()
       # fill the contour
       mask = cv2.drawContours(mask, contours, idx, (255, 255, 2555), cv2.FILLED)
       # ratio of non-zero pixels in the filled region
       r = float(cv2.countNonZero(mask)) / (w * h)
       
       #main loop to do base filter for processing contours that has minimum hieght and width.
       if r > 0.45 and h > 8 and w > 4:
          self.imgresult = cv2.rectangle(self.imgresult, (x, y+h), (x+w, y), (1,255,0),1)
          #print("++idx{}|x{}|y{}|rw{}|rh{}|iw{}|ih{}".format(idx,x,y,w,h,self.dict[idx].iw,self.dict[idx].ih))
          tmpimage = np.zeros(self.imgbuf.shape, np.uint8)
          buf_on_dim_w = 2
          buf_on_dim_h = 2 #buf_on_dim_w * h / w
          if y < buf_on_dim_h:
            ystart = 0
          else:
            ystart = y-buf_on_dim_h
          if x < buf_on_dim_w:
            xstart = 0
          else:
            xstart = x-buf_on_dim_w
          #buf = binaryimg[y-buf_on_dim_h:y+h+buf_on_dim_h,x-buf_on_dim_w:x+w+buf_on_dim_w]
          buf = binaryimg[ystart:y+h+buf_on_dim_h,xstart:x+w+buf_on_dim_w]
          #_,buf = cv2.threshold(src=buf, thresh=127, maxval=255, type=cv2.THRESH_BINARY_INV)
          #tmpimage[y:y+h,x:x+w] = buf
          #tmpimage[y-buf_on_dim_h:y+h+buf_on_dim_h,x-buf_on_dim_w:x+w+buf_on_dim_w] = buf
          self.dict[idx].extractContour(img=buf)
          #print("***idx{}|x{}|y{}|rw{}|rh{}|iw{}|ih{}".format(idx,x,y,w,h,self.dict[idx].iw,self.dict[idx].ih))
   
   def getContoursAsDF(self):
      keys = self.dict.keys()
      cntr_df = pd.DataFrame()
      
      for key in keys:
        cntr_df = cntr_df.append(self.dict[key].getContourAsDF())
      
      cntr_df.to_csv( self.config.ddir + self.id + '_df.csv')
       
      return self.prepareIQRDF(cntr_df)
    
   def prepareIQRDF(self,cntr_df):
      #Get bound for IQR as IQR is required to find rh(image height) SD/Variance for correction y cordination
      cntr_df = cntr_df[cntr_df.ih > 0] #take only rows with imagepath not null #fix while processing safeway rec
      #print("record count [{}]".format(len(cntr_df)))
      lower_bound = cntr_df.rh.quantile(.25) #for 25% mark of quantile range
      upper_bound = cntr_df.rh.quantile(.75) #for 75% mark of quantile range
      
      #Get actual data of IDR
      iqr_df = cntr_df[(cntr_df['rh'] > lower_bound) 
                            & (cntr_df['rh'] <= upper_bound) 
                            #& (cntr_df['imgpath'].notnull())].sort_values(by=['y','x'],ascending=True)      
                            & (cntr_df['rh'] > 0)].sort_values(by=['y','x'],ascending=True)      
      
      #Get factor of Y cordinate correction using SD/Variance in countor rectangle height 
      self.y_variance_correction = 2 * iqr_df.rh.std()
      #save mean and SD in config for future reference.
      self.config.setSWRHeightAndSD( iqr_df.rh.mean(), iqr_df.rh.std())
      print("iqr rec's[{}] ub[{}] lb[{}] mean[{}] std[{}]".format(len(iqr_df),upper_bound,lower_bound,iqr_df.rh.mean(),iqr_df.rh.std()))
      
      #prepare final DF that will be used for processing
      #cntr_df1 = cntr_df[cntr_df.imgpath.notnull()]
      #cntr_df1 = cntr_df.dropna(subset=['imgpath'])
      
      #filter images where heigth or wigth is zero
      cntr_df1 = cntr_df[(cntr_df.ih > 0) & (cntr_df.iw > 0)]
      cntr_df1['orig_y'] = cntr_df1.y
      #print("rec's[{}] imgpath notnull rec's[{}]".format(len(cntr_df),len(cntr_df1)))
      
      for i in range(0,1000): 
        cntr_df1 = cntr_df1.sort_values(by=['y','x'],ascending=True)
        cntr_df1['prev_rec_y'] = cntr_df1.y.shift() #create new col to bring y from prev rec in DF
        cntr_df1['chg_in_y'] = abs(cntr_df1.y - cntr_df1.prev_rec_y) #add col holding change in y unit
         
        #if len(cntr_df1[(cntr_df1.chg_in_y <= self.y_variance_correction) & (cntr_df1.chg_in_y > 0)]) > 0:
        more_rec = len(cntr_df1[(cntr_df1.chg_in_y <= self.y_variance_correction) & (cntr_df1.chg_in_y > 0)]) 
        #print(" i[{}] more_rec[{}] ".format(i,more_rec))
        if more_rec > 0:
          #initialize and then correct the y where deviation in y compare to prev_rec_y is within derived limit 
          cntr_df1['y'] = cntr_df1.apply(lambda x,y_chg_lim=self.y_variance_correction: x.prev_rec_y if ((x.y-x.prev_rec_y)<=y_chg_lim) else x.y,axis=1)
          #cntr_df1 = cntr_df1.sort_values(by=['cor_y','x'],ascending=True)
        else:
          break
     
      #print(cntr_df1.columns) 
      
      #update y in contour 
      for i,x in cntr_df1.iterrows():
        self.dict[x.uid].setY(x.y)
      #unload corrected DF as csv
      cntr_df1.to_csv( self.config.ddir + self.id + '_cory_df.csv')
      self.cntr_df = cntr_df1 #save for future use.
       
      return cntr_df1
   
   def printContourDFOnImage(self):
      mname = "printContourDFOnImage"
      
      #get hold of grey image to layover Contours from DF
      contourImage = self.img.getGrayImage()
      cntr_df = self.cntr_df
      ''' 
      if (cntr_df == None) or (contourImage == None):
        print("{} Error: Either contour DF or Grey image on main Contours object is null.".format(mname))
        self.logger.log("{} Error: Either contour DF or Grey image on main Contours object is null.".format(mname))
      ''' 
      for i,x in cntr_df.iterrows():
        contourImage = cv2.rectangle( contourImage, (x.x, int(x.y)+x.rh), (x.x+x.rw, int(x.y)), (1,255,0),1)
      
      ofile = self.config.odir + self.id + '_cntr_df' + '.jpg'
      cv2.imwrite( ofile, contourImage)
       
     
   def printProcessedImage(self):
      img = iutil.myImg(imageid=self.id + '_imgresult',config=self.config,ekey=self.ekey,path=None,img=self.imgresult)
      img.printImageProp()
      #img.showImageAndHistogram()
   
   def log(self,msg,methodName=""):
      sep = '|'
      self.logger.log( self.ekey + sep + self.key + '::' + methodName + sep + msg + sep)
   
def main(argv):
   i_imgpath = ''
   i_cdir = './'
   i_ref = 'd1'
   
   try:
      opts, args = getopt.getopt(argv,"hir:",["i_img","i_cdir","i_ref"])
   except getopt.GetoptError:
      print 'test.py -r <unique instance id> -i <input contour file>'
      sys.exit(2)
   print("opt[{}] arg[{}]".format(opts,args))
   for opt, arg in opts:
      print("opt[{}] arg[{}]".format(opt,arg))
      if opt == '-h':
         print 'myContours.py -c <home dir> -i <input image file>'
         sys.exit()
      elif opt in ("-i", "--i_img"):
         i_imgpath = arg
      elif opt in ("-c", "--i_cdir"):
         i_cdir = arg
      elif opt in ("-r", "--i_ref"):
         i_ref = arg

   print 'Input contour file is ', i_imgpath
   print 'Input working directory is ', i_cdir
   print 'Input reference number is ', i_ref

   config = cutil.Config(configid="myConfId",cdir=i_cdir)
   cntr = myContours(contourid=i_ref,config=config,ekey='x123',path=i_imgpath)
   cntr.prepareImage()
   cntr.createContours()
   cntr.printProcessedImage()
   cntr.getContoursAsDF()
   cntr.printContourDFOnImage()

if __name__ == "__main__":
   main(sys.argv[1:])
