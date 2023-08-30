from flask import Blueprint, request
from markupsafe import escape
import validators

from app.database import User, db

from app.constants.httpStatusCodes import *

user = Blueprint('user', __name__, url_prefix= '/api/0.1/user')

@user.get('/id/<id>')
def getUser(id):
    id = escape(id)

    user =  User.query.filter_by(id = id).first()

    if(user is not None):
        return {
            'message': 'User data retrieved with success.',
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'created_at': user.created_at
            }
            }, HTTP_200_OK
    else:
        return {'error': 'User with id %s could not be found.'%(id)}, HTTP_400_BAD_REQUEST
    
@user.post('/updateuser')
def updateUser():
    id = request.json['id']
    username = request.json['username']
    email = request.json['email']

    if(" " in username):
        return {'error': 'Username must be alphanumeric and not contain spaces.'}, HTTP_400_BAD_REQUEST
    
    if(not validators.email(email)):
        return {'error': 'Email is not valid.'}, HTTP_400_BAD_REQUEST
    
    if(User.query.filter(email == email, id != id).first() is not None):
        return {'error': 'Email is already in use.'}, HTTP_409_CONFLICT

    user =  User.query.filter_by(id = id).first()

    if(user is not None):
        user.username = username
        user.email = email
        db.session.commit()
        return {'message': 'User updated with success.'}, HTTP_200_OK
    else:
        return {'error': 'User with id %scould not be found.'%(id)}, HTTP_400_BAD_REQUEST