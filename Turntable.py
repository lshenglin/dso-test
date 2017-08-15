# Manually controls turn table, ZNB, matlab
# for testing and debug purpose.

import rohde_znb as rs
import LT360 as tt
import sys
import os
from time import sleep
from datetime import datetime
from socket import *
import errno

from pymatbridge import Matlab

# paras = {'angle_start': 0,
#                  'angle_step': 5,
#                  'angle_single': 30,
#                  'angle_mode': 'SWEEP',
#                  'angle_stop': 359,
#                  'freq_start': 3e9,
#                  'txpower': 10,
#                  'test_mode': 'VNA',
#                  'freq_stop': 6e9,
#                  'freq_step': 10e6,
#                  'save_location': "~/Documents/R1/"}
#
# tr_name = ['CH1Tr1', 'CH1Tr2']  # , 'CH1Tr3']
# meas_obj = ['S14', 'S24']  # , 'S34']
# Turntable manual test
lt = tt.spawn(ipAddr='10.0.1.253', port=9001)
#
#         #     # --------Set turn table to zeo position, turn turntable to certain degree--------------
# lt.zero()
lt.velocity(1)
# lt.ccw(10)

# ------------------------------------------------Manual rotation by step-------------------------------
# -----------------Set step size ----------------
lt.stepSize(10)


# -----------------Clockwise ----------------
# lt.stepCW()
# -----------------Conterclockwise ----------------
# lt.stepCCW()


# ------------------------------------------------Auto rotation -------------------------------
# lt.velocity(1)
# # -----------------Clockwise ----------------
# lt.cw(0)
# lt.cw(300)
#
# # -----------------counterClockwise ----------------
lt.ccw(160)
# lt.ccw(0)

sleep(2.1)
# if float(lt.position())<=180:
print(float(lt.position()))
# else:
    # print(float(lt.position())-360)