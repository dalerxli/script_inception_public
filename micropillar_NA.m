function micropillar_NA(caseID, INP_FILE)

	% if exist('DIR','var')==0
		% disp('DIR not given');
	    % DIR = uigetdir(getuserdir(),'DIR');
	% end
	% if ~(exist(DIR,'dir'))
		% error('dir not found');
	% end
	
	% [ folder, basename, ext ] = fileparts(DIR);
	
	% INP_FILE = fullfile(DIR, [basename,'.inp']);

	if exist('caseID','var')==0
		disp('caseID not given');
		caseID = 0;
	end
	
	if exist('INP_FILE','var')==0
		disp('INP_FILE not given');
		[FileName,PathName] = uigetfile('*.inp','Select the INP file');
		INP_FILE = [PathName, filesep, FileName];
	end

	if ~(exist(INP_FILE,'file'))
		error( ['File not found: ',INP_FILE] );
	end
	
	INP_FILE

	[ folder, basename, ext ] = fileparts(INP_FILE);
	folder
	
	[ entries, structured_entries ] = GEO_INP_reader(INP_FILE);
	Nx = 6;
	Ny = 12;
	Nz = 11;
	Nfs = length(structured_entries.frequency_snapshots)
	Nts = length(structured_entries.time_snapshots)
	
	% normal case:
	% Nfs = (Nx+Ny+Nz+6)*(Nfreq+1)
	% abnormal case:
	% Nfs = (Nx+Ny+Nz)*(Nfreq+1)+6*1
	
	% Nts = (Nx+Ny+Nz+6)

	
	switch caseID
		case {0}
			disp('NORMAL CASE');
			% normal case:
			Nfreq = uint16(Nfs/(Nx+Ny+Nz+6)-1)
			if Nfs ~= (Nx+Ny+Nz+6)*(Nfreq+1)
				error('Nfs incorrect');
			end
		case {1}
			disp('ABNORMAL CASE');
			% abnormal case:
			Nfreq = uint16((Nfs-6)/(Nx+Ny+Nz)-1)
			if Nfs ~= (Nx+Ny+Nz)*(Nfreq+1)+6*1
				error('Nfs incorrect');
			end
		otherwise
			error('Unknown case.');
	end % end of switch
	
	if Nts ~= (Nx+Ny+Nz+6)
		error('Nts incorrect');
	end
	
	Yplane_index = 8:12;
	frequency_index = 1:(Nfreq+1);

	numID_min = Nx*(Nfreq+1+1) + (Yplane_index(1)-1)*(Nfreq+1+1) + frequency_index(1)
	numID_max = Nx*(Nfreq+1+1) + (Yplane_index(length(Yplane_index))-1)*(Nfreq+1+1) + frequency_index(length(frequency_index))
	numID = Nx*(Nfreq+1+1) + (Yplane_index(1)-1)*(Nfreq+1+1) + frequency_index(length(frequency_index))
		
	snap_plane = 'y';
	probe_ident = 'id';
	snap_time_number = 0;
	[ PRN_FILE, alphaID, pair ] = numID_to_alphaID(numID, snap_plane, probe_ident, snap_time_number)

	if ~(exist(PRN_FILE,'file'))
		error([PRN_FILE, ' not found']);
	end
	
	PRN_FILE
	
	NA = calculateNA(INP_FILE, PRN_FILE, 50)
	
end
