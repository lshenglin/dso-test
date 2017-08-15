import matlab.engine
eng = matlab.engine.start_matlab()


matlab_call_cnt = 0

while matlab_call_cnt<300:
    matlab_call_cnt+=1
    print(matlab_call_cnt)
    tf = eng.jt(matlab_call_cnt,nargout=2)
    print(tf[0])
