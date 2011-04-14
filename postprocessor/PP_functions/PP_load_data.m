function [ handles, isLoaded ] = PP_load_data(handles)
  disp('function pushbutton_load_data_Callback(hObject, eventdata, handles)')
  % --- Executes on button press in pushbutton_load_data.
  % hObject    handle to pushbutton_load_data (see GCBO)
  % eventdata  reserved - to be defined in a future version of MATLAB
  % handles    structure with handles and user data (see GUIDATA)

  val = handles.geometryfile;
  if (val<1) | (length(handles.geolist)<val)
    isLoaded = 0;
    return
  end
  geofile = handles.geolist{val};
  handles.geofile = [handles.workdir, filesep, geofile];
  
  val = handles.inputfile;
  if (val<1) | (length(handles.inplist)<val)
    isLoaded = 0;
    return
  end
  inpfile = handles.inplist{val};
  handles.inpfile = [handles.workdir, filesep, inpfile];

  if handles.Type == 1
    val = handles.ProbeID;
    if (val<1) | (length(handles.ProbeList)<val)
      isLoaded = 0;
      return
    end
    name = handles.ProbeList{val};
    handles.ProbeFile = [handles.workdir, filesep, name];
    %load snapshot data
    [handles.header, handles.fin1] = hdrload(handles.ProbeFile);
  elseif handles.Type == 2
    val = handles.TimeSnapshotID;
    if (val<1) | (length(handles.TimeSnapshotList)<val)
      isLoaded = 0;
      return
    end
    name = handles.TimeSnapshotList{val};
    handles.TimeSnapshotFile = [handles.workdir, filesep, name];
    [handles.header, handles.fin1] = hdrload(handles.TimeSnapshotFile);
  elseif handles.Type == 3
    val = handles.FrequencySnapshotID;
    if (val<1) | (length(handles.FrequencySnapshotList)<val)
      isLoaded = 0;
      return
    end
    name = handles.FrequencySnapshotList{val};
    handles.FrequencySnapshotFile = [handles.workdir, filesep, name];
    [handles.header, handles.fin1] = hdrload(handles.FrequencySnapshotFile);
  else
    error('Unknown data type')
    return
  end
  
  %determine orientation of snapshot
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
  
  handles.colplot = columns; % all headers
  columns = columns(3:length(columns));
  columns = char(columns);
  handles.plotcolumn = columns; % all headers except the two first ones
  
  handles.isLoaded = 1;
  isLoaded = 1;
end
