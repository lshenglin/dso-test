#! /usr/bin/env python

#  Jade Yu edit on 08/09/2016 , 
#  edit based on btTbale.py nad vxi11Stream.py to make turtableLT360 is controlable via ks E5810B and/or brainbox

import vxi11
import time
import sys
import optparse
import os
import telnetlib

MAX_TRIES = 3
class spawn:
    def __init__(self,ipAddr=None,SICLaddr=None,interface=None,port=None,autotmo='0.1',KS=False,DEBUG=False):
        self.KS = KS
        if not(ipAddr):      ipAddr      = '169.254.58.10'
        self.timeout = float(autotmo)
        self.DEBUG   = DEBUG
        if self.KS:
            if not(SICLaddr):  SICLaddr  = "488"
            if not(interface): interface = "COM1"
            self.dev = vxi11.Instrument(ipAddr, "%s,%s" % (interface,SICLaddr))
            self.dispPolarity('UNIPOLAR')
            #self.suffix = None
        else:
            error = -1
            self.timeout = float(autotmo)
            self.DEBUG   = DEBUG
            ok =False
            attempt = 0

            while not ok and attempt < MAX_TRIES:
                try:
                    
                    self.ltx = telnetlib.Telnet(ipAddr,port,timeout=10)
                    if self.ltx:         
                        error = 0
                        ok = True
                        
                except Exception,e:
                    print e
                    attempt += 1

            
            if not(error):
                print "Connected to turn table %s" % self.expcmd('Get Name')
                self.dispPolarity('UNIPOLAR')

            # get id info
            self.err = error

    def expcmd(self,cmd,DEBUG=False):
        rtn = None
        if not(DEBUG): DEBUG = self.DEBUG
        if DEBUG:  print('-cmd: %s %s' % (time.strftime('%H%M%S'),cmd.strip()))
        # if use LT360 with KeysightE5810B, bypass all read command 
        if self.KS:
            if cmd.upper().find('GET') >= 0:
                print "E5810B can not get response from LT360 :("  
                #rtn = self.dev.ask(cmd+'\r').encode()
            else:
                self.dev.write(cmd+'\r')                   
        else:
            self.ltx.write('%s\r' % cmd)
            #raw = self.ltx.read_until(self.jfwPrompt,self.timeout)
            # Need to add timeout code on read_some()
            #  may require use of threading to accomplish this
            time.sleep(0.1)
            raw = self.ltx.read_some()
            #ans = raw.split('\n')
            rtn = raw
            if DEBUG:  print('-ans: %s %s' % (time.strftime('%H%M%S'),rtn))                  

        return rtn


    def close(self):
        if self.KS :
            self.dev.close()
        else:
            self.ltx.close()
    # def write(self,cmd,DEBUG = False):
    #     if not(DEBUG): DEBUG = self.DEBUG
    #     if DEBUG:  print('-cmd: %s %s' % (time.strftime('%H%M%S'),cmd.strip()))
    #     self.dev.write(cmd+'\r')
        

    # def read(self):
    #     stb = self.dev.read_stb()
    #     ttl = 5
    #     while ttl and (stb & 0x10)==0:
    #         time.sleep(0.1)
    #         stb = self.dev.read_stb()
    #         ttl -= 1
    #     if stb & 0x10:     ans = self.dev.read()
    #     else:              ans = None
    #     return ans

    def zero(self):
        return self.expcmd('Set Origin')

    def baud(self,rt=None):
        if rt:
            ans = self.expcmd('Set BaudRate %s' % rt)
        else:
            ans = self.expcmd('Get BaudRate')
        return ans
    def ccw(self,ang):

        return self.expcmd('GoTo CCW %s' % ang)
    def cw(self,ang):
        return self.expcmd('GoTo CW %s' % ang)

    def stepSize(self,size=None):
        if size:
            return self.expcmd('Set StepSize %s' % size)
        else:
            return self.expcmd('Get StepSize')
    def stepCW(self):
        return self.expcmd('Step CW')

    def stepCCW(self):
        return self.expcmd('Step CCW')

    def pulseDir(self,dir=None):
        if dir:
            allowDir=['CCW','CW']
            if dir.upper() in allowDir:
                return self.expcmd('Set PulseDir %s' % dir.upper())
            else:
                print "Pulse Direction should be either: %s" % allowDir
        else:
            return self.expcmd('Get PulseDir')

    def pulseEdge(self,edge=None):
        if edge:
            allowEdge=['RISE','FALL']
            if edge.upper() in allowEdge:
                return self.expcmd('Set PulseEdge %s' % edge.upper())
            else:
                print "Pulse Edge should be either: %s" % allowEdge
        else:
            return self.expcmd('Get PulseEdge')
    def pulseInput(self,input=None):
        if input:
            allowInput=['ON','OFF']
            if input.upper() in allowInput:
                return self.expcmd('Set PulseInput %s' % input.upper())
            else:
                print "Inut should be either: %s" % allowInput
        else:
            return self.expcmd('Get PulseInput')

    def velocity(self,vlo=None):
        if vlo:
            if float(vlo) <= 3.00 and float(vlo) >= 0.01:
                return self.expcmd('Set Velocity %s' % vlo)
            else:
                print "The allowable range for the parameter is 0.01 to 3.00 RPM"
        else:
            return self.expcmd('Get Velocity')

    def stopMove(self):
        return self.expcmd('Set MoveAbort')

    def position(self):
        return self.expcmd('Get Position')

    def moving(self):
        return self.expcmd('Get Moving')
        
    def ready(self):
        state = self.moving()
        if state != 'NO':
            return state
        else:
            return 'Yes'
    
    def dispPolarity(self,pol=None):
        # could be set to 'BIPOLAR' but easier to use UNIPOLAR
        if pol:
            pol = pol.upper()
            allowedPols = ['UNIPOLAR', 'BIPOLAR']
            if pol in allowedPols:
                ans = self.expcmd('Set DisplayPolarity %s' % pol)
            else:
                ans = 'Polarity must be either: %s' % allowedPols
        else:
            ans = self.expcmd('Get DisplayPolarity')

    def angle(self,ang=None):                             # cannot use this function with E5810B agilent
        if ang == None:
            return self.position()
        else:
            # routine to determine shortest method to desired angle
            rawAng = float(ang)
            if rawAng >= 360:  ang = rawAng % 360.
            else:              ang = rawAng

            diffAng = ang - float(self.position())
            if diffAng  > 180.:
                self.cw(ang)
            else:
                if diffAng < -180.:
                    self.ccw(ang)
                elif diffAng < 0.0:
                    # by this point;  -180 < ang < 180
                    self.cw(ang)
                else:
                    self.ccw(ang)

    def delta(self,ang=None):                               # cannot use this function with E5810B agilent
        if ang == None:
            return self.angle()
        else:
            # determine angle to go to and feed to angle
            rawAng = float(ang) + float(self.position())
            if rawAng >= 360:  ang = rawAng % 360.
            else:              ang = rawAng
            self.angle(ang)
 
    def enableControl(self,enable=True):
        if enable:
            self.expcmd('Set EnableControls')
        else:
            self.expcmd('Set DisableControls')
            
if __name__ == "__main__":
    lan = spawn(ipAddr='10.0.1.253',port =9001)
  # parser = optparse.OptionParser()
  # parser.usage = """
  # %s -A [hostname or IPaddr] [-P port] gpib_cmd
  #   options specify address and gpib port information
  #   for vxi-11 server controlled devices
  # """  % (os.path.basename(sys.argv[0])) 
  
  # parser.add_option('-A','--ipaddr',dest='ipaddr',
  #                   default=None,
  #                   help=" "
  #                   "ipAddress of agilent E5810A(B)")
  # parser.add_option('-P','--port',dest='port',
  #                   default=None,
  #                   help=" "
  #                   "gpib addr")
  # parser.add_option('-I','--interface',dest='interface',
  #                   default=None,
  #                   help=" "
  #                   "interface: gpib (default) or com")
  # parser.add_option('-r','--recv',dest='rcv',
  #                   action="store_true",default=False,
  #                   help=" "
  #                   "receive ")

  # #parser.disable_interspersed_args()
  # (options, args) = parser.parse_args()


  # langpib = spawn(options.ipaddr,options.port,options.interface)

  # if len(args):
  #     ans = langpib.expcmd(" ".join(args),options.rcv)
  #     print ans

  # langpib.close()
  

    
