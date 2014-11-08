from .gl_utils import *
from . import fonts as blf
from .widget import Widget, BGUI_DEFAULT, BGUI_NO_NORMALIZE
from math import *


class Label(Widget):
	"""Widget for displaying text"""
	theme_section = 'Label'
	theme_options = {
				'Font': '',
				'Color': (1, 1, 1, 1),
				'OutlineColor': (0, 0, 0, 1),
				'OutlineSize': 0,
				'OutlineSmoothing': False,
				'Size': 30,
				}

	def __init__(self, parent, name=None, text="", font=None, pt_size=None, color=None,
				outline_color=None, outline_size=None, outline_smoothing=None, pos=[0, 0], sub_theme='', options=BGUI_DEFAULT):
		"""
		:param parent: the widget's parent
		:param name: the name of the widget
		:param text: the text to display (this can be changed later via the text property)
		:param font: the font to use
		:param pt_size: the point size of the text to draw (defaults to 30 if None)
		:param color: the color to use when rendering the font
		:param pos: a tuple containing the x and y position
		:param sub_theme: name of a sub_theme defined in the theme file (similar to CSS classes)
		:param options: various other options

		"""
		Widget.__init__(self, parent, name, None, [0, 0], pos, sub_theme, options)

		if font:
			self.fontid = blf.load(font)
		else:
			font = self.theme['Font']
			self.fontid = blf.load(font) if font else 0
		blf.enable(self.fontid, blf.ROTATION)

		if pt_size:
			self.pt_size = pt_size
		else:
			self.pt_size = self.theme['Size']

		if color:
			self.color = color
		else:
			self.color = self.theme['Color']

		if outline_color:
			self.outline_color = outline_color
		else:
			self.outline_color = self.theme['OutlineColor']

		if outline_size is not None:
			self.outline_size = outline_size
		else:
			self.outline_size = self.theme['OutlineSize']
		self.outline_size = int(self.outline_size)

		if outline_smoothing is not None:
			self.outline_smoothing = outline_smoothing
		else:
			self.outline_smoothing = self.theme['OutlineSmoothing']

		self.text = text

	@property
	def text(self):
		"""The text to display"""
		return self._text

	@text.setter
	def text(self, value):
		blf.size(self.fontid, self.pt_size, 72)
		size = [blf.dimensions(self.fontid, value)[0], blf.dimensions(self.fontid, 'Mj')[0]]

		if not (self.options & BGUI_NO_NORMALIZE):
			size[0] /= self.parent.size[0]
			size[1] /= self.parent.size[1]

		self._update_position(size, self._base_pos)

		self._text = value

	@property
	def pt_size(self):
		"""The point size of the label's font"""
		return self._pt_size

	@pt_size.setter
	def pt_size(self, value):
		# Normalize the pt size (1000px height = 1)
		if self.system.normalize_text:
			self._pt_size = int(value * (self.system.size[1] / 1000))
		else:
			self._pt_size = value

	def _draw_text(self, x, y, rot=0.0):
		for i, txt in enumerate([i for i in self._text.split('\n')]):
			blf.position(self.fontid, x, y - (self.size[1] * i), 0)
			blf.rotation(self.fontid, rot)
			blf.draw(self.fontid, txt.replace('\t', '    '))

	def _draw(self):
		"""Display the text"""

		blf.size(self.fontid, self.pt_size, 72)

		if self.outline_size:
			glColor4f(*self.outline_color)
			if self.outline_smoothing:
				steps = range(-self.outline_size, self.outline_size + 1)
			else:
				steps = (-self.outline_size, 0, self.outline_size)

			for x in steps:
				for y in steps:
					# Compute all the rotations
					widget = self._parent
					point  = [self.position[0] + x, self.position[1] + y]
					rot    = 0.0
					while True:
						center = [widget.position[0] + 0.5*widget.size[0],
						          widget.position[1] + 0.5*widget.size[1]]
						angle  = widget.rotation
						rot    = rot + angle
						point  = self._rotatePoint(point, center, angle)
						if widget == self._parent:
							break
						widget = self._parent
					self._draw_text(point[0], point[1], rot)

		glColor4f(*self.color)
		# Compute all the rotations
		widget = self
		point  = self.position
		rot    = 0.0
		while True:
			center = [widget.position[0] + 0.5*widget.size[0],
			          widget.position[1] + 0.5*widget.size[1]]
			angle  = widget.rotation
			rot    = rot + angle
			point  = self._rotatePoint(point, center, angle)
			if widget == widget.parent:
				break
			widget = widget._parent
		self._draw_text(point[0], point[1], rot)

		Widget._draw(self)

