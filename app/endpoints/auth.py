from flask import Blueprint, request
from markupsafe import escape
import validators
import bcrypt
from datetime import datetime
import uuid

from app.constants.httpStatusCodes import *
from app.database import User, db

# bcrypt requires data encoded in bytes 
# this is done by encode('utf-8') to encode in bytes, and decode('utf-8') to get back a utf-8 value

auth = Blueprint('auth', __name__, url_prefix= '/api/0.1/auth')

distributedTokens = {}

def hashPassword(password):
    password = password.encode('utf-8')
    salt = bcrypt.gensalt(10)
    hashedPassword = bcrypt.hashpw(password, salt)
    return [salt.decode('utf-8'), hashedPassword.decode('utf-8')]

def verifyPassword(password, salt, dbHashPass):
    if(bcrypt.hashpw(password.encode('utf-8'), salt.encode('utf-8')).decode('utf-8') == dbHashPass):
        return True
    else:
        return False

@auth.post('/signup')
def signUp():
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']

    if(len(password) < 6):
        return {'error': 'Password is too short.'}, HTTP_400_BAD_REQUEST
    
    if(" " in username):
        return {'error': 'Username must be alphanumeric and not contain spaces.'}, HTTP_400_BAD_REQUEST
    
    if(not validators.email(email)):
        return {'error': 'Email is not valid.'}, HTTP_400_BAD_REQUEST
    
    if(User.query.filter_by(email = email).first() is not None):
        return {'error': 'Email is already in use.'}, HTTP_409_CONFLICT

    hashData = hashPassword(password)
    salt  = hashData[0]
    hashedPassword = hashData[1]

    user = User(username = username, email = email, salt = salt, hashpass = hashedPassword)
    db.session.add(user)
    db.session.commit()


    return {
            'message': 'User created with success.',
            'user': {
                'username': username,
                'email': email
            }
        }, HTTP_201_CREATED
    
@auth.post('/signin')
def signIn():
    email = request.json['email']
    password = request.json['password']

    user = User.query.filter_by(email = email).first()

    if(user is not None):
        dbHashedPassword = user.hashpass
        dbSalt = user.salt

        response = verifyPassword(password, dbSalt, dbHashedPassword)

        if(response):
            distributedTokens[user.id] = uuid.uuid4()
            
            return {
                'message': 'User authentified with success.',
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'created_at': user.created_at,
                'token': distributedTokens[user.id]
                }, HTTP_200_OK
        else:
            return {'error': 'User could not be authentified.'}, HTTP_401_UNAUTHORIZED
    else:
        return {'error': 'User not found.'}, HTTP_401_UNAUTHORIZED

@auth.post('/signout')
def signOut():
    id = request.json['id']
    
    if(id not in distributedTokens.keys()):
        return {'error': 'Id unidentified in API array of connected users.'}, HTTP_400_BAD_REQUEST
    else:
        distributedTokens.pop(id)
        message = 'User with id %s disconnected.'%(id)
        return {'message': message}, HTTP_200_OK

@auth.post('/verifytoken')
def verifyToken():
    id = request.json['id']
    token = request.json['token']

    if(id in distributedTokens.keys() and uuid.UUID(token) == distributedTokens[id]):
        return {'message': 'User token verified.'}, HTTP_200_OK
    else:
        return {'error': 'User token could not be verified.'}, HTTP_401_UNAUTHORIZED