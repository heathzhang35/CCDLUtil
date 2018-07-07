import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))
import wx
import time
from Utility.Decorators import threaded
from CCDLUtil.Graphics.Subject import SubjectFrame, SubjectPanel


"""
Graphics for cursor control task
"""
class CursorPanel(SubjectPanel):

	box_ratio = 1/6
	cursor_ratio = 1/30
	collision_speed = 10

	def __init__(self, parent, **kwargs):
		"""
		A wxpython cursor task

		:param parent: wx.Frame
		params:
			- display_index: index of display to use (for multi-display systems)
			- cursor_radius: the radius of the cursor
		"""
		super().__init__(parent)
		self.__parent = parent

		self._x, self._y, self._radius = None, None, None

		self._choices = None # array of choices
		self._centered = False
		self._flashing = 0

		point_size = kwargs.get('point_size', 64)
		self.__set_point_size(point_size)

		self.Bind(wx.EVT_PAINT, self._repaint)

	def _update_dimensions(self):
		x, y = self.GetPosition()
		size = self.GetSize()
		w, h = size.GetWidth(), size.GetHeight()
		if not self._centered:
			self._x, self._y, = x + w // 2, y + h // 2
			self._centered = True
		self._radius = int(w * self.cursor_ratio)
		return x, y, w, h

	def __set_point_size(self, point_size):
		font = wx.SystemSettings.GetFont(wx.TELETYPE)
		font.SetPointSize(point_size)
		self.SetFont(font)

	def _repaint(self, event=None):
		x, y, w, h = self._update_dimensions()
		self._radius = int(w * self.cursor_ratio)

		dc = wx.ClientDC(self)
		dc.Clear()

		if self._choices is not None:
			pen = wx.Pen('green')
			dc.SetPen(pen)
			brush = wx.Brush('green')
			dc.SetBrush(brush)

			# draw choice boxes
			box_w = w * self.box_ratio
			dc.DrawRectangle(x, y, box_w, h)
			dc.DrawRectangle(x + w - box_w, y, box_w, h) 

			pen = wx.Pen('black')
			dc.SetPen(pen)

			# draw text
			this_w, this_h = dc.GetTextExtent(self._choices[0])
			mp = (x + box_w // 2, y + h // 2) # midpoint
			this_x = mp[0] - this_w // 2
			this_y = mp[1] - this_h // 2
			dc.DrawText(self._choices[0], this_x, this_y)

			this_w, this_h = dc.GetTextExtent(self._choices[1])
			mp = (x + w - box_w // 2, y + h // 2) # midpoint
			this_x = mp[0] - this_w // 2
			this_y = mp[1] - this_h // 2
			dc.DrawText(self._choices[1], this_x, this_y)

		if self._flashing == 0:
			pen = wx.Pen('white')
			dc.SetPen(pen)
			brush = wx.Brush('white')
			dc.SetBrush(brush)
			# draw cursor
			dc.DrawCircle(self._x, self._y, self._radius)
		elif self._flashing % 2 == 0:
			brush = wx.Brush('red')
			dc.SetBrush(brush)
			# draw cursor
			dc.DrawCircle(self._x, self._y, self._radius)
		if self._flashing > 0:
			self._flashing += 1


	def set_choices(self, choices):
		assert isinstance(choices, type([])) and len(choices) == 2, "must provide array of choices"
		self._choices = choices

	def reset(self):
		size = self.GetSize()
		self._w = size.GetWidth()
		self._x, self._y = self._w // 2, size.GetHeight() // 2

	def move_x(self, delta):
		self._x += delta
		self._repaint()

	def move_y(self, delta):
		self._y += delta
		self._repaint()

	def collide(self, duration=1.5):
		x, y, w, h = self._update_dimensions()
		if self._x < x + w // 2:
			# collide left
			while self._x > x + self._radius * 2:
				self._x -= self.collision_speed
				self._repaint()
		else:
			# collide right
			while self._x < x + w - self._radius * 2:
				self._x += self.collision_speed
				self._repaint()
		self._flashing = 1 # start flashing
		t = time.time()
		while time.time() - t < duration:
			self._repaint()
			time.sleep(0.2)
		self._flashing = 0 # stop flashing
		

	def reached_boundary(self):
		"""
		Returns 0 if cursor boundary has not been reached, -1 if left boundary has
		been reached, and +1 if right boundary has been reached
		"""
		size = self.GetSize()
		w = size.GetWidth()
		left_cursor_edge = self._x - self._radius // 2
		right_cursor_edge = self._x + self._radius // 2
		left_boundary = self._radius
		right_boundary = w - self._radius
		if left_cursor_edge <= left_boundary:
			return -1
		if right_cursor_edge >= right_boundary:
			return 1
		# no boundary reached
		return 0

	def closest_to(self):
		"""
		Returns -1 if cursor is closer to left,
		and +1 if cursor is closer to right
		"""
		mid = self._w // 2
		if self._x <= mid:
			return -1
		if self._x > mid:
			return 1


### TESTING ###
@threaded(True)
def ani(panel):
	for i in range(10):
		time.sleep(2)
		if i % 2 == 0:
			panel.go_left(30)
		else:
			panel.go_right(30)

def set_frame_display(frame, display_index):
	display = wx.Display(display_index)
	x, y, w, h = display.GetGeometry()
	#frame.SetPosition((x, y))
	frame.SetSize(x, y, w, h)
	frame.ShowFullScreen(True, frame.FULLSCREEN_NOSTATUSBAR)

def multi_display_test():
	app = wx.App(False)
	count = wx.Display.GetCount()
	for index in range(count):
		frame = wx.Frame(None, -1, 'Display %d of %d' % (index + 1, count))
		set_frame_display(frame, index)
		frame.Show()
	app.MainLoop()

def cursor_test():
	app = wx.App()
	frame = SubjectFrame(display_index=1)
	panel = CursorPanel(frame)
	frame.Show()
	ani(panel)
	app.MainLoop()

if __name__ == '__main__':
	#multi_display_test()
	cursor_test()
