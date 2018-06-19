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
import ast
import codecs
import locale
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from models import UserFirebaseDB, Workers, BusyEvent
import django.contrib.auth
import django.contrib.auth.views
from django.contrib.auth.decorators import login_required
import urllib2
import os
from django.template import loader
from django.utils.translation import gettext as _
from polls.forms import BootstrapAuthenticationForm
from datetime import datetime
if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
    pass
else:
    import ptvsd

def index(request):
    #ptvsd.break_into_debugger()
    a = _("test")
    print(a)
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
        worker = Workers.objects.get(localUser=request.user.username)
    except Exception as e:
        print("Error")
        return JsonResponse({'error' : True})
    BusyEvent()
    
    payload = {'success': True}
    return JsonResponse(payload)


def updateOccupation(request):
    occupaitonList = request.POST.getlist('occupationList[]', None)
    # does user exist
    try:
        worker = Workers.objects.get(localUser=request.user.username)
    except Exception as e:
        worker = Workers(localUser=request.user)
    worker.occupationFieldListString = str(occupaitonList)
    worker.save()
    payload = {'success': True}
    return JsonResponse(payload)

def firebaseSuccess(request):
    userEmail = request.GET.get('userEmail', None)
    print('{}'.format(userEmail))
    try:
        fbUser = UserFirebaseDB.objects.get(fireBaseUser=userEmail)
    except:
        fbUser = UserFirebaseDB(fireBaseUser=userEmail, localUser=userEmail, localPassword="zariz001", userID="NotSetYet")
        fbUser.save()
    try:
        user = User.objects.get(username=fbUser.localUser)
    except Exception as e:
        user = User.objects.create_superuser(userEmail, userEmail, 'zariz001')
        user.save()
        fbUser.userID = user.id
        fbUser.save()
    userAuth = django.contrib.auth.authenticate(username = fbUser.localUser, password = fbUser.localPassword)
    
    if userAuth is not None:
        if userAuth.is_active:
            django.contrib.auth.login(request, userAuth)
        else:
            print('{} not active'.  format(userEmail))
    else:
        print('Authentication failed for {}'.format(userEmail))

    # Check if the user exists if not create and log in
    #template = loader.get_template('profilePage.html')
    #context = {}
    payload = {'success': True, 'redirectUrl' : 'accounts/profile/'}
    
    return JsonResponse(payload)
    
@login_required(login_url="/login/")
def profilePage(request):
    return render(
        request,
        'profilePage.html',
        {}
    )

def occupationPage(request):
    locale.setlocale(locale.LC_ALL, '')
    sData = codecs.open('static/content/settings.json', encoding='utf-8').read()
    data = ast.literal_eval(sData)
    sPossibleFields = data['occupationFields']
    possibleFields = [s.decode('utf-8') for s in sPossibleFields]
    pickedFields = []
    try:
        worker = Workers.objects.get(localUser=request.user.username)
        occupaitonList = ast.literal_eval(worker.occupationFieldListString)
        pickedFields = [s for s in occupaitonList if s in possibleFields]
       # if (len(pickedFields) != len(occupaitonList))
       #     worker.occupationFieldListString = str(pickedFields)
    except Exception as e:
        pass

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
    busyEvents = BusyEvent.objects.filter(worker__localUser=request.user.username)
    busyDates = [d.value_to_string() for d in busyEvents]
    return render(
        request,
        'CalanderPick.html',
        {
            'busyDates' : busyDates
        }
    )



