# This script reads UWB sweep data (a folder of zip files) from TeleDyne Lecroy and generates a folder of DSO.mat files.
#
import os
import zipfile
import shutil
import time
import matlab.engine
eng = matlab.engine.start_matlab()

zip_folder = "/Users/shenglinli/Documents/R1/logs/2017_08_01_16_52_01/"

cnt=1
for angle in range(0,361,5):
    for iteration in range(1,4):
        print(str(angle),'#',str(iteration))
        start_time = time.time()
        for root, dirs, files in os.walk(zip_folder):
            for file in files:
                if file.startswith("Angle%d_"%angle) and (file.find('Iter%d'%iteration)!=-1):
                    with zipfile.ZipFile(zip_folder+file, "r") as zip_ref:
                        zip_ref.extractall(zip_folder)
                    timestamp = time.time()
                    print("Unzip costs "+ str(timestamp-start_time))
                    # print((timestamp2.seconds - timestamp.seconds))
                    trace_folder = zip_folder + "MyLabNotebook/Default/" + os.listdir(zip_folder + "MyLabNotebook/Default")[
                        0]
                    print(trace_folder)
                    eng.cvtLecroy2Matlab(trace_folder, angle,iteration,cnt, nargout=0)
                    # timestamp3 = timedelta()
                    print("matlab costs " + str(time.time()-timestamp))
                    shutil.rmtree(zip_folder+"MyLabNotebook/")
                    cnt=cnt+1