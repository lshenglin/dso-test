% 08/07/2017
% Nayef Alsindi
% Apple, Inc. 
% This main function tests the PDOA function to estimate the AoA using the
% acos method.
% PDOA Input:
% dsoFileName           DSO file name including the directory path
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

% main function to test the new PDOA function
% The following assumes 3 antennas separated by 26 mm and the following
% aoaParams!

aoaParams = struct('fc', 6.5e9, ...
                   'deltaD', [26*1e-3;26*1e-3], ...
                    'c', 299792458, ...
                    'threshold', 0.9, ...
                    'upSample', 200, ...
                    'method', 'acos', ...
                    'phaseInit', 1);
                

dsoFileName = ['/Users/shenglinli/Documents/R1_script/DSO_mat_files/001-DSO0-1.mat'];

[aoaAcos, rxPhi, rxPhiDiff, estRange] = PDOA(dsoFileName, aoaParams)
