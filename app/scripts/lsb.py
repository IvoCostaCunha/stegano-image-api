from flask import Blueprint
from datetime import datetime
from PIL import Image
import numpy as np
import uuid

lsb = Blueprint('lsb', __name__)

# Generate an UUID to use to identify a PNG file
def generateUUID():
  uuidBin =  str(uuid.uuid4())
  return uuidBin

# Checks if the img is transparent
def imgIsTranparent(pixelNb):
  if(pixelNb%3 == 0):
    return False
  else:
    return True

# Returns an array of binary Bits from string
def strToByteArray(string):
  binArray = []
  for char in string:
    binArray.append( ''.join( bin(ord(char) )).replace('b','') )
  return binArray

# Returns a string from an array of each char in binary
def bytesToStrArray(bitsArray):
  string = ''
  for bits in bitsArray:
    string = string + ''.join( chr(int(bits, 2 )))
  return string

# Returns a char from a char in binary
def byteToStr(byte):
  return ''.join( chr(int(byte, 2 )))

# Returns a binary Bit from char
def charToByteArray(char):
  return ''.join( bin(ord(char) )).replace('b','')

# Returns an int in binary
def intToByte(int):
  return f'{int:08b}'

def byteArrayToIntArray(byteArray):
  intArray = []
  for byte in byteArray:
    intArray.append(int(byte, 2))
  return intArray

# Returns a array of each pixel value a PNG file in binary
def pixelsToBin(pngPixelData):
  pixelsBin = []
  for pixel in pngPixelData:
    for color in pixel:
      pixelsBin.append(intToByte(color))
  return pixelsBin

# Returns a arrays of ints the the following format [{1, 2, 3}, ...etc] or [{1, 2, 3, T}, ...etc]
def imgDataFromIntArrayList(intArray):
  transparency = imgIsTranparent(len(intArray))
  imgData = []
  if(not transparency):
    for i in range(0, len(intArray), 3):
      pixel = (intArray[i], intArray[i+1], intArray[i+2])
      imgData.append(pixel)
  else:
    for i in range(0, len(intArray), 4):
      pixel = (intArray[i], intArray[i+1], intArray[i+2])
      imgData.append(pixel)
    
  return imgData

# Inserts a string into each last one bit of pixel colors of an image
# Takes an array of each color of each pixel in binary as parameter      
def insertToImgBinArray(string, pixelsBinArray):
  # Tranformation of each char to be inserted into a binary array
  toInsert = []
  for char in string:
    charBin = charToByteArray(char)
    # If the char binary is not 8 in lenght, a 0 must be added at begining
    # Otherwise it cannot be know when an actual char is supposed to be read
    if(len(charBin) < 8):
      charBin = str(0) + charBin
    for bit in charBin:
      toInsert.append(bit)
  
  toInsertIndex = 0
  for i in range(0, len(pixelsBinArray)):
    initialValue = pixelsBinArray[i]
    pixelsBinArray[i] = pixelsBinArray[i][:len(pixelsBinArray[i])-1] + toInsert[i] + pixelsBinArray[i][len(pixelsBinArray[i]):]
    
    # print('(', toInsert[toInsertIndex], ')', initialValue, ' -> ', pixelsBinArray[i], end='\r')
    
    toInsertIndex = toInsertIndex + 1
    
    # Everything should be inserted here
    if(toInsertIndex == len(toInsert)):
      if(i < len(pixelsBinArray)):
        # Everything went fine
        return True
      else:
        return False
  
  # If the function has not returned there then all chars were not inserted
  return False
     
def useLsb (rawPngFiles): 
  timeBefore = datetime.now()
  if(len(rawPngFiles) > 0):
    signedFiles = []
    for f in rawPngFiles:
      
      filename = f[0]
      pilImg = Image.open(f[1])

      imgWidth, imgHeight = pilImg.size
      imgFormat = pilImg.format
      imgExif = pilImg.getexif()

      print('\n--------------------\nImg:', filename, ' \n--------------------\nINFORMATIONS:')
      print('(in pixels) width:', imgWidth, 'height:', imgHeight, 'total:', imgHeight*imgWidth)
      print('format:', imgFormat)
      print('metadata:', imgExif)
      print('--------------------')
      # pilImg.show(pilImg)

      if(imgFormat != 'PNG'):
        return {'error': 'Files format must be PNG.', 'confirmation': False}
      
      else:
        pilImgData = list(pilImg.getdata())
        print('Initial size of image pixel data (in px):', len(pilImgData))
        pilImgDataBinArray = pixelsToBin(pilImgData)
        
        uuid = generateUUID()
        
        # If true function did its job
        if(insertToImgBinArray(uuid, pilImgDataBinArray)):
          data = byteArrayToIntArray(pilImgDataBinArray)
          dataList = imgDataFromIntArrayList(data)
          print('Size of pixel data recreated (in px):', len(dataList))
          pilImg.putdata(dataList)
          pilImg.save(filename, 'PNG')
          # pilImg.show()
          
          timeAfter = datetime.now()
          execTime = timeAfter-timeBefore
          print('Done in ' + str(execTime.seconds) + 's ' + str(execTime.microseconds) + 'ms\n--------------------')
        else:
          print('image too small for data')
        
        signedFiles.append([filename, uuid, pilImg])
        
    return [{'message': 'Image signed with success.', 'confirmation': True}, signedFiles]
        
  else:
    return {'error': 'Files to sign could not be found.', 'confirmation': False}