% this is getting out of hand... Oh well, things need to get done. Code can be cleaned up later...
function analyzePRN3(prn_file, logfile)

  [ folder, basename, ext ] = fileparts(prn_file);
  WORKDIR = dirname(prn_file);

  wavelength_nm = 900;
  iterations = 1231321;
  Qfactor_harminv = 1212.35656;
  Qfactor_fitting = 545.3235;

  %logfile = '~/tmpQ.txt';
  probe_col = 3;

  fid = fopen([WORKDIR, filesep, 'time.txt'], 'r'); A = textscan(fid,'%s %s %d:%d:%d',1); B = textscan(fid,'%d %s %d:%d:%d'); fclose(fid); iterations = B{1}(end);

  %[ wavelength_nm, Q_lorentz, Q_harminv_local, Q_harminv_global ] = plotProbe(prn_file, probe_col, 1, '', true);

  fid = fopen(logfile, 'at');
  %fprintf(fid, 'File\tIterations\tWavelength(nm)\tQ-factor(harminv)\tQ-factor(fitting)\n');
  %fprintf(fid, '%s\t%d\t%0.0f\t%0.0f\t%0.0f\n', prn_file, iterations, wavelength_nm(i), Q_lorentz(i), Q_harminv_local(i), Q_harminv_global(i));
  %fprintf(fid, 'File\tIterations\n');
  fprintf(fid, '%s\t%d\n', GetFullPath(prn_file), iterations);
  %fprintf(fid, 'wavelength_nm\tQ_lorentz\tQ_harminv_local\tQ_harminv_global\n')
  %for i=1:length(wavelength_nm)
    %fprintf(fid, '%0.0f\t%0.0f\t%0.0f\t%0.0f\n', wavelength_nm(i), Q_lorentz(i), Q_harminv_local(i), Q_harminv_global(i));
  %end
  fclose(fid);

end

%plotProbe(filename, probe_col, autosave, imageSaveName, hide_figures)
