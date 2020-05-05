#!/usr/bin/env python
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


import os
import sys
p=os.path.dirname(os.path.abspath(__file__))
sys.path=["{}{}{}{}{}{}{}".format(p,os.sep,"lib",os.sep,"python3.7",os.sep,"site-packages")]+ sys.path
sys.path=["{}{}{}{}{}{}{}{}{}".format(p,os.sep,"venv",os.sep,"lib",os.sep,"python3.7",os.sep,"site-packages")]+ sys.path
#sys.path=['/Users/admin/Projects/zariz_37/venv/lib/python3.7/site-packages', '/Users/admin/Projects/zariz_37/lib','/Users/admin/Projects/zariz_37', '/Users/admin/Projects/zariz_37/lib','/Users/admin/Projects/zariz_37/polls','/Users/admin/Projects/zariz_37/mysite', '/usr/local/Cellar/python/3.7.6_1/Frameworks/Python.framework/Versions/3.7/lib/python3.7','/usr/local/Cellar/python/3.7.6_1/Frameworks/Python.framework/Versions/3.7/lib/python3.7/lib-dynload']
print("sys.path = {}".format(sys.path))
print("sys.version = {}".format(sys.version))
print("sys.executable = {}".format(sys.executable))

import logging
logging.basicConfig(level=logging.INFO)
logging.info("sys.path = {}".format(sys.path))
logging.info("sys.version = {}".format(sys.version))
logging.info("sys.executable = {}".format(sys.executable))
import random
#import ptvsd
#print(ptvsd.__version__)
#print(ptvsd.__file__)
p = random.randint(40000, 50000)
ip = '127.0.0.1'
#print("Enabling Attach on {}:{}".format(ip, p))
#ptvsd.enable_attach(address = (ip, p), redirect_output=True)
#ptvsd.wait_for_attach()
if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
