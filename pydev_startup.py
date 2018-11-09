import sys
import os

#Assuming that pdvsd is located in the working folder
#sys.path = [os.getcwd() + os.sep + 'lib']

#import pip
#pip.main(['install','ptvsd'])
print("BEfore import Google App Engine has started, ready to attach the debugger")

import ptvsd
print(ptvsd.__version__)
# Modify the secret and port number as desired; you're debugging locally so the values don't matter.
# However, be sure the port is not blocked on your computer.
print("After import Google App Engine has started, ready to attach the debugger")
print(ptvsd.__file__)
import random
p = random.randint(40000, 50000)
ip = '127.0.0.1'
print("Enabling Attach on {}:{}".format(ip, p))
ptvsd.enable_attach(address = (ip, p), redirect_output=True)
#ptvsd.wait_for_attach()
#ptvsd.break_into_debugger()
#The debug server has started and you can now use VS Code to attach to the application for debugging
print("Google App Engine has started, ready to attach the debugger")
#ptvsd.wait_for_attach()
print("Google App Engine has started, ready to attach the debugger")