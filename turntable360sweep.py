import rohde_znb as rs
import LT360 as tt
import sys
import os
from time import sleep
from datetime import datetime
from socket import *
import errno

default_paras ={ 'angle_start': 0, 
				 'angle_step': 2,
				 'angle_single': 30, 
  				 'angle_mode': 'SWEEP', 
  				 'angle_stop': 359,
  				 'freq_start': 6.25e9,
				 'txpower': 10, 
 				 'test_mode': 'VNA', 
 				 'freq_stop': 6.75e9,
 				 'freq_step': 10e6,
 				 'save_location' : "~/Documents/R1/"}



def vna(paras=default_paras):
	if paras['test_mode'] is not 'VNA':
		raise Exception("Wrong test mode :%s" % paras['test_mode'])
		exit()
	if paras['angle_mode'].upper() == 'SWEEP':
		angle_list  = range(int(paras['angle_start']),int(paras['angle_stop']+paras['angle_step']),int(paras['angle_step']))
	elif paras['angle_mode'].upper() =='SINGLE':
		angle_list = [paras['angle_single']]
	else:
		raise Exception("Wrong angle mode :%s, angle mode should be either SINGLE or SWEEP " % paras['angle_mode'])
		exit()

	for test_attempt in range(1, 5):
		timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
		file_name = 'Sparameter_' + timestamp + '.csv'
		res_file = os.path.expanduser(paras['save_location']) + file_name
		output=open(res_file,'w')
		tr_name = ['CH1Tr1','CH1Tr2','CH1Tr3']
		meas_obj = ['S14','S24','S34']
		znb = rs.spawn('10.0.1.88')
		try:
			lt = tt.spawn(ipAddr='10.0.1.253',port =9001)

			znb.set_freq_range(paras['freq_start'],paras['freq_stop'])
			znb.set_sweep_params(paras['freq_step'],auto=1)

			#--------Set turn table to zeo position, turn turntable to certain degree--------------
			lt.zero()
			output.write("Angle,Freq[Hz],")
			for i in range(len(tr_name)):
				output.write("%s_%s_re,%s_%s_im," % (tr_name[i],meas_obj[i],tr_name[i],meas_obj[i]))
			output.write("\n")

			for angle in angle_list:
				lt.ccw(angle)
				print "Turn table set to %s degree\n" % angle
				sleep(5)
			#--------Create New trace for S21,31,41 measurement, trace name format should follow 'CH#Tr#'------------
				znb.delete_all_trace()
				for i in range(len(tr_name)):
					znb.create_new_trace(tr_name[i],meas_obj[i])

			#--------Set sweep to single mode nad start sweep once-------------
				znb.set_sweep_control(1,single=True)
				sleep(2)
				re,im = [[],[],[]],[[],[],[]]
				for i in range(len(tr_name)):
					znb.select_active_trace(tr_name[i])
					re[i],im[i] = znb.save_trace_data()
					znb.update_display('ON')

				for i in range(len(re[0])):
					output.write("%.15f,%.15f," % (angle,paras['freq_start']+paras['freq_step']*i))
					for j in range(len(tr_name)):
					#print"%f,%f,%f\n" % (START_FREQ+STEP_SIZE*i,re[i],im[i])
						output.write("%.15f,%.15f," % (re[j][i],im[j][i]))
					output.write("\n")
			#data = znb.interpret("TRAC? CH1DATA").split(',')
			break
		except (timeout, error) as socket_Error:
			print('Oops! Socket ethernet issue. Most likely powerline ethernet connection failure. Will re-initiate test for a maximum of 4 times. This is testrun #' + str(test_attempt + 1))
			output.close()
			continue


if __name__ == "__main__":
	vna()

