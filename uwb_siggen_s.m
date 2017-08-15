function [s_shr_os,s_shr_ADC,s_p,p, sync_cnt, pilot, S, s_sfd]= uwb_siggen_s(Nch, graphics,PulseShape,ADCOSR)
%function uwb_siggen()
%
%Simple signal generator prototype for UWB as per 
%IEEE 802.15.4 Chapter 14 "UWB PHY"
%
%params are examples, while the spec prescribes a set
%of legacl combinations in a variety of tables; this code
%is only to get a feel for what this signaling scheme
%is about ... will refine later
%
%Modified by S.Gambini, May 24,2016- enforced OSF=Nch (always sampled at
%fRF);

% close all
% rng(1)



% params & constants
dL        = 16; % delta_L zero insertion
L_sfd     = 'long'; % length of SFD: 'long' (64) or 'short' (8)
Lpay      = 0;%60; % info (payload) length (bytes) -- this is <=127
b_range   = 0; % is range packet (1) or not (0); for header only
b_rate    = [1,0]; % data rate bits (for header) [R1, R0]
b_hext    = 0; % header extension (typically 0)
pream_dur = '01'; % preamble duration 'P1P0'; '00','01','10','11'==16,64,1024,4096
Ncpb      = 16; % chips per burst
Nburst    = 32; % burst positions per overall symbol
%
Tp  = 2e-9; % pulse duration ~2ns (FIXME: really 1/499.2 MHz); used only for plotting
OSF = Nch;   % oversampling factor for pulse
poly_rs  = gf([1, 55, 61, 37, 48, 47, 20, 6, 22], 6);
trell_cc = poly2trellis(3, [2, 5]);
%
C1s = '-0000+0-0+++0+-000+-+++00-+0-00'; % preamble code C1 (C2 etc. TBD)
C3s = '-+0++000-+-++00++0+00-0000-0+0-'; % preamble code C3
C6s = '++00+00---+-0++-000+0+0-+0+0000'; % preamble code C6
Ms  = '0+0-+00-0+0-+00--00+0-0+0+000-0-0-00+0--0-+0000++00---+-++0000++'; % SFD code
Cs = C6s; % selected preamble code
%
p   = rcosine(1, OSF, 'sqrt',0.5, 4); % "some" pulse (SRRC), oversampled


% arg preprocessing & inits
switch pream_dur % string containing 'P1 P0' (MSB first)
  case '00'
    Nsync     = 16;
    b_pdur = [0,0];
  case '01'
    Nsync     = 64;
    b_pdur = [0,1];
  case '10'
    Nsync     = 1024;
    b_pdur = [1,0];
  case '11'
    Nsync     = 4096;
    b_pdur = [1,1];
end
C    = CstrToNum(Cs);
M    = CstrToNum(Ms);
Nhop = Nburst / 4; % number of possible hop positions in quarter-symbol
mhop = log2(Nhop); % bits needed to represent hop position

% init scrambler state
% - use preable code, remove 0's, replace '-' with 0 (14.3.2)
tmp = CstrToNum(strrep(strrep(Cs, '0',''),'-','0'));
si_scram = fliplr(tmp(1:15));


% sanity checks
if Lpay > 127
    error('Lpay needs to be <= 127 (bytes)')
end
if mhop > Ncpb
    error('not covered - FIXME!! see 14.3.2 in spec ... TBD')
end


% autocorr check
CC  = repmat(C, 1, 5);
pac = xcorr(CC,C); % periodic autocorr

% generation of 1 preamble symbol
    S = kron(C, [1, zeros(1, dL-1)]);
% generate SYNC sequence (repeat symbol)
s_sync = repmat(S, 1, Nsync);

if(graphics==1)
    figure;
    stem(pac) % shows peaks and zeros for non-zero delay

    
    figure
    stem(S);
end;

% SFD (start of frame delimiter)
% - used for frame timing & accounting of T_ta (turnaround time)
% - 8 symbols (1Mbps) or 64 symbols (106 kbps)
if strcmp(L_sfd,'long')
    m_sfd = M;
else
    m_sfd = M(1:8);
end
s_sfd = kron(m_sfd, S);


% Packet Header
% - FIXME: need to double check SECDEC xor's here
b_len = fliplr(de2bi(Lpay, 7));
b_secdec(1) = ... % "C0" = xor(R0,R1,L0/2/4/5,EXT,P1)
    vxor([b_rate, b_len([7,5,3,2]), b_hext, b_pdur(1)]);
b_secdec(2) = ... % "C1" = xor(R1,L2/3/5/6, RNG, EXT, P0)
    vxor([b_rate(1), b_len([5,4,2,1]), b_range, b_hext, b_pdur(2)]);
b_secdec(3) = ... % "C2" = xor(R0, L0/1/5/6, RNG, EXT)
    vxor([b_rate(2), b_len([7,6,2,1]), b_range, b_hext]);
b_secdec(4) = ... % "C3" = xor(L0/1/2/3/4, RNG, EXT)
    vxor([b_len([7,6,5,4,3]), b_range, b_hext]);
b_secdec(5) = ... % "C4" = xor(P0,P1)
    vxor(b_pdur);
b_secdec(6) = ... % "C5" = xor(R0/1, L6/5/4/3/2/1/0, RNG, EXT, P1/0, b_secdec(5/4/3/2/1))
    vxor([b_rate, b_len, b_range, b_hext, b_pdur, b_secdec(1:5)]);
