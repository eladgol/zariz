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

from django.conf.urls import include, url
from django.contrib import admin

import django.contrib.auth.views
from polls.views import index, loginFirebase, profilePage, testlocallogin, ShowWorkers, updateLocation, notifyTest, updateAllInputsForm
from polls.views import firebaseSuccess, occupationPage, updateOccupation, calander, LocationForm, calander2, updateDates, updateInputForm
from polls.views import demoForm, demoForm2, carousel, localLogin, dummy, signUp, getFieldDetails, ExportDB, LoadDBFromFile, occupationDetails
import polls.forms
from datetime import datetime
urlpatterns = [
    url(r'^$', index),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$',
    django.contrib.auth.views.login,
    {
        'template_name': 'loginGrid.html',
        'authentication_form': polls.forms.BootstrapAuthenticationForm,
        'extra_context':
        {
            'title': 'Log in',
            'year': datetime.now().year,
        }
    },
    name='login'),
    url(r'^logout$', django.contrib.auth.views.logout,{ 'next_page': '/',}, name='logout'),
    url(r'^fire/$', loginFirebase),
    url(r'^firebaseSuccess/', firebaseSuccess, name="firebaseSuccess"),
    url(r'^accounts/profile/', profilePage, name='profilePage'),
    url(r'^occupation/', occupationPage, name='occupationPage'),
    url(r'^occupationDetails/', occupationDetails, name='occupationDetails'),
    url(r'^updateOccupation/',updateOccupation, name='updateOccupation'),
    url(r'^updateInputForm/', updateInputForm, name='updateInputForm'),
    url(r'^updateAllInputsForm/', updateAllInputsForm, name='updateAllInputsForm'),
    url(r'^updateDates',updateDates, name='updateDates'),
    url(r'^updateLocation',updateLocation, name='updateLocation'),
    url(r'^calander/',calander, name='calander'),
    url(r'^calander2/',calander2, name='calander2'),
    url(r'^localLogin/',localLogin, name='localLogin'),
    url(r'^signUp/',signUp, name='signUp'),
    url(r'^testlocallogin/', django.contrib.auth.views.login,
    {
        'template_name': 'testlocallogin.html',
        'authentication_form': polls.forms.BootstrapAuthenticationForm,
        'extra_context':
        {
            'title': 'Log in',
            'year': datetime.now().year,
            'next': '/accounts/profile/'
        }
    }, name = 'testlocallogin'),
    url(r'^ShowWorkers/', ShowWorkers, name='ShowWorkers'),
    url(r'^ExportDB', ExportDB, name='ExportDB'),
    url(r'^LoadDBFromFile', LoadDBFromFile, name='LoadDBFromFile'),
    url(r'^demoForm/', demoForm, name='demoForm'),
    url(r'^demoForm2/', demoForm2, name='demoForm2'),
    url(r'^carousel/', carousel, name='carousel'),
    url(r'^LocationForm/', LocationForm, name='LocationForm'),
    url(r'^notifyTest/', notifyTest, name='notifyTest'),
    url(r'^dummy/', dummy, name='dummy'),
    url(r'^getFieldDetails/', getFieldDetails, name='dummy'),
    
]
