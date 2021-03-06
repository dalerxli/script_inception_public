function [ entries, structured_entries ] = GEO_INP_reader(file_list)
  % function [ entries, structured_entries ] = GEO_INP_reader(file_list)
  % creates entries + structured_entries from file_list

  entries = {};
  structured_entries = FDTDobject();

  for idx = 1:length(file_list)
    filename = file_list{idx};
    % disp(['Processing ', filename]);
    [ entries, structured_entries ] = single_GEO_INP_reader(filename, entries, structured_entries);
  end

end % end of function

function [ entries, structured_entries ] = single_GEO_INP_reader(filename, entries, structured_entries)
  % creates entries + structured_entries from filename
  
  %=====================================================================
  % define structures (TODO: switch to octave+matlab compatible classes)
  %=====================================================================
  time_snapshots = struct('name',{},'first',{},'repetition',{},'plane',{},'P1',{},'P2',{},'E',{},'H',{},'J',{},'power',{},'eps',{});
  frequency_snapshots = struct('name',{},'first',{},'repetition',{},'interpolate',{},'real_dft',{},'mod_only',{},'mod_all',{},'plane',{},'P1',{},'P2',{},'frequency',{},'starting_sample',{},'E',{},'H',{},'J',{});

  time_snapshots_X = struct('name',{},'first',{},'repetition',{},'plane',{},'P1',{},'P2',{},'E',{},'H',{},'J',{},'power',{},'eps',{});
  time_snapshots_Y = struct('name',{},'first',{},'repetition',{},'plane',{},'P1',{},'P2',{},'E',{},'H',{},'J',{},'power',{},'eps',{});
  time_snapshots_Z = struct('name',{},'first',{},'repetition',{},'plane',{},'P1',{},'P2',{},'E',{},'H',{},'J',{},'power',{},'eps',{});
  frequency_snapshots_X = struct('name',{},'first',{},'repetition',{},'interpolate',{},'real_dft',{},'mod_only',{},'mod_all',{},'plane',{},'P1',{},'P2',{},'frequency',{},'starting_sample',{},'E',{},'H',{},'J',{});
  frequency_snapshots_Y = struct('name',{},'first',{},'repetition',{},'interpolate',{},'real_dft',{},'mod_only',{},'mod_all',{},'plane',{},'P1',{},'P2',{},'frequency',{},'starting_sample',{},'E',{},'H',{},'J',{});
  frequency_snapshots_Z = struct('name',{},'first',{},'repetition',{},'interpolate',{},'real_dft',{},'mod_only',{},'mod_all',{},'plane',{},'P1',{},'P2',{},'frequency',{},'starting_sample',{},'E',{},'H',{},'J',{});
    
  all_snapshots = struct('name',{},'first',{},'repetition',{},'interpolate',{},'real_dft',{},'mod_only',{},'mod_all',{},'plane',{},'P1',{},'P2',{},'frequency',{},'starting_sample',{},'E',{},'H',{},'J',{},'power',{});

  excitations = struct(...
    'name', {}, ...
    'current_source', {},...
    'P1', {},...
    'P2', {},...
    'E', {},...
    'H', {},...
    'type', {},...
    'time_constant', {},...
    'amplitude', {},...
    'time_offset', {},...
    'frequency', {},...
    'param1', {},...
    'param2', {},...
    'template_filename', {},...
    'template_source_plane', {},...
    'template_target_plane', {},...
    'template_direction', {},...
    'template_rotation', {});

  boundaries = struct('name',{},'type',{},'position',{});
  box = struct('name',{},'lower',{},'upper',{});
  sphere_list = struct('name',{},'center',{},'outer_radius',{},'inner_radius',{},'permittivity',{},'conductivity',{});
  block_list = struct('name',{},'lower',{},'upper',{},'permittivity',{},'conductivity',{});
  cylinder_list = struct('name',{},'center',{},'inner_radius',{},'outer_radius',{},'height',{},'permittivity',{},'conductivity',{},'angle',{});
  rotation_list = struct('name',{},'axis_point',{},'axis_direction',{},'angle_degrees',{});
  probe_list = struct('name',{},'position',{},'step',{},'E',{},'H',{},'J',{},'pow',{});

  % xmesh = [];
  % ymesh = [];
  % zmesh = [];
  % flag = [];
  % boundaries = [];
  %=====================================================================

  % ask for input file if not given
  if exist('filename','var') == 0
    disp('filename not given');
    [file,path] = uigetfile({'*.geo *.inp'},'Select a GEO or INP file');
    filename = [path,file];
  end
  
  % read the whole file as one string
  fulltext = fileread(filename);

  % remove comments
  pattern_stripcomments = '\*\*(?!name=).*\n';
  cleantext =  regexprep(fulltext, pattern_stripcomments, '\n', 'lineanchors', 'dotexceptnewline', 'warnings');

  % extract blocks
  pattern_objects = '^(?<type>\w+)\s*(?<nameblob>[^\{\}]+)?\{(?<data>[^\{\}]*?)\}';
  [tokens_blocks match_blocks names_blocks] =  regexp(cleantext, pattern_objects, 'tokens', 'match', 'names', 'lineanchors', 'warnings');

  % process blocks
  %disp(['length(names_blocks) = ', num2str(length(names_blocks))]);
  for i = 1:length(names_blocks)

    type = names_blocks(:,i).type;
    nameblob = names_blocks(:,i).nameblob;
    
    name = '';
    if strcmpi(nameblob,'') == 0
      pattern_nameblob = '\*\*name=(?<name>.*)';
      [tokens_nameblob match_nameblob names_nameblob] =  regexp(nameblob, pattern_nameblob, 'tokens', 'match', 'names', 'lineanchors', 'warnings');
      if length(names_nameblob.name) > 0
        name = strtrim(names_nameblob.name);
      end
    end
    
    data = names_blocks(:,i).data;
    % disp(['===>type = ',type]);

    dataV = [];
    % remove empty lines
    lines = strread(data,'%s','delimiter','\n');
    
    %cellFlag = 1;
    
    for L = 1:length(lines)
      if ~length(lines{L})
        continue;
      end

      % num_val will be an empty [] if lines{L} is string
      num_val = str2num(lines{L});
      %L
      %num_val
            
      str_val = strtrim(lines{L}); % trim string
      str_val = str_val(str_val ~= '"');% remove double quotes

      % TODO: Check if this can't be simplified, or if it's even necessary.
      %if cellFlag
        if length(num_val) %% num_val is num
          dataV{length(dataV)+1} = num_val;
        else %% num_val is not num
          dataV{length(dataV)+1} = str_val;
        end
      %else
        %if length(num_val) %% num_val is num
          %dataV = [dataV,num_val];
        %else %% num_val is not num
          %cellFlag = 1;
          %dataV = num2cell(dataV);
          %dataV{length(dataV)+1} = str_val;
        %end
      %end
    end % end of loop through lines
    
    entry.name = name;
    entry.type = type;
    entry.data = dataV';
    entries{length(entries)+1} = entry;

    switch upper(entry.type)
      case {'FREQUENCY_SNAPSHOT','SNAPSHOT'}
        % disp('Adding snapshot...');
        snapshot = add_snapshot(entry);
        all_snapshots = [ all_snapshots snapshot ];
        if strcmpi(entry.type,'FREQUENCY_SNAPSHOT')
          snapshot = add_frequency_snapshot(entry);
          frequency_snapshots = [ frequency_snapshots snapshot ];
                    if snapshot.plane == 1
                        frequency_snapshots_X = [ frequency_snapshots_X snapshot ];
                    elseif snapshot.plane == 2
                        frequency_snapshots_Y = [ frequency_snapshots_Y snapshot ];
                    else
                        frequency_snapshots_Z = [ frequency_snapshots_Z snapshot ];
                    end
        elseif strcmpi(entry.type,'SNAPSHOT')
          snapshot = add_time_snapshot(entry);
          time_snapshots = [ time_snapshots snapshot ];
                    if snapshot.plane == 1
                        time_snapshots_X = [ time_snapshots_X snapshot ];
                    elseif snapshot.plane == 2
                        time_snapshots_Y = [ time_snapshots_Y snapshot ];
                    else
                        time_snapshots_Z = [ time_snapshots_Z snapshot ];
                    end
        else
          error('Sense, it makes none.');
        end
      case {'EXCITATION'}
        current_excitation = add_excitation(entry);
        excitations = [ excitations, current_excitation ];
      case {'XMESH'}
        structured_entries.xmesh = cell2mat(entry.data);
      case {'YMESH'}
        structured_entries.ymesh = cell2mat(entry.data);
      case {'ZMESH'}
        structured_entries.zmesh = cell2mat(entry.data);
            case {'FLAG'}
        structured_entries.flag = add_flag(entry);
            case {'BOUNDARY'}
                structured_entries.boundaries = add_boundary(entry);
            case {'BOX'}
                structured_entries.box = add_box(entry);
            case {'SPHERE'}
        sphere = add_sphere(entry);
        sphere_list = [ sphere_list sphere ];
                % geometry_object_list =  = [ geometry_object_list sphere ];
            case {'BLOCK'}
        block = add_block(entry);
        block_list = [ block_list block ];
            case {'CYLINDER'}
        cylinder = add_cylinder(entry);
        cylinder_list = [ cylinder_list cylinder ];
            case {'ROTATION'}
        rotation = add_rotation(entry);
        rotation_list = [ rotation_list rotation ];
            case {'PROBE'}
        probe = add_probe(entry);
        probe_list = [ probe_list probe ];
      otherwise
        % disp('Unknown type.');
    end % end of switch

  end %end of loop through blocks

  structured_entries.all_snapshots = [ structured_entries.all_snapshots, all_snapshots ];
  structured_entries.time_snapshots =  [structured_entries.time_snapshots, time_snapshots];
  structured_entries.frequency_snapshots =  [structured_entries.frequency_snapshots, frequency_snapshots];

  structured_entries.time_snapshots_X =  [structured_entries.time_snapshots_X, time_snapshots_X];
  structured_entries.time_snapshots_Y =  [structured_entries.time_snapshots_Y, time_snapshots_Y];
  structured_entries.time_snapshots_Z =  [structured_entries.time_snapshots_Z, time_snapshots_Z];
    
  structured_entries.frequency_snapshots_X =  [structured_entries.frequency_snapshots_X, frequency_snapshots_X];
  structured_entries.frequency_snapshots_Y =  [structured_entries.frequency_snapshots_Y, frequency_snapshots_Y];
  structured_entries.frequency_snapshots_Z =  [structured_entries.frequency_snapshots_Z, frequency_snapshots_Z];
    
  structured_entries.excitations =  [structured_entries.excitations, excitations];
  structured_entries.sphere_list =  [structured_entries.sphere_list, sphere_list];
  structured_entries.block_list =  [structured_entries.block_list, block_list];
  structured_entries.cylinder_list =  [structured_entries.cylinder_list, cylinder_list];
  structured_entries.rotation_list =  [structured_entries.rotation_list, rotation_list];
  structured_entries.probe_list =  [structured_entries.probe_list, probe_list];
  % structured_entries.geometry_object_list =  [structured_entries.geometry_object_list, geometry_object_list];
