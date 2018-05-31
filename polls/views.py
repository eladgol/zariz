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

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from models import UserFirebaseDB
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
 

def firebaseSuccess(request):
    userEmail = request.GET.get('userEmail', None)
    print('{}'.format(userEmail))
    try:
        fbUser = UserFirebaseDB.objects.get(fireBaseUser=userEmail)
    except:
        fbUser = UserFirebaseDB(fireBaseUser=userEmail, localUser=userEmail, localPassword="zariz001")
        fbUser.save()

    try:
        user = User.objects.get(username=fbUser.localUser)
    except Exception as e:
        user = User.objects.create_superuser(userEmail, userEmail, 'zariz001')
        user.save()
  
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
