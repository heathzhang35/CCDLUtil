import pygame, sys
from pygame.locals import *
import numpy as np
import time
import math
from random import randrange  # for starfield, random number generator
from random import randint
import scipy.signal as sig


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

    for x in range (0,5):
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
def main():
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
    Values = np.random.rand(3, 500)*50
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
                    print(channel)
                if event.key == pygame.K_RIGHT: #right changes channel in the opposite direction in the montage
                    channel += 1
                    if channel == 3:
                        channel = 0
                    print(channel)
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
            dummyindex = dummyindex+.1
            Values = np.concatenate((Values, np.random.rand(3, 500)*50), 1)  # Randomly generated values.
            if len(Values[0, :]) > 25000:
                Values = Values[:, -25000:]



        #needed to exit the program gracefully
        if quittingtime == True:
            break

        DISPLAYSURF.fill((0, 0, 0))     #Clean the slate


        #This portion handles the EEG trace generation
        timeseriesindex = 0             # This is each individual x value in the series.
        numpairs = []                   #this will contain the xy pairs for the EEG positions
        BaselinedValues = Values - np.mean(Values)  #subtracting the mean prevents drift from shifting things too far
        for x in BaselinedValues[channel,0::50]:
            timeseriesindex += 2        # The increment of the x axis. higher number means denser trace
            yposition = x*SizeMultiplier + WINDOWHEIGHT/4
            #This keeps the trace in its window space
            if yposition > WINDOWHEIGHT/2:
                yposition = WINDOWHEIGHT/2
            numpairs.append([10 + timeseriesindex, yposition])      #this is the x,y coordinates being assigned
        pygame.draw.lines(DISPLAYSURF, CYAN, False, numpairs, 1)    #this line connects the dots

        #This is for the Spectral visualizer.
        if len(Values[0, :]) == 25000:                              #25000 is just 5 seconds of data.  it doesn't calculate this beforehand
            freq, density = sig.welch(BaselinedValues[channel, :], fs=5000, nperseg=25000, noverlap=None, scaling='density')
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


        pygame.display.update()
        FPSCLOCK.tick(FPS)# Tells the game system that it is not untouched by the inexorable march of time
        pygame.display.update()

if __name__ == '__main__':
    main()
