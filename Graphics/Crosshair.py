"""
A crosshair, using wxPython
"""
import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))
import wx
import time
from Utility.Decorators import threaded
from Graphics.Subject import SubjectFrame, SubjectPanel


class CHPanel(SubjectPanel):

	size_ratio = 1/15
	thickness = 8

	def __init__(self, parent):
		"""
		A wxpython Crosshair that can flash red.

		:param parent: wx.Frame
		params:
			- crosshair_width: the size of crosshair
			- pen_thickness: the thickness of crosshair
		"""
		super().__init__(parent)
		self._update_dimensions()
		self.pen_color = wx.WHITE
		self.Bind(wx.EVT_PAINT, self._repaint)


	def _update_dimensions(self):
		x, y = self.GetPosition()
		size = self.GetSize()
		w, h = size.GetWidth(), size.GetHeight()
		self._x, self._y = x + w // 2, y + h // 2
		self._size = int(h * self.size_ratio)


	def _repaint(self, event=None):
		"""
		Redraws the crosshair with the current pen color
		"""
		self._update_dimensions()
		dc = wx.PaintDC(self)
		dc.Clear()
		dc.SetPen(wx.Pen(self.pen_color, self.thickness))
		# draw horizontal line
		dc.DrawLine(self._x - self._size // 2, self._y,
					self._x + self._size // 2, self._y)
		# draw vertical line
		dc.DrawLine(self._x, self._y - self._size // 2,
					self._x, self._y + self._size // 2)

		
	def flash_red(self, duration=0.2):
		"""
		Causes the crosshair to flash red for duration seconds.
		:param duration: duration in seconds. defaults to 0.2
		"""
		self.pen_color = wx.RED
		self.Refresh(True)
		t = time.time()
		while time.time() - t < duration:
			time.sleep(0.001)
		self.pen_color = wx.WHITE
		self.Refresh(True)


@threaded(True)
def take_action(ch):
	i = 0
	while True:
		time.sleep(1)
		if i % 1 == 0:
			ch.flash_red(0.2)


def crosshair_test():
	app = wx.App()
	frame = SubjectFrame(display_index=1)
	ch = CHPanel(frame)
	take_action(ch)
	frame.Show()
	app.MainLoop()


if __name__ == '__main__':
	crosshair_test()
