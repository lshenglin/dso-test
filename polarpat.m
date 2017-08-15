function polarpat(ang1,rho1,st1,ang2,rho2,st2,ang3,rho3,st3)
%POLARPAT  Polar coordinate plot used for antenna radiation patterns.
%          POLARPAT(ANG1,RHO1,ST1,ANG2,RHO2,ST2,ANG3,RHO3,ST3) plots up to
%          three curves. ANGi is angles in degress, RHOi is radius, and
%          STi is linestyle.
%          RHOi can be in dB or not in dB.
%          Axis labels can be placed horzontally or vertically.
%          Choice of normalized or unnormalized (showing gains) patterns.
%          Minimum level at the polar center can be specified.
%          Maximum level at the polar outmost circle can be specified for
%            unnormalized patterns.
%          Line width of radiation patternns can be specified.
%          Legend can be placed. To move the legend, press the left mouse
%            button on the legend and drag to the desired location.
%          Grid linetypes can be specified.
%          Default value is inside [], press Enter to chose default.
%          See PLOT for a description of legal linestyles.
%          0 degree can be in the East or North direction.
%          Example:  polarpat(a1,r1,'r-',a2,r2,'y--')
%          Written by Duixian Liu, on September 13, 1996.
%          T.J. Watson Research center
%          IBM
%          P.O.Box 218
%          Yorktown Heights, NY 10598
%          Email: dliu@watson.ibm.com

if nargin==0
  help polarpat;
  return;
end

% get some parameters from user
% db = input('Are input values in dB (Y/N)[Y]? ','s');
db = 'Y';
if isempty(db), db = 'Y'; end
db = upper(db);

% scale = input('Normalize to the Maximum Gain Value (Y/N)[Y]? ','s');
scale = 'Y';
if isempty(scale), scale = 'Y'; end
scale = upper(scale);
maxG=0;
if scale == 'N'
  maxG = input('The maximum dB value at the polar outmost circle [10]? ');
  if isempty(maxG), maxG=10;  end 
end

% minG = input('The minimum dB value at polar center [-50]? ');
minG = -30;
if isempty(minG), minG=-50; end
aminG=abs(minG); 

% HV = input('Put axis laber Vertically or Horizontally (V/H)[H]? ','s');
HV = 'H';
if isempty(HV), HV = 'H'; end
HV = upper(HV);

% LW = input('Pattern line width [1.0]: ');
LW = 2;
if isempty(LW), LW=1.0; end

if nargin > 3
%   LG = input('Put legend on the graph (Y/N)[N]? ','s');
  LG = 'N';
  if isempty(LG), LG='N'; end
  LG=upper(LG);
  if LG == 'Y'
    str1=input('Enter label for curve 1: ','s');
    str2=input('Enter label for curve 2: ','s');
    if nargin>6
      str3=input('Enter label for curve 3: ','s');
    end
    BOX = input('Put a box around the legend (Y/N)[Y]? ','s');
    if isempty(BOX), BOX='Y'; end
    BOX=upper(BOX); 
  end
end

% DIRECT=input('Is 0 degree in the North or East (N/E)[E]? ','s');
DIRECT='N';
if isempty(DIRECT), DIRECT='E'; end
DIRECT=upper(DIRECT);

% LP = input('Line type of grid(-, --, -., :)[-]? ','s');
LP = '-';
if isempty(LP), LP='-'; end

dr=pi/180; cc=10/log(10); er=exp(minG/cc);

% find maximum values
maxA=360; maxR=max(rho1);
if nargin > 3, maxR=max([maxR, max(rho2)]); end
if nargin > 6, maxR=max([maxR, max(rho3)]); end

if scale=='N' & maxR>maxG
  maxRdb=maxR;
  if db=='N', maxRdb=10*log10(maxR); end
  maxG=10*ceil((maxRdb-minG)/10)+minG;
end 
minmax=maxG-minG;

% normalize rho vectors
if db == 'N'
  if scale=='Y', rho1=rho1/maxR;  end  
  for i=1:length(rho1)
    if rho1(i) < er,  rho1(i)=er;  end
    rho1(i)=aminG+cc*log(rho1(i));
  end
  if nargin > 3
    if scale=='Y', rho2=rho2/maxR;  end  
    for i=1:length(rho2)
      if rho2(i) < er,  rho2(i)=er;  end
      rho2(i)=aminG+cc*log(rho2(i));
    end
  end
  if nargin > 6
    if scale=='Y', rho3=rho3/maxR;  end  
    for i=1:length(rho3)
      if rho3(i) < er,  rho3(i)=er;  end
      rho3(i)=aminG+cc*log(rho3(i));
    end
  end
