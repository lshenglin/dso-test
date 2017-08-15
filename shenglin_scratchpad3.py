# This script does not control turntable. It takes VNA measurment and displays measured angle and range on GUI
import rohde_znb as rs
import LT360 as tt
import sys
import os
from time import sleep
from datetime import datetime
from socket import *
import errno
import math
import lecroy_HDO
import tek_arb
import rsSgs100
import zipfile
import shutil




version = sys.hexversion
if version >= 0x020600F0 and version < 0x03000000 :
    py2 = True    # Python 2.6 or 2.7
    from Tkinter import *
    import ttk
elif version >= 0x03000000 and version < 0x03010000 :
    py30 = True
    from tkinter import *
    import ttk
elif version >= 0x03010000:
    py31 = True
    from tkinter import *
    import tkinter.ttk as ttk
else:
    print ("""                                                                                                                                                                                                                                                    
    You do not have a version of python supporting ttk widgets..                                                                                                                                                                                                  
    You need a version >= 2.6 to execute PAGE modules.                                                                                                                                                                                                            
    """)
    sys.exit()

class GUI_Toplevel:
    def __init__(self, master=None):
        # Initialize variables
        self.angle = 0
        self.angle_calibration = 0
        self.range =0
        self.range_calibration = 0
        self.phase_ant1=0
        self.phase_ant2=0
        self.corrected_phase_delta = 0
        self.show_phase=1
        self.matlab_call_cnt = 0

        self.show_corrected_phase_delta = 0
        if self.show_corrected_phase_delta:
            self.show_phase = 0
        # Set background of toplevel window to match
        # current style
        if self.show_phase==0:
            root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth()*5/6, root.winfo_screenheight()/4))
        if self.show_corrected_phase_delta:
            root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth() * 5 / 6, root.winfo_screenheight() / 3))
        style = ttk.Style()
        theme = style.theme_use()
        default = style.lookup(theme, 'background')
        master.configure(background='ivory')
        self.state = 'begin'

        # GUI design:
        # -----------------------------------------------------------------------
        # |       Angle:(label1)     |    -1   (label3)  | (label5)   |         |
        # -----------------------------------------------------------------------
        # |    Distance:(label2)     |    2.53m(label4)  | (label6)   |         |
        # -----------------------------------------------------------------------
        # |  Phase_Ant1:(label7)     |     209 (label9)                         |
        # -----------------------------------------------------------------------
        # |  Phase_Ant2:(label8)     |     173 (label10)                        |
        # -----------------------------------------------------------------------

        self.label = Label(master)
        # self.label.place(relx=0.01+0.315, rely=0.04+0.22, relheight=.50,relwidth=0.50)
        self.label.configure(activebackground="#f9f9f9")
        self.label.configure(activeforeground="black")
        self.label.configure(background="ivory")
        self.label.configure(foreground="black")
        self.label.configure(highlightbackground="#d9d9d9")
        self.label.configure(highlightcolor="black")

        # Configure Text here.
        self.label.configure(text="Angle: ",font=("Courier",88),width=13)
        # self.label.configure(justify="center")
        self.label2 = Label(root,text="Distance: ",font=("Courier",88),width=13)
        self.label3 = Label(root, text="...", font=("Courier", 88),width=8)
        self.label4 = Label(root, text="...", font=("Courier", 88),width=8)
        # self.label5 = Label(root, text="", font=("Courier", 88), width=2)
        # self.label6 = Label(root, text="", font=("Courier", 88), width=2)
        if self.show_phase:
            self.label7 = Label(root, text="Phase Ant1: ", font=("Courier", 88),width=13)
            self.label8 = Label(root, text="Phase Ant2: ", font=("Courier", 88),width=13)
            self.label9 = Label(root, text="...", font=("Courier", 88),width=8)
            self.label10 = Label(root, text="...", font=("Courier", 88),width=8)
        elif self.show_corrected_phase_delta:
            self.label7 = Label(root, text="Phase delta: ", font=("Courier", 56), width=20)
            self.label9 = Label(root, text="...", font=("Courier", 56), width=8)


        self.label.configure(background="ivory")
        self.label2.configure(background="ivory")
        self.label3.configure(background="ivory")
        self.label4.configure(background="ivory")
        # self.label5.configure(background="ivory")
        # self.label6.configure(background="ivory")
        if self.show_phase:
            self.label7.configure(background="ivory")
            self.label8.configure(background="ivory")
            self.label9.configure(background="ivory")
            self.label10.configure(background="ivory")
        elif self.show_corrected_phase_delta:
            self.label7.configure(background="ivory")
            self.label9.configure(background="ivory")


        self.label.configure(foreground="black")
        self.label2.configure(foreground="black")
        self.label3.configure(foreground="black")
        self.label4.configure(foreground="black")
        if self.show_phase:
            self.label7.configure(foreground="black")
            self.label8.configure(foreground="black")
            self.label9.configure(foreground="black")
            self.label10.configure(foreground="black")
        elif self.show_corrected_phase_delta:
            self.label7.configure(foreground="black")
            self.label9.configure(foreground="black")

        self.label.grid(row=0, sticky=E)
        self.label2.grid(row=1, sticky=E)
        self.label3.grid(row=0, column=1, sticky=E)
        self.label4.grid(row=1, column=1,sticky = E)
        # self.label5.grid(row=0, column=2, sticky=E)
        # self.label6.grid(row=1, column=2, sticky=E)
        if self.show_phase:
            self.label7.grid(row=2, sticky=E)
            self.label8.grid(row=3, sticky=E)
            self.label9.grid(row=2, column=1, sticky=E)
            self.label10.grid(row=3, column=1,sticky = E)
        elif self.show_corrected_phase_delta:
            self.label7.grid(row=2, sticky=E)
            self.label9.grid(row=2, column=1, sticky=E)

    def GUI_update_angle(self):
        # if self.angle >360 :
        #     self.label3.configure(text="??")
        #     # self.label5.configure(background="red")
        #     self.change_bg_color('red')
        # else:

        self.label3.configure(text=("%3d" % (self.angle-self.angle_calibration)+u'\xb0'))
        if (self.angle-self.angle_calibration) < 4 and (self.angle-self.angle_calibration) > -4:
            # self.label5.configure(background="green")
            self.change_bg_color('green')
        else:
            # self.label5.configure(background="red")
            self.change_bg_color('ivory')

    def change_bg_color(self,color):
        root.configure(background=color)
        self.label.configure(background = color)
        self.label2.configure(background = color)
        self.label3.configure(background = color)
        self.label4.configure(background = color)
        # self.label5.configure(background = color)
        # self.label6.configure(background = color)
        if self.show_phase:
            self.label7.configure(background = color)
            self.label8.configure(background = color)
            self.label9.configure(background = color)
            self.label10.configure(background = color)
        elif self.show_corrected_phase_delta:
            self.label7.configure(background=color)
            self.label9.configure(background=color)



    def GUI_update_range(self):
        self.label4.configure(text=("%.2f" %(self.range-self.range_calibration) + "m"))

    def GUI_update_phase(self):
        if self.show_phase:
            self.label9.configure(text=("%3d" % (self.phase_ant1)+u'\xb0'))
            self.label10.configure(text=("%3d" % (self.phase_ant2)+u'\xb0'))
        elif self.show_corrected_phase_delta:
            self.label9.configure(text=("%3d" % (self.corrected_phase_delta) + u'\xb0'))
    # def angle_notification(self,angle):
    #     if angle < 10 and angle > -10:
    #         self.label5.configure(background="green")
    #     else:
    #         self.label5.configure(background="red")
    #     self.label6.configure(background="ivory")

    def wait(self):
        # print("something")
        self.label3.configure(text="Wait"  )
        self.label4.configure(text="Wait"  )
        # self.label5.configure(background="ivory")
    # def invalid_input(self):
    #     self.label5.configure(background="red")
    #     self.label6.configure(background="red")

    # def feed_meas_data(self,a):
    #     # -------------------------------------------------------
    #     #  This function extracts measured data from matlab ouput
    #     # -------------------------------------------------------
    #     # if isinstance(res['result'] , float):
    #     # % A legit output will be like: 291273002549055.87
    #     # % where angle =55.87, range is 2.549m, phase of ant1 is 291, phase of ant2
    #     # % is 273 in integer degrees
    #     # Below is algorithm to extract these terms
    #     self.angle = (a / 1e3 - math.floor(a/ 1e3)) * 1e3 - 360
    #     a=(a-self.angle)/1e6
    #     self.range = (a / 1e3 - math.floor(a/ 1e3)) * 1e3
    #     # res2 = round(res['result'] / 1e3) / 1e3
    #     a=(a-self.range)/1e3
    #     self.phase_ant1 = (a / 1e3 - math.floor(a/ 1e3)) * 1e3
    #     a=(a-self.phase_ant1)/1e3
    #     self.phase_ant2 = (a / 1e3 - math.floor(a/ 1e3)) * 1e3




