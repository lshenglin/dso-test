
#! /usr/bin/env python

import argparse
import os,sys
import lecroy_HDO
import LT360
import tek_arb
import rsSgs100
from time import sleep
from datetime import datetime
import zipfile
import shutil
import matlab.engine
eng = matlab.engine.start_matlab()


class spawn:
	def __init__(self,fid=None,file_path=None,LO_pwr=None,Mod_pwr=None,wvf_set=None,wvf_select=None):
		# if fid is None:       self.fid =os.path.expanduser('~/Documents/R1/UWB_angle_5.csv')
		# else :                self.fid = fid
		if file_path is None :self.file_path =  "~/Documents/R1/logs/"
		else :                self.file_path = file_path
		if LO_pwr is None :   self.LO_pwr = 14
		else :                self.LO_pwr = LO_pwr
		if Mod_pwr is None :  self.Mod_pwr = 25      # 25 is the max power level
		else :                self.Mod_pwr = Mod_pwr
		if wvf_set is None :  self.wvf_set = [
					['uwb_channel13_64preamble_nopayload','20us','-64.4e-6'],
					['uwb_channel13','200us','-800e-6']
					                         ]
		else :                self.wvf_set = wvf_set
		if wvf_select is None: self.wvf_select = 1
		else :                 self.wvf_select = wvf_select

	def main_test(self):
		# fid = open(self.fid)
		# lines = fid.readlines()
		# if len(lines) > 1:
		#    angle_list = [x.strip().replace('"','').split(',') for x in lines]
		# else:
		# 	angle_list = [x.strip().replace('"','').split(',') for x in lines[0].split('\r')]
		# fid.close()
		angle_list =range(0,1,5)
		repeat = 3
		print(angle_list)
		### Intinilize  sgs100  ###
		LO_freq = 6500

		sgs1 = rsSgs100.spawn('10.0.1.4')#LO
		sgs2 = rsSgs100.spawn('10.0.1.3')#TX

		sgs1.freq(LO_freq)
		sgs2.freq(LO_freq)
		sgs1.pow(self.Mod_pwr)
		sgs2.pow(self.LO_pwr)
		sgs1.rfon(1)
		sgs2.modon(1)
		sgs2.rfon(1)

		### Config ARB  ###
		### open /import waveform, sample rate ###

		wvf = self.wvf_set[self.wvf_select]
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

		##### Turntable spining from here  #####
		lt = LT360.spawn(ipAddr='10.0.1.253',port =9001)
		print "Set turn table angle to 0 "
		# lt.zero()
		timestamp1 = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
		self.file_path =self. file_path + timestamp1 + '/'
		os.system("mkdir " +self.file_path)
		cnt=0
		for angle in angle_list:
			lt.ccw(float(angle))
			sleep(4)
			for iteration in range(1,repeat+1):
				# print "Measuring angle %s at iteration %s" % (angle[1],angle[0])
				timestamp2 = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
				# hdo.trigger_mode('Auto')
				hdo.trigger_mode('Single')
				sleep(0.5)
				fname = 'Angle' + str(angle) + '_Iter' + str(iteration) +'_Time' + timestamp2 + '.zip'
				# fname = 'Angle' + str(angle[1]) + '_Iter' + str(angle[0]) + '.zip'
				print "Measuring angle %s at iteration %s" % (angle, iteration)
				hdo.new_labnb(fname)
				arb.force_trig('A')
				hdo.save_entry ()
				sleep(7)
				hdo.import_data(file_name=fname,remote_path='D:/Xport',local_path = self.file_path)
				# hdo.trigger_mode('Stopped')
				zip_folder = "../R1/logs/" + timestamp1 + '/'
				zip_name = fname
				zip_path = zip_folder + zip_name
				with zipfile.ZipFile(zip_path,"r") as zip_ref:
					zip_ref.extractall(zip_folder)
				trace_folder = zip_folder + "MyLabNotebook/Default/" + os.listdir(zip_folder + "MyLabNotebook/Default")[0]
				print(trace_folder)
				eng.cvtLecroy2Matlab(trace_folder, angle,iteration,cnt, nargout=0)
				shutil.rmtree(zip_folder+"MyLabNotebook/")
				cnt=cnt+1

		lt.angle(0)
		sgs1.rfon(0)
		sgs2.rfon(0)


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="controls R1 all equipments on turn table")
	parser.add_argument('--fangle',   default=None, help="angle csv file")
 	parser.add_argument('--refpwr', default=None, type=float,help="reference signal power in dBm")
 	parser.add_argument('--LOpwr',   default=None, type=float,help="LO power in dBm")
 	parser.add_argument('--fpath',   default=None, help="output file path")
  	parser.add_argument('--wvf_select',   default=None, type=int, help="which waveform index to choose")
  	parser.add_argument('--wvf_set',    default=None, type=list,help="waveform set in cludes HDO horizontal setting")
  	args = parser.parse_args()
  	r1 = spawn(fid=args.fangle,file_path=args.fpath,LO_pwr=args.LOpwr,Mod_pwr=args.refpwr,wvf_set=args.wvf_set,wvf_select=args.wvf_select)
  	r1.main_test()
