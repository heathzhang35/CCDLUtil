import sys
sys.path.insert(0, 'C:\Users\Experimenter\PycharmProjects\MagStimInterface')
from datetime import datetime
import web
from Magstim.MagstimInterface import Rapid2
import time
import requests
from threading import Lock, Thread

# Separate thread that keeps the TMS awake (unneeded if server is running)
class MaintainCommunication(Thread):
    def run(self):
        while True:
            web.STIMULATOR_LOCK.acquire()
            web.STIMULATOR.remocon = True
            web.STIMULATOR_LOCK.release()
            time.sleep(0.5)

#  Arms, fires, and disarms TMS TMS using old MagStim (fires at specified value instead of range)
#  Returns a string of the time that the TMS was fired.
class TMS():
    def __init__(self):
        web.STIMULATOR = Rapid2(port='COM2')
        web.STIMULATOR_LOCK = Lock()

        # The TMS gets sleepy and needs to be woken up every half second
        poller = MaintainCommunication()
        poller.daemon = True
        poller.start()

    def tms_arm(self):
        web.STIMULATOR.disable_safety()
        web.STIMULATOR.armed = True

    def is_armed(self):
        return web.STIMULATOR.armed

    def tms_fire(self, i, sleep_time=1.5):
        """
        We fire at a the passed intensity i
        """
        assert type(i) is int
        assert 0 < i <= 100
        if not self.is_armed():
            self.tms_arm()
            time.sleep(1.5)
        web.STIMULATOR.disable_safety()
        web.STIMULATOR.intensity = i
        time.sleep(sleep_time)
        web.STIMULATOR.trigger()
        return time.time()

    def tms_disarm(self):
        web.STIMULATOR.armed = False

    def set_intensity(self, intensity, pre_sleep_dur=0, prior_sleep_dur=0):
        time.sleep(pre_sleep_dur)
        intensity = int(intensity)
        assert 0 < intensity <= 100
        web.STIMULATOR.intensity = intensity
        time.sleep(prior_sleep_dur)


if __name__ == '__main__':
    fire_twice = False
    tms = TMS()
    tms.tms_arm()
    time.sleep(2)
    tms.tms_fire(1)

    time.sleep(0.5)
    tms.tms_disarm()
