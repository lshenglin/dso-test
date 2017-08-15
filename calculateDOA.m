function [theta, phi] = calculateDOA(h, ant_geometry_cfg)
%
% This function attempts to calculate DOAs based on the time domain channel
% response. Note that antenna patterns and array manifold are necessary for
% this search, but for now let's just use omnidirectional assumption
%
% calculate the phase and normalize with the first antenna
pha = angle(h);

% the second entry is assumed to be at the origin for the geometry
phase_input = pha([1, 3]) - pha(2);

% wrap between [-pi, pi)
idx = find(phase_input >= pi);
phase_input(idx) = (phase_input(idx) - 2*pi);
idx = find(phase_input < -pi);
phase_input(idx) = (phase_input(idx) + 2*pi);

d12 = ant_geometry_cfg.d12;
d23 = ant_geometry_cfg.d23;
d13 = ant_geometry_cfg.d13;

lambda = ant_geometry_cfg.c / (1e9*ant_geometry_cfg.fc_GHz);
phase_input = phase_input*lambda/2/pi./[d12 d13];

% alpha is the angle position for ant2, should be passed in
alpha = acos((d12^2+d23^2-d13^2)/2/d12/d23);

% set an arbitrary assertion to avoid close to linear formation
assert(alpha < 7*pi/8);
zeta1 = phase_input(1);
zeta2 = phase_input(2);

if ~zeta1 && ~zeta2
  theta = pi/2;
  phi = 0; % phi can be arbitrary in this case
elseif zeta1 == 0
  % two candidates for theta pi/2 or 3*pi/2
  phi_tmp = [pi/2 3*pi/2];
  ptmp = zeta2 ./ cos(phi_tmp - alpha);
  idxpos = find(ptmp >= 0);
  theta = acos(ptmp(idxpos));
  phi = phi_tmp(idxpos);
elseif zeta2 == 0
  % two candidates for theta pi/2 + alpha or 3*pi/2 + alpha
  phi_tmp = [pi/2 3*pi/2] + alpha;
  ptmp = zeta2 ./ cos(phi_tmp);
  idxpos = find(ptmp >= 0);
  theta = acos(ptmp(idxpos));
  phi = phi_tmp(idxpos);
else
  phi = atan2(zeta2 - cos(alpha) * zeta1, zeta1 * sin(alpha));
  theta = acos(zeta1 / cos(phi));
end
phi = phi / pi * 180;
theta = theta / pi * 180;
% fprintf(1, 'ChanEst: Estimated: phi = %.1f, theta = %.1f\n', phi, theta);