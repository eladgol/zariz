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
from requests_toolbelt.adapters import appengine
appengine.monkeypatch()
##################################################################
import ast
import codecs
import locale
import os
import base64

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
import django.contrib.auth
import django.contrib.auth.views
from django.contrib.auth.decorators import login_required
import urllib2
from django.template import loader
from django.utils.translation import gettext as _
from django.forms.models import model_to_dict

from polls.forms import BootstrapAuthenticationForm
from datetime import datetime
from logic import *
from models import UserFirebaseDB, Workers, BusyEvent
from django.utils import timezone
from django.core import serializers
from django.core.files.storage import FileSystemStorage
#from accessGoogleCloudStorage import *

#import firebase_admin
#from firebase_admin import credentials
from ZarizSettings import *
from django.views.decorators.csrf import csrf_exempt
#print("Initalizing firebase SDK")
#toDo: handle fire base authenticatiom the proper way, using a session token
#cred = credentials.Certificate('zariz-204206-firebase-adminsdk-8qex8-1d92e2b93c.json')
#default_app = firebase_admin.initialize_app(cred)

#if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
 #   pass
#else:
#    import ptvsd
def pretty_print_POST(req):
    """
    At this point it is completely built and ready
    to be fired; it is "prepared".

    However pay attention at the formatting used in 
    this function because it is programmed to be pretty 
    printed and may differ from the actual request.
    """
    # print('{}\n{}\n{}\n\n{}'.format(
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
    print(a)
    #b = agcs_get()
    filename = "/bucket/test.txt"
    return django.contrib.auth.views.login(request,
        template_name='loginGrid.html',
        authentication_form=BootstrapAuthenticationForm,
        extra_context=
        {
            'title': 'Log in',
            'year': datetime.now().year,
        }
    )
    #return render(
    #    request,
    #    'loginGrid.html')
    
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
@csrf_exempt
def updateLocation(request):
    lat = request.POST.get('lat', None)
    lng = request.POST.get('lng', None)
    radius = request.POST.get('radius', None)
    place = request.POST.get('place', None)
    try:
        worker = Workers.objects.get(userID=request.user.id)
    except Exception as e:
        worker = Workers(userID=request.user.id)
    worker.lat = float(lat)
    worker.lng = float(lng)
    worker.radius = float(radius)
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
            print(str(e))   
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
def updateAllInputsForm(request):
    firstName = request.POST.get('firstName', None)
    lastName = request.POST.get('lastName', None)
    place = request.POST.get('place', None)
    photoAGCSPath = request.POST.get('photoAGCSPath', None)
    wage = float(request.POST.get('wage', None)) if request.POST.get('wage', None) else None
    lat = float(request.POST.get('lat', None)) if request.POST.get('lat', None) else None
    lng = float(request.POST.get('lng', None)) if request.POST.get('lng', None) else None
    radius = float(request.POST.get('radius', None)) if request.POST.get('radius', None) else None 
    lOccupationFieldListString = str(request.POST.get('lOccupationFieldListString', None).replace(']','').replace('[','').split(','))

    try:
        worker = Workers.objects.get(userID=request.user.id)
    except Exception as e:
        worker = Workers(userID=request.user.id)
    bWorkerChanged = False
    # if photoAGCSPath is not None and photoAGCSPath != worker.photoAGCSPath:
    #     splitVal = photoAGCSPath.split(',')
    #     base64Val = splitVal[1]
    #     header64 = splitVal[0]
    #     file_ext = 'unknown'
    #     if 'jpeg' in header64:
    #         file_ext = 'jpeg'
    #     if 'jpg' in header64:
    #         file_ext = 'jpg'
    #     elif 'gif' in header64:
    #         file_ext = 'gif'
    #     elif 'png' in header64:
    #         file_ext = 'png'
    #     else:
    #         file_ext = header64[len(u'data:image/'):]

    #     buff = base64.b64decode(base64Val)

    #     sFileName = 'profile_pic_{}_{}_.{}'.format(request.user.username, time.time(), file_ext)
    #     worker.photoAGCSPath = uploadBlob(sFileName, buff, header64)
    #     bWorkerChanged = True
    if firstName is not None and worker.firstName != firstName:
        worker.firstName = firstName
        bWorkerChanged = True
    if lastName is not None and worker.lastName != lastName:
        worker.lastName = lastName
        bWorkerChanged = True
    if place is not None and worker.place != place:
        worker.place = place
        bWorkerChanged = True
    if radius is not None and worker.radius != radius:
        worker.radius = radius
        bWorkerChanged = True
    if wage is not None and worker.wage != wage:
        worker.wage = float(wage)
        bWorkerChanged = True
    if lat is not None and worker.lat != lat:
        worker.lat = float(lat)
        bWorkerChanged = True
    if lng is not None and worker.lng != lng:
        worker.lng = lng;
        bWorkerChanged = True   
    if lOccupationFieldListString is not None and worker.occupationFieldListString != lOccupationFieldListString:
        worker.occupationFieldListString = lOccupationFieldListString
        bWorkerChanged = True
    try:
        user = User.objects.get(username=request.user)
    except Exception as e:
        print("SHOULD NOT HAPPEN!!!!No user found - {}".format(e.message))
        return JsonResponse({"success" : False})
    
    if bWorkerChanged:
        worker.save()
        payload = {'success': True, 'firstName' : worker.firstName,
            'lastName' : worker.lastName, 'wage' : str(worker.wage), 'photoAGCSPath' : worker.photoAGCSPath, 'place': worker.place,
            'radius' : str(worker.radius), 'lat' : str(worker.lat), 'lng' : str(worker.lng), 'userID' : str(user.id), 'email' : user.email, 
            'username' : user.username, 'lOccupationFieldListString' : str(worker.occupationFieldListString)}
        print("updateAllInputsForm, success,  returning - {}".format(payload))
    else:
        payload = {'success': True, 'Error' : 'no change', 'firstName' : worker.firstName,
            'lastName' : worker.lastName, 'wage' : str(worker.wage), 'photoAGCSPath' : worker.photoAGCSPath, 'place': worker.place,
            'radius' : str(worker.radius), 'lat' : str(worker.lat), 'lng' : str(worker.lng), 'userID' : str(user.id), 'email' : user.email, 
            'username' : user.username, 'lOccupationFieldListString' : str(worker.occupationFieldListString)}
        print("updateAllInputsForm, Error, call for nothing, no real change, returning - {}".format(payload))
    return JsonResponse(payload)
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
        i=i+1
    
    return JsonResponse(d)
