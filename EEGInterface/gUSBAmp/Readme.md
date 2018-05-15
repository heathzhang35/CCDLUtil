# GUSB AMP Interface

Like the BrainAmp, this requires external software to be running concurrently in order
to allow for data collection.

# How to run the external software

This is labstreaminglayer.


1. Go to C:\Users\eeglab\Desktop\labstreaminglayer\Apps\g.Tec\g.USBamp

2. Open gUSBamp.exe
    1. The sampling rate does not reflect the sampling rate the data
        will be received at.

3. In the window that appears, specify the Device Port
    1. The Device Port is in the format UA-XXXX.XX.XX
        1. Example: UA-2007.02.15
	1. This value should be on the amplifier.  It is the serial number.
	1. If you get an error message, try restarting the computer
	    1.  This could be due to the socket not being closed by a previous process.
	    2. Also, make sure the amplifier in question is on. You can check this by looking at the small LED in the corner of the device

4. Click 'link'.  This opens a socket that is streaming data from the amplifier.

To run the example "ReceiveData.py" file, continue with these instructions:

5. Go to C:\Users\eeglab\Desktop\labstreaminglayer-master\LSL\liblsl-Python\examples

6. Running "ReceiveData.py" will create an incoming stream of packets from the amplifier,
containing the timestamps and a single datapoint in the timeseries.
