import sys
import os

#Assuming that pdvsd is located in the working folder
sys.path.append(os.getcwd())
#import pip
#pip.main(['install','ptvsd'])
import ptvsd
# Modify the secret and port number as desired; you're debugging locally so the values don't matter.
# However, be sure the port is not blocked on your computer.
ptvsd.enable_attach(secret = 'my_secret', address = ('0.0.0.0', 3000))
#ptvsd.break_into_debugger()
#The debug server has started and you can now use VS Code to attach to the application for debugging
print("Google App Engine has started, ready to attach the debugger")
#ptvsd.wait_for_attach()