#from firebase_admin import auth
import logging
from models import UserFirebaseDB, Workers, BusyEvent, Bosses, Jobs, NotficationMessages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from urlparse import urlparse
from os.path import splitext, basename
import time
import urllib
import os
from django.core.files import File
from imageDownload import downloadImageToBuff
import base64
import uuid
import json
import ast
#from accessGoogleCloudStorage import *
def fbAuthenticate(userToken):
    try:
        decodedToken = auth.verify_id_token(userToken)
        uid = decodedToken['uid']
        userSession =  auth.get_user(uid)
        try:
            photoFileName = getPhotoFileName(userSession.photo_url, 
                userSession.display_name, decodedToken[u'firebase']['sign_in_provider'])
        except Exception as e:
            photoFileName = ""
            photoURL= ""
        
    except auth.AuthError as exc:
        if exc.code == 'ID_TOKEN_REVOKED':
            payload = {'success': False, 'redirectUrl' : 'ReInitalizeToken'}
        else:
            # Token is invalid
            payload = {'success': False, 'redirectUrl' : 'InvalidToken'}
    
    payload = {'success': True, 'userEmail' : userSession.email, 'photoURL' : userSession.photo_url, 'photoFileName' : photoFileName}
    
    return payload

def getPhotoFileName(url, username, provider_id):
    disassembled = urlparse(url)
    filename, file_ext = splitext(basename(disassembled.path))
    sFileName = '{}_{}_{}.{}'.format(username, provider_id, time.time(), file_ext)
    return sFileName

def downoladPhotoAndSaveToWorker(url, sFileName, worker):
    try:
        buff, contentType, ContentLength = downloadImageToBuff(url)
        worker.photoAGCSPath = uploadBlob(sFileName, buff, contentType)
        worker.save()
    except Exception as e:
        print(str(e))
    return sFileName

def uploadBlob(sFileName, buff, contentType):
    try:
        url = upload_blob(sFileName, buff, contentType)
    except Exception as e:
        print(str(e))
    return url
    
def updateFireBaseDB(userEmail):
    try:
        fbUser = UserFirebaseDB.objects.get(fireBaseUser=userEmail)
    except:
        fbUser = UserFirebaseDB(fireBaseUser=userEmail, localUser=userEmail, localPassword="zariz001", userID=None)
        fbUser.save()
    try:
        user = User.objects.get(username=fbUser.localUser)
    except Exception as e:
        user = User.objects.create_superuser(userEmail, userEmail, 'zariz001')
        user.save()
        fbUser.userID = user
        fbUser.save()
    return fbUser

def createUser(request, localUser, localPassword, localEmail):
    bNewUser = True
    payload = {"success" : "false"}
    try:
        user = User.objects.get(username=localUser)
        logging.info("User {} already exists".format(localUser))
        bNewUser = False
    except Exception as e:
        try:
            logging.info("New User?? {}".format(e.message))
            user = User.objects.create_superuser(localUser, localEmail, localPassword)
            
        except Exception as e2:
            logging.info("Had problems creating superuser - {}".format(e.message))
        try:
            user.save()
        except Exception as e2:
            logging.info("Unable to save user - {}".format(e.message))
    if bNewUser:
        payload = authenticateUser(request, localUser, localPassword)   
        payload['isNewUser'] = 'true'
        payload['success'] = 'true' 
    else:
        payload['isNewUser'] = 'false'
        payload['success'] = 'true' 
    return payload

def authenticateUser(request, localUser, localPassword):
    userAuth = authenticate(username = localUser, password = localPassword)
    payload = {'success': True}
    if userAuth is not None:
        if userAuth.is_active:
            login(request, userAuth)
        else:
            print('{} not active'.format(localUser))
            payload = {'success': False, 'error': '{} not active'.format(localUser)}
    else:
        sErr = 'Authentication failed for {}'.format(localUser)
        print(sErr)
        payload = {'success': False, 'error': sErr}

    return payload

def getWorker(username):
    bCreateWorker =False
    #print("Start getWorker for {}".format(username))
    try:
        user = User.objects.get(username=username)
    except Exception as e:
        print(str(e))
        return None
    try:
        worker = Workers.objects.filter(userID__username=username)
    except Exception as e:
        bCreateWorker = True
        print("will create worker for {}".format(username))
    if bCreateWorker or len(worker) == 0:
        try:
            worker = Workers(userID=user)
            worker.save()
            return worker
        except Exception as e:
            print(str(e))
            return None
    print("END getWorker for {}, worker userID {}".format(username, worker[0].userID))
    return worker[0]

def getBoss(username):
    bCreateBoss =False
    print("Start getBoss for {}".format(username))
    try:
        user = User.objects.get(username=username)
    except Exception as e:
        print(str(e))
        return None
    try:
        Boss = Bosses.objects.filter(userID__username=username)
    except Exception as e:
        bCreateBoss = True
        print("will create Boss for {}".format(username))
    if bCreateBoss or len(Boss) == 0:
        try:
            Boss = Bosses(userID=user)
            Boss.save()
            return Boss
        except Exception as e:
            print(str(e))
            return None
    print("END getBoss for {}, Boss userID {}".format(username, Boss[0].userID))
    return Boss[0]
