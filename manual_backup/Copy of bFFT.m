function [Y,lambda,f]=bFFT(y,dt)
% function [Y,lambda,f]=bFFT(y,dt)
% y = y value in time domain
% dt = timestep in time domain
% Y = magnitude 
% f = frequency
% lambda = wavelength = c0/f

	L=length(y);
	NFFT = 2^nextpow2(L); % Next power of 2 from length of y
	Y = fft(y,NFFT)/L;
	Y=Y(1:NFFT/2);
	Fs=1/dt;
	f = Fs/2*linspace(0,1,NFFT/2);

	f(2)-f(1);

	c0=2.99792458E8;
	lambda=c0./f;
end
