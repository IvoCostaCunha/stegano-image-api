from flask import Blueprint, send_file
from datetime import datetime
import os

fileManager = Blueprint('fileManager', __name__)

def sendFile(filepath):
  return send_file(filepath, as_attachment = True)