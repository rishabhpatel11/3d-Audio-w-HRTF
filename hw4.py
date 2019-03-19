import matlab
import scipy.io
import numpy as np
import struct
import pyaudio
import wave

# Loading hrir and ITD data from the hrir_final.mat of CIPIC database subject 21
hrir_l=scipy.io.loadmat("hrir_l.mat")
hrir_l=hrir_l['hrir_l']
hrir_r=scipy.io.loadmat("hrir_r.mat")
hrir_r=hrir_r['hrir_r']
ITD=scipy.io.loadmat("ITD.mat")
ITD=ITD['ITD']

# Defining Azimuths and Elevations
# For Azimuths using 0-360 with 15 deg increment
# For elevations using the scale shown in class
azimuths=[]
for a1 in range(25):
    azimuths.append((int)(a1*15))

elevations=[]
for x in range(50):
    elevations.append(x*5.625*-45)


#Opening the audio file
wave=wave.open('mountain.wav')
framesPerS=(int)(wave.getnframes()/wave.getframerate())
fr=wave.getframerate()

p=pyaudio.PyAudio()
chunk=132300
stream = p.open(format=pyaudio.paInt16,channels=wave.getnchannels(),rate=wave.getframerate(),output=True,frames_per_buffer=chunk)
stream.start_stream()
#Default location
aIndex=3
eIndex=25


while 1:
    # Printing Desired Location
    print(aIndex)
    L=[]
    R=[]
    # Creating the filters for the left and right side audio
    for x2 in range(200):
        L.append(hrir_l[aIndex-1][eIndex-1][x2])
        R.append(hrir_r[aIndex-1][eIndex-1][x2])
    left=matlab.squeeze(L)
    right=matlab.squeeze(R)

    #Getting next chunk of frames
    data=wave.readframes(chunk)
    # Checking if enough frames left in file, if not, restart the file
    if(data.__sizeof__()<chunk*2):
        wave.rewind()
        data = wave.readframes(chunk)
    data=struct.unpack("<264600h",data)
    dataT=matlab.transpose(data)

    # Convoluting the audio file with the filters
    wav_left=matlab.convolve(left, dataT)
    wav_right=matlab.convolve(right, dataT)

    # Adding delay for left and right side
    delay=ITD[aIndex-1][eIndex-1]
    delay=(int)(abs(delay))
    if(aIndex<12):
        for x3 in range(delay):
            wav_left=np.append(wav_left,0)
            wav_right=np.insert(wav_right,0,0)
    else:
        for i in range(delay):
            wav_right = np.append(wav_right, 0)
            wav_left = np.insert(wav_left, 0, 0)

    #defining new sound matrix
    y=np.empty([wav_left.size,2])
    for j in range(wav_left.size):
        y[j][0]=(int)(wav_left[j])
        y[j][1]=(int)(wav_right[j])

    #Scaling y and streaming it to audio output
    scaledy = np.int16(y/np.max(np.abs(y)) * 32767)
    stream.write(scaledy,chunk)

    #Next location
    aIndex = aIndex + 1;
    if (aIndex == 25):
        aIndex = 0;
stream.close()
p.terminate()

