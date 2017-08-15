# -----------------------------------------------------------------------------
# FILENAME : rohde_znb.py
# AUTHOR : Jade Yu
# DATE : 8/4/2016

# -----------------------------------------------------------------------------
# DESCRIPTION: Module to control the R&S ZNB
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

        # clear all event registers
        self.send('*CLS\n')
        
    def read_id(self):
        return self.interpret('*IDN?')      

    def interpret(self,cmd,len=4096):
        try:
            self.send("%s\n" % cmd)
            # sleep(0.5)
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

    
    def set_freq_range(self,start='3GHz',stop='8GHz'):
        # start and stop should be within range 9 kHz to 8.5 GHz
        self.interpret("SENSe:FREQuency:STARt {}".format(start).upper())
        self.interpret("SENSe:FREQuency:STOP {}".format(stop).upper())
        
    def set_sweep_params(self,step_size=1000000,points=None,sweep_time=None,auto=None):
        # mininum sweep time is decided by frequency sweep range and setp size, do not change it often, refer to 6.3.15.18

        self.interpret("SWEep:STEP {}".format(step_size))
        if points:
            self.interpret("SWEep:POIN {}".format(points))
        if sweep_time:
            self.interpret("SWE:TIME {}".format(sweep_time))
        if auto:
            self.interpret("SWEep:TIME:AUTO {}".format(auto))

    def set_sweep_type(self,type ='LIN'):
        # type option:  LINear | LOGarithmic | POWer | CW | POINt | SEGMent
        self.interpret("SWE:TYPE {}".format(type))

    def set_sweep_control(self,count=1,single=True):
        if single :
            self.interpret("INIT:CONT OFF")
            self.interpret("SWEep:COUNt {}".format(count))
            self.interpret("INIT:ALL")        #Restart one time single sweep
        else:
            self.interpret("INIT:CONT ON")


    def create_new_trace(self,trace_name,trace_result,format_type='MLOG'):
        # trace_name format should follow "CH1Tr2"
        self.interpret("CALC1:PAR:SDEF '{}', '{}'".format(trace_name,trace_result))
        # format type can be chosen from MLINear | MLOGarithmic | PHASe | UPHase | POLar | SMITh | ISMith | GDELay | REAL | IMAGinary | SWR | COMPlex | MAGNitude
        # self.interpret("CALC1:FORM {}".format(format_type))      
        window = trace_name.split('Tr')[1]
        print "Creating New trace %s for %s on window%s" % (trace_name,trace_result,window)
        self.interpret("DISPlay:WINDow{}:STATe ON".format(window))   # display new trace in new window
        # self.interpret("CALC1:FORM {}; :DISP:WIND:TRAC{}:FEED '{}'".format(format_type,window,trace_name))
        self.interpret("DISPlay:WINDow{}:TRACe{}:FEED '{}'".format(window,window,trace_name))
        self.interpret("SYSTem:DISPlay:UPDate ONCE")                  # update window display

    def delete_all_trace(self):

        self.interpret("CALCulate:PARameter:DELete:ALL")
        self.interpret("SYSTem:DISPlay:UPDate ONCE") 


    def save_trace_data_local(self,trace_name,file_name,format_type='LOGPhase'):
        # data = self.interpret("TRAC? CH1DATA").split(',')
        # for i in range(len(data)-1):
        #     re,im= data[i],data[i+1]
        # return re,im
        self.interpret("MMEM:STOR:TRAC '{}', '{}', UNFORMatted, {}".format(trace_name,file_name,format_type),"*WAI")
        # self.interpret("*WAI")
        # sleep(0.5)

    def select_active_trace(self,trace_name):
        self.interpret("CALCULATE:PARAMETER:SELECT '{}'".format(trace_name),"*WAI")
        # self.interpret("*WAI")

    def save_trace_data(self):
        self.interpret("*WAI")
        data = self.interpret("TRAC? CH1DATA").split(',')
        i = 0
        re ,im = [],[]
        while i < len(data) - 1:
            re.append(float(data[i]))
            im.append(float(data[i+1]))
            i += 2
        return re,im

    def update_display(self,display):
        display_list = ['ON','OFF','ONCE']
        if display.upper() in display_list:
            self.interpret("SYSTem:DISPlay:UPDate {}".format(display.upper()))
        else:
            print "Display value should choose from: {}".format(display_list)

       # znb.interpret("MMEM:STOR:TRAC 'CH1Tr1', 'C:\Users\Public\Documents\Rohde-Schwarz\Vna\Traces\Trc7.dat', UNFORMatted, LOGPhase")
       #       interpret("CALCulate:DATA:CALL:CATalog?")   #  "S21,S31"
       #       znb.interpret("MMEM:STOR:TRAC 'CH1Tr1', 'C:\Users\Public\Documents\Rohde-Schwarz\Vna\Traces\Trc7.dat', UNFORMatted, LOGPhase")
       # znb.interpret("MMEM:STOR:TRAC 'CH1Tr1', 'C:\Users\Public\Documents\Rohde-Schwarz\Vna\Traces\Trc8.dat'")


if __name__ == '__main__':
    znb = spawn('10.0.1.10',port=4001)