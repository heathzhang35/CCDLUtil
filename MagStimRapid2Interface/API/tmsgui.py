#tmsgui.py

import wx
from wx.lib import intctrl
import subprocess

import web
from . import Magstim.Rapid2Constants
from .Magstim.MagstimInterface import Rapid2
import sys
import argparse
import time
import requests
from threading import Lock, Thread, Event

"""
Where the TMS machine is connected to this computer
"""
SERIAL_PORT = 'COM1'

"""
"""
POWER_THRESHOLD = 80;

"""
"""
PERCENT_THRESHOLD = 100;

from mock import patch, MagicMock
from . import server

urls = (
    '/', 'index',
    '/TMS/arm', 'tms_arm',
    '/TMS/disarm', 'tms_disarm',
    '/TMS/fire', 'tms_fire',
    '/TMS/power/(\d*)', 'tms_intensity'
)

DEFAULT_PORT = 25000

class MainWindow(wx.Frame):
	
	def __init__(self, parent, title):
		
		"""
		Set default values
		"""
		self.port = DEFAULT_PORT
		self.intensity = POWER_THRESHOLD
		
		wx.Frame.__init__(self, parent, title = title, size = (500, 500))
		self.CreateStatusBar()
		
		"""
		Create higher-level layout structure, aka display
		"""
		self.panel = wx.Panel(self)
		self.controlLevelSizer = wx.BoxSizer(wx.VERTICAL)
				
		"""
		Create port connection controls, and show them initially
		"""
		self.portSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.connectText = wx.StaticText(self.panel, label = 'Connect to Port:                      ')
		self.portSizer.Add(self.connectText, flag = wx.RIGHT | wx.TOP | wx.LEFT, border = 15)
		
		self.portCtrl = intctrl.IntCtrl(self.panel, value = self.port)
		self.portSizer.Add(self.portCtrl, flag = wx.RIGHT | wx.TOP, border = 10)
		
		self.connectButton = wx.Button(self.panel, -1, 'Connect')
		self.portSizer.Add(self.connectButton, flag = wx.TOP, border = 8)
		self.Bind(wx.EVT_BUTTON, self.ConnectToPort, self.connectButton)
		
		"""
		Create port disconnection controls, and hide them initially
		"""
		self.disconnectText = wx.StaticText(self.panel, label = 'Currently Connected to Port:')
		self.disconnectText.Hide()
		
		self.disconnectButton = wx.Button(self.panel, -1, 'Disconnect')
		self.disconnectButton.Hide()
		self.Bind(wx.EVT_BUTTON, self.DisconnectFromPort, self.disconnectButton)
		
		self.portSizer.Layout()
		
		"""
		Add port connection/disconnection box sizer and separating line to display
		"""
		self.controlLevelSizer.Add(self.portSizer, flag = wx.EXPAND | wx.BOTTOM, border = 10)
		self.line1 = wx.StaticLine(self.panel)
		self.controlLevelSizer.Add(self.line1, flag = wx.EXPAND | wx.BOTTOM, border = 10)
		
		"""
		Create intensity display/controls, add them to the display, and hide them initially
		"""
		self.intensitySizer = wx.BoxSizer(wx.VERTICAL)
		self.intensityDisplaySizer = wx.BoxSizer(wx.HORIZONTAL)
		self.intensityControlSizer = wx.BoxSizer(wx.HORIZONTAL)
		
		self.currentIntensityText = wx.StaticText(self.panel, label = 'Current Intensity Level:')
		self.currentIntensityCtrl = intctrl.IntCtrl(self.panel, value = self.intensity)
		self.currentIntensityCtrl.SetEditable(False)
		self.currentIntensityCtrl.SetBackgroundColour('LIGHT GREY')
		self.setIntensityText = wx.StaticText(self.panel, label = 'Set Intensity Level:')
		self.setIntensityCtrl = intctrl.IntCtrl(self.panel, value = self.intensity)
		self.setIntensityButton = wx.Button(self.panel, -1, 'Set Intensity Level')
		self.Bind(wx.EVT_BUTTON, self.SetIntensity, self.setIntensityButton)
		
		self.intensityDisplaySizer.Add(self.currentIntensityText, flag = wx.RIGHT | wx.TOP | wx.LEFT, border = 15)
		self.intensityDisplaySizer.Add(self.currentIntensityCtrl, flag = wx.RIGHT | wx.TOP, border = 10)
		self.intensityControlSizer.Add(self.setIntensityText, flag = wx.RIGHT | wx.TOP | wx.LEFT, border = 15)
		self.intensityControlSizer.Add(self.setIntensityCtrl, flag = wx.RIGHT | wx.TOP, border = 10)
		self.intensityControlSizer.Add(self.setIntensityButton, flag = wx.TOP, border = 8)
		self.intensitySizer.Add(self.intensityDisplaySizer, flag = wx.EXPAND | wx.BOTTOM, border = 10)
		self.intensitySizer.Add(self.intensityControlSizer, flag = wx.EXPAND | wx.BOTTOM, border = 10)
		
		self.controlLevelSizer.Add(self.intensitySizer, flag = wx.EXPAND|wx.BOTTOM, border = 10)
		self.controlLevelSizer.Show(self.intensitySizer, False)
		
		"""
		Create a separating line between intensity controls and arm/disarm controls and hide it initially
		"""
		self.line2 = wx.StaticLine(self.panel)
		self.controlLevelSizer.Add(self.line2, flag = wx.EXPAND|wx.BOTTOM, border = 10)
		self.controlLevelSizer.Show(self.line2, False)
		
		"""
		Create arm/disarm sizers and buttons, add them to the display, and hide them initially
		"""
		self.armSizer = wx.BoxSizer(wx.VERTICAL)
		self.armButton = wx.Button(self.panel, -1, 'Arm TMS')
		self.Bind(wx.EVT_BUTTON, self.Arm, self.armButton)
		self.disarmButton = wx.Button(self.panel, -1, 'Disarm TMS')
		self.Bind(wx.EVT_BUTTON, self.Disarm, self.disarmButton)
		self.armSizer.Add(self.armButton, flag = wx.TOP, border = 8)
		self.armSizer.Add(self.disarmButton, flag = wx.TOP, border = 8)
		
		self.controlLevelSizer.Add(self.armSizer, flag = wx.EXPAND|wx.BOTTOM, border = 10)
		self.controlLevelSizer.Show(self.armSizer, False)
		
		"""
		Create a separating line between arm/disarm controls and fire controls and hide it initially
		"""
		self.line3 = wx.StaticLine(self.panel)
		self.controlLevelSizer.Add(self.line3, flag = wx.EXPAND|wx.BOTTOM, border = 10)
		self.controlLevelSizer.Show(self.line3, False)
		
		"""
		Create fire sizer and button, and hide it initially
		"""
		self.fireSizer = wx.BoxSizer(wx.VERTICAL)
		self.fireButton = wx.Button(self.panel, -1, 'Fire TMS')
		self.Bind(wx.EVT_BUTTON, self.Fire, self.fireButton)
		self.fireSizer.Add(self.fireButton, flag = wx.TOP | wx.LEFT, border = 180)
		
		self.controlLevelSizer.Add(self.fireSizer, flag = wx.EXPAND|wx.BOTTOM, border = 10)
		self.controlLevelSizer.Show(self.fireSizer, False)
		
		"""
		Wrap up layout instructions
		"""
		self.controlLevelSizer.Layout()
		self.panel.SetSizer(self.controlLevelSizer)
		self.Layout()
		self.Show()
		
		self.serverThread = None
	
	"""
	Hide connection widgets
	Show disconnection widgets.
	Start a new thread to run the server
	"""
	def ConnectToPort(self, e):
		self.port = self.portCtrl.GetValue()
		self.portSizer.Detach(self.connectText)
		self.connectText.Hide()
		self.portSizer.Detach(self.portCtrl)
		self.portCtrl.Hide()
		self.portSizer.Detach(self.connectButton)
		self.connectButton.Hide()
		
		self.portSizer.Add(self.disconnectText, flag = wx.RIGHT | wx.TOP | wx.LEFT, border = 15)
		self.portSizer.Show(self.disconnectText, True)
		self.portSizer.Add(self.portCtrl, flag = wx.RIGHT | wx.TOP, border = 10)
		self.portCtrl.SetEditable(False)
		self.portCtrl.SetBackgroundColour('LIGHT GREY')
		self.portSizer.Show(self.portCtrl, True)
		self.portSizer.Add(self.disconnectButton, flag = wx.TOP, border = 8)
		self.portSizer.Show(self.disconnectButton, True)
		self.portSizer.Layout()
		
		self.controlLevelSizer.Show(self.intensitySizer, True)
		self.intensitySizer.Layout()
		self.controlLevelSizer.Show(self.line2, True)
		self.controlLevelSizer.Show(self.armSizer, True)
		self.disarmButton.Hide()
		self.armSizer.Layout()
		self.controlLevelSizer.Layout()
		
		print('Connecting to port ' + str(self.port))
		self.serverThread = ServerThread(port = self.port)
        	
	"""
	Disconnect from the port by closing the GUI
	"""
	def DisconnectFromPort(self, e):
		print('Disconnecting from port ' + str(self.port))
		sys.exit()
		
	"""
	Set the intensity of the TMS
	"""
	def SetIntensity(self, e):
		self.intensity = self.setIntensityCtrl.GetValue()
		self.currentIntensityCtrl.SetValue(self.intensity)	
		
		web.STIMULATOR_LOCK.acquire()
		web.STIMULATOR.intensity = int(self.intensity)
		web.STIMULATOR_LOCK.release()
	
	"""
	Arm the TMS, hide the arm button, and show the fire button
	"""
	def Arm(self, e):
		self.armButton.Hide()
		self.disarmButton.Show()
		self.armSizer.Layout()
				
		web.STIMULATOR_LOCK.acquire()
		web.STIMULATOR.armed = True

		# Wait a bit
		waitTime = (Magstim.Rapid2Constants.output_intesity[web.STIMULATOR.intensity] - 1050) / 1050.0
		waitTime = max(0.5, waitTime)
		time.sleep(waitTime)
        
		# Just in case
		web.STIMULATOR.disable_safety()
		web.STIMULATOR_LOCK.release()

		self.controlLevelSizer.Show(self.line3, True)
		self.controlLevelSizer.Show(self.fireSizer, True)
		self.controlLevelSizer.Layout()
	
	"""
	Disarm the TMS, hide the disarm button, show the arm button, and hide the fire button
	"""
	def Disarm(self, e):	
		self.disarmButton.Hide()
		self.armButton.Show()
		self.armSizer.Layout()
		
		web.STIMULATOR_LOCK.acquire()
		web.STIMULATOR.armed = False
		web.STIMULATOR_LOCK.release()
		
		self.controlLevelSizer.Show(self.line3, False)
		self.controlLevelSizer.Show(self.fireSizer, False)
		self.controlLevelSizer.Layout()
	
	"""
	Fire the TMS
	"""
	def Fire(self, e):
		#log_event("[TMS] Fire command received")
		web.STIMULATOR_LOCK.acquire()
		web.STIMULATOR.trigger()
		web.STIMULATOR_LOCK.release()

