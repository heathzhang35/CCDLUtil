import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))
import wx

"""
Graphics for subject side of experiment
"""
class SubjectFrame(wx.Frame):

	def __init__(self, display_index=0):
		"""
		A wxpython frame for displaying to subjects

		params:
			- display_index: index of display to use (for multi-display systems)
			- cursor_radius: the radius of the cursor
		"""
		style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX | wx.SYSTEM_MENU) & (wx.STAY_ON_TOP)
		wx.Frame.__init__(self, None, style=style)

		self.ShowFullScreen(True)
		
		# choose display
		if display_index < -1 or display_index >= wx.Display.GetCount():
			raise ValueError('invalid display index given')
		display = wx.Display(display_index)
		x, y, w, h = display.GetGeometry()
		self.SetSize(x, y, w, h)
		self._x, self._y, self._w, self._h = x, y, w, h

		self.SetBackgroundColour("gray")
	

class SubjectPanel(wx.Panel):
	def __init__(self, parent):
		super().__init__(parent)

		self.SetBackgroundColour("gray")
		self.Bind(wx.EVT_PAINT, self._repaint)
		self.Fit()

	def _repaint(self, event=None):
		# wx painting function to be overwritten by child classes
		pass
