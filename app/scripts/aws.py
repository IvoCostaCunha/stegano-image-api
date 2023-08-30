from flask import Blueprint

aws = Blueprint('aws', __name__)

def uploadToAWS(id, files):
    return 'hello'

def getFromAws(id):
    return 'dfff'