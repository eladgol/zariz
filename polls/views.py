# -*- coding: utf-8 -*-
# Copyright 2015 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import unicode_literals

########################################################################
# this is required for firebase backend to work  -
#  according to - https://stackoverflow.com/questions/9604799/can-python-requests-library-be-used-on-google-app-engine/28544823#28544823
#from requests_toolbelt.adapters import appengine
#appengine.monkeypatch()
##################################################################
import ast
import codecs
import locale
import os
import base64
import uuid
import json

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.contrib.auth.models import User
import django.contrib.auth
import django.contrib.auth.views
from django.contrib.auth.decorators import login_required
#import urllib2
from django.template import loader
from django.utils.translation import gettext as _
from django.forms.models import model_to_dict

from polls.forms import BootstrapAuthenticationForm
from datetime import datetime
import sys
sys.path.append(os.path.dirname(__file__))
from polls.logic import *
from polls.models import UserFirebaseDB, Workers, BusyEvent, NotficationMessages
from django.utils import timezone
from django.core import serializers
from django.core.files.storage import FileSystemStorage
#from accessGoogleCloudStorage import *
from ZarizSettings import *
from django.views.decorators.csrf import csrf_exempt
import logging

from fcm_django.models import FCMDevice
d = FCMDevice.objects.all()
#locale.setlocale(locale.LC_ALL, '')
def _get_access_token():
    """
    get access token for firebase
    """
    import firebase_admin
    from firebase_admin import credentials
    cred = credentials.Certificate('..{}serviceAccountKey.json'.format(os.sep))
    access_token_info = credentials.get_access_token()
    return access_token_info.access_token

def pretty_print_POST(req):
    """
    At this point it is completely built and ready
    to be fired; it is "prepared".

    However pay attention at the formatting used in 
    this function because it is programmed to be pretty 
    printed and may differ from the actual request.
    """
    # logging.info('{}\n{}\n{}\n\n{}'.format(
    #     '-----------START-----------',
    #     req.method + ' ' + req.url,
    #     '\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
    #     req.body,
    # ))
    pass

@csrf_exempt
def index(request):
    #ptvsd.break_into_debugger()
    a = _("test")
    logging.info(a)
    #b = agcs_get()
    filename = "/bucket/test.txt"
    return django.contrib.auth.views.LoginView.as_view(
        template_name='loginGrid.html',
        authentication_form=BootstrapAuthenticationForm,
        # extra_context=
        # {
        #     'title': 'Log in',
        #     'year': datetime.now().year,
        # }
    )(request)
    # return render(
    #     request,
    #     'loginGrid.html')
    
@csrf_exempt
def loginFirebase(request):
    #ptvsd.break_into_debugger()
    return render(
        request,
        'loginFirebase.html',
        {}
    )
@csrf_exempt
def testlocallogin(request):
    # import ptvsd
    # ptvsd.break_into_debugger()
    return render(
        request,
        'testlocallogin.html',
        {}
    )
def function_checkemail(email):
    return True
from forms import FpasswordForm
#@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def fPassword(request):
    form = FpasswordForm(request.POST or None)
    #if form.is_valid():
    email = form.cleaned_data["email"]
    if function_checkemail(email):
        form.save(from_email='blabla@blabla.com', email_template_name='password_reset_email.html')
        print("EMAIL SENT")
    else:
        print("UNKNOWN EMAIL ADRESS")
        payload = {'success': True,}
    return JsonResponse(payload)

@csrf_exempt
def updateLocation(request):
    lat = request.POST.get('lat', None)
    lng = request.POST.get('lng', None)
    #radius = request.POST.get('radius', None)
    place = request.POST.get('place', None)
    try:
        worker = Workers.objects.get(userID=request.user.id)
    except Exception as e:
        worker = Workers(userID=request.user.id)
    worker.lat = float(lat)
    worker.lng = float(lng)
    #worker.radius = float(radius)
    worker.place = str(place)
    worker.save()

    payload = {'success': True,}
    return JsonResponse(payload)

@csrf_exempt
def updateDates(request):
    busyDate = request.POST.get('busyDate', None)
    busyTitle = request.POST.get('busyTitle', None)
    d = datetime.strptime(busyDate,'%Y-%m-%d')
    busyId = request.POST.get('busyId', None)
    sDo = request.POST.get('sDo', None)
    remove = {}
    add = []
    if 'Remove' in sDo:
        try:
            a = BusyEvent.objects.filter(eventID=busyId)
        except Exception as e:
            logging.info(str(e))   
        remove = {'start': busyDate, 'title':busyTitle,  'id' : busyId}
        a.delete()
    else:
        from datetime import time
        startTime = d.replace(hour=0,minute=0,second=0)
        endTime = d.replace(hour=23,minute=59,second=59)
        event = BusyEvent(userID=request.user, notes = busyTitle, start_date = startTime, end_date = endTime, eventID = busyId)
        add = {'start' : busyDate, 'title' : busyTitle, 'id' : busyId}
        event.save()

    
    payload = {'success': True, 'remove':remove, 'add':add}
    
    return JsonResponse(payload)

@csrf_exempt
def queryJob(request):
    jobID = request.POST.get('jobID', None)
    payload = {'success': True}
    try:
        job = Jobs.objects.get(jobID=jobID)
    except Exception as e:
        logging.info("queryJob - Failed no such job ID {}".format(jobID))
        return JsonResponse({'success': False, 'error' : 'no such jobID'})
    
    dRet = queryWorkersForJob(job)
    if not dRet["success"]:
        return JsonResponse(dRet)

    lWorkers=dRet["lWorkers"]
    
    payload['workers']=[model_to_dict(w) for w in lWorkers]
            
    logging.info("queryJob End, {}".format(payload))
    job.save()
    return JsonResponse(payload)

def queryWorkersForJob(job):
    try:
        lWorkers = []
        for w in Workers.objects.all():
            logging.info("queryJob - worker - {}, {}, {};".format(w.firstName, w.lastName, w.occupationFieldListString))
            if not checkModelHasAllFieldsFull(w,  ["Path", "radius", "wage"]):
                logging.info("queryJob - worker details not full, ignoring...")
                continue
            if job.occupationFieldListString in ast.literal_eval(w.occupationFieldListString):
                #try:
                #    job.workerID_sentNotification.get(pk=w.pk)
                #    logging.info("queryJob - Already added for {} {} to {}".format(w.firstName, w.lastName, jobID))
                #except Exception as e:
                #    lWorkers.append(w)
                lWorkers.append(w)
    except Exception as e:
        logging.info("queryJob - Some error for job ID {}, {}".format(jobID, str(e)))
        return {'success': False, 'error' : str(e)}
    return {'success': True, 'lWorkers' : lWorkers}

