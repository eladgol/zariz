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

from accessGoogleCloudStorage import *

import firebase_admin
from firebase_admin import credentials
print("Initalizing firebase SDK")
#toDo: handle fire base authenticatiom the proper way, using a session token
cred = credentials.Certificate('zariz-204206-firebase-adminsdk-8qex8-1d92e2b93c.json')
default_app = firebase_admin.initialize_app(cred)

if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
    pass
else:
    import ptvsd

agcs = accessGoogleCloudStorage()

def index(request):
    #ptvsd.break_into_debugger()
    a = _("test")
    print(a)
    b = agcs.get()
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
    
def loginFirebase(request):
    #ptvsd.break_into_debugger()
    return render(
        request,
        'loginFirebase.html',
        {}
    )

def testlocallogin(request):
    return render(
        request,
        'testlocallogin.html',
        {}
    )

def updateDates(request):
    occupaitonList = request.POST.getlist('occupationList[]', None)
    # does user exist
    try:
        worker = Workers.objects.get(userID=request.user.id)
    except Exception as e:
        print("Error")
        return JsonResponse({'error' : True})
    BusyEvent()
    
    payload = {'success': True}
    return JsonResponse(payload)
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
        worker.photoAGCSPath = uploadBlob(sFileName, buff, header64, agcs)

    elif 'firstName' in name:
        worker.firstName = value
    elif 'lastName' in name:
        worker.lastName = value
    elif 'wage' in name:
        worker.minWage = float(name)
    worker.save()
    payload = {'success': True, 'firstName' : worker.firstName,
     'lastName' : worker.lastName, 'wage' : worker.minWage, 'photoAGCSPath' : worker.photoAGCSPath}
    return JsonResponse(payload)

def updateOccupation(request):
    occupaitonList = request.POST.getlist('occupationList[]', None)
    # does user exist
    try:
        worker = Workers.objects.get(userID=request.user.id)
    except Exception as e:
        worker = Workers(userID=request.user.id)
    worker.occupationFieldListString = str(occupaitonList)
    worker.save()
    payload = {'success': True}
    return JsonResponse(payload)

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
    print('saving {} -> {}'.format(payload['photoURL'], payload['photoFileName']))
    downoladPhoto(payload['photoURL'], payload['photoFileName'], worker, agcs)

    return JsonResponse(payload2)
    
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
@login_required(login_url="/carousel/")
def carousel(request):

    worker = getWorker(request.user.username)
    d = model_to_dict(worker)

    possibleFields, pickedFields = getOccupationDetails(request)
    d['fields'] = possibleFields
    d['picked'] = pickedFields


    return render(
        request,
        'carousel.html',
        d
    )
    
def getOccupationDetails(request):
    locale.setlocale(locale.LC_ALL, '')
    sData = codecs.open(os.path.dirname(__file__) + '/../'+ 'static/content/zarizSettings.json', encoding='utf-8').read()
    data = ast.literal_eval(sData)
    sPossibleFields = data['occupationFields']
    possibleFields = [s.decode('utf-8') for s in sPossibleFields]
    pickedFields = []
    try:
        worker = Workers.objects.get(userID=request.user.id)
        occupaitonList = ast.literal_eval(worker.occupationFieldListString)
        pickedFields = [s for s in occupaitonList if s in possibleFields]
    except Exception as e:
        pass
    return possibleFields, pickedFields

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

def calander(request):
    # try:
    #     worker = Workers.objects.get(localUser=request.user.username)
    # except Exception as e:
    #     print("Error")
    #     return JsonResponse({'error' : True})
    busyEvents = BusyEvent.objects.filter(worker__userid=request.user.id)
    busyDates = [d.value_to_string() for d in busyEvents]
    return render(
        request,
        'CalanderPick.html',
        {
            'busyDates' : busyDates
        }
    )
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
def demoForm(request):
    return render(
        request,
        'demoForm.html',
        {}
    )
def demoForm2(request):
    return render(
        request,
        'demoForm2.html',
        {}
    )