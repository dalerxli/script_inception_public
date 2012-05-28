function [x0,y0,A,FWHM] = getLorentzStartValues(X,Y,isInverted)

  % Usage:
  %   [x0,y0,A,FWHM] = getLorentzStartValues(X,Y,isInverted)
  %
  % Returns [x0,y0,A,FWHM] values for a fit based on looking at the maximum, FWHM and position of a lorentz-like peak. cf lorentz() function for more details.
  %
  % TODO: See if code cannot be simplified to handle both cases
  
  if isInverted == 0
    index_max = find(Y == max(Y) );
    x0 = X(index_max);
    y0 = min(Y);
    X1 = X(1:index_max);
    X2 = X(index_max:length(X));
    Y1 = Y(1:index_max);
    Y2 = Y(index_max:length(Y));
    halfmax = 0.5*(min(Y)+max(Y));
    Ydiff1=abs(Y1-halfmax);
    Ydiff2=abs(Y2-halfmax);
    index_FWHM_1 = find( Ydiff1 == min(Ydiff1) );
    index_FWHM_2 = find( Ydiff2 == min(Ydiff2) );
    FWHM = abs(X2(index_FWHM_2) - X1(index_FWHM_1));
    A = 0.5*FWHM*(pi*(max(Y)-y0));
  else
    index_min = find(Y == min(Y) );
    x0 = X(index_min);
    y0 = max(Y);
    X1 = X(1:index_min);
    X2 = X(index_min:length(X));
    Y1 = Y(1:index_min);
    Y2 = Y(index_min:length(Y));
    halfmax = 0.5*(min(Y)+max(Y));
    Ydiff1 = abs(Y1-halfmax);
    Ydiff2 = abs(Y2-halfmax);
    index_FWHM_1 = find( Ydiff1 == min(Ydiff1) );
    index_FWHM_2 = find( Ydiff2 == min(Ydiff2) );
    FWHM = abs(X2(index_FWHM_2) - X1(index_FWHM_1));
    A = 0.5*FWHM*(pi*(min(Y)-y0));
  end
  
end
