% 08/07/2017
% Nayef Alsindi
% Apple, Inc. 
% Function to estimate the Angle of Arrival (AoA) based on the arcosine
% method. This can be modified later to include more methods.
% Input:
% - estPhiDiff      estimated phase differences between M antenna elements
% - fc              center frequency in Hz
% - c               speed of signal propagation m/s (e.g. 3e8)
% - deltaD          antenna spacings (M-1x1 vector for M elements)
% - method          'acos' for now
% - phaseInit       initial phase offset between the antenna elements at 0
%                   degree. This can be used to calibrate the initial offset
%
% Output:
% - aoaAcos         (M-1x1) estimates of the AoA between M elements. This
%                   can be modified to average or discard erraneous ones!

function aoaAcos = estAoA(estPhiDiff, fc, c, deltaD, method, phaseInit)


if strcmp(method, 'acos')
    
    aoaAcos = acos(angle(phaseInit*estPhiDiff) * c/fc/2/pi./deltaD) ...
              * 180/pi - 90;
else
    % populate with other methods later!
end

return
