function [pk_loc_picked_time_sorted, pk_val_picked_time_sorted, h_path] = pkExtract(ht, relThresh, Npk)
[pk, loc]=findpeaks(abs(ht));
[val, idx] = sort(pk, 'descend');
maxPK = max(pk);
thresh = maxPK * relThresh;

if 0
  tIdx = find(val > thresh);
  Np = min(length(tIdx), Npk);
  pk_val_picked = val(1:Np);
  pk_loc_picked = loc(idx(tIdx(1:Np)));
  [pk_loc_picked_time_sorted, idx] = sort(pk_loc_picked, 'ascend');
  pk_val_picked_time_sorted = pk_val_picked(idx);
  h_path = ht(pk_loc_picked_time_sorted); % sorted order
else
  tIdx = find(pk > thresh);
  Np = min(length(tIdx), Npk);
  pk_val_picked = pk(tIdx(1:Np));
  pk_loc_picked = loc((tIdx(1:Np)));
  maxIdx = 76;
  minIdx = 45;
  maxIdx = Inf;
  minIdx = 1;
  [~, idx] = find(pk_loc_picked.' < maxIdx);
  [~, idxmin] = find(pk_loc_picked.' > minIdx);
  idx = intersect(idx, idxmin);
  pk_loc_picked_time_sorted = pk_loc_picked(idx);
  pk_val_picked_time_sorted = pk_val_picked(idx);
  h_path = ht(pk_loc_picked_time_sorted); % sorted order
end