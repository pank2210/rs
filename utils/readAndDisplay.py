#!/Users/mumdi2610/.virtualenvs/cv/bin/python

import sys, getopt

import numpy as np
import cv2
import logging
import math
from matplotlib import pyplot as plt

from skimage import util


class myImg(object):
   cname = 'myImg'

   def __init__(self,inagId,config,ekey,path):
      mname = '__init__' 
      
      self.id = imageId
      self.config = config
      
      self.ekey = ekey
      self.key = self.__class__.__name__

      self.logger = Lib.Logger( self.__class__.__name__, "/Users/pankaj.petkar/dev/cv/ex").get()
      logging.basicConfig(filename='myapp.log', level=logging.INFO)
      #self.log = self.logger.get()
      self.log( mname, 'Instance created.')
      self.imgPath = path
      self.img = cv2.imread(self.imgPath,0)
    
      self.printImageProp()
      #self.addRandNoise()
      #self.printImageProp()

   def log(self,methodName,msg):
      sep = '|'
      logging.info( self.ekey + sep + self.key + '::' + methodName + sep + msg + sep)

   def showImage(self):
      mname = 'showImage' 

      cv2.imshow('image',self.img)
      k = cv2.waitKey(0)
      if k == 27:         # wait for ESC key to exit
         cv2.destroyAllWindows()
      elif k == ord('s'): # wait for 's' key to save and exit
         cv2.imwrite('o.png',self.img)
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
     
      print('------------------------------')
      print(' size - %d',self.img.size)
      print(' shape - ' + str(self.img.shape))
      print(' dtype - ' + str(self.img.shape))
      print(' pixel size - ' + str(sys.getsizeof(self.img.item(1,1))))
      print('------------------------------')

      #print image histogram
      fig, axes = plt.subplots(nrows=1,ncols=2) #init subplot 
      ax = axes.ravel()
      #put image to display
      ax[0].imshow(self.img,cmap=plt.cm.gray)
      ax[0].set_title('Image')
      #put histogram to display
      ax[1].hist(self.img.ravel(),256,[0,256])
      ax[1].set_title('Histogram')
      
      #plt.hist(self.img.ravel(),256,[0,256]); 
      plt.tight_layout()
      plt.show()

   def imageAveraging(self,neig,img):
      mname = 'imageAveraging' 
     
      self.log( mname, 'averagin using ' + str(neig))
      print 'Averaing  - %d X %d' % (neig,neig)
      x,y = img.shape
      print ' Image shape  - %d X %d' % (x,y)
      units =  math.floor(neig/2)
      imgSize = x*y
      x1 = x - 2*units
      y1 = y - 2*units
      print ' processing index shape  - %d X %d' % (x1,y1)
      t_img_ind = np.empty([x1,y1],dtype=int)
      ind = range(imgSize)
      for i in range(t_img_ind.shape[0]):
	s = int(y*(units+i)+units)
	t_img_ind[i,:] = ind[s:int(s+y1)]
      print t_img_ind

   def convoluteUseAverage(self,type,units,img,t_img_ind):
      mname = 'convoluteUseAverage' 
     
      self.log( mname, 'averagin using ' + str(neig))
    
   def blurTheImage(self,imagekey=0):
     # downsample and use it for processing
     rgb = pyrDown(large)
     writeImg("rgb.jpg",rgb)
     
     # apply grayscale
     small = cvtColor(rgb, cv2.COLOR_BGR2GRAY)
     writeImg("gray.jpg",small)
     
     # morphological gradient
     morph_kernel = getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
     grad = morphologyEx(small, cv2.MORPH_GRADIENT, morph_kernel)
     writeImg("grad.jpg",grad)
     
     # binarize
     _, bw = threshold(src=grad, thresh=0, maxval=255, type=cv2.THRESH_BINARY+cv2.THRESH_OTSU)
     writeImg("thresh.jpg",bw)
     
     morph_kernel = getStructuringElement(cv2.MORPH_RECT, (9, 1))
     # connect horizontally oriented regions
     connected = morphologyEx(bw, cv2.MORPH_CLOSE, morph_kernel)
     writeImg("morph1.jpg",connected)
     
     mask = np.zeros(bw.shape, np.uint8)
     # find contours
     im2, contours, hierarchy = findContours(connected, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
     # filter contours
     for idx in range(0, len(hierarchy[0])):
         rect = x, y, rect_width, rect_height = boundingRect(contours[idx])
         # fill the contour
         mask = drawContours(mask, contours, idx, (255, 255, 2555), cv2.FILLED)
         # ratio of non-zero pixels in the filled region
         r = float(countNonZero(mask)) / (rect_width * rect_height)
         if r > 0.45 and rect_height > 8 and rect_width > 8:
             rgb = rectangle(rgb, (x, y+rect_height), (x+rect_width, y), (0,255,0),3)
     

def main(argv):
   i_imgPath = ''
   try:
      opts, args = getopt.getopt(argv,"hi:",["i_img="])
   except getopt.GetoptError:
      print 'test.py -i <input image file>'
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print 'readAndDispImage.py -i <input image file>'
         sys.exit()
      elif opt in ("-i", "--i_img"):
         i_imgPath = arg
   print 'Input image file is "', i_imgPath

   img1 = myImg("standalone", i_imgPath)
   img1.showImage()
   #img1.printPixel(21,5)
   #img1.imageAveraging(3,np.empty([10,10],dtype=int))

if __name__ == "__main__":
   main(sys.argv[1:])
