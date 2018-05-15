# Running 20 Questions

Please see Documentation/gUSBAmp for how to set up the hardware.
Use ActiCap software to monitor impedance.  However, impedences cannot
be monitored concurrently with data recording.

## Opening Arduino Interface

Script is in CCDLUtil.ArduinoInterface. Run it using Arduino IDE

1. Launch BCI2000
2. Select the necessary fields:
    1. Signal Source: Signal Generator (for testing, select gUSBampSource to use real data)
    2. Signal Processing: Dummy Signal Processing, SpectralSignalProcessing or ARSignalProcessing
    3. Application: Brain2Brain
    
3. Parameter File -> SSVEP_FINAL_DRAFT.prm
4. Will get an "Access is Denied message", click the logo next to the open BCI lancher. Software will Launch.
5. Open a web browser and go to localhost:20000
6. Select the question and the SSVEP task will begin.

## Mock Server
1. cd C:\MagStim_PyServer
2. python .\mockServer.py 25000