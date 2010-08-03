function [x0, y0, A, w] = mylorentzfit(x,yOrig, vStart)
	% Fits with a function of the form:
	% y=y0+(2*A/pi).*(w./(4*(x-x0).^2+w.^2));
	% gamma = w/2
	% vStart = [x0, y0, A, w]

	function [y]=lorentz(v,x)
		y0=v(1);
		A=v(2);
		w=v(3);
		x0=v(4);
		y=y0+(2*A/pi).*(w./(4*(x-x0).^2+w.^2));
	end

	%% default arguments
	if nargin<3
		x0=7;
		y0=2.5;
		A=5;
		w=4;
		vStart=[y0,A,w,x0];
	end
	
	%% define start point
	% vStart=[y0,A,w,x0];
	fprintf('Start:  y0=%E  A=%E  w=%E  x0=%E\n',vStart(1),vStart(2),vStart(3),vStart(4)); 

	%% fit using nlinfit
	vEnd=nlinfit(x,yOrig,@lorentz,vStart);
	fprintf('End:  y0=%E  A=%E  w=%E  x0=%E\n',vEnd(1),vEnd(2),vEnd(3),vEnd(4)); 
	
	y0=vEnd(1);
	A=vEnd(2);
	w=vEnd(3);
	x0=vEnd(4);

	% plotting
	figure;
	plot(x,yOrig,'ob');
	hold on;

	yStart=lorentz(vStart,x);
	plot(x,yStart,'-r');
	
	yEnd=lorentz(vEnd,x);
	plot(x,yEnd,'-g');
	legend('Orig','Start','End');
	set(gca,'Color',[0.7,0.7,0.7]);
	set(gcf,'Color',[1,1,1]);

end
