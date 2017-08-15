function [A, epsilon, gamma] = estSinusoid(ang, phaseinput)
%% This function tries to fit a sinsoid with an unknown amplitude, initial
%% phase and DC offset
%
% [A, epsilon, gamma] = estSinusoid(ang, phaseinput)
%
% Input:
%   ang         :     angle for the measurement in degree
%   phaseinput  :     phase observation for ang
% Output:
%   A           :     magnitude of the sinusoid
%   epsilon     :     initial phase in degrees
%   gamma       :     DC offset
%

if size(phaseinput, 2) > size(phaseinput, 1)
  phaseinput = phaseinput.';
end

if size(ang, 2) > size(ang, 1)
  ang = ang.';
end

ang = ang / 180 * pi;
H = [cos(ang) -sin(ang) ones(size(ang))];

x = H\phaseinput;

epsilon = atan2(x(2), x(1));
gamma = x(3);
A = x(1) / cos(epsilon);

epsilon = epsilon / pi * 180;