# Minimal web server wrapper for Magstim Rapid2 TMS device

## Installation

Requires [setuptools](https://pypi.python.org/pypi/setuptools#installation-instructions)
In the project directory run: 
```
python setup.py install
```

## Instructions

To start the server, run:
```
python server.py 25000
```

This provides three REST-ful functions:
* POST /TMS/arm
* POST /TMS/disarm
* POST /TMS/fire
Note: For safety reasons, the server is only bound to the loopback interface.

For other arguments or options, run:
```
python server.py --help
```

To start a test server, without an attached TMS device, run:
```
python mockServer.py 25000
```

## Differences from upstream repository

* No Bistim support
* Adds a layer for REST-ful control of the TMS device
