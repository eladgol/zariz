from firebase_admin import auth
from models import UserFirebaseDB, Workers, BusyEvent
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from urlparse import urlparse
from os.path import splitext, basename
import time
import urllib
import os
from django.core.files import File
from imageDownload import downloadImageToBuff

def fbAuthenticate(userToken):
    try:
        decodedToken = auth.verify_id_token(userToken)
        uid = decodedToken['uid']
        userSession =  auth.get_user(uid)
        try:
            photoFileName = getPhotoFileName(userSession.photo_url, 
                userSession.display_name, decodedToken[u'firebase']['sign_in_provider'])
        except Exception as e:
            pass
        
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

def downoladPhoto(url, sFileName, worker, agcs):
    try:
        buff, contentType, ContentLength = downloadImageToBuff(url)
        uploadBlob(sFileName, buff, contentType)
    except Exception as e:
        print(str(e))
    return sFileName

def uploadBlob(sFileName, buff, contentType, agcs):
    try:
        url = agcs.upload_blob(sFileName, buff, contentType)
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
    try:
        user = User.objects.get(username=username)
    except Exception as e:
        print(str(e))
        return None
    try:
        worker = Workers.objects.filter(userID__username=username)
    except Exception as e:
        bCreateWorker = True

    if bCreateWorker or len(worker) == 0:
        try:
            worker = Workers(userID=user)
            worker.save()
            return worker
        except Exception as e:
            print(str(e))
            return None

    return worker[0]