%
b_hdr = [b_rate, b_len, b_range, b_hext, b_pdur, b_secdec]; % 19 header bits


% Payload Info bits & RS Encode
% - assumes all RS blocks are maxed out (330 info bits) and only last
%   block may be shorter (to use leading dummy zero bits as per spec)
Nblk = 330; % input (info) bits per RS block
b_rand = randi([0,1], 1, Lpay*8); % random payload info bits
b_rsca  = []; % to collect all blocks of RS-coded bits
for blk = 1:ceil(Lpay*8/Nblk) % loop over blocks worth 330 input bits
    b_pi   = zeros(1,Nblk); % fixed block size 330 bits
    inds = (blk-1)*Nblk+1 : min( blk*Nblk, length(b_rand)); % bit indices
    Ninf = length(inds);
    b_pi(Nblk-Ninf+1:end) = b_rand(inds); % has leading dummy zeros if needed
    tmp1     = reshape(b_pi, 6, length(b_pi)/6); % group by 6 bits
    tmp2     = 2.^[0,1,2,3,4,5] * tmp1; % binary to decimal
    syms_rsi = gf(tmp2, 6); % RS info symbols
    syms_rsc = rsenc(syms_rsi, 63, 55, poly_rs); % RS coded symbols
    tmp3     = de2bi(syms_rsc.x, 6); % convert to binary
    tmp4     = tmp3';
    b_rsc    = tmp4(:); % rs encoded bits
    b_rsc    = (b_rsc(Nblk-Ninf+1:end))'; % remove dummy zeros if necessary
    b_rsca   = [b_rsca, b_rsc]; % append this block to overall payload rs encoded bits
end


% concat header and payload bits, add tail bits
z_tail = [0, 0]; % tail bits to go back to 0-state
b_hp  = [b_hdr, b_rsca, z_tail]; % header + payload bits

% Convolutional Encoding
b_hpcc = convenc(b_hp, trell_cc); % hdr + payld after conv coding

% BPSK + Burst-Position-Modulation (BPM)
Nsyms    = length(b_hpcc)/2; % each bit pair is "1 symbol"
s_bpm   = []; % all header + payload symbols, all chips
so_scram = si_scram; % initial state of scrambler
for k = 0 : Nsyms - 1 % loop over all symbols (header + payload)
                         
    % all chips for this symbol init'ed to zero
    s_sym = zeros(1, Ncpb * Nburst);
    
    % pos and phase bit
    pos = b_hpcc(k*2 + 1); % systematic bit (pulse position bit)
    pha = b_hpcc(k*2 + 2); % coded bit (BPSK phase bit)

    % scrambler seq for this symbol (Ncpb values, ie one per "chip"/pulse)
    [b_scram, so_scram] = prbs15(Ncpb, so_scram);
    
    % hopping position (h is one of 0,1, ..., Nhop-1)
    h = 0;
    for ii = 1:mhop 
        h = h + 2^(ii-1)*b_scram(ii);
    end
    
    % compose this symbol
    s_burst   = (1-2*pha) * (1 - 2*b_scram); % chip polarities in active burst
    idx_start = h*Ncpb + pos*Ncpb*Nburst/2;
    s_sym(idx_start+1:idx_start+Ncpb) = s_burst;
    
    % append
    s_bpm = [s_bpm, s_sym];

end

% Concat segments
s_pkt = [s_sync, s_sfd, s_bpm]; % 
sync_cnt = length(s_sync)*OSF;

% pulse shape
s_shr_os = kron(s_pkt, [1, zeros(1, OSF-1)]);
s_shr_ADC= conv(upsample(s_pkt,ADCOSR),ones(1,ADCOSR));
s_p = conv(s_shr_os, PulseShape);

pilot = conv(kron(S, [1, zeros(1, OSF-1)]), PulseShape);

%s_shr_os=conv(s_shr_os,ones(1,Nch));
%//plots(p,1/Tp * OSF * 1e-6);
if(graphics==1)
    figure
    plot(p)
    figure
    plot(s_p);
%//plots(s_p, 1/Tp * OSF * 1e-6);
    zoom on
end



function C = CstrToNum(Cs)
% Convert string representation of ternary seq using elements
% {'0','+', '-'} to numeric vector using elements {0,+1,-1}
for k=1:length(Cs)
    switch Cs(k)
      case '-'
        C(k) = -1;
      case '+'
        C(k) = +1;
      case '0'
        C(k) = 0;
    end
end    



function b = vxor(in_vec)
% xor over vector of binary numbers ("vector xor")
b = mod(sum(in_vec),2);



function [out, so] = prbs15(N, si)
% prbs-15 pseudo-random number generator using shift register: 
% g(D) = 1 + D^14 + D^15
%
% INPUTS
%   N  =  number of bits to generate
%   si =  initial state (15-element binary vector, LSB-to-MSB)
%
% OUTPUTS
%   out = N pseudo-random bits
%   so  = output state (final state)    
%
% EXAMPLE (see spec 802.15.4-2011 / Chapt 14.3.2)
%   si = fliplr([1,1,1,0,0,0,1,0,1,1,0,1,1,0,1]);
%   [out1, so] = prbs15(2, si)
%   [out2, so] = prbs15(14, so)
%   out = [out1, out2]
if ~exist('si', 'var')
    state = ones(15,1);
else
    state = si;
end    
out = zeros(1,N);
for k=1:N
    out(k) = xor(state(14),state(15));
    state  = [out(k), state(1:14)];
end

so = state;

