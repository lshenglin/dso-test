#! /usr/bin/env python



import argparse
import os, sys, time
import telnetlib


class spawn:
    def __init__(self,ipaddr=None,ipPort=5025):
        """ Simple script to simply control RS attenuator
            utilizes basic socket interface to talk to RS attenuator
        """
        if ipaddr == None:  ipaddr = "192.168.100.13"
        if ipPort == None:  ipPort = 5025
        
        self.atn = telnetlib.Telnet(ipaddr,ipPort,timeout=10)


    def expcmd(self,cmd,slp=0.25):
        self.atn.write('%s\n' % cmd)
        time.sleep(slp)
        if cmd.find('?') > -1:  ans = self.atn.read_until('\n')
        else:                   ans = None
        return ans
    
    def onecmd(self,cmd,val=None):
        ans = None
        if val !=None: self.expcmd('%s %s' % (cmd,val))
        else:          ans = self.expcmd('%s?' % cmd)

        if ans:
            try:    ans = float(ans)
            except: pass
        return ans

    def freq(self,val=None):
        if val != None:
            f = self.onecmd('freq','%sMHz' % val)
        else:
            f = self.onecmd('freq')
        if f:  f = f/1.0e6
        return f
    
    def pow(self,pwr=None):
        return self.onecmd('sour:pow',pwr)

    def rfon(self,mode=None):
        return self.onecmd('outp',mode)

    def modon(self,mode=None):
        return self.onecmd('sour:iq:stat',mode)

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="controls the RS SGS100A in a few limited ways")
  parser.add_argument('--ipaddr', default=None, help="ipAddress or Hostname")
  parser.add_argument('--port',   default=5025, help="socket port")    
  parser.add_argument('--freq',   default=None, help="center frequency in MHz")
  parser.add_argument('--pwr',    default=None, type=float, help="output power dbm")    
  parser.add_argument('--rfon',   default=None, action="store_true",  help="rf enable")
  parser.add_argument('--rfoff',  default=None, action="store_true",  help="rf disable")

  args = parser.parse_args()
  sg = spawn(args.ipaddr,args.port)

  if args.freq:          sg.freq(args.freq)
  if args.pwr != None:   sg.pow(args.pwr)
  if args.rfon:          sg.rfon(1)
  if args.rfoff:         sg.rfon(0)

  print('rf output enabled: %s' % sg.rfon())
  print('rf freq MHz: %s' % sg.freq())
  print('rf power: %s' % sg.pow())

  