end

function flag = add_flag(entry)
  flag.name = entry.name;
  flag.iMethod = entry.data{1};
  flag.propCons = entry.data{2};
  flag.flagOne = entry.data{3};
  flag.flagTwo = entry.data{4};
  flag.numSteps = entry.data{5};
  flag.stabFactor = entry.data{6};
  flag.id = entry.data{7};
end

function boundaries = add_boundary(entry)
  boundaries.name = entry.name;
  %entry.data
  d = cell2mat(entry.data);
  %length(entry.data)
  % overly complex, but it works for cell and non-cell data...
  M = reshape(d',4,size(d,1)*size(d,2)/4)';
  %M = reshape(entry.data,4,length(entry.data)/4)';
  for i = 1:6
    boundaries(i).type = M(i,1);
    boundaries(i).position = M(i,2:4);
  end
end

function box = add_box(entry)
  box.name = entry.name;
  entry.data = cell2mat(entry.data);
  box.lower = entry.data(1:3);
  box.upper = entry.data(4:6);
end

function sphere = add_sphere(entry)
  sphere.name = entry.name;
  entry.data = cell2mat(entry.data);
  idx = 1;
  sphere.center = entry.data(idx:idx+2); idx = idx+3;
  sphere.outer_radius = entry.data(idx); idx = idx+1;
  sphere.inner_radius = entry.data(idx); idx = idx+1;
  sphere.permittivity = entry.data(idx); idx = idx+1;
  sphere.conductivity = entry.data(idx); idx = idx+1;
end

function block = add_block(entry)
  block.name = entry.name;
  entry.data = cell2mat(entry.data);
  idx = 1;
  block.lower = entry.data(idx:idx+2); idx = idx+3;
  block.upper = entry.data(idx:idx+2); idx = idx+3;
  block.permittivity = entry.data(idx); idx = idx+1;
  block.conductivity = entry.data(idx); idx = idx+1;
end

function cylinder = add_cylinder(entry)
  cylinder.name = entry.name;
  entry.data = cell2mat(entry.data);
  idx = 1;
  cylinder.center = entry.data(idx:idx+2); idx = idx+3;
  cylinder.inner_radius = entry.data(idx); idx = idx+1;
  cylinder.outer_radius = entry.data(idx); idx = idx+1;
  cylinder.height = entry.data(idx); idx = idx+1;
  cylinder.permittivity = entry.data(idx); idx = idx+1;
  cylinder.conductivity = entry.data(idx); idx = idx+1;
  if length(entry.data)>=idx; cylinder.angle = entry.data(idx); else cylinder.angle = 0; end; idx = idx+1;
end

function rotation = add_rotation(entry)
  rotation.name = entry.name;
  entry.data = cell2mat(entry.data);
  idx = 1;
  rotation.axis_point = entry.data(idx:idx+2); idx = idx+3;
  rotation.axis_direction = entry.data(idx:idx+2); idx = idx+3;
  rotation.angle_degrees = entry.data(idx); idx = idx+1;
end

function probe = add_probe(entry)
  probe.name = entry.name;
  entry.data = cell2mat(entry.data);
  idx = 1;
  probe.position = entry.data(idx:idx+2); idx = idx+3;
  probe.step = entry.data(idx); idx = idx+1;
  probe.E = entry.data(idx:idx+2); idx = idx+3;
  probe.H = entry.data(idx:idx+2); idx = idx+3;
  probe.J = entry.data(idx:idx+2); idx = idx+3;
  probe.pow = entry.data(idx); idx = idx+1;
end

% TODO: check necessity of those multiple snapshot adding functions.
function snapshot = add_frequency_snapshot(entry)
  snapshot.name = entry.name;
  entry.data = cell2mat(entry.data);
  idx = 1;
  snapshot.first = entry.data(idx); idx = idx+1;
  snapshot.repetition = entry.data(idx); idx = idx+1;
  snapshot.interpolate = entry.data(idx); idx = idx+1;
  snapshot.real_dft = entry.data(idx); idx = idx+1;
  snapshot.mod_only = entry.data(idx); idx = idx+1;
  snapshot.mod_all = entry.data(idx); idx = idx+1;
  snapshot.plane = entry.data(idx); idx = idx+1;
  snapshot.P1 = [entry.data(idx), entry.data(idx+1), entry.data(idx+2)]; idx = idx+3;
  snapshot.P2 = [entry.data(idx), entry.data(idx+1), entry.data(idx+2)]; idx = idx+3;
  snapshot.frequency = entry.data(idx); idx = idx+1;
  snapshot.starting_sample = entry.data(idx); idx = idx+1;
  snapshot.E = [entry.data(idx), entry.data(idx+1), entry.data(idx+2)]; idx = idx+3;
  snapshot.H = [entry.data(idx), entry.data(idx+1), entry.data(idx+2)]; idx = idx+3;
  snapshot.J = [entry.data(idx), entry.data(idx+1), entry.data(idx+2)]; idx = idx+3;
end

function snapshot = add_time_snapshot(entry)
  snapshot.name = entry.name;
  entry.data = cell2mat(entry.data);
  idx = 1;
  snapshot.first = entry.data(idx); idx = idx+1;
  snapshot.repetition = entry.data(idx); idx = idx+1;
  snapshot.plane = entry.data(idx); idx = idx+1;
  snapshot.P1 = [entry.data(idx), entry.data(idx+1), entry.data(idx+2)]; idx = idx+3;
  snapshot.P2 = [entry.data(idx), entry.data(idx+1), entry.data(idx+2)]; idx = idx+3;
  snapshot.E = [entry.data(idx), entry.data(idx+1), entry.data(idx+2)]; idx = idx+3;
  snapshot.H = [entry.data(idx), entry.data(idx+1), entry.data(idx+2)]; idx = idx+3;
  snapshot.J = [entry.data(idx), entry.data(idx+1), entry.data(idx+2)]; idx = idx+3;
  snapshot.power = entry.data(idx); idx = idx+1;
  if length(entry.data)>=idx; snapshot.eps = entry.data(idx); else snapshot.eps = 0; end; idx = idx+1;
end

function snapshot = add_snapshot(entry)
  snapshot.name = entry.name;
  if strcmpi(entry.type,'FREQUENCY_SNAPSHOT')
    idx = 1;
    snapshot.first = entry.data(idx); idx = idx+1;
    snapshot.repetition = entry.data(idx); idx = idx+1;
    snapshot.interpolate = entry.data(idx); idx = idx+1;
    snapshot.real_dft = entry.data(idx); idx = idx+1;
    snapshot.mod_only = entry.data(idx); idx = idx+1;
    snapshot.mod_all = entry.data(idx); idx = idx+1;
    snapshot.plane = entry.data(idx); idx = idx+1;
    snapshot.P1 = [entry.data(idx), entry.data(idx+1), entry.data(idx+2)]; idx = idx+3;
    snapshot.P2 = [entry.data(idx), entry.data(idx+1), entry.data(idx+2)]; idx = idx+3;
    snapshot.frequency = entry.data(idx); idx = idx+1;
    snapshot.starting_sample = entry.data(idx); idx = idx+1;
    snapshot.E = [entry.data(idx), entry.data(idx+1), entry.data(idx+2)]; idx = idx+3;
    snapshot.H = [entry.data(idx), entry.data(idx+1), entry.data(idx+2)]; idx = idx+3;
    snapshot.J = [entry.data(idx), entry.data(idx+1), entry.data(idx+2)]; idx = idx+3;
    snapshot.power = -1;
  elseif strcmpi(entry.type,'SNAPSHOT')
    idx = 1;
    snapshot.first = entry.data(idx); idx = idx+1;
    snapshot.repetition = entry.data(idx); idx = idx+1;
    snapshot.interpolate = -1;
    snapshot.real_dft = -1;
    snapshot.mod_only = -1;
    snapshot.mod_all = -1;
    snapshot.plane = entry.data(idx); idx = idx+1;
    snapshot.P1 = [entry.data(idx), entry.data(idx+1), entry.data(idx+2)]; idx = idx+3;
    snapshot.P2 = [entry.data(idx), entry.data(idx+1), entry.data(idx+2)]; idx = idx+3;
    snapshot.frequency = -1;
    snapshot.starting_sample = -1;
    snapshot.E = [entry.data(idx), entry.data(idx+1), entry.data(idx+2)]; idx = idx+3;
    snapshot.H = [entry.data(idx), entry.data(idx+1), entry.data(idx+2)]; idx = idx+3;
    snapshot.J = [entry.data(idx), entry.data(idx+1), entry.data(idx+2)]; idx = idx+3;
    snapshot.power = entry.data(idx); idx = idx+1;
  else
    error('Sense, it makes none.');
  end
end

function current_excitation = add_excitation(entry)
  current_excitation.name = entry.name;
  idx = 1;
  current_excitation.current_source = entry.data(idx); idx = idx+1;
  current_excitation.P1 = cell2mat([entry.data(idx), entry.data(idx+1), entry.data(idx+2)]); idx = idx+3;
  current_excitation.P2 = cell2mat([entry.data(idx), entry.data(idx+1), entry.data(idx+2)]); idx = idx+3;
  %idx
  %entry.data
  %[entry.data(idx), entry.data(idx+1), entry.data(idx+2)]
  current_excitation.E = cell2mat([entry.data(idx), entry.data(idx+1), entry.data(idx+2)]); idx = idx+3;
  %current_excitation.E = [entry.data(idx), entry.data(idx+1), entry.data(idx+2)]; idx = idx+3;
  %current_excitation.E
  %class(current_excitation.E)
  current_excitation.H = cell2mat([entry.data(idx), entry.data(idx+1), entry.data(idx+2)]); idx = idx+3;
  %current_excitation.H = [entry.data(idx), entry.data(idx+1), entry.data(idx+2)]; idx = idx+3;
  current_excitation.type = entry.data(idx); idx = idx+1;
  current_excitation.time_constant = entry.data(idx); idx = idx+1;
  current_excitation.amplitude = entry.data(idx); idx = idx+1;
  current_excitation.time_offset = entry.data(idx); idx = idx+1;
  current_excitation.frequency = entry.data(idx); idx = idx+1;
  current_excitation.param1 = entry.data(idx); idx = idx+1;
  current_excitation.param2 = entry.data(idx); idx = idx+1;

  if cell2mat(entry.data(idx))==0
    current_excitation.template_filename = 'template_filename'; idx = idx+1;
  else
    current_excitation.template_filename = char(entry.data(idx)); idx = idx+1;
  end

  current_excitation.template_source_plane = entry.data(idx); idx = idx+1;

  if idx<=length(entry.data)
    current_excitation.template_target_plane = entry.data(idx); idx = idx+1;
  else
    current_excitation.template_target_plane = 'x'; idx = idx+1;
  end

  if idx<=length(entry.data)
    current_excitation.template_direction = entry.data(idx); idx = idx+1;
  else
    current_excitation.template_direction = 0; idx = idx+1;
  end

  if idx<=length(entry.data)
    current_excitation.template_rotation = entry.data(idx); idx = idx+1;
  else
    current_excitation.template_rotation = 0; idx = idx+1;
  end

end
