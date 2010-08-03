function [fft_out,lambda,freq] = bFFT(datain,dt)
	% function [fft_out,lambda,freq] = bFFT(datain,dt)
	% datain = datain value in time domain
	% dt = timestep in time domain
	% fft_out = magnitude 
	% freq = frequency
	% lambda = wavelength = c0/freq

	Lin=length(datain);
	NFFT = 2^nextpow2(Lin); % Next power of 2 from length of datain

	fft_out = fft(datain,NFFT);

    Lout = length(fft_out);
	fft_out = fft_out(1:Lout/2);

    %relative frequency according to nyquist criterion
    nyqfreq = 1/dt;

	% freq = nyqfreq/2*linspace(0,1,length(fft_out));
    freq = nyqfreq/Lout*linspace(1,Lout/2,length(fft_out));

	%wavelength from FDTD frequency units
	c0 = 2.99792458E8;
    lambda = c0./freq;

end
