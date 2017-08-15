# -----------------------------------------------------------------------------
# FILENAME : tek_arb.py
# AUTHOR : Jade Yu
# DATE : 9/12/2016

# -----------------------------------------------------------------------------
# DESCRIPTION: Module to control the Tek arb70002A
# -----------------------------------------------------------------------------

import socket
from time import sleep


class spawn:
    def __init__(self, host='10.0.1.4', port=5025):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host , port))
        print 'Connected to %s port %d' % (host, port)
        
        # alias for convenience
        self.send = self.socket.send
        self.recv = self.socket.recv
        
        self.socket.settimeout(10)
        
        # hello world
        print self.read_id()

        self.set_resolution()
        print "Set resolution to 9+1mkr "

        # clear all event registers
        self.send('*CLS\n')
        
    def read_id(self):
        return self.interpret('*IDN?')      

    def interpret(self,cmd,len=4096):
        try:
            self.send("%s\n" % cmd)
            sleep(0.5)
            rsp = None
            if cmd.find("?") > -1:
                rsp = self.recvall(len).strip()
                return rsp
        except Exception,e:
            raise e

    def recvall(self,len):
        data = "" 
        part = None
        while True:
            part = self.recv(len)
            data += part
            if part.find('\n') > -1:
                break
        return data

    def check_err(self):
        ans = self.interpret("SYSTem:ERRor?").split(',')
        if ans[0] == '0':
            print "No Error!"
        else:
            print "Remote Error is :%s,%s" % (ans[0],ans[1])

    def __del__(self):
        self.socket.close()

    def open_wvf(self,wvf):
        self.interpret("MMEMORY:OPEN:SASSet \"{}\"".format(wvf))

    def assign_wvf(self,wvf_name,ch=1):
        self.interpret("SOURCE{}:CASSET:WAVEFORM \"{}\"".format(ch,wvf_name))

    def set_resolution(self,resl=9,ch=None):
        if ch is None:
            self.interpret("SOURCE1:DAC:RESolution {}".format(resl))
            self.interpret("SOURCE2:DAC:RESolution {}".format(resl))
 
        else:
            self.interpret("SOURCE{}:DAC:RESolution {}".format(ch,resl))

    def sample_rate(self,srate=None):
        if srate is None:
            return self.interpret("CLOCk:SRATe?")
        else:
            self.interpret("CLOCk:SRATe {}".format(srate))
            
    def run_mode(self,mode='TRIG',trg_input='ATR',ch=1):
        mode_list=['CONT','TRIG','TCON']
        if mode.upper() not in mode_list:
            print "Run mode should choose from:{CONT|TRIG|TCON}" 
            return
        self.interpret("SOURce{}:RMODe {}".format(ch,mode))
        if mode.upper() =='TRIG':
            self.interpret("SOURce{}:TINPut {}".format(ch,trg_input))


    def force_trig(self,seq ='A'):
        self.interpret("TRIGGER:SEQUENCE:IMMEDIATE {}TRIGGER".format(seq.upper()))

    def inst_mode(self,mode='AWG'):
        mode_list = ['AWG','FGEN']
        if mode.upper() not in mode_list:
            print "Mode should choose between :{AWG|FGEN}"
            return
        self.interpret("INSTrument:MODE {}".format(mode.upper()))

    def play_stop(self,play=True):
        if play:
            self.interpret("AWGControl:RUN")
        else:
            self.interpret("AWGControl:STOP")

    def ch_onoff(self,onoff=None,ch=1):
        if onoff is None:
            return self.interpret("OUTPUT1:STATE?")
        else:
            self.interpret("OUTPUT{}:STATE {}".format(ch,onoff))

    def ch_Amp(self,amp=None,ch=1):
        if amp is None:
            return self.interpret("SOURCE{}:VOLTAGE:AMPLITUDE?".format(ch))
        elif amp <=500e-3 and amp>=250e-3:
            self.interpret("SOURCE{}:VOLTAGE:AMPLITUDE {}".format(ch,amp))
        else:
            print "Amplitude should be within range (250mVpp,500mVpp) "
    def __del__(self):
        self.socket.close()

        

if __name__ == '__main__':
    arb = spawn('10.0.1.9',port=4001)