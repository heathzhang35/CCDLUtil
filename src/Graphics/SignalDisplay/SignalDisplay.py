import pygame, sys
from pygame.locals import *
import numpy as np
import time
import math
from random import randrange  # for starfield, random number generator
from random import randint
import scipy.signal as sig
import CCDLUtil.DataManagement.DataParser as CCDLDataParser
import Queue


# For debugging NFT; is updated live by visualizer.py.
DISCONNECT = False
LastDISCONNECT = False  # so current and previous states can be compared

# Number of frames per second
# Change this value to speed up or slow down your game
FPS = 50

pygame.display.init()
disp = pygame.display.Info()
WINDOWWIDTH = 1020 # I like the screen slightly smaller than window size for ease of portability
WINDOWHEIGHT = disp.current_h*2/3
size = [WINDOWWIDTH, WINDOWHEIGHT]

# The number of pixels in pygame line functions, by default
LINETHICKNESS = 10

# Set up the colours (RGB values)
BLACK = (0, 0, 0)
GREY = (120, 120, 120)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
ORANGE = (255, 128, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 127, 255)
VIOLET = (127, 0, 255)

stage = 0




def FeatureDisplay(DISPLAYSURF, channel): #Delineates the sections and labels them

    for x in range(0,5):
        pygame.draw.line(DISPLAYSURF, BLUE, (x*(WINDOWWIDTH-20)/5, WINDOWHEIGHT / 2), (x*(WINDOWWIDTH-20)/5, 0), 1)
    resultsurf = SCOREFONT.render('EEG Trace: Channel ' + str(channel), True, WHITE)
    result_rect = resultsurf.get_rect()
    result_rect.center = (WINDOWWIDTH / 2, 25)
    DISPLAYSURF.blit(resultsurf, result_rect)
    pygame.draw.rect(DISPLAYSURF, WHITE, ((0, 0), (WINDOWWIDTH, WINDOWHEIGHT)), LINETHICKNESS * 2)
    pygame.draw.line(DISPLAYSURF, WHITE, (0, WINDOWHEIGHT / 2), (WINDOWWIDTH, WINDOWHEIGHT / 2), (LINETHICKNESS))


    for x in range (1,9):
        resultsurf = BASICFONT.render(str(x*5), True, WHITE)
        result_rect = resultsurf.get_rect()
        result_rect.center = (x*(WINDOWWIDTH-20)/8, WINDOWHEIGHT-30)
        pygame.draw.line(DISPLAYSURF, WHITE, (x*(WINDOWWIDTH-20)/8, WINDOWHEIGHT), (x*(WINDOWWIDTH-20)/8, WINDOWHEIGHT-20), 2)
        DISPLAYSURF.blit(resultsurf, result_rect)
    resultsurf = SCOREFONT.render('Spectrum: Channel ' + str(channel), True, WHITE)
    result_rect = resultsurf.get_rect()
    result_rect.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2 + 25)
    DISPLAYSURF.blit(resultsurf, result_rect)