else
  if scale=='Y', rho1=rho1-maxR; end
  rho1=rho1-minG;
  for i=1:length(rho1)
    if rho1(i) < 0, rho1(i)=0; end
  end
  if nargin > 3 
    if scale=='Y', rho2=rho2-maxR; end
    rho2=rho2-minG;
    for i=1:length(rho2)
      if rho2(i) < 0, rho2(i)=0; end
    end
  end
  if nargin > 6, 
    if scale=='Y', rho3=rho3-maxR; end
    rho3=rho3-minG;
    for i=1:length(rho3)
      if rho3(i) < 0, rho3(i)=0; end
    end
  end
end


% get hold state
cax = newplot;
next = lower(get(cax,'NextPlot'));
hold_state = ishold;

% get x-axis text color so grid is in same color
tc = get(cax,'xcolor');

% only do grids if hold is off
if ~hold_state
% make a radial grid
   hold on;
   hhh=plot([0 maxA],[0 minmax]);
   v = [get(cax,'xlim') get(cax,'ylim')];
   ticks = length(get(cax,'ytick'));
   delete(hhh);

% check radial limits and ticks
   rmin = 0; rmax = v(4); rticks = ticks-1;
   if rticks > 9	% see if we can reduce the number
      if rem(rticks,2) == 0
	rticks = rticks/2;
      elseif rem(rticks,3) == 0
	rticks = rticks/3;
      end
   end

% define a circle
   th = 0:pi/50:2*pi;
   xunit = cos(th);
   yunit = sin(th);

   rinc = (rmax-rmin)/rticks;
   cc=minmax/(rmax-rmin);
   for i=(rmin+rinc):rinc:rmax
     plot(xunit*i,yunit*i,LP,'color',tc);
     ii=i-rmax;
     if scale == 'N',  ii=minG+cc*(i-rmin);  end
     if HV == 'V'
       if ii < 0
         strr=num2str(ii);
       elseif ii == 0
         strr=['   ' num2str(ii)];
       else
         strr=[' ' num2str(ii)];
       end
       text(0,i+rinc/20,strr,'verticalalignment','middle');
     else
       text(i+rinc/20,0,num2str(ii),'verticalalignment','top',...
                                    'horizontalalignment','center');
     end
   end

% plot spokes
   th = (1:6)*2*pi/12; 
   if DIRECT=='N', th=th+pi/2; end
   cst = cos(th); snt = sin(th);
   cs = [-cst; cst];
   sn = [-snt; snt];
   if DIRECT=='N', cst=-cst; end
   plot(rmax*cs,rmax*sn,LP,'color',tc);

% annotate spokes in degrees
   rt = 1.1*rmax;
   for i = 1:max(size(th))
      loc = int2str(i*30);
      text(rt*cst(i),rt*snt(i),[loc,'\circ'],'horizontalalignment',...
          'center');
      if i == max(size(th))
	 loc = int2str(0);
      else
	 loc = int2str(180+i*30);
      end
      text(-rt*cst(i),-rt*snt(i),[loc,'\circ'],...
          'horizontalalignment','center');
   end

% set viewto 2-D
   view(0,90);
% set axis limits
   axis(rmax*[-1 1 -1.1 1.1]);
end

% first curve
offset=0;
if DIRECT=='N', ang1=ang1+90; offset=pi;  end
ang1 = ang1 * dr;
xx = rho1.*cos(ang1+offset);
yy = rho1.*sin(ang1);
hhh = plot(xx,yy,st1);
% default line width is 0.5
set(hhh,'linewidth',LW)

% second curve
if nargin > 3
  clear xx yy
  if DIRECT=='N', ang2=ang2+90; end
  ang2 = ang2 * dr;
  xx = rho2.*cos(ang2+offset);
  yy = rho2.*sin(ang2);
  hhh = plot(xx,yy,st2);
  set(hhh,'linewidth',LW)
  if LG=='Y' 
    hl=legend(st1,str1,st2,str2);
    if BOX=='N', set(hl,'Visible','off'); end  
  end
end

% third curve
if nargin > 6
  clear xx yy
  if DIRECT=='N', ang3=ang3-270; end
  ang3 = ang3 * dr;
  xx = rho3.*cos(ang3+offset);
  yy = rho3.*sin(ang3);
  hhh = plot(xx,yy,st3);
  set(hhh,'linewidth',LW)
  if LG=='Y'
    hl=legend(st1,str1,st2,str2,st3,str3);  
    if BOX=='N', set(hl,'Visible','off'); end  
  end
end


if ~hold_state
	axis('equal');axis('off');
end

% reset hold state
if ~hold_state, set(cax,'NextPlot',next); end

