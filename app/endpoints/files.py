from flask import Blueprint, request, send_file
import uuid

from app.scripts.lsb import useLsb
from app.scripts.aws import uploadToAWS

from app.constants.httpStatusCodes import *

files = Blueprint('files', __name__, url_prefix= '/api/0.1/files')

autorised_downloads = []

@files.post('/download-request')
def download_request():
    filesId = request.json['filesId']
    userId = request.json['userId']

    filesToSend = []

    for dl in autorised_downloads:
        if dl[0] == filesId:
            filesToSend.append([dl[1], dl[2]])

    if len(filesToSend) > 0:
        uploadToAWS(userId, filesToSend)
        print(filesToSend[0])
        return send_file(filesToSend[0][1], download_name = filesToSend[0][0])
    else:
        return { 'error': 'Files could not be retrived'}, HTTP_400_BAD_REQUEST

@files.post('/upload')
def upload_files():
    requestFiles = request.files.items()

    filesUuid = str(uuid.uuid4())
    files = []

    for filename, file in requestFiles:
        # print(filename, file)
        files.append([filename, file])

    result = useLsb(files)

    print(result)
    # if result[0]['confirmation']:
        # for files in result['signedPngFiles']:
        #     print(result['signedPngFiles'])
        #     for file in files:
        #         print(file[0])
        #         # autorised_downloads.append({'filesUuid': filesUuid, 'filename': f['filename'], 'signature': f['signature'], 'file': f['file']})
        #         # print(autorised_downloads)
        #     return { 'message': result['message'], 'download_id': filesUuid}, HTTP_200_OK
    # else:
    #     return { 'error': result['error']}, HTTP_400_BAD_REQUEST