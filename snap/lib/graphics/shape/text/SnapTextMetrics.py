

def build(ENV):

	class SnapTextMetrics(object):

		__slots__ = ['__parent__']

		"""
		@ENV.SnapProperty
		class span:

			def get(self, MSG):
				"()->[int, int]"
				# just 0 and the length of text
				return [0, len(self)]
		"""

		def text_extents(self, start=None, end=None):
			# TODO lookup the lines involved, then handle as possible subtext?
			raise NotImplementedError('implement in subclass')

		def ink_extents(self, start=None, end=None):
			# implement if available in engine
			return self.text_extents(start, end)

		# TODO get a description for a path that outlines the text?  text_shape() and ink_shape()?

		# NOTE: we can start iterating newlines only or sublines from the beginning of the file...?
		def newlines(self, start=None, end=None):
			# returns list of spans representing the body of each newline (ignoring word wrap, use sublines for all lines)

			parent = self.__parent__
			if parent is None:
				raise ValueError('no parent to index into')

			text = parent['text']
			if not text:
				return []

			if start is None:
				start = 0
			if end is None:
				end = len(text)-1

			# spans are returned without the newline character included, and
			# if first or last character is newline, there will be a 0 width span at the start or end of the sequence
			indices = [start-1] + [idx for idx,val in enumerate(text) if val == '\n' and start <= idx <= end] + [end+1]
			return [(indices[idx]+1, indices[idx+1]) for idx in range(len(indices)-1)]

		# TODO make an iterator for 'text_blocks' which means runs of consecutive non-whitespace characters (words, kinda) (as spans)

		# TODO also make per-symbol iterator?  or that is just spans of delta 1!

		def sublines(self, start=None, end=None):
			#raise NotImplementedError('implement in subclass, this only exists if there is line wrap')
			return []

		def __init__(self, PARENT):

			# TODO listen to the SnapText for text changed?  and if it is then reload source?  or index error?

			self.__parent__ = PARENT

	# XXX TODO better option would be to just iterate the spans for the sublines?  and then we can get the size of a subsection of that span with a text_extents(line[:subtext]) sampling?  XXX except the lines have the height() and other metrics internally...

	ENV.SnapTextMetrics = SnapTextMetrics

def main(ENV):

	text = """
	to be or not to be
	that is the question
	for it is better than something
	or other
	amen
	"""

	m = ENV.SnapTextMetrics(ENV.SnapText(text=text))

	for s,e in m.newlines():
		print((s,e), repr(text[s:e]))

	ENV.snap_out("extents", m.__parent__['extents'][:])


if __name__ == '__main__':
	from snap.SnapEnv import SnapEnv
	SnapEnv().__run__('snap.lib.graphics.shape.text.SnapTextMetrics')

