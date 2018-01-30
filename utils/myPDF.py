
import sys, getopt
import os

import math
import re

import numpy as np
import pandas as pd

import cv2
import struct
import PyPDF2 as pyPDF2

import config as cutil
import myImg as iutil

class myPDF(object):
   cname = 'myPDF'

   def __init__(self,path,id="x123",config=None,ekey=""):
      mname = '__init__' 
      
      self.id = id
      
      if config is None:
        raise Exception("class[" + self.__class__.__name__ + "] error. Exception as config passed is Null.")
      else:
        self.config = config
        self.logger = self.config.logger
      
      self.ekey = ekey
      self.key = self.__class__.__name__
      
      self.path = path
      self.pdf_file_path = self.config.idir + path
      
      self.pdfobj = pyPDF2.PdfFileReader(file(self.pdf_file_path,"rb"))
      
   def tiff_header_for_CCITT(self,width, height, img_size, CCITT_group=4):
      tiff_header_struct = '<' + '2s' + 'h' + 'l' + 'h' + 'hhll' * 8 + 'h'
      
      return struct.pack(tiff_header_struct,
                       b'II',  # Byte order indication: Little indian
                       42,  # Version number (always 42)
                       8,  # Offset to first IFD
                       8,  # Number of tags in IFD
                       256, 4, 1, width,  # ImageWidth, LONG, 1, width
                       257, 4, 1, height,  # ImageLength, LONG, 1, lenght
                       258, 3, 1, 1,  # BitsPerSample, SHORT, 1, 1
                       259, 3, 1, CCITT_group,  # Compression, SHORT, 1, 4 = CCITT Group 4 fax encoding
                       262, 3, 1, 0,  # Threshholding, SHORT, 1, 0 = WhiteIsZero
                       273, 4, 1, struct.calcsize(tiff_header_struct),  # StripOffsets, LONG, 1, len of header
                       278, 4, 1, height,  # RowsPerStrip, LONG, 1, lenght
                       279, 4, 1, img_size,  # StripByteCounts, LONG, 1, size of image
                       0  # last IFD
                       ) 
   
   def processPages(self):
      pages = self.pdfobj.getNumPages()
     
      colnames = ['pdf','page','width','height','size','img_file']
      pdf_df = pd.DataFrame(columns=colnames)
 
      for page_id in range(pages):
        #print("Processing page[{}]".format(page_id))
        page = self.pdfobj.getPage(page_id)
        xObject = page['/Resources']['/XObject'].getObject()
          
        for obj in xObject:
            """
            The  CCITTFaxDecode filter decodes image data that has been encoded using
            either Group 3 or Group 4 CCITT facsimile (fax) encoding. CCITT encoding is
            designed to achieve efficient compression of monochrome (1 bit per pixel) image
            data at relatively low resolutions, and so is useful only for bitmap image data, not
            for color images, grayscale images, or general data.
             
            K < 0 --- Pure two-dimensional encoding (Group 4)
            K = 0 --- Pure one-dimensional encoding (Group 3, 1-D)
            K > 0 --- Mixed one- and two-dimensional encoding (Group 3, 2-D)
            """
            if xObject[obj]['/Filter'] == '/CCITTFaxDecode':
                if xObject[obj]['/DecodeParms']['/K'] == -1:
                    CCITT_group = 4
                else:
                    CCITT_group = 3
                width = xObject[obj]['/Width']
                height = xObject[obj]['/Height']
                data = xObject[obj]._data  # sorry, getData() does not work for CCITTFaxDecode
                img_size = len(data)
                tiff_header = self.tiff_header_for_CCITT(width, height, img_size, CCITT_group)
                img_name = obj[1:] + '.tif'
                
                '''
                print(" Width - [{}]".format(width))
                print(" Height - [{}]".format(height))
                print(" Size - [{}]".format(img_size))
                print(" img_name - [{}]".format(img_name))
                '''
                
                m1 = re.match( "(.*?)\.pdf", self.path) #extract original PDF file name
                f_name = self.config.odir + m1.group(1) + '_' + str(page_id) + '.TIF'
                with open( f_name, 'wb') as img_file:
                    img_file.write(tiff_header + data)
                
                pdf_df.loc[pdf_df.shape[0]] = [ self.path, page_id, width, height, img_size, f_name]
            else:
              print("Error cannot process as /CCITTFaxDecode fileter not supported. File[{}] Page[{}]".format(self.path,page_id))
      
      #update final PDF processing content in pdf_df
      self.pdf_df = pdf_df
      
      return pdf_df
   
   def read_metadata(self):
      '''
      # Scan the last 2048 bytes, the most
      # frequent metadata density block
      stream.seek(-self.metadata_offset, os.SEEK_END)
      properties = dict()
      try:
          properties = dict(('/' + p.group(1), p.group(2).decode('utf-8')) \
              for p in self.metadata_regex.finditer(stream.read(self.metadata_offset)))
          if '/Author' in properties:
              return properties
      except UnicodeDecodeError:
          properties.clear()
      '''
      
      # Parse the xref table using pyPdf
      properties = dict()
      print("-------------------------------------------------------------")
      print(" File - [{}]".format(self.path))
      print(" #pages - [{}]".format(self.pdfobj.getNumPages()))
      docInfo = self.pdfobj.getDocumentInfo()
      for metaItem in docInfo:
        print '[+] ' + metaItem + ':' + str(docInfo[metaItem]) 
      '''
      xmpMetadata = self.pdfobj.getXmpMetadata()
      if type(xmpMetadata).__name__ == self.config.typeNone:
        for xmpMetaItem in xmpMetadata:
          print '[+] ' + xmpMetaItem + ':' + str(xmpMetadata[xmpMetaItem]) 
      '''
      print("-------------------------------------------------------------")
      
      if properties:
          return properties
      
      return {}         