"""
A class that keeps the server running in its own thread,
which can be stopped by disconnecting from the port that
the server is on
"""
class ServerThread(Thread):
	
	def __init__(self, port):
		Thread.__init__(self)
		self.port = port
		#self.abort = Event()
		#self.abort = False
		self.setDaemon(True)
		#self.serverProcess = None
		self.start()
	
	def run(self):
		"""
		Toggle this portion with comments for real/mock server
		"""
		"""
		#MOCK SERVER
		with patch('serial.Serial') as mockedSerialPort:
			serialObj = MagicMock()
			mockedSerialPort.side_effect = lambda: serialObj
	
			# Print out whatever is being written to the serial port
			def show_me(data):
				print data
			serialObj.write.side_effect = show_me
			
			do_main(self.port)
		"""		
		
		#REAL SERVER
		do_main(self.port)
		
		
		"""
		while True:
			#print 'Server Thread Running at port ' + str(self.port)
			time.sleep(0.5)
			print abort
			if self.abort: #.isSet():
				print 'Server Thread Aborting at port ' + str(self.port)
				return
		"""

class maintain_communication(Thread):
    def run(self):
        while True:
            web.STIMULATOR_LOCK.acquire()
            web.STIMULATOR.remocon = True
            web.STIMULATOR_LOCK.release()

            time.sleep(0.5)