def SendHirePushNotifications(lWorkers, job):
    import urllib3
    http = urllib3.PoolManager()
    for w in lWorkers:
        logging.info("SendHirePushNotifications,  worker {}, {}".format(w.firstName, w.lastName))
        try:
            devices=FCMDevice.objects.filter(user=w.userID)
        except:
            return JsonResponse({'success' : False, 'error' : 'no devices are registered'})
        
        for device in devices:
            logging.info("SendHirePushNotifications, sending push notification to {}".format(device.registration_id))
            sendHirePushNotificationMessage(http, job, device, w)            

def SendFiredPushNotifications(lWorkers, job):
    import urllib3
    http = urllib3.PoolManager()
    for w in lWorkers:
        logging.info("SendFiredPushNotifications,  worker {}, {}".format(w.firstName, w.lastName))
        try:
            devices=FCMDevice.objects.filter(user=w.userID)
        except:
            return JsonResponse({'success' : False, 'error' : 'no devices are registered'})
        
        for device in devices:
            logging.info("SendFiredPushNotifications, sending push notification to {}".format(device.registration_id))
            sendFiredPushNotificationMessage(http, job, device, w)       
                 
def SendResignPushNotifications(lBosses, job):
    import urllib3
    http = urllib3.PoolManager()
    for b in lBosses:
        logging.info("SendResignPushNotifications,  boss {}, {}".format(b.firstName, b.lastName))
        try:
            devices=FCMDevice.objects.filter(user=b.userID)
        except:
            return JsonResponse({'success' : False, 'error' : 'no devices are registered'})
        
        for device in devices:
            logging.info("SendResignPushNotifications, sending push notification to {}".format(device.registration_id))
            sendResignedPushNotificationMessage(http, job, device, None)

def SendPushNotifications(lWorkers, job):
    import urllib3
    http = urllib3.PoolManager()
    for w in lWorkers:
        logging.info("SendPushNotifications, device loop, worker {}, {}".format(w.firstName, w.lastName))
        try:
            devices=FCMDevice.objects.filter(user=w.userID)
        except:
            return JsonResponse({'success' : False, 'error' : 'no devices are registered'})
        job.workerID_sentNotification.add(w)
        for device in devices:
            logging.info("SendPushNotifications, sending push notification to {}".format(device.registration_id))
            sendPushNotificationMessage(http, job, device, w)  
    job.save()          

@csrf_exempt
def confirmJob(request):
    jobID = request.POST.get('jobID', None)
    bAccepted = (request.POST.get('accepted', None)=='true') if request.POST.get('accepted', None) else False 
    
    try:
        worker = Workers.objects.get(userID=request.user.id)
    except Exception as e:
        logging.info("confirmJob  - Failed no such worker")
        return JsonResponse({"success" : False, "Error" : "no such Worker"})
    try:
        job = Jobs.objects.filter(jobID=jobID)
    except Exception as e:
        logging.info("confirmJob  - Failed no such job ID {}".format(jobID))
        return JsonResponse({"success" : False, "Error" : "no such JobID"})
    j=job.first()
    lResponded = [w for w in j.workerID_responded.all() if (w.userID == worker.userID)]
    lAccepted = [w for w in j.workerID_authorized.all() if (w.userID == worker.userID)]
    lHired = [w for w in j.workerID_hired.all() if (w.userID == worker.userID)]
    
    bAdded = False
    if len(lResponded)==0:
        j.workerID_responded.add(worker)
        if bAccepted:
            j.workerID_authorized.add(worker)
        j.save()
        payload = JsonResponse({"success" : True, 'Error' : 'accepted first time'})
        bAdded = True
    else:
        if bAccepted:
            if len(lAccepted)==0:
                j.workerID_authorized.add(worker)
                j.save()
                payload = JsonResponse({'success': True, 'Error' : 'accepted'})
                bAdded = True
            else:
                payload = JsonResponse({'success': True, 'Error' : 'confirmed already'})
        else:
            if len(lAccepted)!=0:
                j.workerID_authorized.remove(worker)
                if len(lHired)!=0:
                    j.workerID_hired.remove(worker)
                    j.save()
                    payload = JsonResponse({'success': True, 'Error' : 'changed to refused from hired'})
                    SendResignPushNotifications([j.bossID], j)
                else:
                    j.save()
                    payload = JsonResponse({'success': True, 'Error' : 'changed to refused from accepted'})
                bAdded = True
                
            else:
                if len(lHired)!=0:
                    j.workerID_hired.remove(worker)
                    j.save()
                    payload = JsonResponse({'success': True, 'Error' : 'changed to refused from hired'})
                    SendResignPushNotifications([j.bossID], j)
                else:
                    payload = JsonResponse({'success': True, 'Error' : 'refused'})
                 

    logging.info("confirmJob End, {}, worker {} {} to job {}, {} {}".format(payload.content, worker.firstName, worker.lastName, j.jobID, "updated to" if bAdded else "No change", "Accepted" if bAccepted else "Refused"))
    return payload

@csrf_exempt
def hire(request):
    jobID = request.POST.get('jobID', None)
    workerID = request.POST.get('workerID', None)
    bHired = (request.POST.get('accepted', None)=='true') if request.POST.get('accepted', None) else False 
    
    try:
        worker = Workers.objects.get(userID=workerID)
    except Exception as e:
        logging.info("hire  - Failed no such worker")
        return JsonResponse({"success" : False, "Error" : "no such Worker"}) 
    try:
        job = Jobs.objects.filter(jobID=jobID)
    except Exception as e:
        logging.info("hire  - Failed no such job ID {}".format(jobID))
        return JsonResponse({"success" : False, "Error" : "no such JobID"})
    j=job.first()
    
    payload = JsonResponse({"success" : True})
    lHired = [w for w in j.workerID_hired.all()]
    if bHired: 
        SendHirePushNotifications([worker], j)
    else:
        SendFiredPushNotifications([worker], j)
    logging.info("hire End, {}, worker {} {} {} job {}, length of hired {}".format(payload.content, worker.firstName, worker.lastName, 'hired to' if bHired else 'fired from', j.jobID, len(lHired)))
    return payload
