import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))
import wx
import time
from Utility.Decorators import threaded
import textwrap as tw
from Graphics.Subject import SubjectFrame, SubjectPanel

"""
Graphics for prompt task
"""
class PromptPanel(SubjectPanel):

	def __init__(self, parent, **kwargs):
		"""
		A wxpython prompting task

		:param parent: wx.Frame
		params:
			- display_index: index of display to use (for multi-display systems)
		"""
		super().__init__(parent)
		# array of text to display; each element represents a new line
		self.__text = []

		font = wx.SystemSettings.GetFont(wx.TELETYPE)
		point_size = kwargs.get('point_size', 64)
		font.SetPointSize(point_size)
		pixel_size = font.GetPixelSize()
		size = parent.GetSize()
		w = size.GetWidth()
		self.__char_lim = w // pixel_size.GetWidth()
		self.SetFont(font)
		self.__font = font

		self.Bind(wx.EVT_PAINT, self._repaint)
	
	def _repaint(self, event=None):
		dc = wx.ClientDC(self)
		dc.Clear()
		if not self.__text:
			# return if we've got no text to display
			return
		pixel_size = self.__font.GetPixelSize()
		pixel_height = pixel_size.GetHeight()
		x, y = self.GetPosition()
		size = self.GetSize()
		w, h = size.GetWidth(), size.GetHeight()
		midpoint = (x + w // 2, y + h // 2)
		height = pixel_height * len(self.__text) # height of all text
		for i, line in enumerate(self.__text):
			w, h = dc.GetTextExtent(line)
			x = int(midpoint[0] - (w / 2))
			y = int(midpoint[1] - (height / 2) + (i * height / len(self.__text)))
			dc.DrawText(line, x, y)

	def set_text(self, text):
		assert isinstance(text, str), 'must provide string'
		assert '\n' not in text, 'string must not contain new-line characters'
		self.__text = tw.wrap(text, self.__char_lim)
		self._repaint()

	def clear_text(self):
		self.__text = None


### TESTING ###
@threaded(True)
def ani(prompt):
	text = [
		'Is this working or not?',
		'I don\'t know. Here are some more words.',
		'Look good?',
		'Here\'s some more words: peanut allergies are a government conspiracy; tinfoil will not protect you',
		'a bc def ghij k lm nop qrst u vw xyz a bc def ghij k lm nop qrst u vw xyz a bc def ghij k lm nop qrst u vw xyz'
	]
	for t in text:
		time.sleep(2)
		prompt.set_text(t)

def prompt_test():
	app = wx.App()
	frame = SubjectFrame(display_index=1)
	panel = PromptPanel(frame)
	ani(panel)
	frame.Show()
	app.MainLoop()

if __name__ == '__main__':
	prompt_test()
