% function peakDetection
% 08/07/2017
% Apple Inc. 
% Function to estimate the first path peak for a given threshold
% Input:
% ht            complex impulse response (NxM) N samples and M receivers
% threshold     threshold used detect first path arrival

% Output:   
% fpPhase       complex amplitude of the first path for the M receivers (Mx1)

function [fpVector] = peakDetection(ht, threshold)

numRx = size(ht,2);

for l = 1:numRx
    
    [pk_loc(l,1), pk_val(l,1), fpVector(l,1)] = pkExtract(ht(:,l), threshold, 1);
    
    % Option to normalize the phase vectors 
%     fpVector(l,1) = fpVector(l,1)/norm(fpVector(l,1));

end



return