@csrf_exempt
def deleteJobAsBoss(request):
    jobID = request.POST.get('jobID', None)
    try:
        job = Jobs.objects.get(jobID=jobID).delete()
    except Exception as e:
        print("deleteJobAsBoss - Failed no such job ID {}".format(jobID))
        return JsonResponse({"success" : False, "Error" : "no such JobID"})
    print("deleteJobAsBoss - Deleted job ID {}".format(jobID))
    return JsonResponse({'success': True})
    
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
    print("updateJobAsBoss - jobID {}, discription - {}, place {}, lat {}, lng {}, wage {}, occupationFieldListString {}".
            format(jobID, discription, place, lat, lng, wage, occupationFieldListString))
            
    try:
        Boss = Bosses.objects.get(userID=request.user.id)
    except Exception as e:
        Boss = Bosses(userID=request.user.id)

    if jobID == '-1':
        Job = Jobs(bossID=Boss)
        bNewJob = True
        print("updateJobAsBoss - Created new job id - {}".format(Job.jobID))
    else:
        try:
            Job = Jobs.objects.get(jobID=jobID, bossID=Boss)
            bNewJob = False
            print("updateJobAsBoss - Existing job id - {}".format(Job.jobID))
        except Exception as e2:
            Job = Jobs(bossID=Boss)
            bNewJob = True
            print("updateJobAsBoss - Created new job id - {}".format(Job.jobID))
    
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
        Job.save()
        
        payload = {'success': True, 'jobID': str(Job.jobID), 'discription' : str(discription), 'place' : str(place), 
            'lat' : str(lat), 'lng' : str(lng), 'wage' : str(wage), 'nWorkers' : str(nWorkers), 'occupationFieldListString' : occupationFieldListString}
        print("updateJobAsBoss - Saved Job, payload {}".format(payload))
    else:
        payload = {'success': True, 'Error' : 'no change', 'jobID': str(Job.jobID), 'discription' : str(discription), 'place' : str(place), 
            'lat' : str(lat), 'lng' : str(lng), 'wage' : str(wage), 'nWorkers' : str(nWorkers), 'occupationFieldListString' : occupationFieldListString}
        print("updateJobAsBoss - No change, payload {}".format(payload))
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
        Boss.lng = lng;
        bBossChanged = True    
    try:
        user = User.objects.get(username=request.user)
    except Exception as e:
        print("SHOULD NOT HAPPEN!!!!No user found - {}".format(e.message))
        return JsonResponse({"sucess" : False})
        
    if bBossChanged:
        Boss.save()
        payload = {'success': True, 'firstName' : Boss.firstName,
            'lastName' : Boss.lastName,  'photoAGCSPath' : Boss.photoAGCSPath, 'place': Boss.place,
            'lat' : str(Boss.lat), 'lng' : str(Boss.lng), 'userID' : str(user.id), 'email' : user.email, 
            'username' : user.username}
        print("updateAllBossInputsForm, success,  returning - {}".format(payload))
    else:
        payload = {'success': True, 'Error' : 'no change', 'firstName' : Boss.firstName,
            'lastName' : Boss.lastName, 'photoAGCSPath' : Boss.photoAGCSPath, 'place': Boss.place,
            'lat' : str(Boss.lat), 'lng' : str(Boss.lng), 'userID' : str(user.id), 'email' : user.email, 
            'username' : user.username}
        print("updateAllBossInputsForm, Error, call for nothing, no real change, returning - {}".format(payload))
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
def updateOccupation(request):
    occupaitonList = request.POST.getlist('occupationList[]', None)
    print(occupaitonList)
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
    payload = authenticateUser(request, localUser, localPassword) 
    if payload['success']:
        payload['redirectUrl'] = 'accounts/profile/'
        worker = getWorker(request.user.username)
        if worker.photoAGCSPath is '' and 'photoURL' in payload and payload['photoURL']!='':
            print('saving {} -> {}'.format(payload['photoURL'], payload['photoFileName']))
            downoladPhotoAndSaveToWorker(payload['photoURL'], payload['photoFileName'], worker)
    print("Login payload result {} for {}, {}".format(payload, localUser, request.user.username))
    return JsonResponse(payload)

