# This module encapsulates texture loading so we are not dependent on bge.texture

HAVE_BGE_TEXTURE = False
HAVE_PYQT_TEXTURE = False

from .gl_utils import *

try:
	from bge import texture
	import aud
	HAVE_BGE_TEXTURE = True
except ImportError:
	print("Warning: bge cannot be imported")

try:
	from PyQt4 import QtOpenGL, QtGui
	HAVE_PYQT_TEXTURE = True
except ImportError:
	print("Warning: PyQt4 cannot be imported")
	try:
		from PySide import QtOpenGL, QtGui
		HAVE_PYQT_TEXTURE = True
	except ImportError:
		print("Warning: PySide cannot be imported either")


# We are using the Python duck typing to generate a phony blender image that
# store the image buffer and size
class ImageFromBuff:
	def __init__(self, buff, width, height):
		"""Build the image data
		:param buff: Image data
		:param width: Image width
		:param height: Image height
		"""
		self._image = buff
		self._size = [width, height]
		self._valid = True
		
	@property
	def image(self):
		"""image data"""
		return self._image

	@property
	def size(self):
		"""image size"""
		return self._size

	@property
	def valid(self):
		"""bool to tell if an image is available"""
		return self._valid


class Texture:
	def __init__(self, path, interp_mode):
		self._tex_id = glGenTextures(1)
		self.size = [0, 0]
		self._interp_mode = None
		self.path = None

		# Setup some parameters
		self.bind()
		glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
		self.interp_mode = interp_mode

		self.reload(path)

	def __del__(self):
		glDeleteTextures([self._tex_id])

	@property
	def interp_mode(self):
		return self._interp_mode

	@interp_mode.setter
	def interp_mode(self, value):
		if value != self._interp_mode:
			self.bind()
			glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, value)
			glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, value)
			self._interp_mode = value

	def bind(self):
		glBindTexture(GL_TEXTURE_2D, self._tex_id)


class ImageTexture(Texture):

	_cache = {}

	def __init__(self, image, interp_mode, caching):
		self._caching = caching
		super().__init__(image, interp_mode);

	def reload(self, image):
		if image == self.path:
			return

		print(image)

		img = None
		if image in ImageTexture._cache:
			# Image has already been loaded from disk, recall it from the cache
			img = ImageTexture._cache[image]
		else:
			# Load the image data from disk, try to use BGE first
			if HAVE_BGE_TEXTURE:
				img = texture.ImageFFmpeg(image)
				img.scale = False
				# if not img.valid or img.image is None:
				if img.image is None:
					img = None
				elif self._caching:
					ImageTexture._cache[image] = img
			# Try to use PyQt (or PySide) if BGE has failed
			if img is None and HAVE_PYQT_TEXTURE:
				qt_img = QtGui.QImage(image)
				if qt_img.isNull():
					img = None
				else:
					# Qt returns the image with a lot of weird format, so some
					# operations must be applied before
					qt_img = qt_img.convertToFormat(QtGui.QImage.Format_ARGB32)
					qt_img = qt_img.mirrored()
					qt_img = qt_img.rgbSwapped()
					# Now we can extract the image data and create a valid
					# object for BGE
					data = qt_img.constBits()
					size = qt_img.size()
					data.setsize(qt_img.byteCount())
					data = memoryview(data).tobytes()
					channels = len(data) / (size.width() * size.height())
					buff = Buffer(GL_BYTE,
					              [len(data)],
					              data)
					img = ImageFromBuff(buff, size.width(), size.height())
					if self._caching:
						ImageTexture._cache[image] = img

		if img is None:
			print("Unable to load the image", image)
			return

		# Show the image with the appropiated backend
		data = img.image
		if not img.valid or data is None:
			print("Unhandled image exception...", image)
			return

		# Upload the texture data
		self.bind()
		glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.size[0], img.size[1],
		             0, GL_RGBA, GL_UNSIGNED_BYTE, data)

		self.image_size = img.size[:]

		# Save the image name
		self.path = image

		img = None


class VideoTexture(Texture):
	def __init__(self, video, interp_mode, repeat, play_audio):
		self.repeat = repeat
		self.play_audio = play_audio
		self.video = None
		self.audio = None

		super().__init__(video, interp_mode)

	def __del__(self):
		super().__del__()

		if self.audio:
			self.audio.stop()

		self.video = None

	def reload(self, video):
		if video == self.path:
			return

		if USING_BGE_TEXTURE:
			vid = texture.VideoFFmpeg(video)
			vid.repeat = self.repeat
			vid.play()
			self.video = vid
			data = vid.image

			if self.play_audio:
				self.audio = aud.device().play(aud.Factory(video))
		else:
			data = None

		if data == None:
			print("Unable to load the video", video)
			return

		self.bind()
		glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, vid.size[0], vid.size[1],
				0, GL_RGBA, GL_UNSIGNED_BYTE, data)

		self.image_size = vid.size[:]
		self.path = video

	def update(self):
		if not self.video:
			return

		self.video.refresh()
		data = self.video.image
		if data:
			self.bind()
			glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.video.size[0], self.video.size[1],
					0, GL_RGBA, GL_UNSIGNED_BYTE, data)

	def play(self, start, end, use_frames=True, fps=None):
		if not self.video:
			return

		start = float(start)
		end = float(end)

		if use_frames:
			if not fps:
				fps = self.video.framerate
				print("Using fps:", fps)
			start /= fps
			end /= fps

		if start == end:
			end += 0.1
		self.video.stop()
		self.video.range = [start, end]
		self.video.play()