# Main function
def main(data_queue, fs, nperseg=None, noverlap=None):
    """

    :param data_queue: queue to read data from
    :param fs: sampling rate
    :param nperseg: If none, defaults to fs / 2
    :param noverlap: If none, defaults to int(fs * 0.75)
    :return:
    """
    nperseg = int(fs / 2)
    noverlap = int(fs * 0.4)

    pygame.init()
    ##Font information
    global BASICFONT, BASICFONTSIZE
    global SCOREFONTSIZE, SCOREFONT
    global stage
    global StartTime
    global Keypress
    global COLORTOGGLE


    # Initializing the font values
    BASICFONTSIZE = 10
    SCOREFONTSIZE = 20
    BASICFONT = pygame.font.Font('freesansbold.ttf', BASICFONTSIZE)
    SCOREFONT = pygame.font.Font('freesansbold.ttf', SCOREFONTSIZE)



    # A flag that smooths exiting from script
    quittingtime = False

    # Initialize the pygame FPS clock
    FPSCLOCK = pygame.time.Clock()

    # Set the size of the screen and label it
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Trace')

    # make mouse cursor visible
    pygame.mouse.set_visible(1)

    #Used for Dummy Data
    dummyindex = time.time() + .1

    values = None

    channel = 0
    SizeMultiplier = 1
    SpecMultiplier = 1

    # Let the games (loop) begin!
    while True:
        # Processes game events like quitting or keypresses
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                quittingtime = True
                break
            # This portion does keypresses
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:  #hitting left changes the EEG channel
                    channel -= 1
                    if channel == -1:
                        channel = 2
                    print channel
                if event.key == pygame.K_RIGHT: #right changes channel in the opposite direction in the montage
                    channel += 1
                    if channel == 3:
                        channel = 0
                    print channel
                if event.key == pygame.K_UP:    #This magnifies the trace
                    SizeMultiplier *= 1.5
                if event.key == pygame.K_DOWN:  #this reduces the trace
                    SizeMultiplier *= 0.75
                    if SizeMultiplier <= 0:
                        SizeMultiplier = 0.1
                if event.key == pygame.K_KP_PLUS:   #This increases the scaling on the spectra map
                    SpecMultiplier *= 1.5
                if event.key == pygame.K_KP_MINUS:  #This reduces the spectra scaling
                    SpecMultiplier *= 0.75

        if time.time() > dummyindex:
            dummyindex += .1
            new_values = get_data_packet(data_queue=data_queue)
            if new_values is not None:
                if len(new_values.shape) == 1:
                    new_values = np.expand_dims(new_values, axis=1)
                values = CCDLDataParser.stack_epochs(existing=values, new_trial=new_values, axis=1)  # Randomly generated values.
                if len(values[0, :]) > fs * 5:
                    values = values[:, -fs * 5:]

        if quittingtime:
            break

        DISPLAYSURF.fill((0, 0, 0))     # Clean the slate


        #This portion handles the EEG trace generation
        timeseriesindex = 0             # This is each individual x value in the series.
        numpairs = []                   #this will contain the xy pairs for the EEG positions

        if values is not None:
            BaselinedValues = values[channel,:] - np.mean(values[channel,:])  #subtracting the mean prevents drift from shifting things too far
            # print "Values", values

            # print "NP mean", np.mean(values)
            # print 'baselinevalues', BaselinedValues
            for x in BaselinedValues[0::fs / 100.0]:
                timeseriesindex += 2        # The increment of the x axis. higher number means denser trace
                yposition = x*SizeMultiplier + WINDOWHEIGHT/4
                #This keeps the trace in its window space
                if yposition > WINDOWHEIGHT/2:
                    yposition = WINDOWHEIGHT/2
                numpairs.append([10 + timeseriesindex, yposition])      #this is the x,y coordinates being assigned
            if len(numpairs) > 6:
                pygame.draw.lines(DISPLAYSURF, CYAN, False, numpairs, 1)    #this line connects the dots\

            #This is for the Spectral visualizer.
            if len(values[0, :]) == fs * 5:                              #25000 is just 5 seconds of data.  it doesn't calculate this beforehand.

                #print BaselinedValues[channel, :].shape
                print BaselinedValues.shape
                freq, density = sig.welch(BaselinedValues, fs=fs, nperseg=512, noverlap=200, scaling='density')
                #print 'Density.shape', density.shape

                timeseriesindex = 0
                numpairs = []
                for x in freq[0:205:5]:
                    height = (WINDOWHEIGHT - 10 - density[int(x)]*500*SpecMultiplier) #500 is an arbitrary value I used to make it visible
                    if height < WINDOWHEIGHT/2 + 10:
                        height = WINDOWHEIGHT/2 + 10
                    numpairs.append([10 + timeseriesindex*WINDOWWIDTH/40, height])
                    timeseriesindex += 1
                pygame.draw.lines(DISPLAYSURF, GREEN, False, numpairs, 2)

        # Draw outline of arena, comes last so it overlaps all
        FeatureDisplay(DISPLAYSURF, channel)


        FPSCLOCK.tick(FPS)
        pygame.display.update()


def get_data_packet(data_queue):
    ''' Gets the data packet. returns data packet in shape (channel, sample) '''
    try:
        data_packet = data_queue.get(False)  # taken in as shape (sample, channel)
        return np.swapaxes(data_packet, axis1=0, axis2=1)
    except Queue.Empty:
        pass


