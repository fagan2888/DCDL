# -*- coding: utf-8 -*-
import struct
import numpy as np
import math
import os

dir = os.path.dirname(__file__)
filename = os.path.abspath(os.path.join(os.path.dirname(__file__),'birdwav.wav'))
f = open(filename,'rb')
outputfilepath = os.path.abspath(os.path.join(os.path.dirname(__file__),'spectrogram.spg'))
f.seek(84)
a = struct.unpack('<I',f.read(4))
numsamples = int(a[0]/8)
signals = np.zeros((numsamples,2),dtype='float32')
for i in range(0,numsamples):
    for j in range(0,2):
        a = struct.unpack('<f',f.read(4))
        signals[i][j] = float(a[0])
f.close()
Fs = 44100; #Sampling frequency in Hz
NFFT = 2048; #Size of the sliding window
lf = int(NFFT/2+1)
f = np.linspace(0,1,lf)
for i in range(0,lf):
    f[i] = (Fs/2)*f[i];
freqrange = []
freqrange.append(20)
freqrange.append(415)

a = range(0,NFFT)
#The following variable is a Hamming window which is a set of weights that will increase the accuracy of your resulting spectrogram (see Wikipedia)
w = np.zeros((NFFT),dtype='float32')
for i in range(0,NFFT):
    w[i] = (float(25)/float(46)) - ((float(21)/float(46)) * math.cos((float(2)*math.pi*float(a[i]))/float(NFFT-1)))

#The following variable is the number of samples we will skip when computing the next vertical line in our spectrogram
#1 vertical line represents the strength of all frequencies at a specific time
skipnum = 50   
samplenum = 155 * skipnum
duration = numsamples - NFFT

#Generate spectrogram and store it to disk (specified by outputfilepath)
a = np.zeros((NFFT),dtype='float32')
outfile = open(outputfilepath,'wb')
while (samplenum < duration):
    for i in range(0,NFFT):
        a[i] = w[i] * signals[i+samplenum][0]
    fftoutput = np.fft.fft(a)
    for y in range(freqrange[0],freqrange[1]+1):
        tempval = 20*np.log10(np.absolute(fftoutput[y]))
        outfile.write(struct.pack('<f',tempval))
    samplenum = samplenum + skipnum
outfile.close()

signals = None

#Load spectrogram from disk
duration = math.floor((numsamples - NFFT - (155*skipnum)) / 50) + 1
lf = freqrange[1] - freqrange[0] + 1
spectrogram = np.zeros((lf,duration),dtype='float32')
f = open(outputfilepath,'rb')
for j in range(0,duration):
    for i in range(0,lf):
        a = struct.unpack('<f',f.read(4))
        spectrogram[i][j] = float(a[0])
f.close()

#Determine the loudest frequency at each time point
fmax = np.zeros((duration),dtype='int')
for j in range(0,duration):
    fmax[j] = 0
    mymax = spectrogram[fmax[j]][j]
    for i in range(1,lf):
        if (spectrogram[i][j] > mymax):
            mymax = spectrogram[i][j]
            fmax[j] = i
        
#In the following variable, store the absolute number times that the previous loudest frequency was f (1st dimension), given the current loudest frequency f' (2nd dimension)
markovabs = np.zeros((lf,lf),dtype='int')
#In the following variable, store the total number of times a frequency, f, was the loudest
fmaxtotal = np.zeros((lf),dtype='int')
#The following variable is the sum of the amplitudes of all frequencies, for each time point
sumfreqs = np.zeros((duration),dtype='float32')
fmaxtotal[fmax[0]] = 1
for j in range(1,duration):
    markovabs[fmax[j-1]][fmax[j]] = markovabs[fmax[j-1]][fmax[j]] + 1
    fmaxtotal[fmax[j]] = fmaxtotal[fmax[j]] + 1
for j in range(0,duration):
    for i in range(0,lf):
        sumfreqs[j] = sumfreqs[j] + spectrogram[i][j]
#In the following variable, store the probability of observing the previous loudest frequency to be f (1st dimension), given the current loudest frequency f' (2nd dimension)
markovprobs = np.zeros((lf,lf),dtype='float32')
for j in range(0,lf):
    if (fmaxtotal[j] > 0):
        for i in range(0,lf):
            markovprobs[i][j] = float(markovabs[i][j]) / float(fmaxtotal[j])
            
#The following variable is a threshold for determining a new tweet. We don't want to count as a new tweet - later parts of the same tweet that we are already measuring
tweetthreshold = .01
#In the following variable, we specify the amount of time during which we will record the shape of a tweet
tweetduration = 70
#In the following variable, each row is an observation (1st dimension), each column is a feature (2nd dimension)
tweets = []
#The following variable records how many tweets have been observed
tweetcounter = 0
for j in range(1,duration):
    if ((markovprobs[fmax[j-1]][fmax[j]] < tweetthreshold) and ((tweetduration + j) < duration)):
        tweets.append(np.zeros((tweetduration+1),dtype='float32'))
        tweets[tweetcounter][0] = sumfreqs[j]
        tweets[tweetcounter][1] = float(fmax[j])
        for i in range(1,tweetduration):
            #Measure the cumulative slope
            tweets[tweetcounter][i+1] = float(fmax[j+i] - fmax[j]) / float(i)
        tweetcounter += 1


        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
        
        
        
        