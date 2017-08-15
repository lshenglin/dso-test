function plotResponse(hrx_t, hrx_f, domain, delay, PDP, fs, Np, startF, stopF, plotcfg, str)
%
% hrx_t : time domain response (Npoint x Nrx)
% hrx_f : freq domain response (Npoint x Nrx)
% domain: plot domain
% startF: starting frequency
% stopF : stop frequency
% plotcfg: plot configuration
% str   : extra string on the title
if nargin == 3
  delay = []; PDP = []; Np = 1;
  startF = 3e9;
  stopF = 8e9; fs = stopF - startF;
  plotcfg.phaseunwrap = 'unwrap';
  plotcfg.xaxis = 'dist';
  str = '';
elseif nargin == 4
  PDP = []; Np = 1; fs = stopF - startF;
  startF = 3e9;
  stopF = 8e9;
  plotcfg.phaseunwrap = 'unwrap';
  plotcfg.xaxis = 'dist';
  str = '';
elseif nargin == 5
  Np = 1;
  startF = 3e9;
  stopF = 8e9; fs = stopF - startF;
  plotcfg.phaseunwrap = 'unwrap';
  plotcfg.xaxis = 'dist';
  str = '';
elseif nargin == 6
  Np = 1;
  startF = 3e9;
  stopF = 8e9;
  plotcfg.phaseunwrap = 'unwrap';
  plotcfg.xaxis = 'dist';
  str = '';  
elseif nargin == 7
  startF = 3e9;
  stopF = 8e9;
  plotcfg.phaseunwrap = 'unwrap';
  plotcfg.xaxis = 'dist';
  str = '';
elseif nargin == 8
  stopF = 8e9;
  plotcfg.phaseunwrap = 'unwrap';
  plotcfg.xaxis = 'dist';
  str = '';
elseif nargin == 9
  plotcfg.phaseunwrap = 'unwrap';
  plotcfg.xaxis = 'dist';
  str = '';
elseif nargin == 10
  str = '';
end

if ~isempty(delay) && (size(delay, 1) == 1 || size(delay, 2) == 1)
  delay = delay.';
end

if ~isempty(PDP) && (size(PDP, 1) == 1 || size(PDP, 2) == 1)
  PDP = PDP.';
end

freq_Range = linspace(startF, stopF, size(hrx_f, 1));

showfig_freq = 0;
showfig_time = 0;

if strcmpi(domain, 'both')
  showfig_freq = 1;
  showfig_time = 1;
end

if strcmpi(domain, 'freq')
  showfig_freq = 1;
  showfig_time = 0;
end

if strcmpi(domain, 'time')
  showfig_freq = 0;
  showfig_time = 1;
end

Cstyle = {'r', 'g', 'b'};
Mstyle = {'o', '+', '<', '>', 'd', '*'};
if showfig_freq
  figure; subplot(2, 1, 1);
  leg = {};
  for lp = 1 : size(hrx_f, 2)
    plot(freq_Range, 20*log10(abs(hrx_f(:, lp))), Cstyle{lp}, 'linewidth', 2); hold on;
    leg{lp} = sprintf('RX: %d', lp);
  end
  xlabel('Frequency Range (Hz)');
  ylabel('Magnitude Response in dB'); grid on; legend(leg, 'location', 'best');
  title(sprintf('%sFrequency Domain Channel Response', str));
  
  subplot(2, 1, 2);
  leg = {};
  for lp = 1 : size(hrx_f, 2)
    leg{lp} = sprintf('RX: %d', lp);
    if strcmpi(plotcfg.phaseunwrap, 'none')
      plot(freq_Range, 180/pi*angle(hrx_f(:, lp)), Cstyle{lp}, 'linewidth', 2); hold on;
    else
      plot(freq_Range, 180/pi*unwrap(angle(hrx_f(:, lp))), Cstyle{lp}, 'linewidth', 2); hold on;
    end
  end
  xlabel('Frequency Range (Hz)');
  ylabel('Phase Response in degree'); grid on; legend(leg, 'location', 'best');
end

if showfig_time
  leg = {};
  figure; subplot(2, 1, 1);
  for lp = 1 : size(hrx_t, 2)
    leg{lp} = sprintf('RX: %d', lp);
    if strcmpi(plotcfg.xaxis, 'time')
      plot(((1:size(hrx_t, 1))-1)/fs*1e9, 20*log10(abs(hrx_t(:, lp))), Cstyle{lp}, 'linewidth', 2, 'markersize', 12); hold on;
      xlabel('Delays (ns)');
    else
      if ~isempty(delay) && ~isempty(PDP)
        plot(((1:size(hrx_t, 1))-1)/fs*3e8, 20*log10(abs(hrx_t(:, lp))), Cstyle{lp}, 'linewidth', 2, 'markersize', 12); hold on;
      end
      xlabel('Path distance (m)'); xlim([2.5 8]);
    end
  end

  % show path used
  for lp = 1 : size(hrx_t, 2)
    if strcmpi(plotcfg.xaxis, 'time')
      if ~isempty(delay) && ~isempty(PDP)
        for lp3 = 1 : Np
          plot((delay(lp3, lp)-1)/fs*1e9, 20*log10(abs(PDP(lp3, lp))), 'color', Cstyle{lp}, 'marker', Mstyle{lp3}, 'linewidth', 2); hold on;
        end
      end
    else
      if ~isempty(delay) && ~isempty(PDP)
        for lp3 = 1 : Np
          plot((delay(lp3, lp)-1)/fs*3e8, 20*log10(abs(PDP(lp3, lp))), 'color', Cstyle{lp}, 'marker', Mstyle{lp3}, 'linewidth', 2); hold on;
        end
      end
    end
  end
  
  ylabel('Power Response in dB'); grid on; legend(leg, 'location', 'best');
  title(sprintf('%sTime Domain Channel Response', str)); %ylim([-120 -40]);
  
  leg = {};
  subplot(2, 1, 2);
  for lp = 1 : size(hrx_t, 2)
    leg{lp} = sprintf('RX: %d', lp);
    if strcmpi(plotcfg.xaxis, 'time')
      if strcmpi(plotcfg.phaseunwrap, 'none')
        plot(((1:size(hrx_t, 1))-1)/fs*1e9, 180/pi*(angle(hrx_t(:, lp))), Cstyle{lp}, 'linewidth', 2); hold on;
      else
        plot(((1:size(hrx_t, 1))-1)/fs*1e9, 180/pi*unwrap(angle(hrx_t(:, lp))), Cstyle{lp}, 'linewidth', 2); hold on;
      end
      xlabel('Delays (ns)');
      ylabel('Phase Response in degree'); grid on; legend(leg, 'location', 'best');
    else
      if strcmpi(plotcfg.phaseunwrap, 'none')
        plot(((1:size(hrx_t, 1))-1)/fs*3e8, 180/pi*(angle(hrx_t(:, lp))), Cstyle{lp}, 'linewidth', 2); hold on;
      else
        plot(((1:size(hrx_t, 1))-1)/fs*3e8, 180/pi*unwrap(angle(hrx_t(:, lp))), Cstyle{lp}, 'linewidth', 2); hold on;
      end
      xlabel('Path distance (m)'); xlim([2.5 8]);
      ylabel('Unwrapped Phase Response in degree'); grid on; legend(leg, 'location', 'best');
    end
  end
end