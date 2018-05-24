from psychopy import visual, core, event
from random import shuffle, uniform
import pandas as pd
import glob

trialCnt = 0

def increment():
    global trialCnt
    trialCnt += 1

def connectEEG():
    # Either send a sync pulse or activate EEG recording here
    
    # Initialize the clock once connection/recording is established (tic)
    clock = core.Clock()
    return clock

def runBlock(subjID, blockType, numOfTrials, taskData, win, clock):
    # Start (print something and wait for response before starting first trial)
    message.setText('Press any key to begin the next block...')
    win.flip()
    event.waitKeys()

    # Load the stimuli
    if blockType == 'E':
        # Load A
        with open('Stimuli/DMN_blockA.txt') as file:
            stimuliA = [line.strip() for line in file]

        # Load B
        with open('Stimuli/DMN_blockB.txt') as file:
            stimuliB = [line.strip() for line in file]

        # Concatenate
        stimuliFromFile = stimuliA + stimuliB
    else:
        with open('Stimuli/DMN_block' + blockType + '.txt') as file:
            stimuliFromFile = [line.strip() for line in file]
        

    # Shuffle your stimuli and create a list you can index
    stimuli = stimuliFromFile.copy()
    shuffle(stimuli)

    # Have loop that calls runTrial and runISI
    for trial in list(range(0, numOfTrials)):
        runTrial(subjID, stimuli[trial], taskData, blockType, win, clock)
        ISIlength = uniform(4,6) # random value generated here
        runISI(ISIlength, win)

def runTrial(subjID, stimulus, taskData, blockType, win, clock):
    message.setText(stimulus)
    win.flip()

    # Fill in the dataframe
    trialStart = clock.getTime()

    # Wait for user response
    thisResp = None
    while thisResp == None:
        allKeys = event.waitKeys()
        for thisKey in allKeys:
            if thisKey == 'left':
                key = 'true'
                RT = clock.getTime() - trialStart
                thisResp = True
            elif thisKey == 'right':
                key = 'false'
                RT = clock.getTime() - trialStart
                thisResp = True
            elif thisKey in ['q', 'escape']:
                saveData(subjID, taskData, win)
        event.clearEvents()

    taskData['trial_' + str(trialCnt)] = pd.Series([trialStart, stimulus, key, RT, blockType], \
    index=['trialStart','stimulus','key','RT','blockType'])

    increment() # increase trial counter

def runISI(ISIlength, win):
    message.setText('+')
    win.flip()
    core.wait(ISIlength)

def saveData(subjID, taskData, win):
    # Delete the initialization column
    del taskData['initialize']

    # Check how many files are currently present for this subject
    fileNum = len(glob.glob('SaveData/' + subjID + '*')) + 1

    # Save the data to csv file
    file_name = ('SaveData/' + subjID + '_R' + str(fileNum) + '.csv')
    taskData.to_csv(file_name, encoding='utf-8')

    # Close the window
    win.close()
    core.quit()

if __name__ == "__main__":
    # First ensure EEG is connected
    clock = connectEEG()

    # Ask for subjectID
    subjID = input('Enter subject ID: ')

    # Create the window to display
    win = visual.Window(color=[-1,-1,-1], fullscr=True)

    # Initialize message here
    message = visual.TextStim(win, text='Press the left arrow key for True')
    message.setAutoDraw(True)  # automatically draw every frame
    win.flip()
    core.wait(3)
    message.setText('Press the right arrow key for False')
    win.flip()
    core.wait(3)
    message.setText('Press any key to continue...')
    win.flip()
    event.waitKeys()

    # Create pandas dataframe to store behavioural data
    d = {'initialize' : pd.Series([0., 0, 'X', 0., 'X'], \
    index=['trialStart','stimulus','key','RT','blockType'])}
    taskData = pd.DataFrame(d)

    # Loop to shuffle and run blocks
    """
    Block A: Math
    Block B: Self-referential (autobiographical)
    Block C: Self-internal
    Block D: Self-external
    Block E: Mix of A + B
    """
    blockType = ['A','B','C','D','E']
    numOfTrials = 20
    numOfRepeat = 2

    for repeats in list(range(0, numOfRepeat)):
        blockOrder = list(range(0,len(blockType)))
        shuffle(blockOrder)
        for currentBlock in blockOrder:
            runBlock(subjID, blockType[currentBlock], numOfTrials, taskData, win, clock)

    saveData(subjID, taskData, win)