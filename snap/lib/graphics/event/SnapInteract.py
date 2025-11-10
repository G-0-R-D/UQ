
def build(ENV):

	SnapNode = ENV.SnapNode

	class SnapInteract(SnapNode):

		__slots__ = []

		# TODO handle global and local events separately?

		# also: add properties like 'scale' to remap the float values...

	ENV.SnapInteract = SnapInteract

	class SnapInteractPointerButton(SnapInteract):

		__slots__ = []


	ENV.SnapInteractPointerButton = SnapInteractPointerButton

	class SnapInteractPointerMotion(SnapInteract):

		__slots__ = []

	ENV.SnapInteractPointerMotion = SnapInteractPointerMotion

	class SnapInteractPointerWheel(SnapInteract):

		__slots__ = []

	ENV.SnapInteractPointerWheel = SnapInteractPointerWheel


	class SnapInteractKeyboardKey(SnapInteract):

		__slots__ = []

	ENV.SnapInteractKeyboardKey = SnapInteractKeyboardKey
