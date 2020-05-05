#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
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
#





import logging
logging.basicConfig(level=logging.INFO)
logging.warning("main.py HELLO!!!!!!!!!!!!!!!!!!!!!!!!")
from mysite.wsgi import application

# App Engine by default looks for a main.py file at the root of the app
# directory with a WSGI-compatible object called app.
# This file imports the WSGI-compatible object of your Django app,
# application from mysite/wsgi.py and renames it app so it is discoverable by
# App Engine without additional configuration.
# Alternatively, you can add a custom entrypoint field in your app.yaml:
# entrypoint: gunicorn -b :$PORT mysite.wsgi
app = application
# import os
# import sys
# from django.core.wsgi import get_wsgi_application
# import os
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

# app = get_wsgi_application()
# # os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

# # from django.core.management import execute_from_command_line

# # execute_from_command_line(sys.argv)

# # try:
# #     import webapp2
# # except Exception as e:
# #     logging.warning("{}".format(e))
# # else:
# #     class MainHandler(webapp2.RequestHandler):
# #         def get(self):
# #             self.response.write('Hello world!')
# #     from django.core.wsgi import get_wsgi_application
# #     import os
# #     os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

# #     app = get_wsgi_application()
# #     #app = webapp2.WSGIApplication([
# #     #    ('/', MainHandler)
# #     #])
    


# # #import ptvsd
