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

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')


class Choice(models.Model):
    question = models.ForeignKey(Question)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

class UserFirebaseDB(models.Model):
    fireBaseUser = models.CharField(max_length=200)
    localUser = models.CharField(max_length=200)
    localPassword = models.CharField(max_length=50)

class Workers(models.Model):
    occupationFieldListString = models.CharField(max_length=2048)
    firstName = models.CharField(max_length=200)
    lastName = models.CharField(max_length=200)
    portrait = models.ImageField( default = 'content/portraits/no-portrait.png')
    localUser = models.CharField(max_length=200)