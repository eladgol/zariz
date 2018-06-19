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

from django.db import models

class UserFirebaseDB(models.Model):
    fireBaseUser = models.CharField(max_length=200)
    localUser = models.CharField(max_length=200)
    localPassword = models.CharField(max_length=50)
    userID = models.CharField(max_length=200)

class Workers(models.Model):
    occupationFieldListString = models.CharField(max_length=2048)
    firstName = models.CharField(max_length=200)
    lastName = models.CharField(max_length=200)
    portrait = models.ImageField( default = 'content/portraits/no-portrait.png')
    localUser = models.CharField(max_length=200)
    lat = models.FloatField()
    lng = models.FloatField()
    radius = models.FloatField()
    minWage = models.IntegerField()
    userID = models.CharField(max_length=200)

class BusyEvent(models.Model):
    userToken = models.CharField(max_length=200)
    day = models.DateField(u'Day of the event', help_text=u'Day of the event')
    start_time = models.TimeField(u'Starting time', help_text=u'Starting time')
    end_time = models.TimeField(u'Final time', help_text=u'Final time')
    notes = models.TextField(u'Textual Notes', help_text=u'Textual Notes', blank=True, null=True)
    




