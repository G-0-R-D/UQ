
def build(ENV):

	ENV.__build__('snap.media.SnapAudio')

	class SnapMedia(object):

		__slots__ = []

		AUDIO = ENV.SnapAudio()

	ENV.MEDIA = SnapMedia()
