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
from django.contrib.auth.models import User

class UserFirebaseDB(models.Model):
    fireBaseUser = models.CharField(max_length=200)
    localUser = models.CharField(max_length=200)
    localPassword = models.CharField(max_length=50)
    userID = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True, blank=True,
    )

class Workers(models.Model):
    occupationFieldListString = models.CharField(max_length=2048, default = "")
    firstName = models.CharField(max_length=200, default= "")
    lastName = models.CharField(max_length=200, default = "")
    photoAGCSPath = models.CharField(max_length=200, default = "")
    lat = models.FloatField(default=0.0)
    lng = models.FloatField(default=0.0)
    radius = models.FloatField(default=0.1)
    minWage = models.FloatField(default=29.12)
    userID = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True, blank=True,
    )

class BusyEvent(models.Model):
    day = models.DateField(u'Day of the event', help_text=u'Day of the event')
    start_time = models.TimeField(u'Starting time', help_text=u'Starting time')
    end_time = models.TimeField(u'Final time', help_text=u'Final time')
    notes = models.TextField(u'Textual Notes', help_text=u'Textual Notes', blank=True, null=True)
    userID = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,)