@csrf_exempt
def confirmHire(request):
    jobID = request.POST.get('jobID', None)
    workerID = request.POST.get('workerID', None)
    bHired = (request.POST.get('accepted', None)=='true') if request.POST.get('accepted', None) else False 
    try:
        worker = Workers.objects.get(userID=workerID)
    except Exception as e:
        logging.info("hire  - Failed no such worker")
        return JsonResponse({"success" : False, "Error" : "no such Worker"}) 
    try:
        job = Jobs.objects.filter(jobID=jobID)
    except Exception as e:
        logging.info("hire  - Failed no such job ID {}".format(jobID))
        return JsonResponse({"success" : False, "Error" : "no such JobID"})
    j=job.first()
    if bHired:     
        j.workerID_hired.add(worker)      
    else:
        j.workerID_hired.remove(worker)
        j.workerID_authorized.remove(worker)

    j.save()
    payload = JsonResponse({"success" : True})
    
    logging.info("confirmHire End, {}, worker {} {} {} job {}, length of hired {}".format(payload.content, worker.firstName, worker.lastName, 'hired to' if bHired else 'fired from', j.jobID, len(j.workerID_hired.all())))
    return payload
@csrf_exempt
def updateAllInputsForm(request):
    firstName = request.POST.get('firstName', None)
    lastName = request.POST.get('lastName', None)
    place = request.POST.get('place', None)
    photoAGCSPath = request.POST.get('photoAGCSPath', None)
    wage = float(request.POST.get('wage', None)) if request.POST.get('wage', None) else None
    lat = float(request.POST.get('lat', None)) if request.POST.get('lat', None) else None
    lng = float(request.POST.get('lng', None)) if request.POST.get('lng', None) else None
    #radius = float(request.POST.get('radius', None)) if request.POST.get('radius', None) else None 
    lOccupationFieldListString = str(request.POST.get('lOccupationFieldListString', None).replace(']','').replace('[','').split(','))
    if lOccupationFieldListString == "['']":
        lOccupationFieldListString = ""
    try:
        worker = Workers.objects.get(userID=request.user.id)
    except Exception as e:
        worker = Workers(userID=request.user.id)
    bWorkerChanged = False
    if photoAGCSPath is not None and photoAGCSPath != '' and photoAGCSPath != worker.photoAGCSPath:
        splitVal = photoAGCSPath.split(',')
        if (len(splitVal > 1)):
            base64Val = splitVal[1]
            header64 = splitVal[0]
            file_ext = 'unknown'
            if 'jpeg' in header64:
                file_ext = 'jpeg'
            if 'jpg' in header64:
                file_ext = 'jpg'
            elif 'gif' in header64:
                file_ext = 'gif'
            elif 'png' in header64:
                file_ext = 'png'
            else:
                file_ext = header64[len(u'data:image/'):]

            buff = base64.b64decode(base64Val)

        sFileName = 'profile_pic_{}_{}_{}_.{}'.format(request.user.username, request.user.id, time.time(), file_ext)
        worker.photoAGCSPath = uploadBlob(sFileName, buff, header64)
        bWorkerChanged = True
    if firstName is not None and worker.firstName != firstName:
        worker.firstName = firstName
        bWorkerChanged = True
    if lastName is not None and worker.lastName != lastName:
        worker.lastName = lastName
        bWorkerChanged = True
    if place is not None and worker.place != place:
        worker.place = place
        bWorkerChanged = True
    # if radius is not None and worker.radius != radius:
    #     worker.radius = radius
    #     bWorkerChanged = True
    if wage is not None and worker.wage != wage:
        worker.wage = float(wage)
        bWorkerChanged = True
    if lat is not None and worker.lat != lat:
        worker.lat = float(lat)
        bWorkerChanged = True
    if lng is not None and worker.lng != lng:
        worker.lng = lng
        bWorkerChanged = True   
    if lOccupationFieldListString is not None and worker.occupationFieldListString != lOccupationFieldListString:
        worker.occupationFieldListString = lOccupationFieldListString
        bWorkerChanged = True
    try:
        user = User.objects.get(username=request.user)
    except Exception as e:
        logging.info("SHOULD NOT HAPPEN!!!!No user found - {}".format(e.message))
        return JsonResponse({"success" : False})
        
    bCheckAllFieldsFull = checkModelHasAllFieldsFull(worker, ["Path", "radius", "wage"])
    if bWorkerChanged:
        worker.save()
        payload = {'success': True, "detailsFull" : bCheckAllFieldsFull, 'firstName' : worker.firstName,
            'lastName' : worker.lastName, 'wage' : str(worker.wage), 'photoAGCSPath' : worker.photoAGCSPath, 'place': worker.place,
            # 'radius' : str(worker.radius),
            'lat' : str(worker.lat), 'lng' : str(worker.lng), 'userID' : str(user.id), 'email' : user.email, 
            'username' : user.username, 'lOccupationFieldListString' : str(worker.occupationFieldListString)}
        logging.info("updateAllInputsForm, success,  returning - {}".format(payload))
    else:
        payload = {'success': True, "detailsFull" : bCheckAllFieldsFull, 'Error' : 'no change', 'firstName' : worker.firstName,
            'lastName' : worker.lastName, 'wage' : str(worker.wage), 'photoAGCSPath' : worker.photoAGCSPath, 'place': worker.place,
            # 'radius' : str(worker.radius),
            'lat' : str(worker.lat), 'lng' : str(worker.lng), 'userID' : str(user.id), 'email' : user.email, 
            'username' : user.username, 'lOccupationFieldListString' : str(worker.occupationFieldListString)}
        logging.info("updateAllInputsForm, Error, call for nothing, no real change, returning - {}".format(payload))
    
    
    return JsonResponse(payload)

@csrf_exempt
def getAllJobsAsWorker(request):
    try:
        worker = Workers.objects.get(userID=request.user.id)
    except Exception as e:
        worker = Workers(userID=request.user.id)
    jobs = Jobs.objects.all()
    relevantJobList = []
    for j in jobs:
        lRelevant = [j for w in j.workerID_sentNotification.all() if (w.userID == worker.userID)]
        
        if len(lRelevant)!=0:
            relevantJobList.append(j)
        elif workerJobMatch(worker, j):
            relevantJobList.append(j)
            j.workerID_sentNotification.add(worker.workerID)
            j.save()

    d = {'success': True}
    i=0
    
    for job in relevantJobList:
        d['{}'.format(i)] = {}
        d['{}'.format(i)]['JobDetails']=model_to_dict(job)
        del d['{}'.format(i)]['JobDetails']['workerID_sentNotification']
        del d['{}'.format(i)]['JobDetails']['workerID_authorized']
        del d['{}'.format(i)]['JobDetails']['workerID_hired']
        del d['{}'.format(i)]['JobDetails']['workerID_responded']
        d['{}'.format(i)]['BossDetails']=model_to_dict(job.bossID)
        lAuthorized = [w for w in job.workerID_authorized.all() if (w.userID == worker.userID)]
        bAuthorized = len(lAuthorized)!=0
        lResponded = [w for w in job.workerID_responded.all() if (w.userID == worker.userID)]
        bResponded = len(lResponded)!=0
        lHired = [w for w in job.workerID_hired.all() if (w.userID == worker.userID)]
        bHired = len(lHired)!=0
        d['{}'.format(i)]['bAuthorized'] = bAuthorized
        d['{}'.format(i)]['bResponded'] = bResponded
        d['{}'.format(i)]['bHired'] = bHired
        i=i+1
    
    return JsonResponse(d)

