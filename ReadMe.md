[![Build Status](https://travis-ci.com/lpjiang97/CCDLUtil.svg?token=mfNtTeyrZWrKtxdswJLn&branch=master)](https://travis-ci.com/lpjiang97/CCDLUtil) [![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)

# CCDLUtil

## Introduction

This is the forked repo of [CCDLUtil](<https://github.com/UWCCDL/CCDLUtil>). Our development goal is:
* Python 3.5 (or newer) adaption
* New EEG headset API

Collaborator:
* Preston Jiang
* Nile Wilson

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
