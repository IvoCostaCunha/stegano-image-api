from flask import Blueprint, request, send_file
import uuid

from flask_jwt_extended import jwt_required

from app.scripts.lsb import useLsb
from app.scripts.aws import addToBucket, getFilesUrls, deleteFile, checkIfFileExist
from app.scripts.fileManager import sendFile

from app.constants.httpStatusCodes import *

files = Blueprint('files', __name__, url_prefix= '/api/0.1/files')

toAWS = []

@files.post('/download-request')
@jwt_required()
def download_request():
    filesId = request.json['filesId']
    userId = request.json['userId']

    toUploadToAWS = []

    for f in toAWS:
        if f['fileId'] == filesId:
            toUploadToAWS.append(f)

    if len(toUploadToAWS) > 0:
        urls = addToBucket(str(userId), toUploadToAWS)
        return { 'messages': 'Files are uploaded to AWS.', 'urls': urls}, HTTP_200_OK
    else:
        return { 'error': 'Files could not be uploaded to AWS.'}, HTTP_500_INTERNAL_SERVER_ERROR

@files.post('/upload')
@jwt_required()
def upload_files():
    requestFiles = request.files.items()

    filesUuid = str(uuid.uuid4())
    files = []

    for filename, file in requestFiles:
        files.append([filename, file])

    if(not len(files) > 0):
        return { 'error': 'Files not received'}, HTTP_400_BAD_REQUEST

    result = useLsb(files)

    for r in result:
        r['fileId'] = filesUuid
        toAWS.append(r)
    
    if(len(toAWS) > 0):
        return { 'message': 'Files signed with success.', 'download_id': filesUuid}, HTTP_200_OK
    else:
        return { 'error': 'Files could not be signed.'}, HTTP_500_INTERNAL_SERVER_ERROR
    
@files.post('/getfilesbyid')
@jwt_required()
def getFilesFromId():
    id = request.json['id']
    files = getFilesUrls(str(id))
    return {'message': 'URLs could be retrieved', 'files': files}

@files.post('/deletefile')
@jwt_required()
def deleteFiles():
    id = request.json['id']
    filename = request.json['filename']
    path = str(id) + '/' + filename
    checkIfFileExist(id, path)
    deleteFile(path)
    return {'message': 'File ' + filename + ' deleted.'}
    