@csrf_exempt
def getAllJobsAsBoss(request):
    try:
        Boss = Bosses.objects.get(userID=request.user.id)
    except Exception as e:
        Boss = Bosses(userID=request.user.id)
    
    jobs = Jobs.objects.filter(bossID=Boss)
    d = {'success': True}
    i=0
    for job in jobs:
        d['{}'.format(i)]=model_to_dict(job)
        d['{}'.format(i)]['workerID_responded']=[]
        for w in job.workerID_responded.all():
            d['{}'.format(i)]['workerID_responded'].append(w.workerID)
        d['{}'.format(i)]['workerID_authorized']=[]
        for w in job.workerID_authorized.all():
            d['{}'.format(i)]['workerID_authorized'].append(w.workerID)
        d['{}'.format(i)]['workerID_sentNotification']=[]
        for w in job.workerID_sentNotification.all():
            d['{}'.format(i)]['workerID_sentNotification'].append(w.workerID)
        d['{}'.format(i)]['workerID_hired']=[]
        for w in job.workerID_hired.all():
            d['{}'.format(i)]['workerID_hired'].append(w.workerID)
        i=i+1
    
    return JsonResponse(d)

@csrf_exempt
def deleteJobAsBoss(request):
    jobID = request.POST.get('jobID', None)
    try:
        job = Jobs.objects.get(jobID=jobID).delete()
    except Exception as e:
        logging.info("deleteJobAsBoss - Failed no such job ID {}".format(jobID))
        return JsonResponse({"success" : False, "Error" : "no such JobID"})
    logging.info("deleteJobAsBoss - Deleted job ID {}".format(jobID))
    return JsonResponse({'success': True})

def sendEmail(request):
    email =  request.POST.get('email')
    logging.info("updateJobAsBoss - sendEmail, with {}".format(email))
    try:
        sendEmailDjango(email)
    except Exception as e:
        print("sendEmail, Exception {}".format(e))
def loadFacebookKeys():
    keysDir  = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))
    keysFile = "{}{}FacebookKeys.json".format(keysDir, os.sep)
    logging.info("Accessing {}".format(keysFile))
    with open(keysFile) as f:
        data = json.load(f)
    return data
    

import requests as rq
def generateAppToken(appId, appSecret):
    # generate app token
    sURLGenerateAppToken = "https://graph.facebook.com/oauth/access_token?client_id={}&client_secret={}&grant_type=client_credentials".format(appId, appSecret)
    logging.info("fb_login, sURLGenerateAppToken {}".format(sURLGenerateAppToken))
    response = rq.get(sURLGenerateAppToken)
 
    return response

@csrf_exempt
def fb_login(request):
    keys = loadFacebookKeys()
    logging.info("fb_login, {}".format(request.POST))
    payload = {}
    response = generateAppToken(keys["AppId"], keys["AppSecret"])
    if (response.status_code > 400):
        payload['success'] = False
        payload['error'] = str(response.status_code)
        return JsonResponse(payload)
    # validate user token against app token
    access_token =  json.loads(str(response.content.decode("utf-8")))['access_token']
    sValidateUrl = 'https://graph.facebook.com/debug_token?input_token={}&access_token={}'.format(access_token, request.POST["token"])
    logging.info("fb_login, sValidateUrl {}".format(sValidateUrl))
    response = rq.get(sValidateUrl)
    if (response.status_code > 400):
        payload['success'] = False
        payload['error'] = str(response.status_code)
        return JsonResponse(payload)
        
    bIsValid = False
    data =json.loads(str(response.content.decode("utf-8")))['data']

    if data['is_valid'] and data['app_id']==str(keys["AppId"]):
        try:
            # get details from facebook
            sDetailsURL = 'https://graph.facebook.com/me?fields=id,first_name,last_name,email,picture.type(large)&access_token={}'.format(request.POST["token"])
            graphResponse = rq.get(sDetailsURL)
            if (graphResponse.status_code > 400):
                payload['success'] = False
                payload['error'] = str(response.status_code)
                return JsonResponse(payload)
            logging.info("URL - {}".format(sDetailsURL))
            logging.info("graphResponse - {}".format(graphResponse.content))
            userData = json.loads(str(graphResponse.content.decode("utf-8")))
            sPicutreURL = "http://graph.facebook.com/{}/picture?type=small&redirect=true&width={}&height={}".format(userData["id"], pictureWidth, pictureHeight)
            loginByEmail(request, userData["email"])
            updateDetailsFromSocial(userData, sPicutreURL)
        except Exception as e:
            logging.info("fb_login, 0, {}".format(e))
        
        bIsValid = True
        
    payload = {'success': bIsValid}
    return JsonResponse(payload)

from google.oauth2 import id_token
from google.auth.transport import requests
@csrf_exempt
def google_login(request):
    logging.info("google_login, {}".format(request.POST))
    payload = {'success': False}
    token = request.POST["token"]
    id = request.POST["id"]
    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request())
    except ValueError as e:
        logging.warn("google_login, Invalid token - {}".format(e))
        return JsonResponse(payload)
    except Exception as e:
        logging.warn("google_login, exception - {}".format(e))
        return JsonResponse(payload)
    try:
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            logging.warn("google_login, Wrong issuer")
        else:
            payload['success'] = True
            payload['first_Name'] = idinfo['given_name']
            payload['last_Name'] = idinfo['family_name']
            sPicutreURL = idinfo['picture']
            payload['email'] = idinfo['email']
            loginByEmail(request, payload["email"])
            updateDetailsFromSocial(payload, sPicutreURL)
    except Exception as e:
        logging.warn("google_login, 2, exception - {}".format(e))
            
    return JsonResponse(payload)

def updateDetailsFromSocial(payload, sPicutreURL):
    worker = getWorker(payload["email"])
    worker.firstName = payload["first_name"] if Workers._meta.get_field('firstName').get_default() == worker.firstName else worker.firstName
    worker.lastName = payload["last_name"] if Workers._meta.get_field('lastName').get_default() == worker.lastName else worker.lastName
    pictureWidth = pictureHeight = 240
    worker.photoAGCSPath = sPicutreURL#userData["picture"]["data"]["url"] if Workers._meta.get_field('photoAGCSPath').get_default()  == worker.photoAGCSPath else worker.photoAGCSPath
    worker.save()
    boss = getBoss(payload["email"]) 
    boss.firstName = payload["first_name"]  if Bosses._meta.get_field('firstName').get_default()  == boss.firstName else boss.firstName
    boss.lastName = payload["last_name"]  if Bosses._meta.get_field('lastName').get_default() == boss.lastName else boss.lastName
    boss.photoAGCSPath = sPicutreURL#userData["picture"]["data"]["url"] # if Bosses._meta.get_field('photoAGCSPath').get_default() == boss.photoAGCSPath else boss.photoAGCSPath
    boss.save()
