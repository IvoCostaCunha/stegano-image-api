from flask import Flask
from flask_cors import CORS
import os

from app.endpoints.auth import auth
from app.endpoints.files import files
from app.endpoints.user import user

from app.scripts.fileManager import fileManager
from app.scripts.lsb import lsb
from app.scripts.aws import aws

from app.database import db

# Done with https://www.youtube.com/watch?v=WFzRy8KVcrM

def create_app(test_config = None):
    
  app = Flask(__name__, instance_relative_config = True)
  CORS(app)
  #app.config['CORS_HEADERS'] = 'Content-Type'
    
  # Since Heroku auto updates with postgres://
  uri = os.getenv("DATABASE_URL")
  if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

  if test_config is None:
    app.config.from_mapping(
      SECRET_KEY = os.environ.get("SECRET_KEY"),
      SQLALCHEMY_DATABASE_URI = uri, #os.environ.get("SQLALCHEMY_DATABASE_URI"),
      SQLALCHEMY_TRACK_MODIFICATIONS = False,
      CORS_HEADERS = 'Content-Type'
    )
    
  else:
    app.config.from_mapping(test_config)

  db.app = app
  db.init_app(app)
  
  app.register_blueprint(fileManager)
  app.register_blueprint(lsb)
  app.register_blueprint(aws)

  app.register_blueprint(auth)
  app.register_blueprint(files)
  app.register_blueprint(user)
 
  return app