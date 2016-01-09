import time
import sys
import os
import RPi.GPIO as GPIO

#TODO refactore paths
sys.path.append(os.path.abspath('./utils'))
sys.path.append(os.path.abspath('./models'))
sys.path.append(os.path.abspath('.'))

from senz_parser import *
from crypto_utils import *
from config import*


class SenzHandler():
    """
    Handler incoming senz messages from here. We are dealing with following
    senz types
        1. GET
        2. PUT
        3. SHARE
        4. DATA

    According to the senz type different operations need to be carry out
    """
    def __init__(self, transport):
        """
        Initilize udp transport from here. We can use transport to send message
        to udp socket

        Args:
            trnsport - twisted transport instance
        """
        self.transport = transport

    
    def handleSenz(self, senz):
        """
        Handle differennt types of senz from here. This function will be called
        asynchronously. Whenc senz message receives this function will be
        called by twisted thread(thread safe mode via twisted library)
        """
        print 'senz received %s' % senz.type
        print 'senz sender %s' % senz.sender
        print 'senz receiver %s' % senz.receiver
        sw={'on':1,'off':0,'#s1':22,'#s2':23,'#s3':24,'#s4':25,'#time':'time','#msg':'msg','#pubkey':'pubkey'}
        var=['#s1','#s2','#s3','#s4']
        data=senz.attributes 
        print data
        if senz.type=='PUT':
            get={}
            for i in data:
                print i," in senz attributes"
                if i in var and data[i]!="":
                    print i,"-",data[i] 
                    GPIO.output(sw[i],sw[data[i]])
		    get[i]=sw[data[i]]
            self.send_data("PutDone",get,senz.sender,senz.receiver)
            #self.share_attribute()
            
        if senz.type=='GET':
            print 'get message'
            get={} 
            for i in data:
                if i in var:
                    get[i] = GPIO.input(sw[i])
		    get[i]=0
		    self.send_data("GetResponse",get,senz.sender,senz.receiver)        
        if senz.type == 'DATA':
            print senz.attributes['#msg']
            if senz.attributes['#msg'] == 'UserCreated':
                # SHARE gpio senz from here
                self.share_attribute()

    def postHandle(self, arg):
        """
        After handling senz message this function will be called. Basically
        this is a call back funcion
        """
        # self.transport.write('senz')
        print "handled"


    def share_attribute(self):
        receiver = userName
        sender = homeName
        senz = "SHARE #homez #s1 #s2 #s3 #s4 #time %s @%s ^%s" %(time.time(), receiver, sender)
        signed_senz = sign_senz(senz)
        self.transport.write(signed_senz)
        
    def send_data(self,msg,data,receiver,sender):
        #receiver = 'userpi'
        #sender = 'homepi'
        senz="DATA #app homez #msg "+msg
        for i in data:
            senz=senz+" "+i+" "+str(data[i])

        senz = senz+" #time %s @%s ^%s" %(time.time(),receiver, sender)
        print senz
        signed_senz = sign_senz(senz)
        self.transport.write(signed_senz)
