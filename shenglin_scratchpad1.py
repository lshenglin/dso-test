import argparse
import os,sys
import lecroy_HDO
import LT360
import tek_arb
import rsSgs100
from time import sleep
from datetime import datetime
# arb = tek_arb.spawn('10.0.1.9',port=4001)
# hdo = lecroy_HDO.spawn('10.0.1.8')

# remote_path='/cygdrive/d/Xport'

# hdo.interpret("VBS DELF, FILE, 'Angle360_Iter37_Time2017_07_28_11_53_52.zip'")
# import zipfile
# import matlab.engine
# eng = matlab.engine.start_matlab()
#
# zip_folder = "../R1/logs/" + "2017_07_26_15_03_22" + '/'
# zip_name = 'Angle0_Iter1.zip'
#
#     # zip_path = '~/Documents/R1/logs/2017_07_26_14_22_58/Angle0_Iter1_Time2017_07_26_14_22_58.zip'
# zip_path = zip_folder + zip_name
# with zipfile.ZipFile(zip_path,"r") as zip_ref:
#     zip_ref.extractall(zip_folder)
#
# print(os.listdir(zip_folder + "MyLabNotebook/Default"))
# trace_folder = zip_folder + "MyLabNotebook/Default/" + os.listdir(zip_folder + "MyLabNotebook/Default")[0]
#
# print(trace_folder)
# eng.cvtLecroy2Matlab(trace_folder,0,nargout=0)


sgs1 = rsSgs100.spawn('10.0.1.3')#Gen
sgs2 = rsSgs100.spawn('10.0.1.4')#LO
#
sgs1.pow(25)
sgs2.pow(20)

sgs1.freq(6500)
sgs2.freq(6500)
sgs1.modon(1)
sgs2.modon(0)
#
sgs1.rfon(1)
sgs2.rfon(1)
# #
# print('rf output enabled: %s' % sgs1.rfon())
# print('rf freq MHz: %s' % sgs1.freq())
# print('rf power: %s' % sgs1.pow())
#
#
# print('rf output enabled: %s' % sgs2.rfon())
# print('rf freq MHz: %s' % sgs2.freq())
# print('rf power: %s' % sgs2.pow())


# print  "...Configuring arb now...."
# # wvf_set = [
# # 					['uwb_channel13_64preamble_nopayload','20us','-64.4e-6'],
# # 					['uwb_channel13','200us','-800e-6']
#

# arb.inst_mode('AWG')
# arb.open_wvf('C:/R1/AWG_UWB_8GHz_chan13_64pre_no_payload.mat')
# arb.open_wvf('C:/R1/AWG_UWB_8GHz_chan13_1024pre_60byte.mat')
# arb.assign_wvf('uwb_channel13_64preamble_nopayload',1)
# arb.assign_wvf('uwb_channel13',2)
# arb.sample_rate(8e9)
# arb.ch_onoff(1)
# arb.run_mode('TRIG','ATR',1)
# arb.run_mode('TRIG','ATR',2)
# # arb.play_stop()
# hdo.trigger_mode('Single')
# sleep(0.5)
# arb.force_trig('A')

# fname = 'Angle' + '0' + '_Iter' + '1' +'_Time' + '2017_07_25_14_39_32' + '.zip'
#
# hdo = lecroy_HDO.spawn('10.0.1.8')
#
#
# hdo.import_data(file_name=fname,remote_path='D:/Xport',local_path = '~/Documents')

# hdo.interpret('DATA:SOU CH1')
# hdo.interpret('DATA:WIDTH 1')
# hdo.interpret('DATA:ENC RPB')

# import matplotlib.pyplot as plt
# from readTrc import readTrc
#
# for ch in range(1,2):
#     print("C%d:WAVEFORM?"%ch)
#
#     data = hdo.interpret("C%d:WAVEFORM?"%ch)
#     [x,y,d] = readTrc(data)
#     # print(data)
#     plt.plot(x,y)
#     plt.xlabel('s')
#     plt.ylabel('V')
#     plt.show()
    # f = open('test/C%.trc'%ch, 'w')
    # f.write(data)
    # f.close()
# print(data)

