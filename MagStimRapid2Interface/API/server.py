import web
from . import Magstim.Rapid2Constants
from .Magstim.MagstimInterface import Rapid2
import sys
import argparse
import time
import requests
from threading import Lock, Thread

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

urls = (
    '/', 'index',
    '/TMS/arm', 'tms_arm',
    '/TMS/disarm', 'tms_disarm',
    '/TMS/fire', 'tms_fire',
    '/TMS/power/(\d*)', 'tms_intensity'
)

class index:
    """
    Returns a readme with how to use this API
    """

    def GET(self):
        with open('README.md', 'r') as f:
            return f.read()

class tms_arm:
    """
    Arms the TMS device
    """

    def POST(self):
        web.STIMULATOR_LOCK.acquire()
        web.STIMULATOR.armed = True

        # Wait a bit
        waitTime = (Magstim.Rapid2Constants.output_intesity[web.STIMULATOR.intensity] - 1050) / 1050.0
        waitTime = max(0.5, waitTime)
        time.sleep(waitTime)
        
        # Just in case
        web.STIMULATOR.disable_safety()
        web.STIMULATOR_LOCK.release()
        
        # Return nothing
        web.ctx.status = '204 No Content'

class tms_disarm:
    """
    Disarms the TMS device
    """

    def POST(self):
        web.STIMULATOR_LOCK.acquire()
        web.STIMULATOR.armed = False
        web.STIMULATOR_LOCK.release()
        
        # Return nothing
        web.ctx.status = '204 No Content'

class tms_fire:
    """
    Triggers a TMS pulse
    """

    def POST(self):
        # Joseph this is the first log entry
        log_event("[TMS] Fire command received")
        web.STIMULATOR_LOCK.acquire()
        web.STIMULATOR.trigger()
        web.STIMULATOR_LOCK.release()
        
        # And this is the last 
        log_event("[TMS] Pulse fired")
        
        # Return nothing
        web.ctx.status = '204 No Content'
        
        # Allow Cross-Origin Resource Sharing (CORS)
        # This lets a web browser call this method with no problems
        web.header('Access-Control-Allow-Origin', web.ctx.env.get('HTTP_ORIGIN'))

class tms_intensity:
    """
    Sets the intensity level of the TMS
    """
    
    def POST(self, powerLevel):
        web.STIMULATOR_LOCK.acquire()
        web.STIMULATOR.intensity = int(powerLevel)
        web.STIMULATOR_LOCK.release()
        
        # Return nothing
        web.ctx.status = '204 No Content'

class maintain_communication(Thread):
    def run(self):
        while True:
            web.STIMULATOR_LOCK.acquire()
            web.STIMULATOR.remocon = True
            web.STIMULATOR_LOCK.release()

            time.sleep(0.5)

# Report all errors to the client
web.internalerror = web.debugerror


## Logging code
def log_event(msg):
    """Logs an event on the log file"""
    now = time.time()
    tstruct = time.localtime(now)
    ms = int(round(now % 1, 3)*1000)
    log_string = time.strftime("%Y-%m-%d-%H:%M:%S", tstruct)
    log_string += ".%03d\t%s" % (ms, msg)
    requests.post("http://rogue.cs.washington.edu:20000/log", data=log_string)

def do_main():
    # Take only a port as an argument
    parser = argparse.ArgumentParser(
            description='Opens a server to control the TMS machine on the given port')
    parser.add_argument('port', type=int)
    args = parser.parse_args()

    # Make sure that the server only listens to localhost
    # This is because we cannot allow outside computer to access the TMS
    sys.argv[1] = '127.0.0.1:%d' % args.port

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


if __name__ == '__main__':
    do_main()
