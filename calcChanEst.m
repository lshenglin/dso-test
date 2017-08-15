function [ht, htOSF, protosymbol] = calcChanEst(fname, btcnt, OSF, show_td_plot)
%
%% FIXME: 
%     1) HARD coded preamble type
%     2) No frequency error / SFO correction
%     3) Hard code to use 60 symbols
%
% [ht, htOSF, protosymbol] = calcChanEst(fname, btcnt, OSF)
% 
% Input:
%   fname   : DSO file name
%   btcnt   : back track count in samples
%   OSF     : oversampling rate
%
% Output:
%   ht      : time domain impulse response
%   htOSF   : oversampled time domain impulse response
%   protosymbol: protosymbol (NOTE: the protosymbol here is only the average of raw samples)
%

if ~exist('btcnt', 'var')
  btcnt = 10;
end


if ~exist('OSF', 'var')
  OSF = 1;
end

if ~exist('show_td_plot', 'var')
  show_td_plot = 0;
end

val = load(fname);
C = val.C;

fsDSO = 1/(C(1).x(2) - C(1).x(1));
fs = 499.2e6 * 2;

% resample all the captures to get the same time index. Chop a little more
% to make sure every capture at least has that many data
tvec = C(1).x(1) + (0:1/fs:(length(C(1).x)-10)/fsDSO);

x(1, :) = interp1(C(1).x, C(1).y, tvec, 'spline') + 1i*interp1(C(2).x, C(2).y, tvec, 'spline');
x(2, :) = interp1(C(3).x, C(3).y, tvec, 'spline') + 1i*interp1(C(4).x, C(4).y, tvec, 'spline');
x(3, :) = interp1(C(5).x, C(5).y, tvec, 'spline') + 1i*interp1(C(6).x, C(6).y, tvec, 'spline');
x(4, :) = interp1(C(7).x, C(7).y, tvec, 'spline') + 1i*interp1(C(8).x, C(8).y, tvec, 'spline');

if show_td_plot
  figure; subplot(4, 1, 1); plot(real(x(1, :))); hold on; plot(imag(x(1, :)));
  subplot(4, 1, 2); plot(real(x(2, :))); hold on; plot(imag(x(2, :)));
  subplot(4, 1, 3); plot(real(x(3, :))); hold on; plot(imag(x(3, :)));
  subplot(4, 1, 4); plot(real(x(4, :))); hold on; plot(imag(x(4, :)));
end

Nch=13;
Shape=1;
Nbit=4;
Nsymbol=2;
% fchip=499.2e6;
ADCOSR = 2;
%Generate TX Pulse shape
TXOSF = Nch * 2;
% fsamp = TXOSF * fchip;
% pulse = TX_pulse_s(Shape, Nbit, TXOSF, Nsymbol);
load('pulse');
[~, ~, ~, ~, ~, ~, S, s_sfd] = ...
  uwb_siggen_s(TXOSF, 0, pulse, ADCOSR);

symbolDur = 31*16;
s_sfd_short = s_sfd(1:symbolDur*8);

% pulse2 = TX_pulse_s(Shape, Nbit, 2, Nsymbol);
load('pulse2')
sigTemplate = conv(upsample([repmat(S, 1, 64) s_sfd_short], 2), pulse2);

symb2use = 60;
for lp = 1 : 4
  [acor,lag] = xcorr(sigTemplate,x(lp, :));
  
  [~,I] = max(abs(acor));
  lagDiff = lag(I);
  sig = x(lp, -lagDiff+1:end);
  N0(lp) = -lagDiff+1;
%   figure; plot(real(sig)); hold on; plot(sigTemplate);
  
  % start from the third symbol
  preamble(lp, :) = x(lp, N0(lp)+2*(symbolDur*2):(N0(lp)+62*(symbolDur*2)-1));
  
  %% FIXME: frequency error correction and farrow goes here if desired
  
  % correct frequency error and average, simply average for now
  % NOTE: protosymbol on the chip includes the SRRC filtering. Here we
  % don't. Just a simple hack to average over 60 symbols
  protosymbol(lp, :) = mean(reshape(preamble(lp, :), 2*symbolDur, symb2use), 2);
end
% close all;

pilotS = conv(upsample(S, 2), pulse2);
pilotS = pilotS(1:2*symbolDur);

% Divide out pulse to obtain frequency domain response
fft_h = fft(protosymbol, [], 2) ./ fft(pilotS);

% Oversample
htOSF = circshift(ifft(fftshift([zeros(4, (OSF-1)/2 * symbolDur) fftshift(fft_h, 2) zeros(4, (OSF-1)/2 * symbolDur)], 2), [], 2), btcnt * OSF, 2);

% Normal sampling grid
ht = circshift(ifft(fft_h, [], 2), btcnt, 2);
if show_td_plot
    tvec = (0:1/fs:(length(ht)-1)/fs)*1e9;
    figure; plot(tvec, 20*log10(abs(ht).'));
    xlabel('Time (ns)'); ylabel('Time Domain Path Magnitude (dB)');
    grid on; title('Channel PDP'); legend('RX-1', 'RX-2', 'RX-3', 'RX-REF');

    tvec = (0:1/(OSF*fs):(length(htOSF)-1)/(OSF*fs))*1e9;
    figure; plot(tvec, 20*log10(abs(htOSF).'));
    xlabel('Time (ns)'); ylabel('Time Domain Path Magnitude (dB)');
    grid on; title(sprintf('Channel PDP w. Oversampling = %dx', OSF));
    legend('RX-1', 'RX-2', 'RX-3', 'RX-REF');
end
