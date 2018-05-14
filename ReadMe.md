[![Build Status](https://travis-ci.com/lpjiang97/CCDLUtil.svg?token=mfNtTeyrZWrKtxdswJLn&branch=master)](https://travis-ci.com/lpjiang97/CCDLUtil)

# CCDLUtil

## Introduction

This is the newest version branch of CCDLUtil, set up by [Preston Jiang](<https://homes.cs.washington.edu/~prestonj/>), [Darby Losey](loseydm@uw.edu), and [Nolan Strait](nlstrait@cs.washington.edu). This 
repository contains many useful Python modules for EEG-related experiments and data analysis. Some of the most popular 
functions include:
* Python interface with major EEG hardware devices (BrainAmp, OpenBCI, and Emotiv)
* EEG epoch manipulations
* Graphics (cursor control) for SSVEP experiments
* TCP communication model for creating servers and clients

## Instructions for use

This is intended as a general library.  If using, please clone into your site-packages folder. Example paths are:
* Windows: `C:\Python27\Lib\site_packages`
* OS X: `~/Library/Python/2.7/lib/python/site-packages` (Placing it under `/System` might result in permission issues)
* Linux: `~/.local/lib/python2.7/site-packages` (If you have other setup, you probably know your system well enough to 
figure it out)

## Dependencies
This module is built to work with Python 2.7 (We are working hard to adapt the whole module to be working with Python 3 
without using `__future__`, for the latest update please check out the `python3_updates` branch!). Some modules many not
require all dependencies. 

* numpy	1.8
* scipy	1.0.0	
* matplotlib 2.1.0
* PyYAML 3.12
* pyserial 3.4	
* scikit-learn 0.19.1	
* serial 0.0.21	
* setuptools 28.8.0
* six 1.11.0
* sklearn 0.0

#### Epoched and unepoched EEG Data

As a standard convention used in this library, all epoched data is saved in the form (epoch, sample, channel).
All unepoched data is saved (sample, channel)

#### Log Files

It may be helpful to save events to file in the form: str(trial_dictionary) + \n, with the dictionary containing information relating to a single trial.
Most files have a 1st line that contains meta information.

Because data is saved in this format, each file can be parsed as such:
    
    for line in file:
        trial_dictionary = ast.literal_eval(line)

Where trial_dictionary is a python dictionary with keys such as 'start_time', which contain relevant info pertaining to that trial.
This reduces the need to write scripts to parse individual log files.

## Git
#### How to make git ignore about previously tracked file that are added to .gitignore:


     git rm --cached -r .
     git add .

See this link for reference:
http://stackoverflow.com/questions/1274057/how-to-make-git-forget-about-a-file-that-was-tracked-but-is-now-in-gitignore

###### Pull from remote, but ignoring (and overwriting!) local changes:

    git fetch origin master
    git reset —hard FETCH_head
    git clean -df
    

## CCDL General Documentation

See the Documentation module for additional documentation.

### Open BCI

##### Equipment Instructions
The dongle and board also have different settings.  For standard data collection, insure that the
switches on the side are set properly:

    Dongle: Switch toward computer
    Board: Switch toward PC.

##### Known Errors
The OpenBCI board will not run properly the second time it starts unless
it is physically reset between runs.  Therefore, every time the program is run you must:


        1. Unplug the dongle and turn off the board
        2. Plug in the dongle
        3. Turn on the board.

See the "Error Messages" section below to see markers of this error.

#### Problems with the touch screen

    Occasionally on restart, the touchscreen mapping will be wrong.
    To fix:
        1) Search and select "Tablet PC Settings"
        2) At the top, hit configure your pent and touch displays setup
        3) Select the correct touchscreen


## Common Error Messages / Troubleshooting
[C:\Python27\Lib\site-packages\CCDLUtil\DataManagement](C:%5CPython27%5CLib%5Csite-packages%5CCCDLUtil%5CDataManagement)
* Problems Importing
This should be resolved, but if there is a problem with some of the scripts in this module failing to import,
change the scripts to import from CCDLUtil.Module.Script.  As all of the CCDLUtil repo was in the working path when first developed,
there may be some remaining import Module.Script commands, which will fail if imported from another working
path.  As said before, this should be fixed already, but if I missed it in a few spots, please let me know

Other importing problems - This module was originally named DLUtil. Because of this, it is possible
that when cloning the module, it will clone into a folder called DLUtil. This needs to be CCDLUtil 
in order to work.



* This error means that you are accessing a wxpython object in an unsafe manner. Make sure to use locks, even if you are running everything in the same thread.
wxpython does some threading automatically and they did not make their code thread safe.


            1. Pango:ERROR:/build/pango1.0-_EsyGA/pango1.0-1.40.1/./pango/pango-layout.c:3925:pango_layout_check_lines: assertion failed: (!layout->log_attrs)


* This error likely comes from specifying the directory and not the specific file for loading a TF object.
This provides a very long, complicated error message.  The portion shown below is the last segment.


            2. DataLossError (see above for traceback): Unable to open table file
            /data/Subject3/Subject3_TF: Failed precondition: Subject3/Subject3_TF: perhaps your file is in a
            different file format and you need to use a different restore operator?
             [[Node: save/restore_slice = RestoreSlice[dt=DT_FLOAT, preferred_shard=-1,
             _device="/job:localhost/replica:0/task:0/cpu:0"](_recv_save/Const_0, save/restore_slice/tensor_name, save/restore_slice/shape_and_slice)]]

* This error likely comes about from not stripping off a trailing comma in some versions of data collected from the brain amp system.
    ** The new method takes care of this.

        3.File "/DataInterface/Utility/FileParser.py", line 118, in iter_func
        yield dtype(item)
        ValueError: could not convert string to float:


* OpenBCI Disconnect


        WARNING:root:Skipped 46 bytes before start found
        Warning: Skipped 46 bytes before start found
        WARNING:root:ID:<15> <Unexpected END_BYTE found <0> instead of <192>
        Warning: ID:<15> <Unexpected END_BYTE found <0> instead of <192>
        WARNING:root:Skipped 466 bytes before start found
        'NoneType' object has no attribute 'channel_data' 'NoneType' object has no attribute 'channel_data'

* OpenBCI - Communication Problems

    WARNING:root:No Message

    This means there is a communication problem between the dongle and
    the board. Make sure both are on and that the dongle actually belongs
    to the board (ie, they didn't get mixed up)

    This could also mean that the COM port was entered incorrectly and my
    script autodetect the wrong one (not sure why this happens sometimes,
    please do fix it if you figure out why).


* BrainAmp Disconnect/Software not on
    
    Ensure that the proprietary BrainAmp software is running and the BrainAmp system is fully conenected (see Documentation folder for more details)
    Otherwise, this is the common error message:
    

        No connection could be made because the target machine actively refused it

* Multiprocessing Error

    The picking error means you are attempting to access an object from a different process.  Don't do that.

    This also means you can't use lambda functions when creating a new process.  Use the below format instead.  Note the additional comma, else you'll get an error stating that it is not a tuple (and thus not iterable).


        crosshair_mp_queue = multiprocessing.Queue()
        multiprocessing.Process(target=run_pygame, args=(crosshair_mp_queue,)).start()

    The error message:

        pickle.PicklingError: Can't pickle <function <lambda> at
                0x0DA209B0>: it's not found as __main__.<lambda>