@csrf_exempt
def signUp(request):
    pretty_print_POST(request)
    localUser = request.POST.get('localUser', None)
    localPassword = request.POST.get('localPassword', None)
    localEmail = request.POST.get('localEmail', None)
    payload = createUser(request, localUser, localPassword, localEmail) 
    if payload['success']:
        payload['redirectUrl'] = 'accounts/profile/'
        worker = getWorker(request.user.username)
        if worker is not None:
            if worker.photoAGCSPath is '' and 'photoURL' in payload and payload['photoURL']!='':
                print('saving {} -> {}'.format(payload['photoURL'], payload['photoFileName']))
                downoladPhotoAndSaveToWorker(payload['photoURL'], payload['photoFileName'], worker)

    return JsonResponse(payload)

@csrf_exempt
def firebaseSuccess(request):
    userToken = request.GET.get('userToken', None)
    payload = fbAuthenticate(userToken)
    if not payload['success']:
        return JsonResponse(payload)

    userEmail = payload['userEmail'] 
    print('email - {}, token - {}'.format(userEmail, userToken)) 

    fbUser = updateFireBaseDB(userEmail)

    res = authenticateUser(request, fbUser.localUser, fbUser.localPassword) 
    if res['success']:
        payload2 = {'success': True, 'redirectUrl' : 'accounts/profile/'}
    else:
        payload2 = {'success': True, 'redirectUrl' : 'accounts/profile/'}

    worker = getWorker(request.user.username)
    if worker.photoAGCSPath is '' and payload['photoURL']!='':
        print('saving {} -> {}'.format(payload['photoURL'], payload['photoFileName']))
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
        print(e.message)
    return render(
        request,
        'Carousel.html',
        d
    )

@csrf_exempt
def getFieldDetails(request):
    pretty_print_POST(request)
    print("getFieldDetails for {}".format(request.user.username))
    worker = getWorker(request.user.username)
    print("getFieldDetails after getWorker")
    d = model_to_dict(worker)
    print("getFieldDetails {}".format(d))
    return JsonResponse(d)
@csrf_exempt
def getBossFieldDetails(request):
    pretty_print_POST(request)
    print("getBossFieldDetails for {}".format(request.user.username))
    Boss = getBoss(request.user.username)
    print("getBossFieldDetails after getBoss")
    d = model_to_dict(Boss)
    print("getBossFieldDetails {}".format(d))
    return JsonResponse(d)

@csrf_exempt   
def getOccupationDetails(request):
    locale.setlocale(locale.LC_ALL, '')
    #sData = codecs.open(os.path.dirname(__file__) + '/../'+ 'static/content/zarizSettings.json', encoding='utf-8').read()
    #data = ast.literal_eval(sData)
    sPossibleFields = ZarizSettingsDict['occupationFields']
    possibleFields = [s.decode('utf-8') for s in sPossibleFields]
    pickedFields = []
    try:
        worker = Workers.objects.get(userID=request.user.id)
        occupaitonList = ast.literal_eval(worker.occupationFieldListString)
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
    print("occupationDetails, Start")
    possibleFields, pickedFields = getOccupationDetails(request)
    # if (len(pickedFields) != len(occupaitonList))
    #     worker.occupationFieldListString = str(pickedFields)
    j = JsonResponse({'success' : True, 'possibleFields' : str(possibleFields), 'pickedFields' : str(pickedFields)})
    print("occupationDetails, Returning {}".format(j))
    return j
    

@csrf_exempt
def calander2(request):
    busyDates = []
    try:
        busyEvents = BusyEvent.objects.filter(userID=request.user.id)
        busyDates = [(d.start_date.strftime('%Y-%m-%d'), d.notes) for d in busyEvents]
    except Exception as e:
        print(e.message)
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
    #     print("Error")
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
    return JsonResponse({});

import pdb
def ExportDB(request):
    print("Hello")
    dataWorkers = str([str(w) for w in Workers.objects.values()])
    dataUsers = str([str(u) for u in User.objects.values()])
    data = str({'Workers' : dataWorkers, 'Users' : dataUsers})
    response = HttpResponse(data, content_type='text/plain')
    sFileName = "ZarizExportDB_" + str(time.time()) + ".json"
    response['Content-Disposition'] = 'attachment; filename="' + '"' + sFileName +'"'
    return response

from ast import literal_eval as leval
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
                print("Exception - {}".format(e))
        return render(request, 'ShowWorkers.html')
    return render(request, 'ShowWorkers.html')
