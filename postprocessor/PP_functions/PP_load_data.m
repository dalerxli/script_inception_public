function [ handles ] = PP_load_data(handles)
  disp('function [ handles ] = PP_load_data(handles)')
  % --- Executes on button press in pushbutton_load_data.
  % hObject    handle to pushbutton_load_data (see GCBO)
  % eventdata  reserved - to be defined in a future version of MATLAB
  % handles    structure with handles and user data (see GUIDATA)

  handles.isLoaded = 0;

  val = handles.geometryfile;
  if (1<=val) & (val<=length(handles.geolist))
    geofile = handles.geolist{val};
    handles.geofile = [handles.workdir, filesep, geofile];
  else
    if (handles.Type == 2) | (handles.Type == 3)
      handles.isLoaded = 0;
      return;
    end
  end

  val = handles.inputfile;
  if (1<=val) & (val<=length(handles.inplist))
    inpfile = handles.inplist{val};
    handles.inpfile = [handles.workdir, filesep, inpfile];
  else
    if (handles.Type == 2) | (handles.Type == 3)
      handles.isLoaded = 0;
      return;
    end
  end
  
  if handles.Type == 1
    val = handles.ProbeID;
    if (val<1) | (length(handles.ProbeList)<val)
      handles.isLoaded = 0;
      return
    end
    name = handles.ProbeList{val};
    handles.ProbeFile = [handles.workdir, filesep, name];
    handles.snapfile = handles.ProbeFile;
  elseif handles.Type == 2
    val = handles.TimeSnapshotID;
    if (val<1) | (length(handles.TimeSnapshotList)<val)
      handles.isLoaded = 0;
      return
    end
    name = handles.TimeSnapshotList{val};
    handles.TimeSnapshotFile = [handles.workdir, filesep, name];
    handles.snapfile = handles.TimeSnapshotFile;
  elseif handles.Type == 3
    val = handles.FrequencySnapshotID;
    if (val<1) | (length(handles.FrequencySnapshotList)<val)
      handles.isLoaded = 0;
      return
    end
    name = handles.FrequencySnapshotList{val};
    handles.FrequencySnapshotFile = [handles.workdir, filesep, name];
    handles.snapfile = handles.FrequencySnapshotFile;
  elseif handles.Type == 4
    val = handles.ExcitationTemplateID;
    if (val<1) | (length(handles.ExcitationTemplateList)<val)
      handles.isLoaded = 0;
      return
    end
    name = handles.ExcitationTemplateList{val};
    handles.ExcitationTemplateFile = [handles.workdir, filesep, name];
    handles.snapfile = handles.ExcitationTemplateFile;
  elseif handles.Type == 5
    val = handles.SnapshotID;
    if (val<1) | (length(handles.SnapshotList)<val)
      handles.isLoaded = 0;
      return
    end
    name = handles.SnapshotList{val};
    handles.SnapshotFile = [handles.workdir, filesep, name];
    handles.snapfile = handles.SnapshotFile;
  elseif handles.Type == 6
    % TODO: Implement this.
    error('Energy snapshots not yet implemented. Use createEnergySnapshot() function in the meanwhile.');
  else
    error('Unknown data type')
    return
  end

  %load snapshot data
  [handles.header, handles.data] = hdrload(handles.snapfile);
  
  %determine orientation of snapshot
  % TODO: Use the maximums calculated here
  handles.dataSize = size(handles.data);
  columns = strread(handles.header,'%s');
  if strcmp(columns(1),'y') && strcmp(columns(2),'z')
    handles.plane = 1;
    handles.maxy = handles.data(handles.dataSize(1),1);
    handles.maxz = handles.data(handles.dataSize(1),2);
  elseif strcmp(columns(1),'x') && strcmp(columns(2),'z')
    handles.plane = 2;
    handles.maxx = handles.data(handles.dataSize(1),1);
    handles.maxz = handles.data(handles.dataSize(1),2);
  elseif strcmp(columns(1),'#y') && strcmp(columns(2),'z')
    handles.plane = 1;
    handles.maxy = handles.data(handles.dataSize(1),1);
    handles.maxz = handles.data(handles.dataSize(1),2);
  elseif strcmp(columns(1),'#x') && strcmp(columns(2),'z')
    handles.plane = 2;
    handles.maxx = handles.data(handles.dataSize(1),1);
    handles.maxz = handles.data(handles.dataSize(1),2);
  else
    handles.plane = 3;
    handles.maxx = handles.data(handles.dataSize(1),1);
    handles.maxy = handles.data(handles.dataSize(1),2);
  end
  
  handles.AllHeaders = columns; % all headers

  if handles.Type == 1
    handles.HeadersForPopupList = char(columns(2:length(columns))); % all headers except the one/two first ones
  elseif handles.Type == 2
    handles.HeadersForPopupList = char(columns(3:length(columns))); % all headers except the one/two first ones
  elseif handles.Type == 3
    handles.HeadersForPopupList = char(columns(3:length(columns))); % all headers except the one/two first ones
  elseif handles.Type == 4
    handles.HeadersForPopupList = char(columns(3:length(columns))); % all headers except the one/two first ones
  elseif handles.Type == 5
    handles.HeadersForPopupList = char(columns(3:length(columns))); % all headers except the one/two first ones
  else
    error('Unknown data type')
    return
  end
  
  handles.isLoaded = 1;
end
