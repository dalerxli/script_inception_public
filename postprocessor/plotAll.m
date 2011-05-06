function plotAll(directory, specific_probe_cell)

  % ex: specific_probe_cell = {'pxx.prn','ptyruytue.prn',etc}
  
  if exist('directory','var')==0
    directory = pwd();
  end

  % loop through .sh files  
  [Files,Bytes,Names] = dirr(directory,'\.sh\>','name');
  for script_idx = 1:length(Names)
    script_filename = char(Names(script_idx));
    [ script_folder, script_basename, script_ext ] = fileparts(script_filename);

    handles = struct;

    handles.geofile = [ script_folder, filesep, script_basename, '.geo' ];
    handles.inpfile = [ script_folder, filesep, script_basename, '.inp' ];
    
    disp(['Processing ', script_folder]);
    [entries,FDTDobj]=GEO_INP_reader({handles.geofile,handles.inpfile});
    excitation = FDTDobj.excitations(1).E;

    if excitation == [1,0,0]
      probe_col = 2
      TimeSnapshot_col = 3;
      FrequencySnapshot_col = 3;
    elseif excitation == [0,1,0]
      probe_col = 3
      TimeSnapshot_col = 4;
      FrequencySnapshot_col = 6;
    elseif excitation == [0,0,1]
      probe_col = 4
      TimeSnapshot_col = 5;
      FrequencySnapshot_col = 9;
    else
      error('Unknown excitation');
    end

    % store workdir
    workdir = pwd();

    % loop through .prn files
    cd(script_folder);
    prnFiles = dir('*.prn');
    for prn_idx = 1:length(prnFiles)
      prn_filename = prnFiles(prn_idx).name;
      [ prn_filename_folder, prn_filename_basename, prn_filename_ext ] = fileparts(prn_filename);
      disp(['Processing ', prn_filename]);
      [type_ID, type_name] = getDataType(prn_filename);
      if strcmp(type_name, 'Probe')
        if ( exist('specific_probe_cell','var')==0 ) | ( exist('specific_probe_cell','var')==1 & max(strcmp([prn_filename_basename, prn_filename_ext],specific_probe_cell)) )
          disp('plotting Probe');
          plotProbe(prn_filename, probe_col, false, [ prn_filename_folder, prn_filename_basename, '.png' ],true);
        end
      elseif strcmp(type_name, 'TimeSnapshot')
        disp('plotting TimeSnapshot');
        
        % loading
        handles.snapfile = fullfile(script_folder,prn_filename);
        [handles.header, handles.fin1] = hdrload(handles.snapfile);
        handles.gr = size(handles.fin1);
        columns = strread(handles.header,'%s');
        if strcmp(columns(1),'y') && strcmp(columns(2),'z')
          handles.plane = 1;
          handles.maxy = handles.fin1(handles.gr(1),1);
          handles.maxz = handles.fin1(handles.gr(1),2);
        elseif strcmp(columns(1),'x') && strcmp(columns(2),'z')
          handles.plane = 2;
          handles.maxx = handles.fin1(handles.gr(1),1);
          handles.maxz = handles.fin1(handles.gr(1),2);
        else
          handles.plane = 3;
          handles.maxx = handles.fin1(handles.gr(1),1);
          handles.maxy = handles.fin1(handles.gr(1),2);
        end
        handles.AllHeaders = columns; % all headers
        
        % setting up the handles structure:
        % handles.geofile; % already defined
        % handles.inpfile; % already defined
        % handles.AllHeaders; % defined during load
        % handles.fin1; % defined during load
        % handles.gr; % defined during load
        % handles.plane; % defined during load
        handles.autosave = 0;
        handles.colour = 1;
        handles.geometry = 1;
        handles.interpolate = 0;
        handles.modulus = 0;
        handles.surface = 1;

        % time snapshot specific
        handles.Type = 2;
        col = TimeSnapshot_col;
        imageSaveName = 'test.png';

        % other variables
        maxplotvalue = NaN;
        
        % finally plotting
        plotgen(maxplotvalue, col, handles, imageSaveName, true);

      elseif strcmp(type_name, 'FrequencySnapshot')
        disp('plotting FrequencySnapshot');
      elseif strcmp(type_name, 'Reference')
        disp('skipping Reference');
      else
        warning('Unknown data type');
      end
    end

    % restore workdir
    cd(workdir);
    
  end
  return;

plotProbe(filename, probe_col, autosave, imageSaveName)
plotgen(maxval,column,handles)

  handles.isLoaded = 0;
  handles.workdir = pwd();
  handles.snaplist = {};
  handles.geolist = {};
  handles.inplist = {};

  % browse
  [handles, dirChosen] = PP_browse(handles);
  if ~dirChosen
    return
  end

  handles.Type = 2;
  handles.ProbeID = 1;
  handles.TimeSnapshotID = 1;
  handles.FrequencySnapshotID = 1;
  handles.geometryfile = 1;
  handles.inputfile = 1;
  
  % load data
  [ handles ] = PP_load_data(handles);
  if ~handles.isLoaded
    return
  end
  
  handles.col = 3;
  handles.maxplotvalue = NaN;

  handles.interpolate = 0;
  handles.autosave= 0;
  handles.geometry= 1;
  handles.modulus = 0;

  handles.colour = 1;
  handles.surface = 1;

  % generate plot
  [ handles, ok ] = PP_generate_plot(handles);
end