import matlab.engine
eng = matlab.engine.start_matlab()

def update_estimate():
	timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
	print "Measuring on DSO"
	fname = 'R1_demo_' + timestamp + '.zip'
	#  1. Create DSO lab notebook
	hdo.trigger_mode('Single')
	sleep(0.5)
	hdo.new_labnb(fname)
	#  2. Trigger DSO capture
	arb.force_trig('A')
	hdo.save_entry()
	sleep(7)
	#  3. Copy lab notebook from DSO to mac folder
	hdo.import_data(file_name=fname, remote_path='D:/Xport', local_path=file_path)
	# 4. Unzip
	zip_folder = file_path
	zip_name = fname
	zip_path = zip_folder + zip_name
	with zipfile.ZipFile(zip_path, "r") as zip_ref:
		zip_ref.extractall(zip_folder)
	trace_folder = zip_folder + "MyLabNotebook/Default/" + os.listdir(zip_folder + "MyLabNotebook/Default")[0]
	# print(trace_folder)
	# 5. From traces generate DSO.mat and deletes traces folder.
	eng.cvtLecroy2Matlab(trace_folder, nargout=0)
	shutil.rmtree(zip_folder + "MyLabNotebook/")
    # 6. From DSO.mat generate output to GUI.
	dso_file = '../R1_script/DSO_mat_files/DSO.mat'
	[w.angle, w.range, w.phase_ant1, w.phase_ant2, w.corrected_phase_delta] = eng.PDOA_v1(dso_file,nargout=5)
	# sleep(10)
	print(datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
	print(w.angle)
	print(w.phase_ant1)
	print(w.phase_ant2)
	print(w.corrected_phase_delta)
	w.GUI_update_angle()
	w.GUI_update_range()
	w.GUI_update_phase()
	root.after(1, update_estimate)







    # angle = 0
    # # timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    # # file_name = 'Sparameter_' + timestamp + '.csv'
    # file_name = 'Sparameter_' + '.csv'
    # res_file = os.path.expanduser(paras['save_location']) + file_name
    # # print('********** Creating file :' + res_file)
    # output = open(res_file, 'w')
    # output.write("Angle,Freq[Hz],")
    # for i in range(len(tr_name)):
    #     output.write("%s_%s_re,%s_%s_im," % (tr_name[i], meas_obj[i], tr_name[i], meas_obj[i]))
    # output.write("\n")
    #
    # znb.interpret("INIT:ALL","*WAI")
    # # sleep(1)
    # re, im = [[], [], []], [[], [], []]
    #
    # for i in range(len(tr_name)):
    #     znb.select_active_trace(tr_name[i])
    #     re[i], im[i] = znb.save_trace_data()
    # for i in range(len(re[0])):
    #     output.write("%.15f,%.15f," % (angle, paras['freq_start'] + paras['freq_step'] * i))
    #     for j in range(len(tr_name)):
    #         output.write("%.15f,%.15f," % (re[j][i], im[j][i]))
    #     output.write("\n")
    #
    # ## Add matlab bridge below
    # output.close()
    # print("Matlab call #"+str(w.matlab_call_cnt))
    # # if w.matlab_call_cnt<220:
    # w.matlab_call_cnt+=1
    # # else:
    # #     w.wait()
    # #     w.matlab_call_cnt = 0
    # # sleep(0.1)
    # #     mlab.stop()
    # #     mlab.start()
    #
    # # res = mlab.run_func('/Users/shenglinli/Documents/R1_script/analyze_results_test.m', res_file)
    # [w.angle,w.range,w.phase_ant1,w.phase_ant2,w.corrected_phase_delta] = eng.analyze_results_test_m_engin(res_file,nargout=5)
    # # w.angle=t[0]
    # # w.range=t[1]
    # # w.phase_ant1=t[2]
    # # w.phase_ant2=t[3]
    # # w.feed_meas_data(res1,res2,res3,res4)
    # w.GUI_update_angle()
    # w.GUI_update_range()
    # w.GUI_update_phase()
    # root.after(1,update_estimate)

global default_paras
global tr_name
global meas_obj
global znb
global w
global paras
global file_path

### Intinilize  sgs100  ###
LO_freq = 6500
LO_pwr = 20
Mod_pwr = 25

timestamp1 = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
file_path ="../R1/logs/R1_demo_" + timestamp1 + '/'
os.system("mkdir " +file_path)

wvf_set = [
	['uwb_channel13_64preamble_nopayload', '20us', '-64.4e-6'],
	['uwb_channel13', '200us', '-800e-6']
		]
wvf_select = 1

# if file_path is None:
# 	self.file_path = "~/Documents/R1/logs/"
# else:
# 	self.file_path = file_path
# if LO_pwr is None:
# 	self.LO_pwr = 14
# else:
# 	self.LO_pwr = LO_pwr
# if Mod_pwr is None:
# 	self.Mod_pwr = 25  # 25 is the max power level
# else:
# 	self.Mod_pwr = Mod_pwr
# if wvf_set is None:
# 	self.wvf_set = [
# 		['uwb_channel13_64preamble_nopayload', '20us', '-64.4e-6'],
# 		['uwb_channel13', '200us', '-800e-6']
# 	]
# else:
# 	self.wvf_set = wvf_set
# if wvf_select is None:
# 	self.wvf_select = 1
# else:
# 	self.wvf_select = wvf_select





sgs1 = rsSgs100.spawn('10.0.1.4')#LO
sgs2 = rsSgs100.spawn('10.0.1.3')#TX

sgs1.freq(LO_freq)
sgs2.freq(LO_freq)
sgs1.pow(Mod_pwr)
sgs2.pow(LO_pwr)
sgs1.rfon(1)
sgs2.modon(1)
sgs2.rfon(1)

### Config ARB  ###
### open /import waveform, sample rate ###

wvf = wvf_set[wvf_select]
wvf_name = wvf[0]
timeDiv = wvf[1]
offSet = wvf[2]
srate = 8e9

print  "...Configuring arb now...."
arb = tek_arb.spawn('10.0.1.9',port=4001)
arb.inst_mode('AWG')
arb.open_wvf('C:/R1/AWG_UWB_8GHz_chan13_64pre_no_payload.mat')
arb.open_wvf('C:/R1/AWG_UWB_8GHz_chan13_1024pre_60byte.mat')
arb.assign_wvf(wvf_name,1)
arb.assign_wvf(wvf_name,2)
arb.sample_rate(srate)
arb.ch_onoff(1)
arb.run_mode('TRIG','ATR',1)
arb.run_mode('TRIG','ATR',2)
arb.play_stop()


### Intinilize DSO  ###
print "...Configuring HDO now ..."

ch_list = ['C1','C2','C3','C4','C5','C6','C7','C8']
hdo = lecroy_HDO.spawn('10.0.1.8')

hdo.set_config()
hdo.multitap_display('Normal')
hdo.time_div(timeDiv)
hdo.hor_offset(offSet)
for ch in ch_list:
	hdo.ver_div(ch,1)
	hdo.ver_offset(ch,'0')
	hdo.trace_on(ch,-1)

hdo.trigger_type('Edge')
hdo.trigger_source('Ext')
hdo.trigger_level('Ext',0.1)
hdo.trigger_slope('Positive')
hdo.trigger_coupling ('DC')
hdo.trigger_mode('Auto')




# global root
root = Tk()
root.title('R1  Demo')
root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth()*5/6, root.winfo_screenheight()/2))
root.lift()
root.focus_set()
root.attributes('-topmost', True)  # Bring it always to front
root.attributes('-topmost', False)  # Allows user to access other windows
hMsg = msg = "R1 Demo"
root.title(' %s' % hMsg)
w = GUI_Toplevel(root)

root.after(1000,update_estimate)
root.mainloop()

# mlab.stop()