@csrf_exempt
def updateJobAsBoss(request):
    discription = request.POST.get('discription', None)
    
    place = request.POST.get('place', None)
    lat = float(request.POST.get('lat', None)) if request.POST.get('lat', None) else None
    lng = float(request.POST.get('lng', None)) if request.POST.get('lng', None) else None
    wage = float(request.POST.get('wage', None)) if request.POST.get('wage', None) else None
    nWorkers = float(request.POST.get('nWorkers', None)) if request.POST.get('nWorkers', None) else None
    occupationFieldListString = request.POST.get('lOccupationFieldListString', '') # toDo: change to support multiple occupations per Job
    bNewJob = False
    jobID = request.POST.get('jobID', None)
    logging.info("updateJobAsBoss - jobID {}, discription - {}, place {}, lat {}, lng {}, wage {}, occupationFieldListString {}".
            format(jobID, discription, place, lat, lng, wage, occupationFieldListString))
    
    try:
        Boss = Bosses.objects.get(userID=request.user.id)
    except Exception as e:
        Boss = Bosses(userID=request.user.id)

    if jobID == '-1':
        Job = Jobs(bossID=Boss)
        bNewJob = True
        logging.info("updateJobAsBoss - Created new job id - {}".format(Job.jobID))
    else:
        try:
            Job = Jobs.objects.get(jobID=jobID, bossID=Boss)
            bNewJob = False
            logging.info("updateJobAsBoss - Existing job id - {}".format(Job.jobID))
        except Exception as e2:
            Job = Jobs(bossID=Boss)
            bNewJob = True
            logging.info("updateJobAsBoss - Created new job id - {}".format(Job.jobID))
    if (bNewJob or [Job.discription, Job.place, Job.lat, Job.lng, Job.wage, Job.nWorkers, Job.occupationFieldListString] 
        != [discription, place, lat, lng, wage, nWorkers, occupationFieldListString]):
        Job.discription = discription
        Job.place = place
        Job.lat = lat
        Job.lng = lng
        Job.wage = wage
        Job.nWorkers = nWorkers
        Job.bossID=Boss
        Job.occupationFieldListString = occupationFieldListString
        Job.workerID_responded.clear()
        Job.workerID_authorized.clear()
        Job.workerID_sentNotification.clear()
        Job.workerID_hired.clear()
        bDetailsFull = checkModelHasAllFieldsFull(Job, ['lat', 'lng', 'wage', 'nWorkers'])
        if not bDetailsFull:
            payload = {'success': False, 'error' : 'details not full'}
        else:
            Job.save()
            
            
            payload = {'success': True, 'jobID': "{}".format(Job.jobID), 'discription' : "{}".format(discription), 'place' : "{}".format(place), 
                'lat' : "{}".format(lat), 'lng' : "{}".format(lng), 'wage' : "{}".format(wage), 'nWorkers' : "{}".format(nWorkers), 'occupationFieldListString' : occupationFieldListString}
            logging.info("updateJobAsBoss - Saved Job, payload {}".format(payload))
            dRet = queryWorkersForJob(Job)
            if not dRet["success"]:
                return JsonResponse(dRet)

            lWorkers=dRet["lWorkers"]
            try:
                SendPushNotifications(lWorkers, Job)
            except Exception as e:
                logging.info("updateJobAsBoss, exception on send push notitification - {}".format(e.message))
  
    else:
        payload = {'success': True, 'Error' : 'no change', 'jobID': "{}".format(Job.jobID), 'discription' : "{}".format(discription), 'place' : "{}".format(place), 
            'lat' : "{}".format(lat), 'lng' : "{}".format(lng), 'wage' : "{}".format(wage), 'nWorkers' : "{}".format(nWorkers), 'occupationFieldListString' : occupationFieldListString}
        logging.info("updateJobAsBoss - No change, payload {}".format(payload))
    return JsonResponse(payload)

@csrf_exempt
def updateAllBossInputsForm(request):
    firstName = request.POST.get('firstName', None)
    lastName = request.POST.get('lastName', None)
    buisnessName = request.POST.get('buisnessName', None)
    place = request.POST.get('place', None)
    photoAGCSPath = request.POST.get('photoAGCSPath', None)
    
    lat = float(request.POST.get('lat', None)) if request.POST.get('lat', None) else None
    lng = float(request.POST.get('lng', None)) if request.POST.get('lng', None) else None
    

    try:
        Boss = Bosses.objects.get(userID=request.user.id)
    except Exception as e:
        Boss = Bosses(userID=request.user.id)
    bBossChanged = False
    
    if firstName is not None and Boss.firstName != firstName:
        Boss.firstName = firstName
        bBossChanged = True
    if lastName is not None and Boss.lastName != lastName:
        Boss.lastName = lastName
        bBossChanged = True
    if place is not None and Boss.place != place:
        Boss.place = place
        bBossChanged = True
    if buisnessName is not None and Boss.buisnessName != buisnessName:
        Boss.buisnessName = buisnessName
        bBossChanged = True
   
    if lat is not None and Boss.lat != lat:
        Boss.lat = float(lat)
        bBossChanged = True
    if lng is not None and Boss.lng != lng:
        Boss.lng = lng
        bBossChanged = True    
    try:
        user = User.objects.get(username=request.user)
    except Exception as e:
        logging.info("SHOULD NOT HAPPEN!!!!No user found - {}".format(e.message))
        return JsonResponse({"sucess" : False})
    
    bCheckAllFieldsFull = checkModelHasAllFieldsFull(Boss, ["Path", "radius", "wage"])
    
    if bBossChanged:
        Boss.save()
        payload = {'success': True, 'firstName' : Boss.firstName,
            'lastName' : Boss.lastName, "detailsFull" : bCheckAllFieldsFull, 'photoAGCSPath' : Boss.photoAGCSPath, 'place': Boss.place,
            'lat' : "{}".format(Boss.lat), 'lng' : "{}".format(Boss.lng), 'userID' : "{}".format(user.id), 'email' : user.email, 
            'username' : user.username}
        logging.info("updateAllBossInputsForm, success,  returning - {}".format(payload))
    else:
        payload = {'success': True, 'Error' : 'no change', 'firstName' : Boss.firstName,
            'lastName' : Boss.lastName, "detailsFull" : bCheckAllFieldsFull, 'photoAGCSPath' : Boss.photoAGCSPath, 'place': Boss.place,
            'lat' : "{}".format(Boss.lat), 'lng' : "{}".format(Boss.lng), 'userID' : "{}".format(user.id), 'email' : user.email, 
            'username' : user.username}
        logging.info("updateAllBossInputsForm, Error, call for nothing, no real change, returning - {}".format(payload))
    payload["detailsFull"] = checkModelHasAllFieldsFull(Boss, ["Path", "radius", "wage"])
    return JsonResponse(payload)


