function restOfFunction_cal(hEst_t, PDP, delay, vnaCfg, antCfg, pkCfg, Nup, Npath, mode, ang_val, valid_range, ang)

show_plot = 0;
try
    load Q5.mat;
catch
    Q5 = [0 1 0 0 0 0];
end

Nrx = vnaCfg.Nrx;
startFreq = vnaCfg.startFreq;
stopFreq = vnaCfg.stopFreq;
% fc = 1/2*(startFreq + stopFreq);
fc = 6.5e9;
BW = 499.2e6;

% Nch=13;
% TXOSF = Nch * 2;
% %%% What is the fc for the transmitted signal?
% fc = TXOSF*Fsymbol; % Carrier Frequency



% loop over all angles and for each angles extract peaks and perform
% estimates
ang_plot_vec = ang;
if size(ang_plot_vec, 1) < size(ang_plot_vec)
    ang_plot_vec = ang_plot_vec.';
end

plotcfg.phaseunwrap = 'unwrap';
plotcfg.xaxis = 'dist';

cnt = 1;
% loop over angles
% idx_all = [];
valid_range = round(1+valid_range/2);
idx0 = find(ang == 0);
if ~exist('exp_phase_0', 'var')
    exp_phase_0 = PDP(idx0, 1, 1)*conj(PDP(idx0, 1, 2));
