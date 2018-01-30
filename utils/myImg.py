
import sys, getopt

import numpy as np
import cv2
import math
import re

from matplotlib import pyplot as plt
from skimage import util

import config as cutil

class myImg(object):
   cname = 'myImg'

   def __init__(self,path,imageid="x123",config=None,ekey="",img=None):
      mname = '__init__' 
      
      self.id = imageid
      self.i_img_file_name = path

      if config is None:
        raise Exception("class[" + self.__class__.__name__ + "] error. Exception as config passed is Null.")
      else:
        self.config = config
        self.logger = self.config.logger
      
      self.ekey = ekey
      self.key = self.__class__.__name__
     
     
      #img param which is numpy image array takes precedence over path 
      #If path is passed along with img then path will be overwritten with img content as .jpg
      if type(img).__name__ != self.config.typeNone: #img is passed so use it.
         self.img = img
         if path is None: #construct if path doesn't exists when img is passed.
            self.imgpath = self.config.odir + 'img_' + self.id + '.jpg'
         else:
            self.imgpath = self.config.odir + path
         cv2.imwrite( self.imgpath, img) #since img is passed, persist it in config.odir
      else: #path is passed, so use it to build img
         #check if mandatory param are passed. 
         if type(path).__name__ == self.config.typeNone:
            raise Exception("class[" + self.__class__.__name__ + "] error. A path<valid image path> argument cannot be null if img is None.")
         self.imgpath = self.config.idir + path
         self.img = cv2.imread(self.imgpath,1) #1 param is for color/multi channel image read.

      self.setImageMetadata()      
      self.imgdict = {} #initialize image dictionay
      self.logger.log( "myImage instance initialization. id[{}] configid[{}] imgpath[{}]".format(self.id,self.config.id,self.imgpath))
   
   def setImageMetadata(self):
      self.size = self.img.size
      self.width = self.img.shape[0]
      self.height = self.img.shape[1]
      if len(self.img.shape) > 2:
         self.channels = self.img.shape[2]
      else:
         self.channels = 1

   def getImage(self):
      return self.img

   def getImagePath(self):
      return self.imgpath

   def getImageSize(self):
      return self.size

   def getImageDim(self):
      return self.width, self.height

   def log(self,msg,methodName=""):
      sep = '|'
      self.logger.log( self.ekey + sep + self.key + '::' + methodName + sep + msg + sep)

   def showImage(self,imagekey=""):
      mname = 'showImage' 
      imgid = None
      img = None
      
      if imagekey != "":
        imgid = imagekey
        img = self.imgdict.get(imagekey,None)
      else:
        imgid = self.id
        img = self.img
       
      cv2.imshow(imagekey,img)
      k = cv2.waitKey(0)
      if k == 27:         # wait for ESC key to exit
         cv2.destroyAllWindows()
      elif k == ord('s'): # wait for 's' key to save and exit
         #cv2.imwrite('o.png',self.img)
         cv2.destroyAllWindows()

   def printPixel(self,x,y):
      mname = 'printPixel' 
     
      if x<0:
        x=0 
      if y<0:
        y=0 

      px = self.img[x,y]
      #print('px - ' + px)
      print(px)
      print(self.img.item(x,y))

   def addRandNoise(self):
      mname = 'addRandNoise'
       
      img_noisy = util.random_noise(self.img,mode='gaussian',seed=None,clip=True,mean=0,var=0.01)
      self.img = self.img ** img_noisy
      #print(' noise - ' + str(img_noisy[5:6,93:105]))

   def printImageProp(self):
      mname = 'printImageProp' 
      
      self.logger.log('-------------------------------------------------------------------------------')
      self.logger.log('      id         - {}'.format(self.id))
      self.logger.log('      imgpath    - {}'.format(self.imgpath))
      self.logger.log('      size       - {}'.format(self.size))
      self.logger.log('      shape      - {} X {}'.format(str(self.width),str(self.height)))
      self.logger.log('      rawshape   - {}'.format(self.img.shape))
      self.logger.log('      pixel size - {}'.format(type(self.img)))
      imagekeys = self.imgdict.keys()
      for imagekey in imagekeys:
        self.logger.log('        image[{}] - size[{}] shape[{}]'.format(imagekey,self.imgdict.get(imagekey).size,self.imgdict.get(imagekey).shape))
      #self.logger.log('----------------------------------------------------')


   def showImageAndHistogram(self):
      #prepare keys for iterating all dictionary images.
      imagekeys = self.imgdict.keys()
      #Create subplot to accomodate all images and historgram
      fig, axes = plt.subplots(nrows=len(imagekeys)+1,ncols=2) #init subplot 
      ax = axes.ravel()
       
      #put source or original image to display
      ax[0].imshow(self.img)
      ax[0].set_title(self.id)
      #put histogram to display
      ax[1].hist(self.img.ravel(),256,[0,256])
      ax[1].set_title('Histogram')
       
      #iterate dictionary
      for i,imagekey in enumerate(imagekeys):
        #put image to display
        ax[i+2].imshow(self.imgdict.get(imagekey,None))
        ax[i+2].set_title(imagekey)
        #put histogram to display
        ax[i+3].hist(self.img.ravel(),256,[0,256])
        ax[i+3].set_title(imagekey + ' Histogram')
      
      #plt.hist(self.img.ravel(),256,[0,256]); 
      plt.tight_layout()
      plt.show()
   
   def getImageByKey(self,imagekey):
      return self.imgdict[imagekey]
    
   def saveImage(self,img=None,img_type_ext='.jpg',gen_new_filename=False):
      ofile = ""
       
      if gen_new_filename:
        m1 = re.search("(^.*?)\.(\w{3})$",self.i_img_file_name)
        ofile = self.config.odir + m1.group(1) + '_u' + img_type_ext
      else:
        ofile = self.config.odir + 'cntr_' + self.id + img_type_ext
       
      if type(img).__name__ != self.config.typeNone: #img is passed so use it.
        #print("saveImage: Saving override Image.")
        cv2.imwrite( ofile, img)
      else:
        cv2.imwrite( ofile, self.getImage())

   def writeDictImages(self):
      imagekeys = self.imgdict.keys()
      for imagekey in imagekeys:
         ofile = self.config.odir + self.id + '_' + imagekey + '.jpg'
         cv2.imwrite( ofile ,self.imgdict.get(imagekey))

   def imageAveraging(self,neig,img):
      mname = 'imageAveraging' 
      
      self.logger.log('{} averaging using {}'.format(mname,str(neig)))
      self.logger.log('Averaing  - {} X {}'.format(neig,neig))
      x,y = img.shape
      #self.logger.log(' Image shape  - %d X %d' % (x,y))
      units =  math.floor(neig/2)
      imgSize = x*y
      x1 = x - 2*units
      y1 = y - 2*units
      self.logger.log(' processing index shape  - {} X {} '.format(x1,y1))
      t_img_ind = np.empty([x1,y1],dtype=int)
      ind = range(imgSize)
      for i in range(t_img_ind.shape[0]):
	s = int(y*(units+i)+units)
	t_img_ind[i,:] = ind[s:int(s+y1)]
      #self.logger.log(t_img_ind)

   def convoluteUseAverage(self,type,units,img,t_img_ind):
      mname = 'convoluteUseAverage' 
      
      self.logger.log( mname + ' averagin using ' + str(neig))
    
   def getBlurImage(self,imagekey=""):
     # downsample and use it for processing
     img = None
     
     if imagekey == "": #set imagekey if null
       imagekey = "blur"
    
     img = self.imgdict.get(imagekey,None)
     if img is not None: #check if blur image already in dict and if not create one
       return img
     else: 
       self.imgdict[imagekey] = cv2.pyrDown(self.img)
       
       return self.imgdict[imagekey]
     
   def getGrayImage(self,imagekey=""):
     # apply grayscale
     img = None
     
     if imagekey == "": #set imagekey if null
       imagekey = "gray"
   
     img = self.imgdict.get(imagekey,None)
     if img is not None: #check if blur image already in dict and if not create one
       return img
     else: 
       #img = self.img  #if blurring is not done then #no contours blow up 2.5 times.
       img = self.getBlurImage()
       self.imgdict[imagekey] = cv2.cvtColor( img, cv2.COLOR_BGR2GRAY)
       
       return self.imgdict[imagekey]
   
   '''     
    Apply errosion to make highlight thinner.
   '''     
   def getMorphErode(self,imagekey=""):
     # Add's one iteration of erosion to normal gray image.
     img = None
     #morph_kernel_mask = (3,3) #initialize morph kernel to 3 X 3
     morph_kernel_mask = np.ones((3,3) ,np.uint8) #initialize morph kernel to 3 X 3
     
     if imagekey == "": #set imagekey if null
       imagekey = "morpherode"
    
     img = self.imgdict.get(imagekey,None)
     if img is not None: #check if blur image already in dict and if not create one
       return img
     else:
       oimg = self.getGrayImage() #works on gray image. Actual it enhances write content
       eroded = cv2.erode( oimg, morph_kernel_mask, iterations=1)
       ''' #commented as this code is useless. it produces emobossing.
       temp = cv2.dilate( eroded, morph_kernel_mask)
       temp = cv2.subtract( oimg, temp)
       skel = np.zeros( oimg.shape, np.uint8)
       skel = cv2.bitwise_or( skel, temp)
       self.imgdict[imagekey] = skel
       '''
       self.imgdict[imagekey] = eroded
       
       return self.imgdict[imagekey]
     
   '''     
    Apply gradient change of thicken edges also called as dialetion.
   '''     
   def getMorphGradientImage(self,imagekey=""):
     # morphological gradient
     img = None
     morph_kernel_mask = (3,3) #initialize morph kernel to 3 X 3
     
     if imagekey == "": #set imagekey if null
       imagekey = "morphgradient"
    
     img = self.imgdict.get(imagekey,None)
     if img is not None: #check if blur image already in dict and if not create one
       return img
     else: 
       morph_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, morph_kernel_mask )
       self.imgdict[imagekey] = cv2.morphologyEx( self.getGrayImage(), cv2.MORPH_GRADIENT, morph_kernel)
       
       #build image with key "emorphgradient" to represent gray image with one iteration using erode.
       self.imgdict['e' + imagekey] = cv2.morphologyEx( self.getMorphErode(), cv2.MORPH_GRADIENT, morph_kernel)
       
       return self.imgdict[imagekey]
     
   def getGBinaryImage(self,imagekey="",fromimagekey=""):
     # Gaussian binarize
     img = None
     
     if imagekey == "": #set imagkey if null
       imagekey = "gbinary"
    
     img = self.imgdict.get(imagekey,None)
     if img is not None: #check if blur image already in dict and if not create one
       return img
     else:
       if fromimagekey == "":
          #tmpimg = cv2.GaussianBlur(self.getMorphGradientImage(),(3,3),0)
          tmpimg = self.getImageByKey(imagekey="emorphgradient")
          _, self.imgdict[imagekey] = cv2.threshold( src=tmpimg, thresh=0, maxval=255, type=cv2.THRESH_BINARY+cv2.THRESH_OTSU)
          return self.imgdict[imagekey]
       else:
          #print("Pulling image from [{}]".format(fromimagekey))
          _, tmpimg = cv2.threshold(src=self.getImageByKey(imagekey=fromimagekey), thresh=0, maxval=255, type=cv2.THRESH_BINARY+cv2.THRESH_OTSU)
          self.imgdict[imagekey] = tmpimg
          
          return tmpimg
       
   def getBinaryImage(self,imagekey="",fromimagekey=""):
     # binarize
     img = None
     
     if imagekey == "": #set imagkey if null
       imagekey = "binary"
    
     img = self.imgdict.get(imagekey,None)
     if img is not None: #check if blur image already in dict and if not create one
       return img
     else:
       if fromimagekey == "":
          _, self.imgdict[imagekey] = cv2.threshold(src=self.getMorphGradientImage(), thresh=0, maxval=255, type=cv2.THRESH_BINARY+cv2.THRESH_OTSU)
          return self.imgdict[imagekey]
       else:
          _, tmpimg = cv2.threshold(src=self.getImageByKey(imagekey=fromimagekey), thresh=0, maxval=255, type=cv2.THRESH_BINARY+cv2.THRESH_OTSU)
          return tmpimg
       
   def getHorizontalDialtedImageWithRect(self,imagekey=""):
     # connect horizontally oriented regions
     img = None
     morph_kernel_mask = (9,1)
     
     if imagekey == "": #set imagkey if null
       imagekey = "horizontaldialated"
    
     img = self.imgdict.get(imagekey,None)
     if img is not None: #check if blur image already in dict and if not create one
       return img
     else: 
       morph_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, morph_kernel_mask)
       self.imgdict[imagekey] = cv2.morphologyEx( self.getBinaryImage(), cv2.MORPH_CLOSE, morph_kernel)
        
       return self.imgdict[imagekey]
    
   def add_text( self, text, x=0, y=0, image_scale=10):
      """
      Args:
          img (numpy array of shape (width, height, 3): input image
          text (str): text to add to image
          text_top (int): location of top text to add
          image_scale (float): image resize scale
  
      Summary:
          Add display text to a frame.
  
      Returns:
          Next available location of top text (allows for chaining this function)
      """
      u_img = cv2.putText(
                    img=self.img,
                    text=text,
                    org=(x, y),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale = 0.15 * image_scale,
                    color = (255, 0, 0),
                    thickness = 2)
      #self.saveImage(img=u_img,img_type_ext='.tif')
      self.saveImage(img_type_ext='.tif',gen_new_filename=True)
       
      return y + int(5 * image_scale)  

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
         print 'myImg.py -i <input image file>'
         print 'myImg.py -c <home dir> -i <input image file>'
         sys.exit()
      elif opt in ("-i", "--i_img"):
         i_imgpath = arg
      elif opt in ("-c", "--i_cdir"):
         i_cdir = arg
   print 'Input image file is "', i_imgpath
   print 'Input working directory is "', i_cdir

   config = cutil.Config(configid="myConfId",cdir=i_cdir)
   img1 = myImg(imageid="xx",config=config,ekey='x123',path=i_imgpath)
   #img2 = myImg(imageid="myImgId2",config=config,ekey='x123',path=None,img = img1.getMorphGradientImage())
   img1.printImageProp()
   img1.add_text( "FileName: " + i_imgpath, x=200, y=70, image_scale=10)
   #img2.printImageProp()
   '''
   img1.getHorizontalDialtedImageWithRect()
   img1.getGBinaryImage(fromimagekey="emorphgradient")
   img1.getMorphErode()
   img1.writeDictImages()
   '''
   #img2.showImageAndHistogram()

if __name__ == "__main__":
   main(sys.argv[1:])