@csrf_exempt
def updateInputForm(request):
    name = request.POST.get('name', None)
    value = request.POST.get('value', None)

    try:
        worker = Workers.objects.get(userID=request.user.id)
    except Exception as e:
        worker = Workers(userID=request.user.id)

    if 'photoAGCSPath' in name:
        splitVal = value.split(',')
        base64Val = splitVal[1]
        header64 = splitVal[0]
        file_ext = 'unknown'
        if 'jpeg' in header64:
            file_ext = 'jpeg'
        elif 'gif' in header64:
            file_ext = 'gif'
        elif 'png' in header64:
            file_ext = 'png'
        else:
            file_ext = header64[len(u'data:image/'):]

        buff = base64.b64decode(base64Val)

        sFileName = 'profile_pic_{}_{}_.{}'.format(request.user.username, time.time(), file_ext)
        worker.photoAGCSPath = uploadBlob(sFileName, buff, header64)

    elif 'firstName' in name:
        worker.firstName = value
    elif 'lastName' in name:
        worker.lastName = value
    elif 'wage' in name:
        worker.wage = float(name)
    worker.save()
    payload = {'success': True, 'firstName' : worker.firstName,
     'lastName' : worker.lastName, 'wage' : worker.wage, 'photoAGCSPath' : worker.photoAGCSPath}
    return JsonResponse(payload)

@csrf_exempt

def registerDevice(request):
    logging.info("registerDevice, start")
    name = request.POST.get('name', "")
    deviceType = request.POST.get('type', "")
    reg_id = request.POST.get('token', None)
    device_id = request.POST.get('id', None)
    if reg_id is None or device_id is None:
        logging.info("registerDevice, missing reg_id or device_id")
        return JsonResponse({'success': False, 'error':'missing reg_id or device_id'})
    try:
        device = FCMDevice.objects.get(user=request.user, device_id=device_id)
        logging.info("registerDevice, already registered device")
    except Exception as e:
        device = FCMDevice(user=request.user, device_id=device_id)
        logging.info("registerDevice, added device")
    
    device.registration_id = reg_id
    device.type = deviceType
    device.name = name
    device.save()
    return JsonResponse({'success': True})

@csrf_exempt
def updateOccupation(request):
    occupaitonList = request.POST.getlist('occupationList[]', None)
    logging.info(occupaitonList)
    # does user exist
    try:
        worker = Workers.objects.get(userID=request.user.id)
    except Exception as e:
        worker = Workers(userID=request.user.id)
    worker.occupationFieldListString = str(occupaitonList)
    worker.save()
    payload = {'success': True}
    return JsonResponse(payload)

@csrf_exempt
def localLogin(request):
    pretty_print_POST(request)
    localUser = request.POST.get('localUser', None)
    localPassword = request.POST.get('localPassword', None)
    try:
        payload = authenticateUser(request, localUser, localPassword) 
    except Exception as e:
        logging.warn("localLogin, login failed, {}".format(e))
        payload = {'success': False, 'error': str(e)}
    if payload['success']:
        payload['redirectUrl'] = 'accounts/profile/'
        worker = getWorker(request.user.username)
        if worker.photoAGCSPath is '' and 'photoURL' in payload and payload['photoURL']!='':
            logging.info('saving {} -> {}'.format(payload['photoURL'], payload['photoFileName']))
            downoladPhotoAndSaveToWorker(payload['photoURL'], payload['photoFileName'], worker)
    logging.info("localLogin, Login payload result {} for {}, {}".format(payload, localUser, request.user.username))
    return JsonResponse(payload)

@csrf_exempt
def signUp(request):
    pretty_print_POST(request)
    logging.info("Hello!!!!!!")
    localUser = request.POST.get('localUser', None)
    localPassword = request.POST.get('localPassword', None)
    localEmail = request.POST.get('localEmail', None)
    payload = createUser(request, localUser, localPassword, localEmail) 
    if payload['success']:
        payload['redirectUrl'] = 'accounts/profile/'
        worker = getWorker(request.user.username)
        if worker is not None:
            if worker.photoAGCSPath is '' and 'photoURL' in payload and payload['photoURL']!='':
                logging.info('saving {} -> {}'.format(payload['photoURL'], payload['photoFileName']))
                downoladPhotoAndSaveToWorker(payload['photoURL'], payload['photoFileName'], worker)

    return JsonResponse(payload)

@csrf_exempt
def firebaseSuccess(request):
    userToken = request.GET.get('userToken', None)
    payload = fbAuthenticate(userToken)
    if not payload['success']:
        return JsonResponse(payload)

    userEmail = payload['userEmail'] 
    logging.info('email - {}, token - {}'.format(userEmail, userToken)) 

    fbUser = updateFireBaseDB(userEmail)

    res = authenticateUser(request, fbUser.localUser, fbUser.localPassword) 
    if res['success']:
        payload2 = {'success': True, 'redirectUrl' : 'accounts/profile/'}
    else:
        payload2 = {'success': True, 'redirectUrl' : 'accounts/profile/'}

    worker = getWorker(request.user.username)
    if worker.photoAGCSPath is '' and payload['photoURL']!='':
        logging.info('saving {} -> {}'.format(payload['photoURL'], payload['photoFileName']))
        downoladPhotoAndSaveToWorker(payload['photoURL'], payload['photoFileName'], worker)


    return JsonResponse(payload2)

@csrf_exempt   
@login_required(login_url="/login/")
def profilePage(request):
    # worker = getWorker(request.user.username)
    # dWorker = model_to_dict(worker)
    # return render(
    #     request,
    #     'demoForm2.html',
    #     dWorker
    # )
    return carousel(request)


@csrf_exempt
@login_required(login_url="/carousel/")
def carousel(request):

    worker = getWorker(request.user.username)
    d = model_to_dict(worker)

    possibleFields, pickedFields = getOccupationDetails(request)
    d['fields'] = possibleFields
    d['picked'] = pickedFields
    
    d['busyDates'] = []
    try:
        busyEvents = BusyEvent.objects.filter(userID=request.user.id)
        d['busyDates'] = [(b.start_date.strftime('%Y-%m-%d'), b.notes, b.eventID) for b in busyEvents]
        if d['photoAGCSPath']=='':
            d['photoAGCSPath'] = 'https://storage.googleapis.com/zariz-204206.appspot.com/BlankProfile.png'
            
    except Exception as e:
        logging.info(e.message)
    return render(
        request,
        'Carousel.html',
        d
    )