class myPDFProcessor(object):
   cname = 'myPDF'

   def __init__(self,file_pattern,id="x123",config=None,ekey=""):
      mname = '__init__' 
      
      self.id = id
      
      if config is None:
        raise Exception("class[" + self.__class__.__name__ + "] error. Exception as config passed is Null.")
      else:
        self.config = config
        self.logger = self.config.logger
      
      self.ekey = ekey
      self.key = self.__class__.__name__
      
      self.file_pattern = file_pattern
    
   def processPDFFiles(self):
      ddir = self.config.idir
      
      filelist = os.listdir(ddir)
      pdf_df = pd.DataFrame()
      
      for i,f_name in enumerate(filelist):
        m1 = re.match( self.file_pattern, f_name)
        #m1 = re.match( ".*?\.pdf", f_name)
        
        if m1:
          print("Processing [{}]".format(f_name))
          pdf = myPDF(path=f_name,id="xx",config=self.config,ekey='x123')
          pdf_df = pdf_df.append(pdf.processPages())
          pdf = None
      
      self.pdf_df = pdf_df
      pdf_df.to_csv( self.config.odir + self.id + '.csv')
      
      return pdf_df
   
      
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
         print 'myPDFProcessor.py -i <input image file name pattern>'
         print 'myPDFProcessor.py -c <home dir> -i <input image file>'
         sys.exit()
      elif opt in ("-i", "--i_img"):
         i_imgpath = arg
      elif opt in ("-c", "--i_cdir"):
         i_cdir = arg
   print 'Input image file pattern is "', i_imgpath
   print 'Input working directory is "', i_cdir

   config = cutil.Config(configid="myConfId",cdir=i_cdir)
   pdf_proc = myPDFProcessor(file_pattern=i_imgpath,id="pdf_df1",config=config,ekey='x123')
   #pdf_proc = myPDFProcessor(file_pattern=".*?\.pdf",id="pdf_df1",config=config,ekey='x123')
   pdf_proc.processPDFFiles()

if __name__ == "__main__":
   main(sys.argv[1:])
