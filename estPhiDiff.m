% 08/07/2017
% Nayef Alsindi
% Apple, Inc.
% This function estimates the phase differences between the M antenna
% elements. 
% Input     Mx1 vector of antenna phases
% Output    (M-1)x1 vector of phase differences between antenna elements

function [estPhiDiff] = estPhiDiff(fpVector)

phiDiffMatrix = fpVector*fpVector';

% phase differences between antennas 1-2 and 2-3
estPhiDiff = diag(phiDiffMatrix, -1);


return