@csrf_exempt
def getFieldDetails(request):
    pretty_print_POST(request)
    logging.info("getFieldDetails for {}".format(request.user.username))
    worker = getWorker(request.user.username)
    logging.info("getFieldDetails after getWorker")
    d = model_to_dict(worker)
    d["detailsFull"] = checkModelHasAllFieldsFull(worker, ["Path", "radius", "wage"])
    logging.info("getFieldDetails {}".format(d))
    return JsonResponse(d)

@csrf_exempt
def getWorkerDetailsForID(request):
    pretty_print_POST(request)
    id = request.POST.get('id', None)
    d={}
    logging.info("getWorkersDetailsForID for {}".format(request.user.username))
    try:
        worker = Workers.objects.get(pk=id)
    except Exception as e:
        logging.info("getWorkersDetailsForID Faild {}".format(e))
        return JsonResponse({'success':False})
    logging.info("getWorkersDetailsForID after getWorker")
    d = model_to_dict(worker)
    d['success']=True
    logging.info("getWorkersDetailsForID {}".format(d))
    return JsonResponse(d)
    
@csrf_exempt
def getBossFieldDetails(request):
    pretty_print_POST(request)
    logging.info("getBossFieldDetails for {}".format(request.user.username))
    Boss = getBoss(request.user.username)
    logging.info("getBossFieldDetails after getBoss")
    d = model_to_dict(Boss)
    d["detailsFull"] = checkModelHasAllFieldsFull(Boss, ["Path", "radius", "wage"])
    logging.info("getBossFieldDetails {}".format(d))
    return JsonResponse(d)

@csrf_exempt   
def getOccupationDetails(request):
    #locale.setlocale(locale.LC_ALL, '')
    #sData = codecs.open(os.path.dirname(__file__) + '/../'+ 'static/content/zarizSettings.json', encoding='utf-8').read()
    #data = ast.literal_eval(sData)
    sPossibleFields = ZarizSettingsDict['occupationFields']
    possibleFields = [s for s in sPossibleFields]
    pickedFields = []
    try:
        worker = Workers.objects.get(userID=request.user.id)
        occupaitonList = ast.literal_eval(worker.occupationFieldListString) if worker.occupationFieldListString!='' else []
        pickedFields = [s for s in occupaitonList if s in possibleFields]
    except Exception as e:
        pass
    return possibleFields, pickedFields

@csrf_exempt
def occupationPage(request):
    possibleFields, pickedFields = getOccupationDetails(request)
    # if (len(pickedFields) != len(occupaitonList))
    #     worker.occupationFieldListString = str(pickedFields)
   
    return render(
        request,
        'OccupationPick.html',
        {
             'fields' : possibleFields,
             'picked' : pickedFields
             #'fields' : data
        }
    )
@csrf_exempt
def occupationDetails(request):
    logging.info("occupationDetails, Start")
    possibleFields, pickedFields = getOccupationDetails(request)
    # if (len(pickedFields) != len(occupaitonList))
    #     worker.occupationFieldListString = str(pickedFields)
    j = JsonResponse({'success' : True, 'possibleFields' : str(possibleFields), 'pickedFields' : str(pickedFields)})
    logging.info("occupationDetails, Returning {}".format(j))
    return j
    

@csrf_exempt
def calander2(request):
    busyDates = []
    try:
        busyEvents = BusyEvent.objects.filter(userID=request.user.id)
        busyDates = [(d.start_date.strftime('%Y-%m-%d'), d.notes) for d in busyEvents]
    except Exception as e:
        logging.info(e.message)
    return render(
        request,
        'FullCalanderPick.html',
        {
            'busyDates' : busyDates
        }
    )

@csrf_exempt
def calander(request):
    # try:
    #     worker = Workers.objects.get(localUser=request.user.username)
    # except Exception as e:
    #     logging.info("Error")
    #     return JsonResponse({'error' : True})
    
    busyDates = []
    try:
        busyEvents = BusyEvent.objects.get(userID=request.user.id)
        busyDates = [d.value_to_string() for d in busyEvents]
    except:
        pass
    return render(
        request,
        'CalanderPick.html',
        {
            'busyDates' : busyDates
        }
    )

@csrf_exempt
def ShowWorkers(request):
    workers = Workers.objects.all()
    workerList = [w for w in workers]
    return render(
        request,
        'ShowWorkers.html',
        {
            'workers' : workerList
        }
    )

@csrf_exempt
def demoForm(request):
    return render(
        request,
        'demoForm.html',
        {}
    )

@csrf_exempt
def demoForm2(request):
    return render(
        request,
        'demoForm2.html',
        {}
    )

@csrf_exempt
def LocationForm(request):
    worker = getWorker(request.user.username)
    d = model_to_dict(worker)
    return render(
        request,
        'LocationForm.html',
        d
    )

@csrf_exempt
def notifyTest(request):
    return render(
        request,
        'notifyTest.html',
        {}
    ) 

@csrf_exempt
def dummy(request):
    return JsonResponse({})

import pdb
def ExportDB(request):
    logging.info("Hello")
    dataWorkers = str([str(w) for w in Workers.objects.values()])
    dataUsers = str([str(u) for u in User.objects.values()])
    data = str({'Workers' : dataWorkers, 'Users' : dataUsers})
    response = HttpResponse(data, content_type='text/plain')
    sFileName = "ZarizExportDB_" + str(time.time()) + ".json"
    response['Content-Disposition'] = 'attachment; filename="' + '"' + sFileName +'"'
    return response

from ast import literal_eval as leval
from django.template.base import Token
def LoadDBFromFile(request):
    if request.method == 'POST' and request.FILES['myfile']:
        f = request.FILES['myfile']
        
        for chunk in f:
            try:
                userList = leval(leval(chunk)['Users'])
                for u in userList:
                    pass
                workerList = leval(leval(chunk)['Workers'])
                for w in workerList:
                    pass                   
            except Exception as e:
                logging.info("Exception - {}".format(e))
        return render(request, 'ShowWorkers.html')
    return render(request, 'ShowWorkers.html')

