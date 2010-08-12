function [header,data,ux,uy]=readPrnFile(filename)

if (nargin==0)
    [FileName,PathName] = uigetfile({'*.prn *.dat'},'Select the prn-file','D:\Simulations\BFDTD\');
    filename=[PathName,'\',FileName];
end

fid = fopen(filename,'rt');

try
    dummy = fgets(fid);
    words=regexp(dummy,'(?<word>\w+)\s*|\s*(?<word>\w+)','names');
    ncols=size(words,2);

    for m=1:ncols
       header{m} =words(m).word;
    end

    M=fscanf(fid,'%f');
    fclose(fid);
    
    data=reshape(M,ncols,length(M)/ncols);
    data=data';
    
    ux=[];
    uy=[];
    if nargout>3 && not(strcmp(header{1},'Time'))
        x=data(:,1);
        y=data(:,2);
        ux=unique(x);
        nx=length(ux);
        ny=length(x)/nx;
        uy=y(1:ny);
        for m=3:size(data,2)
            Data(:,:,m-2)=reshape(data(:,m),ny,nx);
        end
        data=Data;
        imagesc(ux,uy,Data(:,:,1));
    end
catch
    header=[];
    data=[];
end



% figure
% plot(data(:,1),data(:,2:end));

% if nargout>3
%     sp=1;
% %     for m=1:2:size(Data,3)
%     for m=2:size(data,3)
% %         Int=Data(:,:,m).^2+Data(:,:,m+1).^2;
%         Int=Data(:,:,m);
%         subplot(3,2,sp);
%         imagesc(Int)
% %         title([header{m+2},'^2+',header{m+3},'^2'])
%         title(header{m})
%         set(gca,'YDir','normal')
%         colorbar
%         sp=sp+1;
%     end
% end

