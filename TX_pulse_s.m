function pulse=TXpulse(Shape,Nbit,Nch,Nsymbol);


Fsymbol=499.2e6;
Fc=Nch*Fsymbol; % Carrier Frequency
Fs=Fc;
Fdac=Fc/1;
trun=Nsymbol/Fsymbol;

t=-trun:1/Fs:trun-1/Fs;
tbb=-trun:1/Fc:trun-1/Fs;

if Shape==1
    % Gaussian Pulse
    Pulse_Width = 2.4e-9;
    alpha=Pulse_Width*sqrt(2);
    Var=alpha./4./pi;
    % op = sqrt(2)./alpha.*exp(-2.*pi.*t.^2./alpha^2);
    pulse = 1*exp(-2.*pi.*t.^2./alpha^2);

elseif Shape==2
    %RRC Pulse
    alpha=0.6;
    Tc=2.3278e-9;
    Term1 = 4*alpha./pi./sqrt(Tc); 
    TermNumA = cos((1+alpha)./Tc.*pi.*t);
    TermNumB = Tc./4./alpha./t.*sin((1-alpha)./Tc.*pi.*t);
    TermDenum = 1-(4.*alpha.*t./Tc).^2;
    RRCpulse = Term1.*(TermNumA+TermNumB)./TermDenum;
    pulse = RRCpulse./max(RRCpulse);
    pulse(Fs*trun+1)=1;
end

%Quantize the pulse
DSpulse=downsample(pulse,Fs/Fdac);
Qsigns=sign(DSpulse);
Qpartition = 1/2^Nbit:1/2^Nbit:1-1/2^Nbit;
Qcodebook = 0:1/2^Nbit:1-1/2^Nbit;
[index,Qpulse] = quantiz(abs(DSpulse),Qpartition,Qcodebook);
Qpulse=Qpulse.*Qsigns;
pulse=Qpulse;