end
for lp = ang_plot_vec.'
    idx = find(ang == lp);
    %   idx_all = [idx_all idx];
    if isempty(idx)
        error('The turn table angle %f does not show up in this result', lp);
    end
    
    % plot both time and frequency response
    if show_plot|| strcmpi(mode, 'mat')
        plotResponse(squeeze(hEst_t(idx, :, :)), squeeze(hEst_f(idx, :, :)), 'time', ...
            squeeze(delay(idx, :, :)), squeeze(PDP(idx, :, :)), fs, Npath, ...
            startFreq, stopFreq, plotcfg, ['ang = ' num2str(lp) ', '])
    end
    
    % calculate DOA for the first path
    if 0
        [theta(cnt), phi(cnt)] = calculateDOA(squeeze(PDP(idx, 1, :)).', antCfg); %#ok<UNRCH>
    else
        theta(cnt) = 0; %#ok<AGROW>
        phi_acos(cnt) = acos(angle(exp_phase_0*PDP(idx, 1, 2)*conj(PDP(idx, 1, 1))) * antCfg.c / fc / 2 / pi / antCfg.d12) * 180/pi - 90; %#ok<AGROW>
%         phi_acos(cnt) = acos(angle(exp_phase_0*PDP(idx, 1, 2)*conj(PDP(idx, 1, 1))) * antCfg.c / fc / 2 / pi / antCfg.d12) * 180/pi - 90; %#ok<AGROW>
        
        phi_phase(cnt) = angle(exp_phase_0*PDP(idx, 1, 2)*conj(PDP(idx, 1, 1))); %#ok<AGROW>
        MY_PHI = phi_phase(cnt)*180/pi;
        MY_AOA = polyval(Q5, MY_PHI);
        phi(cnt) = MY_AOA; %#ok<AGROW>
    end
    fprintf(1, 'ang = %.1f: Estimated: phi = %.1f (%.1f), theta = %.1f\n', lp, phi(cnt), phi_acos(cnt), theta(cnt));
    cnt = cnt + 1;
end

phi_shift = [phi_phase(19:36) phi_phase(1:18)];
phi_ls = unwrap(phi_shift);
% phi_ls = unwrap(phi_shift(valid_range));
phi_ls = 180/pi*phi_ls.';
ang_plot_vec_shift = unwrap([ang_plot_vec(19:36); ang_plot_vec(1:18)]/180*pi)*180/pi-360;
ang_ls = ang_plot_vec_shift;
% ang_ls = ang_plot_vec_shift(valid_range);

% H = [ones(length(phi_ls), 1) phi_ls phi_ls.^2];
% abc_ls = pinv(H'*H)*H'*ang_ls;
Q5 = polyfit(phi_ls, ang_ls, 5); %#ok<NASGU>
exp_phase_0 = PDP(idx0, 1, 1)*conj(PDP(idx0, 1, 2)); %#ok<NASGU>
save('Q5.mat', 'Q5', 'exp_phase_0');

if strcmpi(mode, 'csv')
    figure;
    for idx = 1:Nrx
        for lp2 = 1 : Npath
            subplot(3, 1, 1); hold on;
            if idx == 1
                plot(ang, fftshift(20*log10(abs(PDP(:, lp2, idx)))));
            else
                plot(ang, fftshift(20*log10(abs(PDP(:, lp2, idx)))));
                %             plot(ang, fftshift(20*log10(abs(PDP(end:-1:1, lp2, idx)))));
            end
            grid; xlabel('Turn table angles (degree)'); ylabel('Power of Path (dB)');
            title(sprintf('Power of Path for RX: %d, Path index = %d', idx, lp2));
            subplot(3, 1, 2); hold on;
            plot(ang, fftshift(antCfg.c/fc*delay(:, lp2, idx)/Nup));
            grid; xlabel('Turn table angles (degree)'); ylabel('Distance (m)');
            title(sprintf('Path distance for RX: %d, Path index = %d', idx, lp2));
            subplot(3, 1, 3); hold on;
            plot(ang, fftshift(180/pi*(unwrap(angle(PDP(:, lp2, idx))))));
            grid; xlabel('Turn table angles (degree)'); ylabel('Phase (degree)');
            title(sprintf('Phase angle for RX: %d, Path index = %d', idx, lp2));
        end
    end
    
    figure; plot(ang-180, fftshift(phi_acos), 'r-.', 'linewidth', 2); hold on; plot(ang-180, fftshift(phi), 'b-', 'linewidth', 2);
    plot(ang-180, ang-180-fftshift(phi.'), 'g', 'linewidth', 2);
    legend('ArcCos-based', 'Calibrated', 'location', 'best');
    axis([-180, 180, -90, 90]); grid on;
    xlabel('Turn table angle (degrees)'); set(gca, 'xtick', [-180:30:-120 -90:15:90 120:30:180]);
    ylabel('Azimuth Angle (degrees)'); set(gca, 'ytick', -90:15:90);
    
    %   subplot(2, 1, 2); plot(ang, theta, 'r-', 'linewidth', 2); hold on;
    %   legend('Raw Estimate', 'location', 'best'); grid on;
    %   xlabel('Turn table angles (degree)');
    %   ylabel('Elevation Angles');
    %
    h_first_path = squeeze(PDP(:, 1, :));
    % keyboard;
    exclusion_flag = 0;
    % keyboard;
    if exclusion_flag
        idx40 = find(ang == 40); %#ok<UNRCH>
        ang(idx40) = [];
        h_first_path(idx40, :) = [];
        
        idx70 = find(ang == 70);
        ang(idx70) = [];
        h_first_path(idx70, :) = [];
        
        idx220 = find(ang == 220);
        ang(idx220) = [];
        h_first_path(idx220, :) = [];
        
        idx230 = find(ang == 230);
        ang(idx230) = [];
        h_first_path(idx230, :) = [];
        
        idx240 = find(ang == 240);
        ang(idx240) = [];
        h_first_path(idx240, :) = [];
    end
    
    diff_angle = diff(unwrap(angle(h_first_path), [], 2), [], 2);
    anglediff = [diff_angle, sum(diff_angle, 2)] * 180 / pi;
    figure; plot(ang, fftshift(anglediff(:, 1)), 'linewidth', 2); hold on;
    xlabel('Turn table angles (starting 0 position centered in the plot showing as 180, ending 0 as 178)'); ylabel('Phase difference btw antenna in degrees');
    
    %   % fit the phase difference
    %   [A1, epsilon1, gamma1] = estSinusoid(ang, anglediff(:, 1));
    %   plot(ang, A1*cos((ang+epsilon1)/180*pi)+gamma1, '--b', 'linewidth', 2);
    %   [A2, epsilon2, gamma2] = estSinusoid(ang, anglediff(:, 2));
    %   plot(ang, A2*cos((ang+epsilon2)/180*pi)+gamma2, '--r', 'linewidth', 2);
    %   [A3, epsilon3, gamma3] = estSinusoid(ang, anglediff(:, 3));
    %   plot(ang, A3*cos((ang+epsilon3)/180*pi)+gamma3, '--g', 'linewidth', 2);
    %
    %   grid on;
    %   legend('P2-P1', 'P3-P2', 'P3-P1', 'Fit:P2-P1', 'Fit:P3-P2', 'Fit:P3-P1');
    
    
    % Plot antenna response as a function of angles
    h_first_path_abs = abs(h_first_path);
    h_first_path_abs = [h_first_path_abs; h_first_path_abs(1, :)];
    ang_abs = [ang; ang(1, :)];
    
    figure; polarpat(ang_abs, 20*log10(abs(h_first_path_abs(:, 1))), 'r-', ...
        ang_abs, 20*log10(abs(h_first_path_abs(:, 2))), 'g-', ...
        ang_abs, 20*log10(abs(h_first_path_abs(:, 3))), 'c-');
end
