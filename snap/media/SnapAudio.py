
import os,sys
import json
import numpy

THISDIR = os.path.realpath(os.path.dirname(__file__))
CONFIG_FILE = os.path.join(THISDIR, os.path.basename(__file__).replace('.py', '.json'))

def build(ENV):

	# using qt5 multimedia backend for now...  the key is to design the interface well!  we'll swap the backend out later!

	# user api:
	# audio module just provides a list of devices that can be queried, and we open streams from the device... easy as one would expect.

	SnapNode = ENV.SnapNode

	Qt5 = ENV.extern.Qt5
	QAudioDeviceInfo = Qt5.QAudioDeviceInfo
	QAudio = Qt5.QAudio
	QAudioFormat = Qt5.QAudioFormat
	QIODevice = Qt5.QIODevice
	QAudioOutput = Qt5.QAudioOutput
	QAudioInput = Qt5.QAudioInput

	#if not numpy_array.flags['C_CONTIGUOUS']:
	#	numpy_array = np.ascontiguousarray(numpy_array)
	# qbyte_array = QByteArray.fromRawData(numpy_array.data)
	# buffer = QBuffer(qbyte_array)

	QENDIAN = {
		'little':QAudioFormat.Endian.LittleEndian,
		'big':QAudioFormat.Endian.BigEndian,
		QAudioFormat.Endian.LittleEndian:'little',
		QAudioFormat.Endian.BigEndian:'big',
		}

	SYS_ENDIAN = sys.byteorder

	QTYPES = {
		QAudioFormat.SampleType.SignedInt:'int',
		QAudioFormat.SampleType.UnSignedInt:'uint',
		QAudioFormat.SampleType.Float:'float',
		'int':QAudioFormat.SampleType.SignedInt,
		'uint':QAudioFormat.SampleType.UnSignedInt,
		'float':QAudioFormat.SampleType.Float,
	}

	def set_to_qformat(QFORMAT, ATTR, VALUE):
		if ATTR == 'channels':
			QFORMAT.setChannelCount(VALUE)
		elif ATTR == 'rate':
			QFORMAT.setSampleRate(VALUE)
		elif ATTR == 'format':
			start = ''.join([c for c in VALUE if not c.isdigit()]).lower()
			QFORMAT.setSampleType( QTYPES[start] )
			QFORMAT.setSampleSize( int(VALUE[len(start):]) )
		elif ATTR == 'codec':
			QFORMAT.setCodec(VALUE)
		elif ATTR == 'byte_order':
			QFORMAT.setByteOrder(QENDIAN[VALUE])
		else:
			raise AttributeError(ATTR)

	def get_from_qformat(QFORMAT, ATTR):
		if ATTR == 'channels':
			return int(QFORMAT.channelCount())
		elif ATTR == 'rate':
			return int(QFORMAT.sampleRate())
		elif ATTR == 'format':
			return QTYPES[QFORMAT.sampleType()] + str(QFORMAT.sampleSize())
		elif ATTR == 'codec':
			return str(QFORMAT.codec())
		elif ATTR == 'byte_order':
			return QENDIAN[QFORMAT.byteOrder()]
		else:
			raise AttributeError(ATTR)

	def spec_to_qformat(QFORMAT, **SPEC):
		if QFORMAT is None:
			QFORMAT = QAudioFormat()
		set_to_qformat(QFORMAT, 'channels', SPEC.get('channels',2))
		set_to_qformat(QFORMAT, 'rate', SPEC.get('rate', 48000))
		set_to_qformat(QFORMAT, 'format', SPEC.get('format', 'float32'))

		set_to_qformat(QFORMAT, 'byte_order', SPEC.get('byte_order', SYS_ENDIAN))
		set_to_qformat(QFORMAT, 'codec', SPEC.get('codec', 'audio/pcm'))
		return QFORMAT

	def qformat_to_spec(QFORMAT):		
		return {
			'channels':get_from_qformat(QFORMAT, 'channels'),
			'rate':get_from_qformat(QFORMAT, 'rate'),
			'format':get_from_qformat(QFORMAT, 'format'),

			'endian':get_from_qformat(QFORMAT, 'byte_order'),
			'codec':get_from_qformat(QFORMAT, 'codec'),
		}

	class FakeQIODevice(QIODevice):
		# this is just a bridge between the Q stream and our stream, user won't touch it (might be a better way?)

		__slots__ = ['__SnapAudioStream__']

		def readData(self, SIZE):
			# this is output; returned bytes are played by output device
			# NOTE: returning None is ok; blank playback
			return self.__SnapAudioStream__._outgoing_bytes_callback(SIZE)

		def writeData(self, BYTES, SIZE):
			# this is input; bytes should be recorded, or passed to an output device
			# NOTE: returning 0 is ok; no bytes written, but default should take all the bytes
			if SIZE != len(BYTES):
				ENV.snap_warning('bytes != size?', len(BYTES), SIZE)
			return self.__SnapAudioStream__._incoming_bytes_callback(BYTES)

		def __init__(self, STREAM):
			QIODevice.__init__(self)
			self.open(QIODevice.ReadWrite)

			self.__SnapAudioStream__ = STREAM


	class SnapAudioStream(SnapNode):

		__slots__ = []

		@ENV.SnapProperty
		class uptime:
			set = None
			def get(self, MSG):
				"()->float"
				stream = self.__snap_data__['__stream__']
				if stream is not None:
					return stream.elapsedUSecs() / 1000000. # seconds
				return 0.

		@ENV.SnapProperty
		class running:

			def get(self, MSG):
				"()->bool"
				stream = self.__snap_data__['__stream__']
				try:
					if stream is not None and stream.state() == QAudio.ActiveState:
						return True
				except:
					pass
				return False

			def set(self, MSG):
				"(bool!)"
				state = MSG.args[0]
				if state:
					self.start()
				else:
					self.stop()

		@ENV.SnapProperty
		class finished:
			set = None
			def get(self, MSG):
				"()-bool"
				return not self['running']

		@ENV.SnapProperty
		class buffer_size:
			set = None
			def get(self, MSG):
				"()->int"
				buf = self.__snap_data__['__buffer__']
				if buf is not None:
					return len(buf)
				return 0

		# ready?

		# TODO do a format as a group?  rate, channel count, width / type

		# int sample_rate (hz) -> 44100
		# int bit_width (bit count/width of channel sample)
		#	sample_width, sample_format?  -- just sample format?  -> int8, int16, float32, ...?

		@ENV.SnapProperty
		class format:
			# this is just sampleSize() and sampleType() together in a tuple...
			# "int8", "int16", "uint8", "uint16", "float32", ...
			set = None
			def get(self, MSG):
				"()->str"
				qfmt = self.__snap_data__['__QAudioFormat__']
				if qfmt is None:
					return None
				return get_from_qformat(qfmt, 'format')

		@ENV.SnapProperty
		class rate:
			# usually 44100 or 48000 Hz (samples per second -- per-channel)
			set = None
			def get(self, MSG):
				"()->int"
				qfmt = self.__snap_data__['__QAudioFormat__']
				if qfmt is None:
					return None
				return get_from_qformat(qfmt, 'rate')

		@ENV.SnapProperty
		class channels:
			set = None
			def get(self, MSG):
				"()->int"
				qfmt = self.__snap_data__['__QAudioFormat__']
				if qfmt is None:
					return None
				return get_from_qformat(qfmt, 'channels')


		# TODO codec?  portaudio does this with format description -- maybe just stick to format?
		# this is really just always "audio/pcm" -- ffmpeg will handle other codec stuff, playback is 'unencoded' (and if some other implementation is required that should be hidden from the end-user anyway -- we just want high-quality output, best option...)


		# QAudioFormat.bytesForDuration(int microseconds) # microseconds, based on samplerate
		# QAudioFormat.bytesForFrames(int count)
		# QAudioFormat.bytesPerFrame() # size of one sample * nchannels
		# QAudioFormat.channelCount()
		# QAudioFormat.codec()
		# QAudioFormat.durationForBytes(byteCount)
		# QAudioFormat.durationForFrames(frameCount)
		# QAudioFormat.framesForBytes(byteCount)
		# QAudioFormat.framesForDuration(duration)
		# QAudioFormat.isValid()


		# TODO make a set() to configure in one go?  then we can validate, and stream starts on start()

		# TODO query / audio format info

		# start / stop / kill?

		def closest_format(self, **SETTINGS):
			fmt = spec_to_qformat(None, **SETTINGS)
			# TODO closestFormat()
			raise NotImplementedError()

		def set(self, **SETTINGS):

			was_running = self['running']
			if was_running:
				self.stop()

			# these have already been set to defaults in __init__
			#sample_type = self['sample_type']
			#sample_size = self['sample_size']

			current = {
				'channels':self['channels'],
				'rate':self['rate'],
				'format':self['format'],
				# byte_order and codec?
			}
			current.update(SETTINGS)

			self.__snap_data__['__QAudioFormat__'] = spec_to_qformat(None, **current)

			if was_running:
				self.start()

		@ENV.SnapChannel
		def stop(self, MSG):
			"()"

			if not self['running']:
				return

			data = self.__snap_data__['__stream__']
			
			data['__stream__'].stop()
			data['__stream__'] = None
			data['__FakeQIODevice__'] = None

			self.stop.emit()

		# TODO pause, resume

		@ENV.SnapChannel
		def start(self, MSG):
			"()"
			# TODO support changing settings and callback?

			self.stop()

			data = self.__snap_data__

			fmt = data['__QAudioFormat__']
			assert fmt and fmt.isValid(), 'invalid format; cannot start audio stream'

			mode = data['__mode__']
			device = data['__device__']
			assert device is not None, 'no device for {} playback'.format(mode)
			qinfo = device.__snap_data__['__' + mode + '__']['QInfo']
			assert qinfo and qinfo.isFormatSupported(fmt), 'unsupported format for device: {}'.format(device)
			
			if mode == 'output':
				data['__stream__'] = QAudioOutput(qinfo, fmt)
			elif mode == 'input':
				data['__stream__'] = QAudioInput(qinfo, fmt)
			else:
				raise TypeError(mode)

			fake_dev = data['__FakeQIODevice__'] = FakeQIODevice(self)
			data['__stream__'].start(fake_dev)

			data['__buffer__'] = b''

			ENV.snap_out('start stream', qformat_to_spec(fmt))

			self.start.emit()

			

		def close(self):
			self.stop()






		def _outgoing_bytes_callback(self, SIZE):

			callback = self.__snap_data__['callback']
			if callback is not None:
				_return = callback(SIZE)
				if _return is not None and not isinstance(_return, bytes):
					if isinstance(_return, numpy.ndarray):
						_return = _return.tobytes()
					# TODO ?
					else:
						raise TypeError('unsupported read value:', type(_return))

				return _return
			else:
				# TODO send hungry event: self.ready.send()?
				return self.read_bytes(SIZE)

			return None


		def _incoming_bytes_callback(self, BYTES):
			# if size is < 1 or None, then just read as much as is available...

			callback = self.__snap_data__['callback']
			if callback is not None:
				_return = callback(BYTES)
				assert isinstance(_return, int), 'wrong return type; must be int of bytes written'
				# TODO on error stop the stream ourself?
				# TODO if the return value is larger than the len(BYTES) then only return len(BYTES) and buffer the rest?  and pull in previous bytes first?
				return _return

			else:
				return self.write_bytes(BYTES)

			return len(BYTES) if BYTES else 0

		def read_bytes(self, SIZE):
			data = self.__snap_data__
			buf = data['__buffer__']
			_return = buf[:SIZE]
			data['__buffer__'] = buf[SIZE:]
			return _return

		def write_bytes(self, BYTES):
			if BYTES is not None:
				data = self.__snap_data__
				data['__buffer__'] = data['__buffer__'] + BYTES
				return len(BYTES)
			return 0



		def __init__(self, DEVICE, MODE, callback=None, **SETTINGS):
			SnapNode.__init__(self)

			data = self.__snap_data__

			assert MODE in ('input','output'), 'invalid mode: {}'.format(str(MODE))
			data['__mode__'] = MODE
			assert isinstance(DEVICE, ENV.SnapAudioDevice), 'stream must have reference to SnapAudioDevice instance, not: {}'.format(type(DEVICE))
			data['__device__'] = DEVICE
			data['__stream__'] = None # the QAudioOutput|QAudioInput on start()

			try:
				qinfo = DEVICE.__snap_data__['__' + MODE + '__']['QInfo']
			except:
				raise TypeError('device has no', repr(MODE))
			fmt = data['__QAudioFormat__'] = qinfo.preferredFormat()

			data['callback'] = callback
			data['__buffer__'] = None

			# sensible defaults: # TODO also take in the device, and then we can verify the device supports the format
			#fmt.setSampleRate(44100)
			#fmt.setChannelCount(2)

			#fmt.setSampleSize(16)
			#fmt.setSampleType(QAudioFormat.SampleType.SignedInt)

			# these are not in user domain:
			#fmt.setCodec("audio/pcm") # just always best raw output available, this shouldn't need to be exposed to user...
				# -- if device format doesn't fit user format we should use ffmpeg to just convert it to device format automatically (best quality; upscale)
			#fmt.setByteOrder(SYS_ENDIANESS) # TODO just assume user is always using system endianess, and if device does not support system endianess, then do the conversion internally -- TODO

			if SETTINGS:
				self.set(**SETTINGS)

		def __del__(self):
			self.close()


	ENV.SnapAudioStream = SnapAudioStream

	class SnapAudioOutput(SnapAudioStream):

		__slots__ = []	

		def __init__(self, DEVICE, **SETTINGS):
			SnapAudioStream.__init__(self, DEVICE, 'output', **SETTINGS)

	ENV.SnapAudioOutput = SnapAudioOutput

	class SnapAudioInput(SnapAudioStream):

		__slots__ = []

		def __init__(self, DEVICE, **SETTINGS):
			SnapAudioStream.__init__(self, DEVICE, 'input', **SETTINGS)
			
	ENV.SnapAudioInput = SnapAudioInput


	def get_supported_info(self, QINFO):
		# TODO this should handle subprocess branch
		return {
			'channels':[int(c) for c in QINFO.supportedChannelCounts()],
			'formats':[QTYPES[t] + str(s) for t in QINFO.supportedSampleTypes() for s in QINFO.supportedSampleSizes()],
			'rates':[int(r) for r in QINFO.supportedSampleRates()],
			#'codecs':[str(c) for c in QINFO.supportedCodecs()],
			#'byte_orders':[QENDIAN[b] for b in QINFO.supportedByteOrders()],
		}

	
	class SnapAudioDevice(SnapNode):

		__slots__ = []

		@ENV.SnapProperty
		class name:
			set = None
			def get(self, MSG):
				"()->str"
				return self.__snap_data__['name']

		@ENV.SnapProperty
		class server:
			set = None
			def get(self, MSG):
				"()->str"
				return self.__snap_data__['server'] # like 'alsa'

		@ENV.SnapProperty
		class inputs:
			set = None
			def get(self, MSG):
				"()->dict"

				inputs = self.__snap_data__['__input__']

				try:
					return inputs['supported']
				except:
					if not inputs:
						return None
					info = inputs['supported'] = get_supported_info(inputs['QInfo'])
					return info

				return None

		@ENV.SnapProperty
		class outputs:
			set = None
			def get(self, MSG):
				"()->dict"

				outputs = self.__snap_data__['__output__']

				try:
					return outputs['supported']
				except:
					if not outputs:
						return None
					info = outputs['supported'] = get_supported_info(outputs['QInfo'])
					return info

				return None

		@ENV.SnapProperty
		class is_default_output:
			set = None
			def get(self, MSG):
				"()->bool"
				try:
					return self.__snap_data__['__output__']['is_default']
				except:
					return False

		@ENV.SnapProperty
		class is_default_input:
			set = None
			def get(self, MSG):
				"()->bool"
				try:
					return self.__snap_data__['__input__']['is_default']
				except:
					return False				

		# TODO register the stream with the device so we can find them all through the audio api
		def OutputStream(self, **SETTINGS):
			return SnapAudioOutput(self, **SETTINGS)

		def InputStream(self, **SETTINGS):
			return SnapAudioInput(self, **SETTINGS)
				
		def __repr__(self):

			extras = []

			inputs = self.__snap_data__['__input__']
			if inputs and inputs.get('is_default'):
				extras.append('[in]')
			elif inputs.get('QInfo'):
				extras.append('+in')

			outputs = self.__snap_data__['__output__']
			if outputs and outputs.get('is_default'):
				extras.append('[out]')
			elif outputs.get('QInfo'):
				extras.append('+out')

			if extras:
				extras.insert(0, '|')
			return '{}("{}"{})'.format(self.__class__.__name__, self['name'], ''.join(extras))

		def __init__(self, **SETTINGS):
			SnapNode.__init__(self)


	ENV.SnapAudioDevice = SnapAudioDevice

	def register_device(self, QINFO, MODE, IS_DEFAULT):
		devices = self.__snap_data__['__devices__']
		if devices is None:
			devices = self.__snap_data__['__devices__'] = {}

		name = QINFO.deviceName()
		dev = devices.get(name)
		if dev:
			assert dev['name'] == name
			assert dev['server'] == QINFO.realm()
			# make sure mode isn't assigned?
			assert not dev.__snap_data__['__' + MODE + '__'], 'double assigned device? {}'.format((name, MODE, dev.__snap_data__['__' + MODE + '__']))
			x = dev.__snap_data__['__' + MODE + '__'] = {'QInfo':QINFO}
			if IS_DEFAULT:
				x['is_default'] = True
		else:
			dev = devices[name] = SnapAudioDevice()
			dev.__snap_data__['name'] = name
			dev.__snap_data__['server'] = QINFO.realm()
			for m in ('input','output'):
				x = {}
				if m == MODE:
					x = {'QInfo':QINFO}
					if IS_DEFAULT:
						x['is_default'] = True
				dev.__snap_data__['__' + m + '__'] = x
			

		return dev

	class SnapAudio(SnapNode):

		__slots__ = []

		@ENV.SnapProperty
		class devices:
			set = None
			def get(self, MSG):
				"()->SnapAudioDevice[]"

				devices = self.__snap_data__['__devices__']
				if devices is None:
					devices = self.__snap_data__['__devices__'] = {}

					# so defaults are at the front of the list
					default_output_name = self['default_output_device']['name']
					default_input_name = self['default_input_device']['name']

					for qinfo in QAudioDeviceInfo.availableDevices(QAudio.AudioOutput):
						if qinfo.deviceName() == default_output_name: continue
						register_device(self, qinfo, 'output', None)
					for qinfo in QAudioDeviceInfo.availableDevices(QAudio.AudioInput):
						if qinfo.deviceName() == default_input_name: continue
						register_device(self, qinfo, 'input', None)	
				
				return devices.values()

		@ENV.SnapProperty
		class default_output_device:
			set = None
			def get(self, MSG):
				"()->SnapAudioDevice"
				devices = self.__snap_data__['__devices__']
				if devices:
					for dev in devices.values():
						if dev['is_default_output']:
							return dev

				return register_device(self, QAudioDeviceInfo.defaultOutputDevice(), 'output', True)

		@ENV.SnapProperty
		class default_input_device:
			set = None
			def get(self, MSG):
				"()->SnapAudioDevice"
				devices = self.__snap_data__['__devices__']
				if devices:
					for dev in devices.values():
						if dev['is_default_input']:
							return dev

				return register_device(self, QAudioDeviceInfo.defaultInputDevice(), 'input', True)

		@ENV.SnapProperty
		class streams:
			def get(self, MSG):
				"()->SnapAudioStream[]"
				# TODO list of all open streams (in or out)
				# for device in open devices (just get list of already loaded devices), report the stream on it...
				devices = self.__snap_data__['__devices__']
				open_streams = []
				if devices:
					for device in devices.values():
						'get open streams on device' # TODO
						'add the streams to the open streams'
				return open_streams


	ENV.SnapAudio = SnapAudio