# Report all errors to the client
web.internalerror = web.debugerror		
		
def do_main(port):
    """
	# Take only a port as an argument
    parser = argparse.ArgumentParser(
            description='Opens a server to control the TMS machine on the given port')
    parser.add_argument('port', type=int)
    args = parser.parse_args()
	"""

    # Make sure that the server only listens to localhost
    # This is because we cannot allow outside computer to access the TMS
    sys.argv.append('127.0.0.1:%d' % port)

    # Initialize the shared state between web threads
    web.STIMULATOR = Rapid2(port=SERIAL_PORT)
    web.STIMULATOR_LOCK = Lock()
    web.STIMULATOR.remocon = True
    # Start the thread to keep the TMS awake
    poller = maintain_communication()
    poller.daemon = True
    poller.start()

    # Set the power level
    powerLevel = int(POWER_THRESHOLD * PERCENT_THRESHOLD / 100);
    if powerLevel > 100:
        powerLevel = 100
    elif powerLevel < 0:
        powerLevel = 0
    web.STIMULATOR.intensity = powerLevel
    web.STIMULATOR.disable_safety()

    # Start the server
    app = web.application(urls, globals())
    app.run()

if __name__ == "__main__":
    gapp = wx.App(False)
    frame = MainWindow(None, title = "TMS GUI")
    gapp.MainLoop()