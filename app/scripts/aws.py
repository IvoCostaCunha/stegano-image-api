from flask import Blueprint, jsonify
from datetime import datetime
import boto3
import os
import shutil

from app.scripts.fileManager import sendFile

aws = Blueprint('aws', __name__, url_prefix= '/api/0.1/aws')

bucketName= os.getenv("BUCKET_NAME")
accessKeyId = os.getenv("ACCESS_KEY_ID")
secretAccessKeyId = os.getenv("SECRET_ACCESS_KEY_ID")
region = os.environ.get("REGION")

s3Session = boto3.Session(
    aws_access_key_id = accessKeyId,
    aws_secret_access_key = secretAccessKeyId,
    # region_name = region
)

s3Ressource = s3Session.resource('s3')
s3Client = s3Ressource.meta.client
bucket = s3Ressource.Bucket(bucketName)

def deleteFile(filePath):
  s3Ressource.Object(bucketName, filePath).delete()

def checkIfFileExist(id, filepath):
  print('all')
  for file in bucket.objects.all():
    print(file)
    
  print('filter')
  for file in bucket.objects.filter(Prefix=str(id)):
    print(file)
  # return jsonify(files)

def addToBucket(id, files):
  timeStamp = datetime.now().strftime("%Y%m%d%H%M%S")
  publicUrls = []
  for file in files:
    filename = os.path.splitext(file['filename'])[0]
    fileExt = os.path.splitext(file['filename'])[1]
    filenameStamped = filename + timeStamp + fileExt
    key = id + '/'+ filenameStamped
    path = 'tmp/' + id
    
    if not os.path.isdir(path):
      os.mkdir(path)
    
    savedFilePath = 'tmp/' + id + '/' + filenameStamped
    file['file'].save(savedFilePath)
    
    s3Client.upload_file(Filename = savedFilePath, Bucket = bucketName, Key = key)
    publicUrls.append({'filename': filenameStamped, 'url': getFileUrlFromId(id, filenameStamped)})
    
    os.remove(savedFilePath)
    
  return publicUrls
  
def downloadFileToLocal(id, filename):
  filepath = id + '/' + filename
  if not os.path.isdir('tmp/' + id):
    os.mkdir('tmp/' + id)
  s3Client.download_file(bucketName, filepath, 'tmp/' + id + '/' + filename)

def getFileUrlFromId(id, filename):
  key = id + '/' + filename
  url = s3Client.generate_presigned_url(
    'get_object',
    Params={'Bucket': bucketName, 'Key': key},
    ExpiresIn=300)
  return url

def getFileUrlFromPath(path):
  key = path
  url = s3Client.generate_presigned_url(
    'get_object',
    Params={'Bucket': bucketName, 'Key': key},
    ExpiresIn=300)
  return url

def getFilesUrls(id):
  key = id
  files = list(bucket.objects.filter(Prefix=key))
  urls = []
  
  if not os.path.isdir('tmp/' + id):
    os.mkdir('tmp/' + id)

  for f in files:
    fileId = os.path.splitext(f.key)[0]
    fileId = fileId[-14:]
    filename = f.key.split("/",1)[1]
    ownerId = f.key.split("/",1)[0]
    urls.append({'id': fileId, 'ownerId': ownerId, 'filename': filename, 'url': getFileUrlFromPath(f.key)})
  return urls