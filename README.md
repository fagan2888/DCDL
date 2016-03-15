analyze_bird2
==============

Birdsong entry generation


About
-----

This script isolates bird chirps and characterizes important characteristics about them, using an audio recording as input.
Matt Anderson

Data
----

The data is a 12 min stereo audio recording of a forest full of birds. Data is sampled at a rate of 44100 Hz and is a string of 32-bit floats with alternating left and right channels.
Data may be accessed at https://slack-files.com/T03AGEMF5-F0NPEVA56-b20f2ebc60

Note that posting this raw data to github is not going to happen. Github has a filesize limit of 25MB.

Goal
----

This script uses a short-time sliding discrete fourier transform to generate a spectrogram of an audio recording. A Markov process of the loudest frequency at each moment in time is used to distinguish new instances of a chirp.

Approach
--------

One of the best methods of representing sounds to computer is with a spectrogram. A spectrogram is a heatmap representation of sounds in frequency space. Most spectrograms represent frequency along their vertical axis and time along the horizontal. The heatmap representation of a spectrogram refers to the power of a certain frequency at a certain time. The spectrogram is generated using a short-time sliding discrete fourier transform (DFT). This method offers maximal resolution in the frequency and time domains. As the sliding window progresses through the recording, it creates short audio segments shaped by a Hamming window (https://en.wikipedia.org/wiki/Window_function#Generalized_Hamming_windows). This step increases the spectrogram's accuracy. A fourier transform is applied to each segment and the magnitude results in units of decibels are saved to disk. To save memory, only the relevant frequencies from 430-8936 Hz are recorded.

After the spectrogram is generated, the original audio signals are cleared from memory and the spectrogram is loaded from disk. The loudest frequency at each moment in time is computed. To distinguish new instances of a chirp, I exploit the observation that most chirps have stereotyped sounds. Chirps can be modeled as strings of specific frequencies across time. A first-order Markov process is used to model the probability distribution of the previously observed loudest frequency, given the current loudest frequency. The reasoning is that when you are observing a stereotyped chirp, the string of loudest frequencies is predictable. In contrast, when you are observing a new instance of a chirp, the frequency that was the loudest during the previous time window is not predictable. The threshold for unpredictability may be customized and is currently set at p=0.01.

Important characteristics about each instance of a chirp are recorded. One of these is the sum of the amplitudes of all the frequencies, as a function of time. This seems to vary in a predictable way during certain types of chirps. It is characterized at only one timepoint at the chirp's onset. An improvement could be made if this characteristic was instead a "local average" of these values. Another recorded characteristic is the loudest frequency observed at the beginning of a chirp. The overall shape of a chirp is recorded in the difference from this initial frequency at each moment in time following the chirp's onset. This difference is normalized by the time difference from the chirp onset (thus, the "cumulative slope" is recorded).