def sendFiredPushNotificationMessage(http, job, device, w):
    bodyMessage="\n{}".format(job.discription)  
    bodyMessage="\n{} {} הוחלט שלא להעסיק אותך! מאת ".format(job.bossID.firstName, job.bossID.lastName)
    bodyMessage+="\n{} בשכר של".format(job.wage)
    bodyMessage+="\n{}ב".format(job.place)
    messageID = str(uuid.uuid4())
    body = {
        "to" : device.registration_id,
        "notification" : {        
                "body" : bodyMessage,
                "title" : "{} {}הוחלט שלא להעסיק אותך! מ ".format(job.bossID.firstName, job.bossID.lastName)
        },
        "priority": "high",
        "data": {
            "click_action": "FLUTTER_NOTIFICATION_CLICK",
            "id": messageID,
            "status": "done",
            "firstName" : job.bossID.firstName,
            "lastName" : job.bossID.lastName,
            "wage" : job.wage,
            "place" : job.place,
            "jobID" : str(job.jobID),
            "discription" : job.discription,
            "message_status" : "Fired",
            "workerID" : str(w.userID.id),
        },
    }
    sendPushNotificationMessageGeneral(body, bodyMessage, http, job, device, w)

def sendResignedPushNotificationMessage(http, job, device, w):
    bodyMessage="\n{}".format(job.discription)  
    bodyMessage="\n{} {} הודעה על התפטרות מאת ".format(job.bossID.firstName, job.bossID.lastName)
    bodyMessage+="\n{} בשכר של".format(job.wage)
    bodyMessage+="\n{}ב".format(job.place)
    messageID = str(uuid.uuid4())
    
    body = {
        "to" : device.registration_id,
        "notification" : {        
                "body" : bodyMessage,
                "title" : "{} {}הודעה על התפטרות מ ".format( job.bossID.firstName, job.bossID.lastName)
        },
        "priority": "high",
        "data": {
            "click_action": "FLUTTER_NOTIFICATION_CLICK",
            "id": messageID,
            "status": "done",
            "firstName" : job.bossID.firstName,
            "lastName" : job.bossID.lastName,
            "wage" : job.wage,
            "place" : job.place,
            "jobID" : str(job.jobID),
            "discription" : job.discription,
            "message_status" : "Resigned",
            "workerID" : str(""),
        },
    }
    sendPushNotificationMessageGeneral(body, bodyMessage, http, job, device, None)


def sendHirePushNotificationMessage(http, job, device, w):
    bodyMessage="\n{}".format(job.discription)  
    bodyMessage="\n{} {} ברכות! התקבלת לעבודה מאת ".format(job.bossID.firstName, job.bossID.lastName)
    bodyMessage+="\n{} בשכר של".format(job.wage)
    bodyMessage+="\n{}ב".format(job.place)
    messageID = str(uuid.uuid4())
    sID = ""
    if w is not None:
        sID = str(w.userID.id)
    body = {
        "to" : device.registration_id,
        "notification" : {        
                "body" : bodyMessage,
                "title" : "{} {}ברכות! התקבלת לעבודה מ ".format(job.bossID.firstName, job.bossID.lastName)
        },
        "priority": "high",
        "data": {
            "click_action": "FLUTTER_NOTIFICATION_CLICK",
            "id": messageID,
            "status": "done",
            "firstName" : job.bossID.firstName,
            "lastName" : job.bossID.lastName,
            "wage" : job.wage,
            "place" : job.place,
            "jobID" : str(job.jobID),
            "discription" : job.discription,
            "message_status" : "Hired",
            "workerID" : sID,
        },
    }
    sendPushNotificationMessageGeneral(body, bodyMessage, http, job, device, w)

def sendPushNotificationMessage(http, job, device, w):
    bodyMessage="\n{}".format(job.discription)  
    bodyMessage="\n{} {} עבודה מאת".format(job.bossID.firstName, job.bossID.lastName)
    bodyMessage+="\n{} בשכר של".format(job.wage)
    bodyMessage+="\n{}ב".format(job.place)
    messageID = str(uuid.uuid4())
    body = {
        "to" : device.registration_id,
        "notification" : {        
                "body" : bodyMessage,
                "title" : "{} {}הצעת עבודה מ ".format(job.bossID.firstName, job.bossID.lastName)
        },
        "priority": "high",
        "data": {
            "click_action": "FLUTTER_NOTIFICATION_CLICK",
            "id": messageID,
            "status": "done",
            "firstName" : job.bossID.firstName,
            "lastName" : job.bossID.lastName,
            "wage" : job.wage,
            "place" : job.place,
            "jobID" : str(job.jobID),
            "discription" : job.discription,
            "message_status" : "Offer"
        },
    }
    sendPushNotificationMessageGeneral(body, bodyMessage, http, job, device, w)

def sendPushNotificationMessageGeneral(body, bodyMessage, http, job, device, w):
    headers = {
        'Authorization': 'key=AAAAUyJvk20:APA91bHU-nH6dn5veHSzCMAyeyw3ewSMaaBSnbmCrbZvCm-E3WpMyKb-lHno1LrPi7-BJsk7Otdlho1LYj1XlTS2RmC2mry4i3zOnLUQmNZlhqCHK98AQMz3f7spuErcojd8lNN6CNCU',
        'Content-Type': 'application/json; UTF-8',
    }
    #url = 'https://fcm.googleapis.com/v1/projects/zariz-204206/messages:send'
    url = 'https://fcm.googleapis.com/fcm/send'
    logging.info("sendPushNotificationMessageGeneral - {}".format(json.dumps(body)))
    try:
        #device.send_message(title="הצעת עבודה", body=bodyMessage, data={"test": "test"})
        #r = requests.post(url, headers=headers);
        
        r = http.request('POST', url, headers=headers,body=json.dumps(body))
        if w is not None:   
            #if ast.literal_eval(r.data)["success"]==1:
            if ast.literal_eval(str(str(r.data)[2:-1]))["success"]==1:
                notficationMessage = NotficationMessages(JobID=job, workerID=w, to=device.registration_id)
                notficationMessage.save()
                logging.info("sendPushNotificationMessageGeneral, sent message to {}{}, device ID {}, {} ".format(w.firstName, w.lastName, device.device_id, bodyMessage))
            else:
                logging.info("sendPushNotificationMessageGeneral, Failed to sent message, no success returned, to {}{}, device ID {}, {} ".format( w.firstName, w.lastName, device.device_id, bodyMessage))
                notficationMessage = NotficationMessages(JobID=job, workerID=w, to=device.registration_id, status="failed")
                notficationMessage.save()
    except Exception as e:
        logging.info("sendPushNotificationMessageGeneral, Failed to sent message, error - {}, to {}{}, device ID {}, {} ".format(e, w.firstName, w.lastName, device.device_id, bodyMessage))
        notficationMessage = NotficationMessages(JobID=job, workerID=w, to=device.registration_id, status="failed")
        notficationMessage.save()
