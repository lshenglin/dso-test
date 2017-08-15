function []=cvtLecroy2Matlab(folder_name,angle,iteration,count)
% folder_name as string, which contains DSO trace C1 to C8.
% Reads C1 to C8 and stores in DSO.mat

  for nch = 1 : 8
    tmp = ReadLeCroyBinaryWaveform([folder_name sprintf('/C%d.trc', nch)]);
    C(nch) = tmp; 
  end
  
%   make folder "DSO_mat_files" to save all DSO.mat.
  if exist('DSO_mat_files', 'file') ~= 7
      mkdir('DSO_mat_files');
  end
  
  if nargin == 4
      save(sprintf('DSO_mat_files/%03d-DSO%d-%d.mat', count,angle,iteration), 'C');
  else
      save(sprintf('DSO_mat_files/DSO.mat'), 'C');      
  end
  clear C

end