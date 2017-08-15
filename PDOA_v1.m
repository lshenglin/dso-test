% 08/07/2017
% Nayef Alsindi
% Apple Inc.
% PDOA_v1
% This version of PDOA returns the phase and phase difference in
% degrees. Also the AoA params are instantiated inside the function 

% Input:
% - dsoFileName         should include the directory path and file name 



% Output:           
% - aoaAcos         estimated AoA using arcos method 
% - rx1Phi          estimated phase from Rx1 converted to degrees
% - rx2Phi          estimated phase from Rx2 converted to degrees
% - rxPhiDiff       estimated phase difference between Rx1 and Rx2 in
%                   radians
% - estRange        Estimated Range (currently a place holder for future
%                   versions



function [aoaAcos, estRange, rx1Phi, rx2Phi, rxPhiDiff] = PDOA_v1(dsoFileName)
% aoaParams             structure that holds the main aoa parameters needed
%                       for estimation:
%                       1)  fc - center frequency 
%                       2)  deltaD - M-1 vector containing spacing between
%                           M antenna elements
%                       3)  c - speed of signal propagation
%                       4)  threshold - used for CIR peak detection
%                       5)  upSample - upsample the dso estimated CIR
%                       6)  method - 'acos' for now!
%                       7) phaseInit - initial phase difference (this
%                           typically should be the phase difference between
%                           the antennas at 0 degrees
aoaParams = struct('fc', 6.5e9, ...
                   'deltaD', [26*1e-3], ...
                    'c', 299792458, ...
                    'threshold', 0.9, ...
                    'upSample', 200, ...
                    'method', 'acos', ...
                    'phaseInit', 1);

% Estimate the CIR from the DSO.mat file
[temp_ht, htOSF, protosymble] = calcChanEst(dsoFileName, 200, 1, 0);
ht = htOSF.';
% ht = resample(ht, aoaParams.upSample, 1);
% detect the complex first path arrival for the M antennas
rxPhiAll = peakDetection(ht, aoaParams.threshold);


% Estimate the phase difference between the M antennas (should be M-1
% vector
rxPhiDiffAll = estPhiDiff(rxPhiAll);


% Pick out first two antenna phases
rxPhi = rxPhiAll(1:2);
% pick out first phase difference between Rx1/2
rxPhiDiff = rxPhiDiffAll(1);


% estimate the AoA from the phase differences using the 'acos' method
% phaseInit - is the phase difference between antennas1 and 2 at 0 degrees.
% This is used to calibrate the phase to 0!
%
% 
aoaAcos = estAoA(rxPhiDiff, ...
                 aoaParams.fc, ... 
                 aoaParams.c, ..., 
                 aoaParams.deltaD, ...
                 aoaParams.method, ...
                 aoaParams.phaseInit);

% convert to degrees
rx1Phi = round(angle(rxPhi(1))/pi*180+180);%in degrees
rx2Phi = round(angle(rxPhi(2))/pi*180+180);

% phase of rxPhiDiff
rxPhiDiff = angle(aoaParams.phaseInit*rxPhiDiff); 


% place holder - include a function to estimate the range
%[]
estRange = 0;
return;
end

