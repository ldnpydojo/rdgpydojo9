import math
import numpy
import pyaudio
import analyse
import pygame

from pygame import *
import pygame, time, numpy, pygame.sndarray

sample_rate = 44100
pygame.mixer.pre_init(sample_rate, -16, 2) # 44.1kHz, 16-bit signed, stereo
pygame.init()

screen = pygame.display.set_mode((800, 600))
font = pygame.font.SysFont('Arial', 200)

chunk = 768
channels = 1
format = pyaudio.paInt16
rate = 44100


# Initialize PyAudio
p = pyaudio.PyAudio()
stream = p.open(format=format, channels=channels, rate=rate,
                input=True, frames_per_buffer=chunk)

NOTES = [
    'C',
    'C#',
    'D',
    'D#',
    'E',
    'F',
    'F#',
    'G',
    'G#',
    'A',
    'A#',
    'B'
]

channel = pygame.mixer.find_channel()
channel.set_volume(0.5, 0.5)


def play_for(sample_array):
    sound = pygame.sndarray.make_sound(sample_array)
    channel.queue(sound)

    
def sine_array_onecycle(hz, peak):
    length = sample_rate / float(hz)
    omega = numpy.pi * 2 / length
    xvalues = numpy.arange(int(length)) * omega
    return (peak * numpy.sin(xvalues))

    
def sine_array(hz, n_samples = sample_rate):
    peak = 32000.0
    fp = sine_array_onecycle(hz, peak) + peak

    sized = numpy.zeros((n_samples,), numpy.int16)
    sized += numpy.resize(fp, (n_samples,))
    return sized 

 
def play_note(note):
    MIDDLE_C =  math.log(65.4) / math.log(2)

    hz = 2.0 ** (MIDDLE_C + (note - 60.0) / 12.0)

    f = sine_array(hz, sample_rate // 4)
    f = numpy.array(zip(f, f))
    play_for(f)


last = []

while True:
    # Read raw microphone data
    rawsamps = stream.read(chunk)
    # Convert raw data to NumPy array
    samps = numpy.fromstring(rawsamps, dtype=numpy.int16)
    # Show the volume and pitch
    # print analyse.loudness(samps),
    note = analyse.musical_detect_pitch(samps)
    if note:
        n = int(note + 0.5) 

        if [i for i in last if i != n]:
            last = []
        elif len([i for i in last if i == n]) > 3:
            strnote = NOTES[n % 12] + str(n // 12 - 1)
            play_note(n)
            screen.fill((128, 128, 200))
            screen.blit(
                    font.render(strnote, True, (255, 255, 0)),
                (200, 200)
            )
            pygame.display.flip()
            last = []
        else:
            last.append(n)