def main(ENV):

	import numpy

	SnapContainer = ENV.SnapContainer

	AUDIO = ENV.MEDIA.AUDIO

	class AudioTest(SnapContainer):

		def draw(self, CTX):
			''#print('draw')

		def generate_sound(self, BYTE_SIZE):

			FRAME_COUNT = BYTE_SIZE / 8. # size of one sample (float32 * 2channels = 8 bytes)

			duration = FRAME_COUNT / 44100.

			volume = .5

			t = numpy.linspace(self.time, self.time+duration, int(FRAME_COUNT), endpoint=False)

			left_channel = volume * numpy.sin(2 * numpy.pi * 261.6 * t)
			right_channel = volume * numpy.sin(2 * numpy.pi * 392 * t)

			stereo_data = numpy.empty((2 * len(left_channel),), dtype=numpy.float32)
			stereo_data[::2] = left_channel
			stereo_data[1::2] = right_channel

			self.time += duration

			return stereo_data.tobytes()

		def __init__(self):
			SnapContainer.__init__(self)

			#for device in AUDIO['devices']:
			#	print(device)

			self.time = 0.

			out = AUDIO['default_output_device']
			dev_in = AUDIO['default_input_device']

			self.stream = out.OutputStream(rate=44100, channels=2, format='float32', callback=self.generate_sound)
			self.stream.start()

			''
			#self.database = ENV.SnapAudioDeviceDatabase()
			#del self.database
			#for device in AUDIO['devices']:
			#	print(device['outputs'])

	ENV.__run_gui__(AudioTest)

if __name__ == '__main__':
	import snap; main(snap.SnapEnv())

