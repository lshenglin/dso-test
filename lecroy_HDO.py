# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
#!/usr/bin/env python
# Use partial of the script from LeCrunch @https://bitbucket.org/tlatorre/lecrunch/src/a2650454083c7d453841c11f2c585bea1118bf9c/lecroy.py?at=default 
""" 
Module to use LeCroy oscilloscope HDO8108.
To use import_data function to transfer files from remote pc to local, need to install sshpass first.
Author : Jade Yu 
Date : 09/2016
"""

import struct
import os
import socket
from time import sleep

headerformat = '>BBBBL'
CHAN_LIST = ['C1','C2','C3','C4','C5','C6','C7','C8']
errors = { 1  : 'unrecognized command/query header',
           2  : 'illegal header path',
           3  : 'illegal number',
           4  : 'illegal number suffix',
           5  : 'unrecognized keyword',
           6  : 'string error',
           7  : 'GET embedded in another message',
           10 : 'arbitrary data block expected',
           11 : 'non-digit character in byte count field of arbitrary data '
                'block',
           12 : 'EOI detected during definite length data block transfer',
           13 : 'extra bytes detected during definite length data block '
                'transfer' }

class spawn:
    def __init__(self, host='10.0.1.8', port=1861):
        self.ip_addr = host
        self.username = 'lab'
        self.password = 'lablab'
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host , port))
        self.socket.settimeout(10)
        self.remote_path ='/cygdrive/d/Xport'
        print 'Connected to %s port %d' % (host, port)
        
        # # alias for convenience
        # self.send = self.socket.send
        # self.recv = self.socket.recv
     
        # hello world
        print self.read_id()
         
        #Change all channels couplings to 50ohm
        self.ch_coupling()
        print "Changed all channels coupling to 50ohm "
        self.max_memory('25MA')
        print "Set Max sample points to 25MS"


        # clear all event registers
        self.send('*CLS\n')
        
    def read_id(self):
        return self.interpret('*IDN?')      

    def interpret(self,cmd,len=4096):
        try:
            self.send("%s" % cmd)
            # sleep(0.5)
            rsp = None
            if cmd.find("?") > -1 :
                rsp = self.recv().strip()
                return rsp
        except Exception,e:
            raise e
    def send(self, msg):
        """Format and send the string `msg`."""
        if not msg.endswith('\n'):
            msg += '\n'
        header = struct.pack(headerformat, 129, 1, 1, 0, len(msg))
        self.socket.sendall(header + msg)

    def check_last_command(self):
        """
        Check that the last command sent was received okay; if not, raise
        an exception with details about the error.
        """
        self.send('cmr?')
        err = int(self.recv().split(' ')[-1].rstrip('\n'))

        if err in errors:
            self.socket.close()
            raise Exception(errors[err])

    def recv(self):
        """Return a message from the scope."""
        reply = ''
        while True:
            header = ''

            while len(header) < 8:
                header += self.socket.recv(8 - len(header))

            operation, headerver, seqnum, spare, totalbytes = \
                struct.unpack(headerformat, header)
            buffer = ''
            while len(buffer) < totalbytes:
                buffer += self.socket.recv(totalbytes - len(buffer))

            reply += buffer

            if operation % 2:
                break

        return reply
    def recvall(self,len):
        data = "" 
        part = None
        while True:
            part = self.recv(len)
            data += part
            if part.find('\n') > -1:
                break
        return data

    def ch_coupling(self,value='D50'):
        if value not in ['D50','D1M','A1M','GND']:
            print "coupling value should in this list :'D50','D1M','A1M','GND'"
        for ch in CHAN_LIST:
            self.interpret("%s:COUPLING %s" % (ch,value))

    def max_memory(self,sample_pts):
        self.interpret("Memory_SIZe {}".format(sample_pts))

    def sample_rate(self,rate=2.5e9):
        self.interpret("VBS 'app.Acquisition.Horizontal.SampleRate={}'".format(rate))

    def time_div(self,tiv='200us'):
        if tiv:
            self.interpret("TDIV {}".format(tiv))
        else:
            return self.interpret("TDIV?").split(" ")[1]

    def hor_offset(self,delay=None):
        if delay:
            self.interpret("VBS 'app.Acquisition.Horizontal.HorOffset = {}'".format(delay))
        else :
            return self.interpret("VBS? 'Return=app.Acquisition.Horizontal.HorOffset'").split(" ")[1]

    def trace_on(self,ch='C1',onoff=None):
        ###  onoff shoud be in [0,-1,'false','true' ]   ###
        if onoff is None:
            return hdo.interpret("VBS? 'Return=app.Acquisition.{}.View'".format(ch)).split(" ")[1]
        else:
            self.interpret("VBS 'app.Acquisition.{}.View={}'".format(ch,onoff))

    def ver_div(self,ch='C1',viv=None):
        if viv:
            self.interpret("VBS 'app.Acquisition.{}.VerScale ={}'".format(ch,viv))
        else:
            return self.interpret("VBS? 'Return=app.Acquisition.{}.VerScale'".format(ch)).split(" ")[1]

    def ver_offset(self,ch='C1',offset=None):
        if offset != None:
            self.interpret("VBS 'app.Acquisition.{}.VerOffset={}'".format(ch,offset))
        else:
            return self.interpret("VBS? 'Return=app.Acquisition.{}.VerOffset'".format(ch)).split(" ")[1]

    def save_entry(self,entry_note=None):
        if entry_note:
            pass
        else:
            self.interpret("VBS 'app.LabNotebook.Save'")

    def save_wvfm(self,source='C1',dir='D:/WaveForms',trc_name='00'):
        ###  source can be C1~C8, M1~M12, F1~F12,Z1~Z12   ###
        # self.interpret("VBS 'app.SaveRecall.Waveform.SaveTo = \"File\"'")    
        self.interpret("VBS 'app.SaveRecall.Waveform.SaveSource = \"{}\"'".format(source))
        # self.interpret("VBS 'app.SaveRecall.Waveform.WaveformDir =\"{}\"'".format(dir))
        # self.interpret("VBS 'app.SaveRecall.Waveform.TraceTitle =\"{}\"'".format(trc_name))
        self.interpret("VBS 'app.SaveRecall.Waveform.DoSave'")

    def set_config(self,prompt='False',scribble='False'):
        #Set to False to prevent promt screen pops up before saving for description and anotation window 
        self.interpret("VBS 'app.LabNotebook.PromptBeforeSaving = {}'".format(prompt))
        self.interpret("VBS 'app.LabNotebook.ScribbleBeforeSaving = {}'".format(scribble))

    def new_labnb(self,labnb_name=None):
        if labnb_name:
            self.interpret("VBS 'app.LabNotebook.StartNewLabNotebookMD=\"{}\"'".format(labnb_name))
        else:
            self.interpret("VBS 'app.LabNotebook.StartNew'")
        #self.interpret("VBS 'app.LabNotebook.StartNewLabNotebookMD=\"D:\Xport\zzz.zip\"'")

    def recall_labnb(self):
        self.interpret("VBS 'app.LabNotebook.FlashBackToRecord'")

    def import_entries(self,labnb_name='D:\XPort\labconfig.zip'):
        self.interpret("VBS 'app.LabNotebook.ImportEntriesFrom=\"{}\"'".format(labnb_name))


    def trigger_mode(self,tri_mode =None):
        mode_list = ['Normal','Single','Stopped','Auto']
        if tri_mode is None:
            self.interpret("TRig_MoDe?").split(" ")[1]
            return self.interpret("TRig_MoDe?").split(" ")[1]
        elif tri_mode in mode_list:
            self.interpret("VBS 'app.Acquisition.TriggerMode = \"{}\"'".format(tri_mode))
        else:
            print "Trigger mode should choose from: Auto/Single/Normal/Stopped"

    def trigger_type(self,type=None):
        if type:
            self.interpret("VBS 'app.Acquisition.Trigger.Type={}'".format(type))
        else:
            return self.interpret("VBS? 'Return=app.Acquisition.Trigger.Type'").split(" ")[1]


    def trigger_source(self,source=None):
        if source:
            self.interpret("VBS 'app.Acquisition.Trigger.Source = \"{}\"'".format(source))
        else:
            return self.interpret("VBS? 'Return=app.Acquisition.Trigger.Source'").split(" ")[1]

    def trigger_level(self,ch='C8',level=None):
        if level:
            self.interpret("VBS 'app.Acquisition.Trigger.{}.Level = {}'".format(ch,level))
        else:
            return self.interpret("VBS? 'Return=app.Acquisition.Trigger.{}.Level'".format(ch)).split(" ")[1]   

    def trigger_slope(self,slope=None):
        slope_list = ['Positive','Negative','Either']
        if slope in slope_list:
            self.interpret("VBS 'app.Acquisition.Trigger.Edge.Slope={}'".format(slope))
        elif slope is None:
            return self.interpret("VBS? 'Return=app.Acquisition.Trigger.Edge.Slope'").split(" ")[1]
        else:
            print "Slope value should choose from {}".format(slope_list)   

    def trigger_coupling(self,coupling=None):
        coupling_list = ['DC','AC','LFREJ','HFREJ']
        if coupling in coupling_list:
            self.interpret("VBS 'app.Acquisition.Trigger.Edge.Coupling={}'".format(coupling))
        elif coupling is None:
            return self.interpret("VBS? 'Return=app.Acquisition.Trigger.Edge.Coupling'").split(" ")[1]
        else:
            print "Coupling value should choose from {}".format(coupling_list)     

    def measure_showtable(self,showtable=None):
        if showtable is None:
            self.interpret("VBS? 'Return=app.Measure.ShowMeasure'").split(" ")[1]
        else:
            self.interpret("VBS 'app.Measure.ShowMeasure={}'".format(showtable))
    def measure_state(self,state=None):
        if showtable is None:
            self.interpret("VBS? 'Return=app.Measure.StatsOn'").split(" ")[1]
        else:
            self.interpret("VBS 'app.app.Measure.StatsOn={}'".format(state))

    def measure_histo(self,histo=None):
        if showtable is None:
            self.interpret("VBS? 'Return=app.Measure.HistoOn'").split(" ")[1]
        else:
            self.interpret("VBS 'app.Measure.HistoOn={}'".format(histo))
            

    def measure_source(self,meas_ID=1,source1=None,source2=None):
        if source1 is None or source2 is None:
            source1 =  self.interpret("VBS? 'Return=app.Measure.P{}.Source1'".format(meas_ID)).split(" ")[1]
            source2 =  self.interpret("VBS? 'Return=app.Measure.P{}.Source2'".format(meas_ID)).split(" ")[1]
            return source1,source2
        self.interpret("VBS 'app.Measure.P{}.Source1=\"{}\"'".format(meas_ID,source1))
        self.interpret("VBS 'app.Measure.P{}.Source1=\"{}\"'".format(meas_ID,source2))

    def measure_param(self,param=None,meas_ID=1):
        if param:
            self.interpret("VBS 'app.Measure.P{}.ParamEngine=\"{}\"'".format(meas_ID,param))
        else:
            return self.interpret("VBS? 'Return=app.Measure.P{}.ParamEngine'".format(meas_ID)).split(" ")[1]

    def measure_type(self,type=None,meas_ID=1):
        type_list = ['measure','math','WebEdit']
        if type in type_list:
            self.interpret("VBS 'app.Measure.P{}.MeasurementType=\"{}\"'".format(meas_ID,type))
        elif type is None:
            return self.interpret("VBS? 'Return=app.Measure.P{}.MeasurementType'".format(meas_ID)).split(" ")[1]
        else:
            print "Type value should choose from {}".format(type_list)         

    def measure_view(self,view=None,p=1):
        view_list = ['true','false',-1,0]
        if view in view_list:
            self.interpret("VBS 'app.Measure.P{}.view={}'".format(p,view))
        elif view is None:
            self.interpret("VBS? 'Return=app.Measure.P{}.view'".format(p)).split(" ")[1]
        else:
            print "view value should choose from {}".format(view_list)

    def math_traceon(self,enable=None,f=1):
        enable_list = ['true','false',-1,0]
        if enable in enable_list:
            self.interpret("VBS 'app.Math.F{}.View={}'".format(f,enable))
        elif enable is None:
            self.interpret("VBS? 'Return=app.Math.F{}.view'".format(f)).split(" ")[1]
        else:
            print "view value should choose from {}".format(enable_list)    

    def clear_sweeps(self):
        self.interpret("CLSW")

    def import_data(self,file_name='ss.zip',remote_path='/cygdrive/d/Xport',local_path='~/Documents'):
        if file_name.find('.') >-1:
            print "Copying file from DSO to local machine..."
            os.system("sshpass -p \"{}\" scp {}@{}:{}/{} {}".format(self.password,self.username,self.ip_addr,remote_path,file_name,local_path))
        else:
            print "Copying folder from DSO to local machine..."
            os.system("sshpass -p \"{}\" scp -r {}@{}:{}/{} {}".format(self.password,self.username,self.ip_addr,remote_path,file_name,local_path))

    def multitap_display(self,mode=None):
        mode_list = ['Normal','Single','Dual','Mosaic']
        if mode in mode_list:
            self.interpret("VBS 'app.Display.MultiTabMode=\"{}\"'".format(mode))
        elif mode is None:
            return self.interpret("VBS? 'Return=Return=app.Display.MultiTabMode'").split(" ")[1]
        else:
            print "Multitap value should choose from {}".format(mode_list)
    def grid_ontop(self,enable='false'):
        pass

    # def sample_rate(self,rate):
    #     self.send("VBS 'app.Acquisition.Horizontal.MaxSamples = 500'")

    # def fix_saprate(self):
    #     self.send("VBS 'app.Acquisition.Horizontal.SmartMemory = "FixedSampleRate"'")


    def __del__(self):
        self.socket.close()

  
if __name__ == '__main__':
    hdo = spawn('10.0.1.8')