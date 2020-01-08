import sys
import os

#Assuming that pdvsd is located in the working folder
#libDir = os.getcwd() + os.sep + 'lib'
#sys.path = [libDir, libDir+os.sep+'ptvsd' , libDir+os.sep+'l']

#import pip
#pip.main(['install','ptvsd'])
print("BEfore import Google App Engine has started, ready to attach the debugger")

#print("1")
#p=os.path.dirname(os.path.abspath(__file__))
#print("2")
#sys.path=["{}{}{}".format(p,os.sep,"lib")]+ sys.path
print("sys.path = {}".format(sys.path))
try:
    import ptvsd
except Exception as e:
    print("ptvsd Exception {}".format(e))

print(ptvsd.__version__)
# Modify the secret and port number as desired; you're debugging locally so the values don't matter.
# However, be sure the port is not blocked on your computer.
print("After import Google App Engine has started, ready to attach the debugger")
#print(__file__)
print(ptvsd.__file__)
import random
p = random.randint(40000, 50000)
ip = '127.0.0.1'
print("ptvsd version {}".format(ptvsd.__version__)) 
print("Enabling Attach on {}:{}".format(ip, p))
ptvsd.enable_attach(address = (ip, p), redirect_output=True)
#ptvsd.wait_for_attach()
#ptvsd.break_into_debugger()
#The debug server has started and you can now use VS Code to attach to the application for debugging
print("Google App Engine has started, ready to attach the debugger")
